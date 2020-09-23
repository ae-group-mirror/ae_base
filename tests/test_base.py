""" ae.base unit tests """
import pytest
import os
import sys
from typing import cast

from ae.base import UNSET, app_name_guess, base_app_instance, deep_assignment, deep_object, deep_replace, env_str, \
    norm_line_sep, \
    norm_name, sys_env_dict, sys_env_text, sys_host_name, sys_platform, sys_user_name, AppBase


class TestHelpers:
    def test_app_name_guess(self):
        assert app_name_guess()     # app.exe name in pytest returning '_jb_pytest_runner'(PyCharm)/'__main__'(console)
        assert app_name_guess() != 'main'
        assert app_name_guess() == 'ae_base'

    def test_base_app_instance(self):
        app = base_app_instance()
        assert hasattr(app, 'dpo')
        assert hasattr(app, 'vpo')
        assert hasattr(app, 'font_size')

    def test_deep_assignment(self):
        tst_str = "bCd"
        tst_tup = (0, "1", 2.3)

        dic = dict(str_item=tst_str, tup_item=tst_tup)

        deep_assignment(tst_str, 0, "_", mutable_parent=dic)    # works because `tst_str is dic['str_item']`
        assert tst_str[0] == 'b'
        assert dic['str_item'][0] == '_'
        deep_assignment(dic['str_item'], 0, "B", mutable_parent=dic)
        assert dic['str_item'][0] == 'B'
        deep_assignment(dic['str_item'], 2, 'D', mutable_parent=dic)
        assert dic['str_item'][2] == 'D'
        assert dic['str_item'] == "BCD"
        assert deep_object(dic, 'str_item') == "BCD"
        deep_assignment(dic, 'str_item', tst_str)
        assert dic['str_item'] == tst_str

        assert dic['tup_item'][1] == "1"
        deep_assignment(dic['tup_item'], 1, 1, mutable_parent=dic)
        assert dic['tup_item'][1] == 1
        assert deep_object(dic, "['tup_item'][1]") == 1
        deep_assignment(dic, "tup_item", "new_string")
        assert dic['tup_item'] == "new_string"
        assert deep_object(dic, "['tup_item']") == "new_string"

        lst = ['a', tst_str, tst_tup]

        deep_assignment(lst[1], 0, "_", mutable_parent=lst)
        assert lst[1][0] == "_"
        deep_assignment(lst[1], 0, "x", mutable_parent=lst)
        assert lst[1][0] == "x"
        deep_assignment(lst[1], 1, 'y', mutable_parent=lst)
        deep_assignment(lst[1], 2, 'z', mutable_parent=lst)
        assert lst[1] == "xyz"
        assert deep_object(lst, "[1]") == "xyz"

        deep_assignment(lst[2], 1, "Y", mutable_parent=lst)
        assert lst[2][1] == "Y"
        assert deep_object(lst, "[2][1]") == "Y"

        deep_assignment(lst, 2, "new_string")
        assert lst[2] == "new_string"
        assert deep_object(lst, "2]") == "new_string"

    def test_deep_assignment_exception(self):
        tst_str = "bCd"
        tst_tup = (0, "1", 2.3)

        dic = dict(str_item=tst_str, tup_item=tst_tup)
        with pytest.raises(TypeError):
            deep_assignment(dic['str_item'], 0, "_")
        with pytest.raises(TypeError):
            deep_assignment(dic['tup_item'], 1, 1)

        lst = ['a', tst_str, tst_tup]
        with pytest.raises(TypeError):
            deep_assignment(lst[1], 0, "_")
        with pytest.raises(TypeError):
            deep_assignment(lst[2], 1, "Y")

    def test_deep_object_get(self):
        class TstA:
            """ test class """
            att = 'a_att_value'
            dic = dict(a_key='a_dict_val', a_dict={'a_key': 'a_a_dict_val', 33: 'a_a_num_key_val'})
            lis = ['a_list_val']

        class TstB:
            """ test class """
            att = 'b_att_value'
            a_att = TstA()

        a = TstA()
        b = TstB()
        c = list((TstA(), b))
        d = dict(a=TstA(), b=b, c=c)

        assert deep_object(a, 'att') == 'a_att_value'
        assert deep_object(a, 'att[-1]') == 'e'
        assert deep_object(a, "dic['a_key']") == 'a_dict_val'
        assert deep_object(a, 'dic["a_key"]') == 'a_dict_val'
        assert deep_object(a, 'dic[a_key]') == 'a_dict_val'
        assert deep_object(a, "dic['a_dict']") == {33: 'a_a_num_key_val', 'a_key': 'a_a_dict_val'}
        assert deep_object(a, "dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(a, "dic['a_dict'][33]") == 'a_a_num_key_val'
        assert deep_object(a, "lis[0]") == 'a_list_val'

        assert deep_object(b, 'att') == 'b_att_value'
        assert isinstance(deep_object(b, 'a_att'), TstA)
        assert deep_object(b, 'a_att.att') == 'a_att_value'
        assert deep_object(b, 'a_att.att[-1]') == 'e'
        assert deep_object(b, "a_att.dic['a_key']") == 'a_dict_val'
        assert deep_object(b, "a_att.dic['a_dict']") == {33: 'a_a_num_key_val', 'a_key': 'a_a_dict_val'}
        assert deep_object(b, "a_att.dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(b, "a_att.dic['a_dict'][33]") == 'a_a_num_key_val'
        assert deep_object(b, "a_att.lis[0]") == 'a_list_val'

        assert deep_object(c, '[0].att') == 'a_att_value'
        assert deep_object(c, '0].att') == 'a_att_value'
        assert isinstance(deep_object(c, '0]'), TstA)
        assert deep_object(c, '0].att[-1]') == 'e'
        assert deep_object(c, "0].dic['a_key']") == 'a_dict_val'
        assert deep_object(c, "0].dic['a_dict']") == {33: 'a_a_num_key_val', 'a_key': 'a_a_dict_val'}
        assert deep_object(c, "0].dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(c, "0].dic['a_dict'][33]") == 'a_a_num_key_val'
        assert deep_object(c, "0].lis[0]") == 'a_list_val'

        assert deep_object(c, '1].a_att.att') == 'a_att_value'
        assert isinstance(deep_object(c, '1].a_att'), TstA)
        assert deep_object(c, '1].a_att.att[-1]') == 'e'
        assert deep_object(c, "1].a_att.dic['a_key']") == 'a_dict_val'
        assert deep_object(c, "1].a_att.dic['a_dict']") == {33: 'a_a_num_key_val', 'a_key': 'a_a_dict_val'}
        assert deep_object(c, "1].a_att.dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(c, "1].a_att.dic['a_dict'][33]") == 'a_a_num_key_val'
        assert deep_object(c, "1].a_att.lis[0]") == 'a_list_val'

        assert deep_object(d, "'a'].att") == 'a_att_value'
        assert isinstance(deep_object(d, "'a']"), TstA)
        assert deep_object(d, "'a'].att[-1]") == 'e'
        assert deep_object(d, "'a'].dic['a_key']") == 'a_dict_val'
        assert deep_object(d, "'a'].dic['a_dict']") == {33: 'a_a_num_key_val', 'a_key': 'a_a_dict_val'}
        assert deep_object(d, "'a'].dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(d, "'a'].dic['a_dict'][33]") == 'a_a_num_key_val'
        assert deep_object(d, "'a'].lis[0]") == 'a_list_val'

        assert deep_object(d, "a].att") == 'a_att_value'
        assert isinstance(deep_object(d, "a]"), TstA)
        assert deep_object(d, "a].att[-1]") == 'e'
        assert deep_object(d, "a].dic['a_key']") == 'a_dict_val'
        assert deep_object(d, "a].dic['a_dict']") == {33: 'a_a_num_key_val', 'a_key': 'a_a_dict_val'}
        assert deep_object(d, "a].dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(d, "a].dic['a_dict'][33]") == 'a_a_num_key_val'
        assert deep_object(d, "a].lis[0]") == 'a_list_val'

        assert deep_object(d, 'b].att') == 'b_att_value'
        assert deep_object(d, 'b].a_att.att') == 'a_att_value'
        assert deep_object(d, 'b].a_att.att[-1]') == 'e'
        assert deep_object(d, "b].a_att.dic['a_key']") == 'a_dict_val'
        assert deep_object(d, "b].a_att.dic['a_dict']") == {33: 'a_a_num_key_val', 'a_key': 'a_a_dict_val'}
        assert deep_object(d, "b].a_att.dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(d, "b].a_att.dic['a_dict'][33]") == 'a_a_num_key_val'
        assert deep_object(d, "b].a_att.lis[0]") == 'a_list_val'

        assert deep_object(d, 'c][0].att') == 'a_att_value'
        assert deep_object(d, 'c][0].att') == 'a_att_value'
        assert deep_object(d, 'c][0].att[-1]') == 'e'
        assert deep_object(d, "c][0].dic['a_key']") == 'a_dict_val'
        assert deep_object(d, "c][0].dic['a_dict']") == {33: 'a_a_num_key_val', 'a_key': 'a_a_dict_val'}
        assert deep_object(d, "c][0].dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(d, "c][0].dic['a_dict'][33]") == 'a_a_num_key_val'
        assert deep_object(d, "c][0].lis[0]") == 'a_list_val'

        assert deep_object(a, "invalid_attr") == UNSET
        assert deep_object(a, "[invalid_key]") == UNSET
        with pytest.raises(TypeError):
            deep_object(c, "[invalid_idx]")
        assert deep_object(d, "[invalid_key]") == UNSET

    def test_deep_object_set(self):
        class TstA:
            """ test class """
            att = 'a_att_value'
            dic = dict(a_key='a_dict_val', a_dict={'a_key': 'a_a_dict_val', 33: 'a_a_num_key_val'})
            lis = ['a_list_val']
            tup = (0, "1", 2.3)

        class TstB:
            """ test class """
            att = 'b_att_value'
            a_att = TstA()

        a = TstA()
        b = TstB()

        assert deep_object(a, 'att', new_value='a_att_new_value') == 'a_att_value'
        assert deep_object(a, 'att') == 'a_att_new_value'

        assert deep_object(a, "dic['a_key']", new_value='a_dict_new_val') == 'a_dict_val'
        assert deep_object(a, 'dic["a_key"]') == 'a_dict_new_val'

        assert deep_object(a, "dic[99]", new_value='new_dict_item_with_int_key') == UNSET
        assert deep_object(a, "dic[99]") == 'new_dict_item_with_int_key'

        assert deep_object(a, "dic['a_dict']", {'a_key': 'a_a_dict_new_val', 33: 'a_a_num_key_val'}
                           ) == {33: 'a_a_num_key_val', 'a_key': 'a_a_dict_val'}
        assert deep_object(a, "dic['a_dict']['a_key']", new_value='a_a_dict_newer_val') == 'a_a_dict_new_val'
        assert deep_object(a, "dic['a_dict']['a_key']") == 'a_a_dict_newer_val'
        assert deep_object(b, "a_att.dic['a_dict']['a_key']") == 'a_a_dict_newer_val'

        assert deep_object(a, "dic['a_dict'][33]", new_value='new_dict_with_int_key') == 'a_a_num_key_val'
        assert deep_object(a, "dic['a_dict'][33]") == 'new_dict_with_int_key'

        assert deep_object(a, "lis[0]", new_value='a_list_new_val') == 'a_list_val'
        assert deep_object(a, "lis[0]") == 'a_list_new_val'
        assert deep_object(b, "a_att.lis[0]") == 'a_list_new_val'

        assert deep_object(b, 'att', new_value='b_att_new_value') == 'b_att_value'
        assert deep_object(b, 'att') == 'b_att_new_value'

        assert deep_object(b, 'a_att.att', new_value='xxx') == 'a_att_value'
        assert deep_object(b, 'a_att.att') == 'xxx'
        assert deep_object(b, 'a_att.att[-1]') == 'x'

    def test_deep_object_set_immutable(self):
        tst_str = "bCd"
        tst_tup = (0, "1", 2.3)

        class Tst:
            """ test class """
            dic_att = dict(str_item=tst_str, tup_item=tst_tup)

        dic = dict(str_item=tst_str, tup_item=tst_tup)
        obj = Tst()

        assert deep_object(dic, "str_item[0]", new_value="B") == 'b'
        assert deep_object(dic, "str_item[0]") == 'B'
        assert deep_object(dic, "str_item", new_value=tst_str) == 'BCd'
        assert dic['str_item'] == tst_str

        assert deep_object(obj, "dic_att[str_item][2]") == 'd'
        assert deep_object(obj, "dic_att['str_item'][2]", new_value='D') == "d"
        assert obj.dic_att['str_item'][2] == "D"

        assert deep_object(dic, "tup_item[1]", new_value=1) == "1"
        assert dic['tup_item'][1] == 1
        assert deep_object(dic, "tup_item][1]") == 1

    def test_deep_object_dict_keys(self):
        d = dict()

        assert 123 not in d
        assert deep_object(d, '[123]', new_value="int_key_val") == UNSET
        assert deep_object(d, '[123]') == "int_key_val"
        assert 123 in d

        assert "123" not in d
        assert deep_object(d, '["123"]', new_value="str_key_val") == UNSET
        assert deep_object(d, '["123"]') == "str_key_val"
        assert "123" in d

        assert (1, "2") not in d
        assert deep_object(d, '[(1, "2")]', new_value="tuple_key_val") == UNSET
        assert deep_object(d, '[(1, "2")]') == "tuple_key_val"
        assert (1, "2") in d

    def test_deep_replace_data(self):
        sub = ['b_list_0', 'search_index_value', 'search_key_value3']
        data = dict(
            a_str='a_str',
            a_list=['a_list_0', 'search_index_value', 2, dict(
                a_list_a='a_list_a_str', search_key='search_key_value1')],
            a_dict=dict(
                b_str="b_str",
                b_dict=dict(
                    c_tuple=('1st_tuple_value', 'search_value', '3rd_tuple_value', 3, ),
                    c_str='c str',
                    search_key='search_key_value2',
                ),
                b_list=sub,
            )
        )

        deep_replace(data, lambda d, k, v: 'replaced_value' if v == 'search_value' else UNSET)
        assert data['a_dict']['b_dict']['c_tuple'][1] == 'replaced_value'

        deep_replace(data, lambda d, k, v: 'replaced_index_value' if k == 2 else UNSET)     # search_index_value
        assert data['a_list'][2] == 'replaced_index_value'
        assert data['a_dict']['b_list'][2] == 'replaced_index_value'

        deep_replace(data, lambda d, k, v: 'replaced_key_value' if k == 'search_key' or d == sub and k == 2 else UNSET)
        assert data['a_list'][3]['search_key'] == 'replaced_key_value'
        assert data['a_dict']['b_dict']['search_key'] == 'replaced_key_value'
        assert data['a_dict']['b_list'][2] == 'replaced_key_value'

        deep_replace(data, lambda d, k, v: 'WIPED')
        for _k, _v in data.items():
            assert _v == 'WIPED'

    def test_deep_replace_exception(self):
        with pytest.raises(ValueError):
            deep_replace(cast(list, ('tuple', 'are', 'only', 'replace', 'in', 'deeper', 'data')),
                         lambda d, k, v: 'replacing all')

    def test_deep_replace_immutable(self):
        tst_str = "AbCbE"
        tst_tuple = (3, '0', 1)
        tst_list = [tst_str, tst_tuple]
        tst_dict = dict(l=tst_list)

        deep_replace(tst_dict, lambda _d, k, v: 'd' if v == 'b' and k == 3 else UNSET)
        assert tst_list[0][3] == 'b'
        deep_replace(tst_dict, lambda _d, k, v: 'd' if v == 'b' and k == 3 else UNSET, immutable_types=(str,))
        assert tst_list[0][3] == 'd'

        deep_replace(tst_dict, lambda _d, k, v: 2 if v == '0' else UNSET, immutable_types=(str,))
        assert tst_list[1][1] == '0'
        deep_replace(tst_dict, lambda _d, k, v: 2 if v == '0' else UNSET)
        assert tst_list[1][1] == 2

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

    def test_norm_line_sep(self):
        assert norm_line_sep('a\r\nb') == 'a\nb'
        assert norm_line_sep('a\rb') == 'a\nb'

    def test_norm_name(self):
        assert norm_name("AnyCamelCaseName") == "ANY_CAMEL_CASE_NAME"
        assert norm_name("any_name") == "ANY_NAME"
        assert norm_name("@special/chars!included") == "_SPECIAL_CHARS_INCLUDED"

        assert norm_name("NoUnderScoreOnToLower", to_lower=True) == "nounderscoreontolower"

        assert norm_name("NoUnderScoreOnNone", to_lower=None) == "NoUnderScoreOnNone"

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

    def test_sys_host_name(self):
        print(sys_host_name())
        assert sys_host_name()

    def test_sys_platform_android(self):
        try:
            os.environ['ANDROID_ARGUMENT'] = 'tst'
            assert sys_platform() == 'android'
        finally:
            os.environ.pop('ANDROID_ARGUMENT', None)

        try:
            os.environ['KIVY_BUILD'] = 'android'
            assert sys_platform() == 'android'
        finally:
            os.environ.pop('KIVY_BUILD', None)

    def test_sys_platform_cygwin(self):
        old_platform = sys.platform
        try:
            sys.platform = 'cygwin'
            assert sys_platform() == 'cygwin'
        finally:
            sys.platform = old_platform

    def test_sys_platform_darwin(self):
        old_platform = sys.platform
        try:
            sys.platform = 'darwin'
            assert sys_platform() == 'darwin'
        finally:
            sys.platform = old_platform

    def test_sys_platform_freebsd(self):
        old_platform = sys.platform
        try:
            sys.platform = 'freebsd'
            assert sys_platform() == 'freebsd'
        finally:
            sys.platform = old_platform

    def test_sys_platform_ios(self):
        try:
            os.environ['KIVY_BUILD'] = 'ios'
            assert sys_platform() == 'ios'
        finally:
            os.environ.pop('KIVY_BUILD', None)

    def test_sys_platform_win32(self):
        old_platform = sys.platform
        try:
            sys.platform = 'win32'
            assert sys_platform() == 'win32'
        finally:
            sys.platform = old_platform

    def test_sys_user_name(self):
        print(sys_user_name())
        assert sys_user_name()


class TestAppBase:
    def test_app_base_instance(self, capsys):
        app = AppBase()
        assert app

        tst_out = "test run printout test"
        app.dpo(tst_out + "dpo")
        app.vpo(tst_out + "vpo")
        out, err = capsys.readouterr()
        assert tst_out in out
        assert tst_out + "dpo" in out
        assert tst_out + "vpo" in out
