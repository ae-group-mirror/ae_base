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

The functions :func:`deep_assignment`, :func:`deep_object`
and :func:`deep_replace` is making your programmer life much
easier when you need to determine or change parts of deeply
nested data/object structures.

For to determine the value of an OS environment variable
with automatic variable name conversion you can use the
function :func:`env_str`.

:func:`norm_line_sep` is converting any combination of line
separators (`\r\n` or `\r`) in any string to a single new-line
character (`\n`).

Use the function :func:`norm_name` for to convert any string
into a name that can be used e.g. as file name or as
method/attribute name.

Other helper functions provided by this namespace portion for to
determine the values of the most important system environment
variables for your application are :func:`sys_env_dict`
and :func:`sys_env_text`.

The helper function :func:`sys_platform` are extending Python's
:func:`os.name` and :func:`sys.platform` functions for the
operating systems iOS and Android (not supported by Python).


lightweight base app class
==========================

This namespace portion is providing a very lightweight substitute
of an app base class (:class:`AppBase`) that can be used as a fallback
for other namespace portions if the features of the class
:class:`ae.core.AppBase` (declared in the module :mod:`ae.core`) are not
needed in your Python app.

The app base class that get normally determined via the helper function
:func:`ae.core.main_app_instance`. For to make the implementation of the
fallback easier the helper function :func:`~ae.base.base_app_instance`
can be used in the following manner::

    try:
        from ae.core import main_app_instance
    except ImportError:
        from ae.base import base_app_instance as main_app_instance

With this code block you can implement other modules/portions that
will automatically use the :class:`AppBase` substitute if the module
:mod:`ae.core` is not required by the importing app code/project.
"""
import ast
import getpass
import os
import platform
import sys
from operator import getitem
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union


__version__ = '0.1.2'


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


def base_app_instance() -> 'AppBase':
    """ lightweight substitute for :func:`ae.core.main_app_instance`.

    This method can be used as lightweight substitute if your app is not including/requiring the :mod:`ae.core`
    portion of the `ae` namespace.

    :return:                    instance of :class:`AppBase` as lightweight replacement of :class:`ae.core.AppBase`.
    """
    return _APP_BASE


def deep_assignment(obj: Any, key_or_attr: Union[str, int, tuple], new_value: Any,
                    mutable_parent: Optional[Any] = None):
    """ helper function for to set any (possibly immutable sub-) object attribute of list/dict item to a new value.

    :param obj:                 object to change. If immutable - like a str or tuple object - then a mutable object
                                situated higher in the same deep nested data structure has to be passed into the
                                optional argument :paramref:`~deep_assignment.mutable_parent`.
    :param key_or_attr:         dict/list/tuple/str key/index or attribute name to identify the element within
                                :paramref:`~deep_assignment.obj` to be changed.
    :param new_value:           value to be assigned to the item/attribute of :paramref:`~deep_assignment.obj`.
    :param mutable_parent:      mutable object which is situated in the same deep nested data structure anywhere
                                above of the immutable object (specified by :paramref:`~deep_assignment.obj`).
    """
    try:    # catch exception if obj is immutable (like e.g. str or tuple)
        if isinstance(obj, (list, dict)):
            obj[key_or_attr] = new_value            # type: ignore # mypy does not recognize correctly list/dict
        else:
            setattr(obj, key_or_attr, new_value)    # type: ignore
    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        if not mutable_parent:
            raise
        deep_replace(mutable_parent,
                     lambda d, k, v: new_value if (d == obj or d == list(obj)) and k == key_or_attr else UNSET,
                     immutable_types=(str, tuple))


def deep_object(obj: Any, key_path: str, new_value: Union[Any, None] = UNSET) -> Any:
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
                                        a_obj = AClass()

                                    b = BClass()
                                    assert deep_object(b, 'str_attr_name') == 'b_b_b_b_b'
                                    assert deep_object(b, 'a_obj.str_attr_name') == 'a_attr_val'
                                    assert deep_object(b, 'a_obj.dict_attr["a"]') == 3

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

    last_writable_obj = None
    get_func = getitem if isinstance(obj, (dict, list, tuple)) else getattr
    while key_path and obj != UNSET:
        idx = 0
        for char in key_path:
            if char in ('.', '[', ']'):     # == `char in '.[]'` - keep strings separate for speedup
                break
            idx += 1
        else:
            char = ""

        if isinstance(obj, (dict, list)):
            last_writable_obj = obj
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
                deep_assignment(last_obj, key, new_value, mutable_parent=last_writable_obj)
            break

        get_func = getitem if char == '[' else getattr
        key_path = key_path[idx + 1:]

    return obj


def deep_replace(data: DeepDataType, replace_with: Callable[[DeepDataType, Any, Any], Any],
                 immutable_types: Tuple[Type, ...] = (tuple, )):
    """ replace values within the passed (nested) data structure.

    :param data:                list or dict data structure for to be deep searched and replaced. Can contain any
                                combination of deep nested list/dict objects. The sub-structure-types dict and list
                                as well as the immutable types specified by :paramref:`~deep_replace.immutable_types`
                                will be recursively deep searched (top down) by passing their items one by one
                                to the function specified by :paramref:`~deep_replace.replace_with`.
    :param replace_with:        called for each item with 3 arguments (data-structure, key in data-structure, value),
                                and if the return value is not equal to :data:`UNSET` then it will be used for
                                to overwrite the value in the data-structure.
    :param immutable_types:     tuple of immutable iterable types which will be treated as replaceable items.
                                Each of the immutable types passed in this tuple has to be convertible to a list object.
                                By default only the items of a tuple are replaceable. For to also
                                allow the replacement of single characters in a string pass the argument value
                                `(tuple, str)` into this parameter.
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
        name = norm_name(name)
    return os.environ.get(name)


def norm_line_sep(text: str) -> str:
    """ convert any combination of line separators of the passed :paramref:`~norm_line_sep.text` to new-line characters.

    :param text:                string containing any combination of line separators (`\r\n` or `\r`).
    :return:                    normalized/converted string with only new-line (`\n`) line separator characters.
    """
    return text.replace('\r\n', '\n').replace('\r', '\n')


def norm_name(name: str, to_lower: Optional[bool] = False) -> str:
    """ normalize name for to contain only alpha-numeric and underscore chars (e.g. for a variable-/method-/file-name).

    :param name:                any string to be converted into a valid variable/method/file/... name.
    :param to_lower:            By default (`False`) the resulting name will only contain upper-case characters
                                and upper-case characters in the passed :paramref:`~norm_name.name` argument
                                will be preceded by an underscore character (excluding the first character).
                                Pass `True` to get only lower-case characters in the returned normalized name.
                                Pass `None` for to not change the case of the characters.
    :return:                    normalized/converted name string.
    """
    str_parts = list()
    for idx, char in enumerate(name):
        if idx != 0 and char.isupper() and to_lower is False:
            str_parts.append('_' + char)
        elif char.isalnum():
            if to_lower and char.isupper():
                char = char.lower()
            elif to_lower is False and char.islower():
                char = char.upper()
            str_parts.append(char)
        else:
            str_parts.append('_')
    return ''.join(str_parts)


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


class AppBase:
    """ stub class for to simulate/substitute :class:`ae.core.AppBase` for small apps not using :mod:`ae.core`. """
    font_size: float = 39

    @staticmethod
    def dpo(*args, **kwargs):
        """ print to console """
        print(*args, **kwargs)

    @staticmethod
    def vpo(*args, **kwargs):
        """ print to console """
        print(*args, **kwargs)


_APP_BASE = AppBase()
