"""
basic constants and helper functions
====================================

This module is pure python and has no external dependencies.


base constants
--------------

Generic ISO format strings for `date` and `datetime` values
are provided by the constants :data:`DATE_ISO` and
:data:`DATE_TIME_ISO`.

The :data:`UNSET` object is useful in cases where `None`
is a valid data value and another special value is needed
for to specify that e.g. an argument or attribute has
no (valid) value.


base helper functions
---------------------

The functions :func:`deep_object` and :func:`deep_replace`
is making your programmer life much easier when you need
to determine or change parts of deeply nested data/object
structures.

For to determine the value of an OS environment variable
with automatic variable name conversion you can use the
function :func:`env_str`.

Other helper functions provided by this namespace portion for to
determine the values of the most important system environment
variables for your application are :func:`sys_env_dict`
and :func:`sys_env_text`.

The helper function :func:`sys_platform` are extending Python's
:func:`os.name` and :func:`sys.platform` functions for the
operating systems iOS and Android (not supported by Python).
"""
import ast
import getpass
import os
import platform
import sys
from operator import getitem
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union


__version__ = '0.1.1'


DATE_ISO: str = '%Y-%m-%d'                      #: ISO string format for date values (e.g. in config files/variables)
DATE_TIME_ISO: str = '%Y-%m-%d %H:%M:%S.%f'     #: ISO string format for datetime values


DeepDataType = Union[dict, list]


class _UNSET:
    """ class for singleton UNSET object (using only object() does not provide proper representation string). """


UNSET = _UNSET()                                #: used for attributes/arguments if `None` is needed as a valid value


def app_name_guess() -> str:
    """ guess/try to determine the name of the currently running app (w/o assessing not yet initialized app instance).

    :return:                    application name/id.
    """
    path = sys.argv[0]
    app_name = os.path.splitext(os.path.basename(path))[0]
    if app_name.lower() in ('main', '__main__', '_jb_pytest_runner'):
        path = os.getcwd()
        app_name = os.path.basename(path)
    return app_name


def deep_object(obj: object, key_path: str, new_value: Union[Any, None] = UNSET) -> object:
    """ determine object in a deep nested object structure and optionally assign a new value to it.

    :param obj:                 start object to search in (and its sub-objects).
    :param key_path:            composed key string containing dict keys, tuple/list/str indexes and attribute names.
                                The dot (`.`) character is identifying attribute names. `[` and `]` are enclosing
                                index values, like shown in the following examples::

                                    class AClass:
                                        str_attr_name = 'a_attr_val'
                                        dict_attr = dict(a=3)

                                    class BClass:
                                        str_attr_name = 'b_b_b_b_b'
                                        instance = AClass()

                                    b = BClass()
                                    assert deep_object(b, 'str_attr_name') == 'b_b_b_b_b'
                                    assert deep_object(b, 'instance.str_attr_name') == 'a_attr_val'
                                    assert deep_object(b, 'instance.dict_attr["a"]') == 3

                                key path strings for dicts can alternatively be specified without the high commas
                                (enclosing the key string), like e.g.::

                                    d = dict(a_str_key=1)
                                    assert deep_object(d, '["a_str_key"]') == 1  # with high commas returns 1
                                    assert deep_object(d, '[a_str_key]') == 1    # same result/return value

                                When the first part of the key path string is specifying an index you can also
                                leave away the opening square bracket::

                                    assert deep_object(d, 'a_str_key]') == 1     # again - the same return 1

    :param new_value:           optional new value for the found object. Specified/Found object has to be
                                a mutable object (list, dict or object). The old value will be returned.

    :return:                    specified object/value (old value if :paramref:`~deep_object.new_value` got passed)
                                or UNSET if not found/exists (key path string is invalid).
    """
    if key_path[0] == '[':
        key_path = key_path[1:]       # for to support fully specified indexes (starting with a square bracket)

    get_func = getitem if isinstance(obj, (dict, list, tuple)) else getattr
    while key_path and obj != UNSET:
        idx = 0
        for char in key_path:
            if char in ('.', '[', ']'):     # == `char in '.[]'` - keep strings separate for speedup
                break
            idx += 1
        else:
            char = ""

        last_obj = obj
        try:
            key = ast.literal_eval(key_path[:idx])
        except (SyntaxError, ValueError):
            key = key_path[:idx]
        try:
            obj = get_func(obj, key)                                    # type: ignore
        except (AttributeError, IndexError, KeyError, ValueError):
            obj = UNSET

        if char == ']':
            idx += 1
            char = key_path[idx: idx + 1]

        if idx >= len(key_path):
            if new_value != UNSET:
                if isinstance(last_obj, (list, dict)):
                    last_obj[key] = new_value           # type: ignore # mypy does not recognize correctly list/dict
                else:
                    setattr(last_obj, key, new_value)  # type: ignore # raise if last_obj is a str/tuple then key is int
            break

        get_func = getitem if char == '[' else getattr
        key_path = key_path[idx + 1:]

    return obj


def deep_replace(data: DeepDataType, replace_with: Callable[[DeepDataType, Any, Any], Any],
                 immutable_types: Tuple[Type, ...] = (tuple, )):
    """ replace values within the passed (nested) data structure.

    :param data:                list or dict data structure for to be deep searched and replaced. Can
                                contain any combination of deep nested objects. The sub-structure-types dict and list
                                as well as the immutable types specified by :paramref:`~deep_replace.immutable_types`
                                will be recursively deep searched (top down) by passing their items one by one
                                to the function specified by :paramref:`~deep_replace.replace_with`.
    :param replace_with:        called for each item with 3 arguments (data-structure, key in data-structure, value),
                                and if the return value is not equal to :data:`UNSET` then it will be used for
                                to overwrite the value in the data-structure.
    :param immutable_types:     tuple of immutable iterable types which will be treated as replaceable items.
                                By default only the items of a tuple are replaceable. For to also
                                allow the replacement of single characters in a string pass the argument value
                                `(tuple, str)` into this parameter.
    :return:
    """
    if isinstance(data, dict):
        iter_func = data.items()
    elif isinstance(data, list):
        iter_func = enumerate(data)             # type: ignore # we treat them like dicts with the index as the key
    else:
        raise ValueError(f"deep_replace(): invalid data type {type(data)} (allowed={DeepDataType})")

    replace_items = list()
    for key, value in iter_func:
        new_value = replace_with(data, key, value)
        if new_value != UNSET:
            replace_items.append((key, new_value))
        elif isinstance(value, (dict, list)):
            deep_replace(value, replace_with, immutable_types=immutable_types)
        elif isinstance(value, immutable_types):
            type_converter = type(value)
            if type_converter is str:   # for string immutables: prevent recursion; ensure correct conversion from list
                corr_immutable_types = tuple([typ for typ in immutable_types if typ is not str])
                type_converter = lambda v: "".join(v)   # type: ignore # noqa: E731
            else:
                corr_immutable_types = immutable_types
            value = list(value)
            deep_replace(value, replace_with, immutable_types=corr_immutable_types)
            replace_items.append((key, type_converter(value)))

    for key, new_value in replace_items:
        data[key] = new_value


def env_str(name: str, convert_name: bool = False) -> Optional[str]:
    """ determine the string value of an OS environment variable, optionally preventing invalid variable name.

    :param name:                name of a OS environment variable.
    :param convert_name:        pass True for to prevent invalid variable names by converting
                                CamelCase names into SNAKE_CASE, lower-case into
                                upper-case and all non-alpha-numeric characters into underscore characters.
    :return:                    string value of OS environment variable if found, else None.
    """
    if convert_name:
        str_parts = list()
        for char in name:
            if char.isupper():
                str_parts.append('_' + char)
            elif char.isalnum():
                str_parts.append(char.upper())
            else:
                str_parts.append('_')
        name = ''.join(str_parts)

    return os.environ.get(name)


def norm_line_sep(text: str) -> str:
    """

    :param text:
    :return:
    """
    return text.replace('\r\n', '\n').replace('\r', '\n')


def sys_env_dict(file: str = __file__) -> Dict[str, Any]:
    """ returns dict with python system run-time environment values.

    :param file:                optional file name (def=__file__/base.py).
    :return:                    python system run-time environment values like python_ver, argv, cwd, executable,
                                __file__, frozen and bundle_dir.
    """
    sed: Dict[str, Any] = dict()
    sed['python_ver'] = sys.version
    sed['argv'] = sys.argv
    sed['executable'] = sys.executable
    sed['cwd'] = os.getcwd()
    sed['__file__'] = file
    sed['frozen'] = getattr(sys, 'frozen', False)
    if getattr(sys, 'frozen', False):
        sed['bundle_dir'] = getattr(sys, '_MEIPASS', '*#ERR#*')
    return sed


def sys_env_text(file: str = __file__, ind_ch: str = " ", ind_len: int = 18, key_ch: str = "=", key_len: int = 12,
                 extra_sys_env_dict: Optional[Dict[str, str]] = None) -> str:
    """ compile formatted text block with system environment info.

    :param file:                main module file name (def=__file__/base.py).
    :param ind_ch:              indent character (def=" ").
    :param ind_len:             indent depths (def=18 characters).
    :param key_ch:              key-value separator character (def=" =").
    :param key_len:             key-name maximum length (def=12 characters).
    :param extra_sys_env_dict:  dict with additional system info items.
    :return:                    text block with system environment info.
    """
    sed = sys_env_dict(file=file)
    if extra_sys_env_dict:
        sed.update(extra_sys_env_dict)
    ind = ""
    text = "\n".join([f"{ind:{ind_ch}>{ind_len}}{key:{key_ch}<{key_len}}{val}" for key, val in sed.items()])
    return text


def sys_host_name() -> str:
    """ determine the operating system host/machine name.

    :return:                    machine name string.
    """
    return platform.node()


def sys_platform() -> str:
    """ determine the operating system where this code is running.

    :return:                    operating system (extension) as string:

                                * `'android'` for all Android systems.
                                * `'cygwin'` for MS Windows with an installed Cygwin extension.
                                * `'darwin'` for all Apple Mac OS X systems.
                                * `'freebsd'` for all other BSD-based unix systems.
                                * `'ios'` for all Apple iOS systems.
                                * `'linux'` for all other unix systems (like Arch, Debian/Ubuntu, Suse, ...).
                                * `'win32'` for MS Windows systems (w/o the Cygwin extension).

    """
    if env_str('ANDROID_ARGUMENT') is not None:  # p4a env variable; alternatively use ANDROID_PRIVATE
        return 'android'
    return env_str('KIVY_BUILD') or sys.platform    # KIVY_BUILD == 'android'/'ios' on Android/iOS


def sys_user_name() -> str:
    """ determine the operating system user name.

    :return:                    user name string.
    """
    return getpass.getuser()
