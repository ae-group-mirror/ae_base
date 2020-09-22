""" ae.system unit tests """
import pytest
import os
import sys
from typing import cast

from ae.base import UNSET, app_name_guess, deep_object, deep_replace, env_str, norm_line_sep, \
    sys_env_dict, sys_env_text, sys_host_name, sys_platform, sys_user_name


class TestHelpers:
    def test_app_name_guess(self):
        assert app_name_guess()     # app.exe name in pytest returning '_jb_pytest_runner'(PyCharm)/'__main__'(console)
        assert app_name_guess() != 'main'
        assert app_name_guess() == 'ae_base'

    def test_deep_object(self):
        class TstA:
            """ test class """
            att = 'a_att_value'
            dic = dict(a_key='a_dict_val', a_dict=dict(a_key='a_a_dict_val'))
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
        assert deep_object(a, "dic['a_dict']") == dict(a_key='a_a_dict_val')
        assert deep_object(a, "dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(a, "lis[0]") == 'a_list_val'

        assert deep_object(b, 'att') == 'b_att_value'
        assert isinstance(deep_object(b, 'a_att'), TstA)
        assert deep_object(b, 'a_att.att') == 'a_att_value'
        assert deep_object(b, 'a_att.att[-1]') == 'e'
        assert deep_object(b, "a_att.dic['a_key']") == 'a_dict_val'
        assert deep_object(b, "a_att.dic['a_dict']") == dict(a_key='a_a_dict_val')
        assert deep_object(b, "a_att.dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(b, "a_att.lis[0]") == 'a_list_val'

        assert deep_object(c, '[0].att') == 'a_att_value'
        assert deep_object(c, '0].att') == 'a_att_value'
        assert isinstance(deep_object(c, '0]'), TstA)
        assert deep_object(c, '0].att[-1]') == 'e'
        assert deep_object(c, "0].dic['a_key']") == 'a_dict_val'
        assert deep_object(c, "0].dic['a_dict']") == dict(a_key='a_a_dict_val')
        assert deep_object(c, "0].dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(c, "0].lis[0]") == 'a_list_val'

        assert deep_object(c, '1].a_att.att') == 'a_att_value'
        assert isinstance(deep_object(c, '1].a_att'), TstA)
        assert deep_object(c, '1].a_att.att[-1]') == 'e'
        assert deep_object(c, "1].a_att.dic['a_key']") == 'a_dict_val'
        assert deep_object(c, "1].a_att.dic['a_dict']") == dict(a_key='a_a_dict_val')
        assert deep_object(c, "1].a_att.dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(c, "1].a_att.lis[0]") == 'a_list_val'

        assert deep_object(d, "'a'].att") == 'a_att_value'
        assert isinstance(deep_object(d, "'a']"), TstA)
        assert deep_object(d, "'a'].att[-1]") == 'e'
        assert deep_object(d, "'a'].dic['a_key']") == 'a_dict_val'
        assert deep_object(d, "'a'].dic['a_dict']") == dict(a_key='a_a_dict_val')
        assert deep_object(d, "'a'].dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(d, "'a'].lis[0]") == 'a_list_val'

        assert deep_object(d, "a'].att") == 'a_att_value'
        assert isinstance(deep_object(d, "a']"), TstA)
        assert deep_object(d, "a'].att[-1]") == 'e'
        assert deep_object(d, "a'].dic['a_key']") == 'a_dict_val'
        assert deep_object(d, "a'].dic['a_dict']") == dict(a_key='a_a_dict_val')
        assert deep_object(d, "a'].dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(d, "a'].lis[0]") == 'a_list_val'

        assert deep_object(d, "a].att") == 'a_att_value'
        assert isinstance(deep_object(d, "a']"), TstA)
        assert deep_object(d, "a].att[-1]") == 'e'
        assert deep_object(d, "a].dic['a_key']") == 'a_dict_val'
        assert deep_object(d, "a].dic['a_dict']") == dict(a_key='a_a_dict_val')
        assert deep_object(d, "a].dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(d, "a].lis[0]") == 'a_list_val'

        assert deep_object(d, 'b].att') == 'b_att_value'
        assert deep_object(d, 'b].a_att.att') == 'a_att_value'
        assert deep_object(d, 'b].a_att.att[-1]') == 'e'
        assert deep_object(d, "b].a_att.dic['a_key']") == 'a_dict_val'
        assert deep_object(d, "b].a_att.dic['a_dict']") == dict(a_key='a_a_dict_val')
        assert deep_object(d, "b].a_att.dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(d, "b].a_att.lis[0]") == 'a_list_val'

        assert deep_object(d, 'c][0].att') == 'a_att_value'
        assert deep_object(d, 'c][0].att') == 'a_att_value'
        assert deep_object(d, 'c][0].att[-1]') == 'e'
        assert deep_object(d, "c][0].dic['a_key']") == 'a_dict_val'
        assert deep_object(d, "c][0].dic['a_dict']") == dict(a_key='a_a_dict_val')
        assert deep_object(d, "c][0].dic['a_dict']['a_key']") == 'a_a_dict_val'
        assert deep_object(d, "c][0].lis[0]") == 'a_list_val'

        assert deep_object(a, "invalid_attr") == UNSET
        assert deep_object(a, "[invalid_key]") == UNSET
        assert deep_object(c, "[invalid_idx]") == UNSET
        assert deep_object(d, "[invalid_key]") == UNSET

    def test_deep_replace(self):
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

        with pytest.raises(ValueError):
            deep_replace(cast(list, ('tuple', 'are', 'only', 'replace', 'in', 'deeper', 'data')),
                         lambda d, k, v: 'replacing all')

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
