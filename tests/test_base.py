""" ae.base unit tests """
import datetime
import os
import socket
import ssl
import string
import sys
import textwrap
import time
import timeit

from collections import OrderedDict
# noinspection PyProtectedMember
from http.client import HTTPMessage
from typing import Any, cast
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest

from tests.conftest import skip_gitlab_ci


from ae.base import (
    ASCII_TO_UNICODE, ASCII_UNICODE,
    TESTS_FOLDER, UNICODE_TO_ASCII, UNSET, URI_SEP_STR, URI_SEP_UNICODE_CHAR,
    ascii_dec_str, ascii_enc_lit, camel_to_snake, dedefuse, deep_dict_update, defuse, dummy_function, duplicates,
    env_str, evaluate_literal, extend_file, force_encoding, format_given, in_wd, mask_secrets, mask_url,
    norm_line_sep, norm_name, norm_path, now_str, on_ci_host,
    parse_date, pep8_format, read_bin_file, read_file, round_traditional, sign, snake_to_camel,
    to_ascii, url_failure, utc_datetime, write_bin_file, write_file)


tst_uni_str = "äáàâÄÁÀÂëéèêËÉÈÊïíìîÏÍÌÎńǹñŃǸÑöóòôÖÓÒÔßüúùûÜÚÙÛźẑŹẐ"

tst_uri1 = "schema://user:pwd@domain/path_root/path_sub\\path+file% Üml?ä|ït.path_ext*\"<>|*'()[]{}#^;&=$,~" + chr(127)
tst_fna1 = "schema⫻user﹕pwd﹫domain⁄path_root⁄path_sub﹨path﹢file﹪␣Üml﹖ä।ït.path_ext﹡＂⟨⟩।﹡‘⟮⟯⟦⟧﹛﹜﹟＾﹔﹠﹦﹩﹐~␡"
tst_uri2 = "test control chars" + "".join(chr(_) for _ in range(1, 32))
tst_fna2 = "test␣control␣chars␁␂␃␄␅␆␇␈␉␊␋␌␍␎␏␐␑␒␓␔␕␖␗␘␙␚␛␜␝␞␟"


def test_proof_os_path_join_shortcut_performance_win():
    att_call_setup = textwrap.dedent("""
    import os
    path1, path2, path3 = "folder1", "folder2", "file.tst"
    """)
    sho_call_setup = att_call_setup + textwrap.dedent("""
    os_path_join = os.path.join
    """)

    att_call_code = "os.path.join(path1, path2, path3)"
    sho_call_code = "os_path_join(path1, path2, path3)"

    time_att = timeit.timeit(att_call_code, setup=att_call_setup, number=3_000_000)
    time_sho = timeit.timeit(sho_call_code, setup=sho_call_setup, number=3_000_000)

    assert time_sho < time_att or sys.version_info[:2] == (3, 12)  # sometimes equal/not-faster in Python 3.12
    print(f"\n¡!¡!¡! os_path_join shortcut is ~{((time_att - time_sho) / time_att) * 100:.2f}% faster")


def test_proof_os_path_sep_shortcut_performance_win():
    att_call_setup = textwrap.dedent("""
    import os
    """)
    sho_call_setup = att_call_setup + textwrap.dedent("""
    import os
    os_path_sep = os.path.sep
    """)

    att_call_code = "var = os.path.sep"
    sho_call_code = "var = os_path_sep"

    time_att = timeit.timeit(att_call_code, setup=att_call_setup, number=3_000_000)
    time_sho = timeit.timeit(sho_call_code, setup=sho_call_setup, number=3_000_000)

    assert time_sho < time_att
    print(f"\n¡!¡!¡! os_path_sep shortcut is ~{((time_att - time_sho) / time_att) * 100:.2f}% faster")  # 40-50% faster!


class TestBaseHelpers:
    def test_ascii_dec_str(self):
        assert isinstance(ascii_dec_str(ascii_enc_lit("tst")), str)

        assert ascii_dec_str(ascii_enc_lit("tst")) == "tst"

        assert ascii_dec_str(ascii_enc_lit(tst_uni_str)) == tst_uni_str

        uni_str = "".join(_uco for _asc, _uco in ASCII_UNICODE)
        assert ascii_dec_str(ascii_enc_lit(uni_str)) == uni_str

        asc_str = "".join(_asc for _asc, _uco in ASCII_UNICODE)
        assert ascii_dec_str(ascii_enc_lit(asc_str)) == asc_str

    def test_ascii_dec_str_errors(self):
        with pytest.raises(SyntaxError):
            ascii_dec_str("")

        with pytest.raises(SyntaxError):
            ascii_dec_str("any tst string not detected as string literal (not encoded/converted via ascii_enc_lit())")

    def test_ascii_enc_lit(self):
        assert isinstance(ascii_enc_lit(""), str)

        assert all(ord(_) >= 128 for _ in tst_uni_str)
        assert all(ord(_) < 128 for _ in ascii_enc_lit(tst_uni_str))

        uni_str = "".join(_uco for _asc, _uco in ASCII_UNICODE)
        assert any(ord(_) >= 128 for _ in uni_str)
        assert all(ord(_) < 128 for _ in ascii_enc_lit(uni_str))

        asc_str = "".join(_asc for _asc, _uco in ASCII_UNICODE)
        assert any(ord(_) < 128 for _ in asc_str)
        assert all(ord(_) < 128 for _ in ascii_enc_lit(asc_str))

    def test_camel_to_snake(self):
        assert camel_to_snake("AnyCamelCaseName") == "_Any_Camel_Case_Name"
        assert camel_to_snake("anyCamelCaseName") == "any_Camel_Case_Name"

        assert camel_to_snake("_under_score") == "_under_score"
        assert camel_to_snake("any_name") == "any_name"
        assert camel_to_snake("@special/chars!") == "@special/chars!"

    def test_deep_dict_update_empty(self):
        str_val = "str_val"
        upd = {'setup_kwargs': {'entry_points': {'console_scripts': str_val}}}

        ori = {}
        deep_dict_update(ori, upd)
        assert ori
        assert 'setup_kwargs' in ori
        assert 'entry_points' in ori['setup_kwargs']
        assert 'console_scripts' in ori['setup_kwargs']['entry_points']
        assert ori['setup_kwargs']['entry_points']['console_scripts'] == str_val

        ori = {}
        deep_dict_update(ori, upd, overwrite=False)
        assert ori
        assert 'setup_kwargs' in ori
        assert 'entry_points' in ori['setup_kwargs']
        assert 'console_scripts' in ori['setup_kwargs']['entry_points']
        assert ori['setup_kwargs']['entry_points']['console_scripts'] == str_val

    def test_deep_dict_update_half_empty_ordered(self):
        str_val = "str_val"
        lst_val = [str_val]
        upd = {'setup_kwargs': {'entry_points': {'console_scripts': lst_val}}}

        ori: dict[str, Any] = OrderedDict({'setup_kwargs': {'untouched_key1': "untouched val 1"},
                                           'untouched_key2': "untouched val 2"})
        deep_dict_update(ori, upd)
        assert ori
        assert 'setup_kwargs' in ori
        assert 'entry_points' in ori['setup_kwargs']
        assert 'console_scripts' in ori['setup_kwargs']['entry_points']
        assert ori['setup_kwargs']['entry_points']['console_scripts'] == lst_val
        assert ori['setup_kwargs']['entry_points']['console_scripts'][0] == str_val
        assert ori['untouched_key2'] == "untouched val 2"
        assert ori['setup_kwargs']['untouched_key1'] == "untouched val 1"
        assert list(ori.keys()) == ['setup_kwargs', 'untouched_key2']
        assert list(ori['setup_kwargs'].keys()) == ['untouched_key1', 'entry_points']

        ori: dict[str, Any] = OrderedDict({'setup_kwargs': {'untouched_key1': "untouched val 1"},
                                           'untouched_key2': "untouched val 2"})
        deep_dict_update(ori, upd, overwrite=False)
        assert ori
        assert 'setup_kwargs' in ori
        assert 'entry_points' in ori['setup_kwargs']
        assert 'console_scripts' in ori['setup_kwargs']['entry_points']
        assert ori['setup_kwargs']['entry_points']['console_scripts'] == lst_val
        assert ori['setup_kwargs']['entry_points']['console_scripts'][0] == str_val
        assert ori['untouched_key2'] == "untouched val 2"
        assert ori['setup_kwargs']['untouched_key1'] == "untouched val 1"
        assert list(ori.keys()) == ['setup_kwargs', 'untouched_key2']
        assert list(ori['setup_kwargs'].keys()) == ['untouched_key1', 'entry_points']

    def test_deep_dict_update_full(self):
        str_old = "old_val"
        str_new = "new_val"
        lst_val = [str_new]
        upd = {'setup_kwargs': {'entry_points': {'console_scripts': lst_val}}}

        ori = {'setup_kwargs': {'entry_points': {'console_scripts': str_old}}}
        deep_dict_update(ori, upd)
        assert ori
        assert 'setup_kwargs' in ori
        assert 'entry_points' in ori['setup_kwargs']
        assert 'console_scripts' in ori['setup_kwargs']['entry_points']
        assert ori['setup_kwargs']['entry_points']['console_scripts'] == lst_val
        assert ori['setup_kwargs']['entry_points']['console_scripts'][0] == str_new

        ori = {'setup_kwargs': {'entry_points': {'console_scripts': str_old}}}
        deep_dict_update(ori, upd, overwrite=False)
        assert ori
        assert 'setup_kwargs' in ori
        assert 'entry_points' in ori['setup_kwargs']
        assert 'console_scripts' in ori['setup_kwargs']['entry_points']
        assert ori['setup_kwargs']['entry_points']['console_scripts'] == str_old
        assert ori['setup_kwargs']['entry_points']['console_scripts'][0] == str_old[0]

    def test_dedefuse_file_name(self):
        assert dedefuse(tst_fna1) == tst_uri1
        assert dedefuse(tst_fna2) == tst_uri2

        assert dedefuse(defuse(tst_uri1)) == tst_uri1
        assert dedefuse(defuse(tst_uri2)) == tst_uri2

    def test_defuse_file_name(self):
        assert defuse(tst_uri1) == tst_fna1
        assert defuse(tst_uri2) == tst_fna2

        assert defuse(dedefuse(tst_fna1)) == tst_fna1
        assert defuse(dedefuse(tst_fna2)) == tst_fna2

    def test_defuse_os_file_name(self):
        try:
            write_file(tst_fna1, "tst uri file content1")
            assert os.path.exists(tst_fna1)
            write_file(tst_fna2, "tst uri file content2")
            assert os.path.exists(tst_fna2)
        finally:
            if os.path.exists(tst_fna1):
                os.remove(tst_fna1)
            if os.path.exists(tst_fna2):
                os.remove(tst_fna2)

    def test_defuse_maps_integrity(self):
        assert len(ASCII_TO_UNICODE) == len(ASCII_UNICODE)      # duplicates check in ASCII_UNICODE map
        assert len(UNICODE_TO_ASCII) == len(ASCII_UNICODE) + 1  # -"-, having also the ord(URI_SEP_UNICODE_CHAR) key
        assert ord(URI_SEP_UNICODE_CHAR) in UNICODE_TO_ASCII
        assert UNICODE_TO_ASCII[ord(URI_SEP_UNICODE_CHAR)] == URI_SEP_STR

    def test_defuse_maps_not_touching_chars_allowed_as_slug_and_filename(self):
        assert ord('-') not in ASCII_TO_UNICODE
        assert ord('_') not in ASCII_TO_UNICODE
        assert ord('.') not in ASCII_TO_UNICODE
        assert ord('~') not in ASCII_TO_UNICODE
        for char in string.ascii_letters + string.digits:
            assert ord(char) not in ASCII_TO_UNICODE

    def test_dummy_function(self):
        assert dummy_function() is None
        assert dummy_function(999, "any_args") is None
        assert dummy_function(3, kw_arg1=3, kw_arg2="6") is None

    def test_duplicates(self):
        lst = ['a', 3, 'bb', 3, 'ccc', 3]
        assert duplicates(lst) == [3, 3]

    def test_env_str_unconverted(self):
        ev = 'PATH'
        assert env_str(ev)

    def test_env_str_case_conversions(self):
        ev = 'path'
        assert env_str(ev, convert_name=True)

        ev = 'camelCase'
        vv = "test variable value"
        os.environ['CAMEL_CASE'] = vv
        assert env_str(ev, convert_name=True) == vv

        ev = 'CamelCase'
        vv = "test variable value"
        os.environ['_CAMEL_CASE'] = vv
        assert env_str(ev, convert_name=True) == vv

    def test_env_str_non_alpha_num_conversions(self):
        ev = 'non\talpha\\num/chars-69'
        vv = "test variable value"
        os.environ['NON_ALPHA_NUM_CHARS_69'] = vv
        assert env_str(ev, convert_name=True) == vv

    def test_evaluate_literal(self):
        tst_str = "unquoted string"

        assert evaluate_literal(tst_str) == tst_str                 # actually: evaluate_literal(tst_str) is tst_str

        assert evaluate_literal("'" + tst_str + "'") == tst_str

        tst_dict = dict(a=1, b=[dict(b3=3), (1, 2, 3), set()])

        assert evaluate_literal(repr(tst_dict)) == tst_dict

    def test_evaluate_literal_errors(self):
        assert evaluate_literal("") == ""

        # noinspection PyTypeChecker
        assert evaluate_literal(None) is None                       # raising ValueError: malformed node or string: None

        tst = dict(a=1, b=[dict(b3=3), (1, "22", 333), set()])

        if sys.version_info < (3, 10):
            assert evaluate_literal("    " + repr(tst) + "    ") == "    " + repr(tst) + "    "  # IndentationError
        else:
            assert evaluate_literal("    " + repr(tst) + "    ") == tst     # no longer raises IndentationError

        assert evaluate_literal(repr(tst) + "    ") == tst          # trailing white space chars are ok

        # noinspection PyTypeChecker
        assert evaluate_literal(tst) is tst

    def test_extend_file(self, tmp_path):
        test_file = os.path.join(str(tmp_path), 'tst_file_written.ext')
        content = "any content"
        assert not os.path.exists(test_file)

        extend_file(test_file, content)
        assert os.path.exists(test_file)
        assert os.path.isfile(test_file)
        assert read_file(test_file) == content

    def test_extend_file_make_dirs(self, tmp_path):
        root_dir = os.path.join(str(tmp_path), 'root path of file')
        test_dir = os.path.join(root_dir, '1st sub dir of file', 'subDir2')
        test_file = os.path.join(test_dir, 'file in sub dir.ext')
        content = "any content"
        assert not os.path.exists(test_dir)
        assert not os.path.exists(test_file)

        with pytest.raises(FileNotFoundError):
            extend_file(test_file, content)
        extend_file(test_file, content, make_dirs=True)
        assert os.path.exists(test_dir)
        assert os.path.isdir(test_dir)
        assert os.path.exists(test_file)
        assert os.path.isfile(test_file)
        assert read_file(test_file) == content

    def test_force_encoding_bytes(self):
        s = 'äöü'

        assert s.encode('ascii', errors='replace') == b'???'
        ba = s.encode('ascii', errors='backslashreplace')   # == b'\\xe4\\xf6\\xfc'
        assert force_encoding(ba, encoding='ascii') == str(ba, encoding='ascii')
        assert force_encoding(ba) == str(ba, encoding='ascii')

        bw = s.encode('cp1252')                             # == b'\xe4\xf6\xfc'
        assert force_encoding(bw, encoding='cp1252') == s
        with pytest.raises(UnicodeDecodeError):
            force_encoding(bw)

    def test_force_encoding_umlaut(self):
        tst_str = "äöü"
        enc_str = "\\xe4\\xf6\\xfc"
        assert force_encoding(tst_str) == enc_str

        assert force_encoding(tst_str, encoding='utf-8') == tst_str
        assert force_encoding(tst_str, encoding='utf-16') == tst_str
        assert force_encoding(tst_str, encoding='cp1252') == tst_str

        assert force_encoding(tst_str, encoding='utf-8', errors='strict') == tst_str
        assert force_encoding(tst_str, encoding='utf-8', errors='replace') == tst_str
        assert force_encoding(tst_str, encoding='utf-8', errors='backslashreplace') == tst_str
        assert force_encoding(tst_str, encoding='utf-8', errors='xmlcharrefreplace') == tst_str
        assert force_encoding(tst_str, encoding='utf-8', errors='ignore') == tst_str
        assert force_encoding(tst_str, encoding='utf-8', errors='') == tst_str

        with pytest.raises(TypeError):
            # noinspection PyInvalidCast
            assert force_encoding(tst_str, encoding=cast(str, None)) == enc_str

    def test_format_given(self):
        assert format_given("test text with {placeholder}", {}) == "test text with {placeholder}"
        assert format_given("test text with {placeholder:.2e}", {}) == "test text with {placeholder:.2e}"
        assert format_given("a {placeholder} {{test}}", {}) == "a {placeholder} {test}"

        assert format_given("test text with {placeholder}", {'placeholder': "replaced"}) == "test text with replaced"
        assert format_given("test text with {placeholder:.2e}", {'placeholder': 3.14159}) == "test text with 3.14e+00"

        assert format_given("a {ph} {{test}}", {'ph': "rep"}) == "a rep {test}"
        assert format_given("a {{ph}} {test}", {'ph': "rep"}) == "a {ph} {test}"
        assert format_given("a {{ph} {test}}", {'ph': "rep"}) == "a {{ph} {test}}"

        assert format_given("a non-ph}", {'ph': "rep"}) == "a non-ph}"
        assert format_given("a non-{ph", {'ph': "rep"}) == "a non-{ph"

    def test_format_given_err(self):
        with pytest.raises(ValueError):
            format_given("test text with {placeholder", {}, strict=True)     # missing closing curly bracket
        with pytest.raises(ValueError):
            format_given("test text with placeholder}", {}, strict=True)     # missing opening curly bracket

    def test_in_wd(self, tmp_path):
        old_dir = os.getcwd()
        tst_dir = str(tmp_path)
        with in_wd(tst_dir):
            assert os.getcwd() == tst_dir
        assert os.getcwd() == old_dir

    def test_mask_secrets(self):
        assert mask_secrets({}) == {}
        assert mask_secrets([]) == []
        assert mask_secrets(tuple()) == ()
        assert mask_secrets("") == ""

        assert mask_secrets({'password': "secret"}) == {'password': "sec*********"}
        assert mask_secrets({'PASSWORD': "secret"}) == {'PASSWORD': "sec*********"}
        assert mask_secrets([{'pwd': "secret"}, "any"]) == [{'pwd': "sec*********"}, "any"]
        assert mask_secrets([{'Pwd': "secret"}, "Any"]) == [{'Pwd': "sec*********"}, "Any"]

        assert mask_secrets({'secret': "secret"}, fragments=('token', 'secret')) == {'secret': "sec*********"}
        assert mask_secrets({'_token': "secret"}, fragments=('token', 'secret')) == {'_token': "sec*********"}
        assert mask_secrets({'_token': "secret"}, fragments=('TOKEN', 'secret')) == {'_token': "secret"}

        untouched = 'untouched_Pw_d_p_a_s_s_word'
        dat = {'key1': {'subKey1': (
                                    {'host_Pwd': "secret"},
                                    untouched,
                                    ),
                        'passWord___': "secRet",
                        },
               'any_PASSWORD_to_hide': "Se",
               untouched: untouched,
               }
        assert mask_secrets(dat) is dat
        # noinspection PyTypeChecker
        assert dat['key1']['subKey1'][0]['host_Pwd'] == "sec*********"
        assert dat['key1']['passWord___'] == "sec*********"
        assert dat['any_PASSWORD_to_hide'] == "Se*********"

        assert dat['key1']['subKey1'][1] == untouched
        assert dat[untouched] == untouched

    def test_mask_url(self):
        assert mask_url("") == ""

        password, domain, path = "toBeMaskedPassword", "any-not_existing-host_domain.zzz", "any/not/existing/url/path"

        url = f"https://username:{password}@{domain}/{path}"
        assert password not in mask_url(url)
        assert domain in mask_url(url)
        assert path in mask_url(url)

        url = f"https://username@{domain}:8081/{path}"
        assert mask_url(url) == url

    def test_norm_line_sep(self):
        assert norm_line_sep('a\r\nb') == 'a\nb'
        assert norm_line_sep('a\rb') == 'a\nb'

    def test_norm_name(self):
        assert norm_name("AnyCamelCaseName") == "AnyCamelCaseName"
        assert norm_name("anyCamelCaseName") == "anyCamelCaseName"
        assert norm_name("NoUnderScoreOnNone") == "NoUnderScoreOnNone"
        assert norm_name("any_name") == "any_name"
        # noinspection SpellCheckingInspection
        assert norm_name("äáßñìÄÏÜ") == "äáßñìÄÏÜ"
        assert norm_name("@special/chars!:;-`¡'´") == "_special_chars________"
        assert norm_name("abc123") == "abc123"
        assert norm_name("123abc") == "_23abc"
        assert norm_name("123abc", allow_num_prefix=True) == "123abc"

    def test_norm_path(self):
        new_folder = "non_existent_folder"
        tst_cwd = os.getcwd()
        
        assert norm_path(".") == tst_cwd
        assert norm_path(".", resolve_sym_links=False) == tst_cwd
        assert norm_path(".", make_absolute=False) == tst_cwd
        assert norm_path(".", make_absolute=False, remove_base_path=tst_cwd) == "."

        assert norm_path(new_folder) == os.path.join(tst_cwd, new_folder)
        assert norm_path(new_folder, resolve_sym_links=False) == os.path.join(tst_cwd, new_folder)
        assert norm_path(new_folder, make_absolute=False) == os.path.join(tst_cwd, new_folder)
        assert norm_path(new_folder, make_absolute=False, remove_base_path=tst_cwd) == new_folder

        assert norm_path(os.path.join(TESTS_FOLDER, "..")) == tst_cwd
        assert norm_path(os.path.join(TESTS_FOLDER, ".."), resolve_sym_links=False) == tst_cwd
        assert norm_path(os.path.join(TESTS_FOLDER, ".."), make_absolute=False) == tst_cwd
        assert norm_path(os.path.join("ae", ".."), make_absolute=False, remove_base_path=tst_cwd) == "."

        assert norm_path("~") != ""
        assert norm_path(os.path.join("~", new_folder)).endswith(new_folder)
        assert norm_path(os.path.join("~", new_folder), remove_base_path="~").endswith(new_folder)

        assert norm_path(TESTS_FOLDER + "\\" + "..") == tst_cwd

    def test_now_str(self):
        assert len(now_str()) == 20
        assert len(now_str("_")) == 23

    @skip_gitlab_ci
    def test_on_ci_host_local(self):
        assert not on_ci_host()

    def test_on_ci_host_on_gitlab(self):
        assert on_ci_host() == ('CI_PROJECT_ID' in os.environ)

    @skip_gitlab_ci
    def test_on_ci_host_with_ci_var(self, monkeypatch):
        assert not on_ci_host()

        monkeypatch.setenv('CI', "any value")
        assert on_ci_host()

    @skip_gitlab_ci
    def test_on_ci_host_with_ci_project_id(self, monkeypatch):
        assert not on_ci_host()

        monkeypatch.setenv('CI_PROJECT_ID', "any value")
        assert on_ci_host()

    def test_parse_date_only(self):
        assert parse_date('2033-12-24') == datetime.datetime(year=2033, month=12, day=24)
        assert parse_date('2033-12-24', ret_date=True) == datetime.date(year=2033, month=12, day=24)
        assert parse_date('2033-12-24', ret_date=None) == datetime.date(year=2033, month=12, day=24)

    def test_parse_date_hour_min(self):
        assert parse_date('2033-12-24 12:59') == datetime.datetime(year=2033, month=12, day=24, hour=12, minute=59)
        assert parse_date('2033-12-24 12:59', ret_date=True) == datetime.date(year=2033, month=12, day=24)
        assert parse_date('2033-12-24 12:59', ret_date=None) == datetime.datetime(year=2033, month=12, day=24,
                                                                                  hour=12, minute=59)

        assert parse_date('2033-12-24T12:59') == datetime.datetime(year=2033, month=12, day=24, hour=12, minute=59)
        assert parse_date('2033-12-24T12:59', ret_date=True) == datetime.date(year=2033, month=12, day=24)
        assert parse_date('2033-12-24T12:59', ret_date=None) == datetime.datetime(year=2033, month=12, day=24,
                                                                                  hour=12, minute=59)

    def test_parse_date_hour_min_sec(self):
        assert parse_date('2033-12-24 12:59:12') == datetime.datetime(year=2033, month=12, day=24, hour=12,
                                                                      minute=59, second=12)
        assert parse_date('2033-12-24 12:59:12', ret_date=True) == datetime.date(year=2033, month=12, day=24)
        assert parse_date('2033-12-24 12:59:12', ret_date=None) == datetime.datetime(year=2033, month=12, day=24,
                                                                                     hour=12, minute=59, second=12)

        assert parse_date('2033-12-24T12:59:12') == datetime.datetime(year=2033, month=12, day=24,
                                                                      hour=12, minute=59, second=12)
        assert parse_date('2033-12-24T12:59:12', ret_date=True) == datetime.date(year=2033, month=12, day=24)
        assert parse_date('2033-12-24T12:59:12', ret_date=None) == datetime.datetime(year=2033, month=12, day=24,
                                                                                     hour=12, minute=59, second=12)

        assert parse_date('2033-1-2 3:4:5') == datetime.datetime(year=2033, month=1, day=2, hour=3, minute=4, second=5)
        assert parse_date('2033-1-2 3:4:5', ret_date=True) == datetime.date(year=2033, month=1, day=2)
        assert parse_date('2033-1-2 3:4:5', ret_date=None) == datetime.datetime(year=2033, month=1, day=2,
                                                                                hour=3, minute=4, second=5)

        assert parse_date('2033-1-2 3:4:5.6') == datetime.datetime(
            year=2033, month=1, day=2, hour=3, minute=4, second=5, microsecond=600000)
        assert parse_date('2033-1-2 3:4:5.6', ret_date=True) == datetime.date(year=2033, month=1, day=2)
        assert parse_date('2033-1-2 3:4:5.6', ret_date=None) == datetime.datetime(
            year=2033, month=1, day=2, hour=3, minute=4, second=5, microsecond=600000)

    def test_parse_date_invalid(self):
        assert parse_date('2033-12-24 12:59:12:36') is None
        assert parse_date('2033-12-24 12:59.678') is None
        assert parse_date('xx-yy-zz a:b:c') is None
        assert parse_date(cast(str, cast(object, None))) is None

    def test_pep8_format(self):
        assert pep8_format(3.690) == "3.69"
        assert pep8_format(99) == "99"
        assert pep8_format(False) == "False"
        assert pep8_format(True) == "True"

        assert pep8_format([]) == "[]"
        assert pep8_format({}) == "{}"

        assert pep8_format({}, indent_level=1) == "{}"
        assert pep8_format({}, indent_level=2) == "{}"

    def test_pep8_format_deep(self):
        sp = " " * 4

        assert pep8_format([1, [2, 3], 4]) == "[\n    1,\n    [\n        2,\n        3,\n    ],\n    4,\n]"
        assert pep8_format([1, [2, 3], 4]) == f"[\n{sp}1,\n{sp}[\n{sp}{sp}2,\n{sp}{sp}3,\n{sp}],\n{sp}4,\n]"

        assert pep8_format([1, [2]], indent_level=1) == "[\n        1,\n        [\n            2,\n        ],\n    ]"
        assert pep8_format([1, [2]], indent_level=1) == f"[\n{sp}{sp}1,\n{sp}{sp}[\n{sp}{sp}{sp}2,\n{sp}{sp}],\n{sp}]"

        value = {
            'a': [
                1,
                {
                    2: 3
                },
            ],
            'b': [
                'c',
                3,
                {
                    'd': '',
                },
            ],
            True: False,
        }
        assert evaluate_literal(pep8_format(value)) == value
        assert pep8_format(value) == textwrap.dedent("""\
            {
                'a': [
                    1,
                    {
                        2: 3,
                    },
                ],
                'b': [
                    'c',
                    3,
                    {
                        'd': '',
                    },
                ],
                True: False,
            }""")

    def test_read_bin_file(self):
        with open(__file__, mode='rb') as file_handle:
            content = file_handle.read()
        assert read_bin_file(__file__) == content
        assert read_bin_file(__file__) == bytes(read_file(__file__), 'utf8')

    def test_read_file(self):
        with open(__file__) as file_handle:
            content = file_handle.read()
        assert read_file(__file__) == content
        assert read_file(__file__) == read_bin_file(__file__).decode(encoding='utf8')

    def test_round_traditional(self):
        assert round_traditional(1.01) == 1
        assert round_traditional(10.1, -1) == 10
        assert round_traditional(1.123, 1) == 1.1
        assert round_traditional(0.5) == 1
        assert round_traditional(0.5001, 1) == 0.5

        assert round_traditional(0.075, 2) == 0.08
        assert round(0.075, 2) == 0.07

    def test_sign_with_float_arg(self):
        assert sign(1.11) == 1
        assert sign(-0.000003) == -1
        assert sign(0.0000000) == 0
        assert sign(-0.0) == 0

    def test_sign_with_int_arg(self):
        assert sign(3) == 1
        assert sign(-6) == -1
        assert sign(0) == 0
        assert sign(-0) == 0

    def test_sign_with_invalid_arg(self):
        with pytest.raises(TypeError):
            # noinspection PyArgumentList
            sign()

        with pytest.raises(TypeError):
            # noinspection PyArgumentList,PyTypeChecker
            sign(None)

        with pytest.raises(TypeError):
            # noinspection PyArgumentList,PyTypeChecker
            sign(UNSET)

    def test_snake_to_camel(self):
        assert snake_to_camel("_Any_Camel_Case_Name") == "AnyCamelCaseName"
        assert snake_to_camel("any_Camel_Case_Name") == "AnyCamelCaseName"
        assert snake_to_camel("any_Camel_Case_Name", back_convertible=True) == "anyCamelCaseName"

        assert snake_to_camel("houseMen") == "Housemen"
        assert snake_to_camel("any_name") == "AnyName"
        assert snake_to_camel("any_name", back_convertible=True) == "anyName"
        assert snake_to_camel("@special/chars!") == "@special/chars!"

    def test_to_ascii(self):
        assert to_ascii("áéí óú") == "aei ou"
        assert to_ascii("ÁÉÍ ÓÚ") == "AEI OU"

        assert to_ascii("àèì òù") == "aei ou"
        assert to_ascii("ÀÈÌ ÒÙ") == "AEI OU"

        assert to_ascii("äëï öü") == "aei ou"
        assert to_ascii("ÄËÏ ÖÜ") == "AEI OU"

        assert to_ascii("âêî ôû") == "aei ou"
        assert to_ascii("ÂÊÎ ÔÛ") == "AEI OU"

        assert to_ascii("ß") == "ss"
        assert to_ascii("€") == "Euro"

    def test_to_ascii_length(self):
        assert to_ascii(tst_uni_str)
        assert len(to_ascii(tst_uni_str)) == len(tst_uni_str) + 1   # +1 because "ß" gets converted into "ss"
        assert len(to_ascii("€")) == 4  # == "Euro"

    @staticmethod
    def url_failure_httpbin_50x_retryer(url: str, timeout: float | None = None) -> tuple[str, str]:
        """ retry if httpbin is unavailable with 503 error (sometimes 502) """
        retries = 9
        while True:
            err_msg = url_failure(url, timeout=timeout)
            if not err_msg or int(err_msg[:3]) not in (502, 503) or retries == 0:
                break
            time.sleep(3)
            retries -= 1
        return err_msg, f"url_failure({url=}, {timeout=}) httpbin is sometimes unavailable/503. retry later; {err_msg=}"

    def test_url_failure(self):
        assert not url_failure("https://gitlab.com/ae-group/ae_base")

        assert not url_failure("https://gitlab.com/ae-group/ae_base.git")

        assert not url_failure("https://gitlab.com/ae-group/ae_base", git_repo=True)

        assert not url_failure("https://www.google.com")

        if not on_ci_host():
            ret, message = self.url_failure_httpbin_50x_retryer("https://httpbin.org/status/200")
            assert not ret, message

    def test_url_failure_authentication_errors(self):
        password, domain, path = "toBeMaskedPassword", "any-not_existing-host_domain.zzz", "any/not/existing/url/path"
        url = f"https://username:{password}@{domain}/{path}"
        err_msg = "raised exception error message"

        ret = url_failure(url, token=password)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret

        ret = url_failure(url, username="any user name", password=password)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret

        ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret

        # noinspection PyInvalidCast
        mocked_headers = cast(HTTPMessage, {})

        def _mock_raise_http_error404(*_args, **_kwargs):
            raise HTTPError(url=url, code=404, msg=err_msg, hdrs=mocked_headers, fp=None)

        with patch('ae.base.urlopen', _mock_raise_http_error404):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert err_msg in ret

        def _mock_raise_http_error503(*_args, **_kwargs):
            raise HTTPError(url=url, code=503, msg=err_msg, hdrs=mocked_headers, fp=None)

        with patch('ae.base.urlopen', _mock_raise_http_error503):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert err_msg in ret

        def _mock_raise_gai_error(*_args, **_kwargs):
            raise URLError(reason=socket.gaierror(err_msg))

        with patch('ae.base.urlopen', _mock_raise_gai_error):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert err_msg in ret

        def _mock_raise_timeout(*_args, **_kwargs):
            raise URLError(reason=socket.timeout(err_msg))

        with patch('ae.base.urlopen', _mock_raise_timeout):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert err_msg in ret

        def _mock_raise_socket_timeout(*_args, **_kwargs):
            raise socket.timeout(err_msg)

        with patch('ae.base.urlopen', _mock_raise_socket_timeout):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert f"{mask_url(url)} raised socket-timeout exception" in ret

        def _mock_raise_ssl_error(*_args, **_kwargs):
            raise URLError(reason=ssl.SSLCertVerificationError(1, err_msg))

        with patch('ae.base.urlopen', _mock_raise_ssl_error):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert err_msg in ret

        def _mock_raise_generic_url_error(*_args, **_kwargs):
            raise URLError(reason=err_msg)

        with patch('ae.base.urlopen', _mock_raise_generic_url_error):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert err_msg in ret

        def _mock_raise_unexpected_error(*_args, **_kwargs):
            raise ValueError(err_msg)

        with patch('ae.base.urlopen', _mock_raise_unexpected_error):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret

    def test_url_failure_ssl_errors(self):
        ret = url_failure(f"https://expired.badssl.com")

        assert ret
        assert int(ret[:3]) > 0

    @skip_gitlab_ci
    def test_url_failure_timeout_errors(self):
        ret, message = self.url_failure_httpbin_50x_retryer("https://httpbin.org/delay/3", timeout=0.9)

        assert ret, message
        assert ret[:3] == '997', message

    @skip_gitlab_ci
    def test_url_failure_url_errors(self):
        assert url_failure("")

        ret, message = self.url_failure_httpbin_50x_retryer(url2 := "https://httpbin.org/status/504")

        assert ret, message
        assert ret[:3] == '504', message
        assert ret[4:].startswith(mask_url(url2)), message

        with pytest.raises(AttributeError):
            # noinspection PyInvalidCast
            url_failure(cast(str, 123456))

    def test_utc_datetime(self):
        dt1 = utc_datetime()
        dt2 = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        assert dt2 - dt1 < datetime.timedelta(seconds=1)

    def test_write_bin_file(self, tmp_path):
        test_file = os.path.join(str(tmp_path), 'bin_file_written.ext')
        content = b"any content"
        assert not os.path.exists(test_file)

        write_bin_file(test_file, content)
        assert os.path.exists(test_file)
        assert os.path.isfile(test_file)
        assert read_bin_file(test_file) == content

        new_content = b"pre" + content + b"post"
        write_bin_file(test_file, new_content)  # overwrite
        assert os.path.exists(test_file)
        assert os.path.isfile(test_file)
        assert read_bin_file(test_file) == new_content

    def test_write_bin_file_make_dirs(self, tmp_path):
        root_dir = os.path.join(str(tmp_path), 'root path of file')
        test_dir = os.path.join(root_dir, '1st sub dir of file', 'subDir2')
        test_file = os.path.join(test_dir, 'file in sub dir.ext')
        content = b"any binary content"
        assert not os.path.exists(test_dir)
        assert not os.path.exists(test_file)

        with pytest.raises(FileNotFoundError):
            write_bin_file(test_file, content)
        write_bin_file(test_file, content, make_dirs=True)
        assert os.path.exists(test_dir)
        assert os.path.isdir(test_dir)
        assert os.path.exists(test_file)
        assert os.path.isfile(test_file)
        assert read_bin_file(test_file) == content

    def test_write_file(self, tmp_path):
        test_file = os.path.join(str(tmp_path), 'tst_file_written.ext')
        content = "any content"
        assert not os.path.exists(test_file)

        write_file(test_file, content)
        assert os.path.exists(test_file)
        assert os.path.isfile(test_file)
        assert read_file(test_file) == content

    def test_write_file_make_dirs(self, tmp_path):
        root_dir = os.path.join(str(tmp_path), 'root path of file')
        test_dir = os.path.join(root_dir, '1st sub dir of file', 'subDir2')
        test_file = os.path.join(test_dir, 'file in sub dir.ext')
        content = "any content"
        assert not os.path.exists(test_dir)
        assert not os.path.exists(test_file)

        with pytest.raises(FileNotFoundError):
            write_file(test_file, content)
        write_file(test_file, content, make_dirs=True)
        assert os.path.exists(test_dir)
        assert os.path.isdir(test_dir)
        assert os.path.exists(test_file)
        assert os.path.isfile(test_file)
        assert read_file(test_file) == content


class TestUnsetType:
    def test_unset_truthiness(self):
        assert bool(UNSET) is False
        assert not UNSET

    def test_unset_null_length(self):
        assert len(UNSET) == 0
