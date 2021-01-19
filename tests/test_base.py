""" ae.base unit tests """
import os
import pytest
import sys

from typing import cast

# noinspection PyProtectedMember
from ae.base import (
    app_name_guess, camel_to_snake, env_str, file_content, file_lines, file_write, force_encoding,
    norm_line_sep, norm_name, now_str, round_traditional, snake_to_camel,
    sys_env_dict, sys_env_text, os_host_name, os_local_ip, _os_platform, os_user_name, to_ascii)


class TestHelpers:
    def test_app_name_guess(self):
        assert app_name_guess()     # app.exe name in pytest returning '_jb_pytest_runner'(PyCharm)/'__main__'(console)
        assert app_name_guess() != 'main'
        assert app_name_guess() == 'ae_base'

    def test_camel_to_snake(self):
        assert camel_to_snake("AnyCamelCaseName") == "_Any_Camel_Case_Name"
        assert camel_to_snake("anyCamelCaseName") == "any_Camel_Case_Name"

        assert camel_to_snake("_under_score") == "_under_score"
        assert camel_to_snake("any_name") == "any_name"
        assert camel_to_snake("@special/chars!") == "@special/chars!"

    def test_env_var_unconverted(self):
        ev = 'PATH'
        assert env_str(ev)

    def test_env_var_case_conversions(self):
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

    def test_env_var_non_alpha_num_conversions(self):
        ev = 'non\talpha\\num/chars-69'
        vv = "test variable value"
        os.environ['NON_ALPHA_NUM_CHARS_69'] = vv
        assert env_str(ev, convert_name=True) == vv

    def test_file_content(self):
        text = "line1\nline2\rline3\r\n"
        fnm = "tests/tst_content.txt"
        try:
            file_write(text, fnm)
            assert file_content(fnm) == norm_line_sep(text)

            file_write(norm_line_sep(text), fnm)
            assert file_content(fnm) == norm_line_sep(text)
        finally:
            if os.path.exists(fnm):
                os.remove(fnm)

    def test_file_content_error(self):
        assert file_content("tests/not_existing file.xxx") == ""
        assert file_content(":invalid \\=// file name....") == ""

    def test_file_lines(self):
        text = "line1\nline2\rline3\r\n"
        fnm = "tests/tst_lines.txt"
        try:
            file_write(text, fnm)
            assert file_lines(fnm) == tuple(norm_line_sep(text).split("\n"))
        finally:
            if os.path.exists(fnm):
                os.remove(fnm)

    def test_file_write(self):
        text = "line1\nline2\rline3\r\n"
        fnm = "tests/tst_write.txt"
        try:
            assert file_write(text, fnm)
            assert file_content(fnm) == norm_line_sep(text)
        finally:
            if os.path.exists(fnm):
                os.remove(fnm)

    def test_file_write_error(self):
        assert not file_write("what ever", "folder_not_existing/writefile.xxx")
        assert not file_write("what else", ":invalid \\=// file name....")

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
        s = 'äöü'
        assert force_encoding(s) == '\\xe4\\xf6\\xfc'

        assert force_encoding(s, encoding='utf-8') == s
        assert force_encoding(s, encoding='utf-16') == s
        assert force_encoding(s, encoding='cp1252') == s

        assert force_encoding(s, encoding='utf-8', errors='strict') == s
        assert force_encoding(s, encoding='utf-8', errors='replace') == s
        assert force_encoding(s, encoding='utf-8', errors='backslashreplace') == s
        assert force_encoding(s, encoding='utf-8', errors='xmlcharrefreplace') == s
        assert force_encoding(s, encoding='utf-8', errors='ignore') == s
        assert force_encoding(s, encoding='utf-8', errors='') == s

        with pytest.raises(TypeError):
            assert force_encoding(s, encoding=cast(str, None)) == '\\xe4\\xf6\\xfc'

    def test_norm_line_sep(self):
        assert norm_line_sep('a\r\nb') == 'a\nb'
        assert norm_line_sep('a\rb') == 'a\nb'

    def test_norm_name(self):
        assert norm_name("AnyCamelCaseName") == "AnyCamelCaseName"
        assert norm_name("anyCamelCaseName") == "anyCamelCaseName"
        assert norm_name("NoUnderScoreOnNone") == "NoUnderScoreOnNone"
        assert norm_name("any_name") == "any_name"
        assert norm_name("äáßñìÄÏÜ") == "äáßñìÄÏÜ"
        assert norm_name("@special/chars!:;-`¡'´") == "_special_chars________"

    def test_now_str(self):
        assert len(now_str()) == 20
        assert len(now_str("_")) == 23

    def test_os_host_name(self):
        print(os_host_name())
        assert os_host_name()

    def test_os_local_ip(self):
        assert os_local_ip() or os_local_ip() == ""

    def test_os_platform_android(self):
        try:
            os.environ['ANDROID_ARGUMENT'] = 'tst'
            assert _os_platform() == 'android'
        finally:
            os.environ.pop('ANDROID_ARGUMENT', None)

        try:
            os.environ['KIVY_BUILD'] = 'android'
            assert _os_platform() == 'android'
        finally:
            os.environ.pop('KIVY_BUILD', None)

    def test_os_platform_cygwin(self):
        old_platform = sys.platform
        try:
            sys.platform = 'cygwin'
            assert _os_platform() == 'cygwin'
        finally:
            sys.platform = old_platform

    def test_os_platform_darwin(self):
        old_platform = sys.platform
        try:
            sys.platform = 'darwin'
            assert _os_platform() == 'darwin'
        finally:
            sys.platform = old_platform

    def test_os_platform_freebsd(self):
        old_platform = sys.platform
        try:
            sys.platform = 'freebsd'
            assert _os_platform() == 'freebsd'
        finally:
            sys.platform = old_platform

    def test_os_platform_ios(self):
        try:
            os.environ['KIVY_BUILD'] = 'ios'
            assert _os_platform() == 'ios'
        finally:
            os.environ.pop('KIVY_BUILD', None)

    def test_os_platform_win32(self):
        old_platform = sys.platform
        try:
            sys.platform = 'win32'
            assert _os_platform() == 'win32'
        finally:
            sys.platform = old_platform

    def test_os_user_name(self):
        print(os_user_name())
        assert os_user_name()

    def test_round_traditional(self):
        assert round_traditional(1.01) == 1
        assert round_traditional(10.1, -1) == 10
        assert round_traditional(1.123, 1) == 1.1
        assert round_traditional(0.5) == 1
        assert round_traditional(0.5001, 1) == 0.5

        assert round_traditional(0.075, 2) == 0.08
        assert round(0.075, 2) == 0.07

    def test_snake_to_camel(self):
        assert snake_to_camel("_Any_Camel_Case_Name") == "AnyCamelCaseName"
        assert snake_to_camel("any_Camel_Case_Name") == "AnyCamelCaseName"
        assert snake_to_camel("any_Camel_Case_Name", back_convertible=True) == "anyCamelCaseName"

        assert snake_to_camel("houseMen") == "Housemen"
        assert snake_to_camel("any_name") == "AnyName"
        assert snake_to_camel("any_name", back_convertible=True) == "anyName"
        assert snake_to_camel("@special/chars!") == "@special/chars!"

    def test_sys_env_dict(self):
        assert sys_env_dict().get('python_ver')
        assert sys_env_dict().get('cwd')
        assert sys_env_dict().get('frozen') is False

        assert sys_env_dict().get('bundle_dir') is None
        sys.frozen = True
        assert sys_env_dict().get('bundle_dir')
        del sys.__dict__['frozen']
        assert sys_env_dict().get('bundle_dir') is None

    def test_sys_env_text(self):
        assert isinstance(sys_env_text(), str)
        assert 'python_ver' in sys_env_text()
        ret = sys_env_text(extra_sys_env_dict=dict(test_add='TstAdd'))
        assert 'test_add' in ret
        assert 'TstAdd' in ret

    def test_to_ascii(self):
        assert to_ascii('äöü') == 'aou'
