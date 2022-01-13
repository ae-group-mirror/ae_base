""" ae.base unit tests """
import os
import shutil

import pytest
import sys

from configparser import ConfigParser
from typing import cast

# noinspection PyProtectedMember
from ae.base import (
    BUILD_CONFIG_FILE, PY_EXT, TESTS_FOLDER, UNSET,
    app_name_guess, build_config_variable_values, camel_to_snake, duplicates, env_str, force_encoding, in_wd,
    instantiate_config_parser, main_file_paths_parts, norm_line_sep, norm_name, norm_path, now_str, project_main_file,
    read_file,
    round_traditional, snake_to_camel, sys_env_dict, sys_env_text, os_host_name, os_local_ip, _os_platform,
    os_user_name, to_ascii, write_file)


def test_unset_truthiness():
    assert not UNSET
    assert bool(UNSET) is False


def test_unset_null_length():
    assert len(UNSET) == 0


class TestHelpers:
    def test_app_name_guess(self):
        assert app_name_guess()     # app.exe name in pytest returning '_jb_pytest_runner'(PyCharm)/'__main__'(console)
        assert app_name_guess() != 'main'
        assert app_name_guess() == 'unguessable'

    def test_build_config_variable_values_with_spec(self):
        try:
            with open(BUILD_CONFIG_FILE, "w") as file_handle:
                file_handle.write("""[app]\nexisting = tst""")
            existing, not_existing = build_config_variable_values(
                ('existing', ""),
                ('not_existing', "default_value")
            )
            assert existing == "tst"
            assert not_existing == "default_value"
        finally:
            if os.path.exists(BUILD_CONFIG_FILE):
                os.remove(BUILD_CONFIG_FILE)

    def test_build_config_variable_values_no_spec(self):
        existing, not_existing = build_config_variable_values(
            ('not_existing1', "default_value1"),
            ('not_existing2', "default_value2")
        )
        assert existing == "default_value1"
        assert not_existing == "default_value2"

        try:
            write_file(BUILD_CONFIG_FILE, "")
            existing, not_existing = build_config_variable_values(
                ('not_existing1', "default_value1"),
                ('not_existing2', "default_value2"),
                section="tst_section"
            )
            assert existing == "default_value1"
            assert not_existing == "default_value2"
        finally:
            if os.path.exists(BUILD_CONFIG_FILE):
                os.remove(BUILD_CONFIG_FILE)

    def test_camel_to_snake(self):
        assert camel_to_snake("AnyCamelCaseName") == "_Any_Camel_Case_Name"
        assert camel_to_snake("anyCamelCaseName") == "any_Camel_Case_Name"

        assert camel_to_snake("_under_score") == "_under_score"
        assert camel_to_snake("any_name") == "any_name"
        assert camel_to_snake("@special/chars!") == "@special/chars!"

    def test_duplicates(self):
        lst = ['a', 3, 'bb', 3, 'ccc', 3]
        assert duplicates(lst) == [3, 3]

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

    def test_in_wd(self):
        old_dir = os.getcwd()
        tst_dir = norm_path(TESTS_FOLDER)
        with in_wd(TESTS_FOLDER):
            assert os.getcwd() == tst_dir
        assert os.getcwd() == old_dir

    def test_instantiate_config_parser(self):
        cfg_parser = instantiate_config_parser()
        assert isinstance(cfg_parser, ConfigParser)
        assert cfg_parser.optionxform is str

    def test_main_file_paths_parts(self):
        assert isinstance(main_file_paths_parts(""), tuple)
        assert len(main_file_paths_parts(""))
        assert isinstance(main_file_paths_parts("")[0], tuple)

        assert any("__init__" + PY_EXT in _ for _ in main_file_paths_parts(""))
        assert any("__main__" + PY_EXT in _ for _ in main_file_paths_parts(""))
        assert any("main" + PY_EXT in _ for _ in main_file_paths_parts(""))
        por_name = "portion_tst_name"
        assert any(por_name in _ for _ in main_file_paths_parts(por_name))
        assert any(por_name + PY_EXT in _ for _ in main_file_paths_parts(por_name))

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
        
        assert norm_path(".") == os.getcwd()
        assert norm_path(".", resolve_sym_links=False) == os.getcwd()
        assert norm_path(".", make_absolute=False) == os.getcwd()
        assert norm_path(".", make_absolute=False, remove_base_path=os.getcwd()) == "."

        assert norm_path(new_folder) == os.path.join(os.getcwd(), new_folder)
        assert norm_path(new_folder, resolve_sym_links=False) == os.path.join(os.getcwd(), new_folder)
        assert norm_path(new_folder, make_absolute=False) == os.path.join(os.getcwd(), new_folder)
        assert norm_path(new_folder, make_absolute=False, remove_base_path=os.getcwd()) == new_folder

        assert norm_path(os.path.join(TESTS_FOLDER, "..")) == os.getcwd()
        assert norm_path(os.path.join(TESTS_FOLDER, ".."), resolve_sym_links=False) == os.getcwd()
        assert norm_path(os.path.join(TESTS_FOLDER, ".."), make_absolute=False) == os.getcwd()
        assert norm_path(os.path.join("ae", ".."), make_absolute=False, remove_base_path=os.getcwd()) == "."

        assert norm_path("~") != ""
        assert norm_path(os.path.join("~", new_folder)).endswith(new_folder)
        assert norm_path(os.path.join("~", new_folder), remove_base_path="~").endswith(new_folder)

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

    def test_project_main_file(self):
        assert project_main_file("not_existing_xy.tst") == ""

        ae_base_main_file = norm_path(os.path.join("ae", "base" + PY_EXT))
        assert project_main_file("ae.base") == ae_base_main_file
        assert project_main_file("ae.base", norm_path("")) == ae_base_main_file

        local_project_dir = os.path.join(TESTS_FOLDER, "ae_base")
        local_main_file = norm_path(os.path.join(local_project_dir, "main.py"))
        try:
            os.makedirs(local_project_dir)
            write_file(local_main_file, "# main file content")
            assert project_main_file("ae.base") == ae_base_main_file
            assert project_main_file("ae.base", norm_path("")) == ae_base_main_file
            assert project_main_file("ae.base", local_project_dir) == local_main_file
            assert project_main_file("ae.base", norm_path(local_project_dir)) == local_main_file

        finally:
            if os.path.isdir(local_project_dir):
                shutil.rmtree(local_project_dir)

    def test_read_file(self):
        with open(__file__) as file_handle:
            content = file_handle.read()
        assert read_file(__file__) == content
        assert read_file(__file__, extra_mode="b") == bytes(content, 'utf8')

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
        assert to_ascii('áéí óú') == 'aei ou'
        assert to_ascii('ÁÉÍ ÓÚ') == 'AEI OU'

        assert to_ascii('àèì òù') == 'aei ou'
        assert to_ascii('ÀÈÌ ÒÙ') == 'AEI OU'

        assert to_ascii('äëï öü') == 'aei ou'
        assert to_ascii('ÄËÏ ÖÜ') == 'AEI OU'

        assert to_ascii('âêî ôû') == 'aei ou'
        assert to_ascii('ÂÊÎ ÔÛ') == 'AEI OU'

        assert to_ascii('ß') == 'ss'
        assert to_ascii('€') == 'Euro'

    def test_write_file_as_text(self):
        test_file = os.path.join(TESTS_FOLDER, 'tst_file_written.ext')
        content = "any content"
        assert not os.path.exists(test_file)
        try:
            write_file(test_file, content)
            assert os.path.exists(test_file)
            assert os.path.isfile(test_file)
            assert read_file(test_file) == content
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_write_file_as_binary(self):
        test_file = os.path.join(TESTS_FOLDER, 'bin_file_written.ext')
        content = b"any content"
        assert not os.path.exists(test_file)
        try:
            write_file(test_file, content, extra_mode="b")
            assert os.path.exists(test_file)
            assert os.path.isfile(test_file)
            assert read_file(test_file, extra_mode="b") == content
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
