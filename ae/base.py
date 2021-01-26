"""
basic constants and helper functions
====================================

This module is pure python and has no external dependencies. Apart from providing base constants and common helper
functions it is also patching the :mod:`shutil` module for to prevent crashes on the Android OS.


base constants
--------------

Generic ISO format strings for `date` and `datetime` values are provided by the constants :data:`DATE_ISO` and
:data:`DATE_TIME_ISO`.

The :data:`UNSET` constant is useful in cases where `None` is a valid data value and another special value is needed
for to specify that e.g. an argument or attribute has no (valid) value.


base helper functions
---------------------

For to determine the value of an OS environment variable with automatic variable name conversion you can use the
function :func:`env_str`.

Other helper functions provided by this namespace portion for to determine the values of the most important system
environment variables for your application are :func:`sys_env_dict` and :func:`sys_env_text`.

:func:`norm_line_sep` is converting any combination of line separators of a string to a single new-line character.

Use the function :func:`norm_name` for to convert any string into a name that can be used e.g. as file name or as
method/attribute name.

:func:`camel_to_snake` and :func:`snake_to_camel` does also small and very useful name conversions of class and
method names.

The provided string :data:`os_platform` gets determined for most of the operating systems with the help of Python's
:func:`os.name` and :func:`sys.platform` functions and additionally detects the operating systems iOS and Android (not
supported by Python).

For to encode unicode strings to other codecs the functions :func:`force_encoding` and :func:`to_ascii` can be used.

The :func:`round_traditional` function get provided by this module for traditional rounding of float values. The
function signature is fully compatible to Python's :func:`round` function.
"""
import datetime
import getpass
import os
import platform
import shutil
import socket
import sys
import unicodedata

from typing import Any, AnyStr, Dict, Iterable, Optional, cast


__version__ = '0.1.12'


DATE_ISO: str = '%Y-%m-%d'                      #: ISO string format for date values (e.g. in config files/variables)
DATE_TIME_ISO: str = '%Y-%m-%d %H:%M:%S.%f'     #: ISO string format for datetime values

DEF_ENCODE_ERRORS: str = 'backslashreplace'     #: default encode error handling for UnicodeEncodeErrors
DEF_ENCODING: str = 'ascii'
""" encoding for :func:`force_encoding` that will always work independent from destination (console, file sys, ...).
"""

NAME_PARTS_SEP = '_'                            #: name parts separator character, e.g. for :func:`norm_name`


# using only object() does not provide proper representation string, hopefully  UNSET = _UNSET() is not needed
class UNSET:
    """ (singleton) UNSET (type) object used for attributes/arguments if `None` is needed as a valid value. """


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


def camel_to_snake(name: str) -> str:
    """ convert name from CamelCase to snake_case.

    :param name:                name string in snake case format.
    :return:                    name in camel case.
    """
    str_parts = list()
    for char in name:
        if char.isupper():
            str_parts.append(NAME_PARTS_SEP + char)
        else:
            str_parts.append(char)
    return "".join(str_parts)


def duplicates(values: Iterable) -> list:
    """ determine all duplicates in the passed iterable.

    Inspired by Ritesh Kumars answer to https://stackoverflow.com/questions/9835762.

    :param values:              iterable (list, tuple, str, ...) to search for duplicate items.
    :return:                    list of the duplicate items found (can contain the same duplicate multiple times).
    """
    seen_set: set = set()
    seen_add = seen_set.add
    dup_list: list = list()
    dup_add = dup_list.append
    for item in values:
        if item in seen_set:
            dup_add(item)
        else:
            seen_add(item)
    return dup_list


def env_str(name: str, convert_name: bool = False) -> Optional[str]:
    """ determine the string value of an OS environment variable, optionally preventing invalid variable name.

    :param name:                name of a OS environment variable.
    :param convert_name:        pass True for to prevent invalid variable names by converting
                                CamelCase names into SNAKE_CASE, lower-case into
                                upper-case and all non-alpha-numeric characters into underscore characters.
    :return:                    string value of OS environment variable if found, else None.
    """
    if convert_name:
        name = norm_name(camel_to_snake(name)).upper()
    return os.environ.get(name)


def force_encoding(text: AnyStr, encoding: str = DEF_ENCODING, errors: str = DEF_ENCODE_ERRORS) -> str:
    """ force/ensure the encoding of text (str or bytes) without any UnicodeDecodeError/UnicodeEncodeError.

    :param text:                text as str/bytes.
    :param encoding:            encoding (def= :data:`DEF_ENCODING`).
    :param errors:              encode error handling (def= :data:`DEF_ENCODE_ERRORS`).

    :return:                    text as str (with all characters checked/converted/replaced for to be encode-able).
    """
    enc_str: bytes = cast(str, text).encode(encoding=encoding, errors=errors) if isinstance(text, str) else text
    return enc_str.decode(encoding=encoding)


def norm_line_sep(text: str) -> str:
    """ convert any combination of line separators in the passed :paramref:`~norm_line_sep.text` to new-line characters.

    :param text:                string containing any combination of line separators ('\\\\r\\\\n' or '\\\\r').
    :return:                    normalized/converted string with only new-line ('\\\\n') line separator characters.
    """
    return text.replace('\r\n', '\n').replace('\r', '\n')


def norm_name(name: str) -> str:
    """ normalize name for to contain only alpha-numeric and underscore chars (e.g. for a variable-/method-/file-name).

    :param name:                any string to be converted into a valid variable/method/file/... name.
    :return:                    cleaned/normalized/converted name string.
    """
    str_parts = list()
    for char in name:
        if char.isalnum():
            str_parts.append(char)
        else:
            str_parts.append('_')
    return "".join(str_parts)


def now_str(sep: str = "") -> str:
    """ return the current timestamp as string (for to use as suffix for file and variable/attribute names).

    :param sep:                 optional prefix and separator character (separating date from time and in time part
                                the seconds from the microseconds).
    :return:                    timestamp as string (length=20 + 3 * len(sep)).
    """
    return datetime.datetime.now().strftime("{sep}%Y%m%d{sep}%H%M%S{sep}%f".format(sep=sep))


def os_host_name() -> str:
    """ determine the operating system host/machine name.

    :return:                    machine name string.
    """
    return platform.node()


def os_local_ip() -> str:
    """ determine ip address of this system/machine in the local network (LAN or WLAN).

    inspired by answers of SO users @dml and @fatal_error to the question: https://stackoverflow.com/questions/166506.

    :return:                    ip address of this machine in the local network (WLAN or LAN/ethernet)
                                or empty string if this machine is not connected to any network.
    """
    socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        socket1.connect(('10.255.255.255', 1))      # doesn't even have to be reachable
        ip_address = socket1.getsockname()[0]
    except (OSError, IOError):                      # pragma: no cover
        # ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError inherit from OSError
        socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            socket2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            socket2.connect(('<broadcast>', 0))
            ip_address = socket2.getsockname()[0]
        except (OSError, IOError):
            ip_address = ""
        finally:
            socket2.close()
    finally:
        socket1.close()

    return ip_address


def _os_platform() -> str:
    """ determine the operating system where this code is running (used to initialize the :data:`os_platform` variable).

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


os_platform = _os_platform()        #: operating system / platform string (see :func:`_os_platform`).


def os_user_name() -> str:
    """ determine the operating system user name.

    :return:                    user name string.
    """
    return getpass.getuser()


def round_traditional(num_value: float, num_digits: int = 0) -> float:
    """ round numeric value traditional.

    Needed because python round() is working differently, e.g. round(0.075, 2) == 0.07 instead of 0.08
    inspired by https://stackoverflow.com/questions/31818050/python-2-7-round-number-to-nearest-integer.

    :param num_value:           float value to be round.
    :param num_digits:          number of digits to be round (def=0 - rounds to an integer value).

    :return:                    rounded value.
    """
    return round(num_value + 10 ** (-len(str(num_value)) - 1), num_digits)


if os_platform == 'android':                                    # pragma: no cover
    # monkey patch the :func:`shutil.copystat` and :func:`shutil.copymode` helper functions, which are crashing on
    # 'android' (see # https://bugs.python.org/issue28141 and https://bugs.python.org/issue32073). These functions are
    # used by shutil.copy2/copy/copytree/move for to copy OS-specific file attributes.
    # Although shutil.copytree() and shutil.move() are copying/moving the files correctly when the copy_function
    # arg is set to :func:`shutil.copyfile`, they will finally also crash afterwards when they try to set the attributes
    # on the destination root directory.
    shutil.copymode = lambda *args, **kwargs: None      # print("shutil.copymode ae.base.PATCH", args, kwargs)
    shutil.copystat = lambda *args, **kwargs: None      # print("shutil.copystat ae.base.PATCH", args, kwargs)


def snake_to_camel(name: str, back_convertible: bool = False) -> str:
    """ convert name from snake_case to CamelCase.

    :param name:                name string composed of parts separated by an underscore character
                                (:data:`NAME_PARTS_SEP`).
    :param back_convertible:    pass `True` to have lower-case character at the begin of the returned name
                                if the snake name has no leading underscore character (and for to allow
                                the conversion between snake and camel case without information loss).
    :return:                    name in camel case.
    """
    ret = "".join(part.capitalize() for part in name.split(NAME_PARTS_SEP))
    if back_convertible and name[0] != NAME_PARTS_SEP:
        ret = ret[0].lower() + ret[1:]
    return ret


def sys_env_dict() -> Dict[str, Any]:
    """ returns dict with python system run-time environment values.

    :return:                    python system run-time environment values like python_ver, argv, cwd, executable,
                                frozen and bundle_dir (if bundled with pyinstaller).

    .. hint:: see also https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
    """
    sed: Dict[str, Any] = dict()

    sed['python_ver'] = sys.version.replace('\n', ' ')
    sed['platform'] = os_platform
    sed['argv'] = sys.argv
    sed['executable'] = sys.executable
    sed['cwd'] = os.getcwd()
    sed['frozen'] = getattr(sys, 'frozen', False)
    if getattr(sys, 'frozen', False):
        sed['bundle_dir'] = getattr(sys, '_MEIPASS', '*#ERR#*')
    sed['user_name'] = os_user_name()
    sed['host_name'] = os_host_name()
    sed['app_name_guess'] = app_name_guess()

    return sed


def sys_env_text(ind_ch: str = " ", ind_len: int = 12, key_ch: str = "=", key_len: int = 15,
                 extra_sys_env_dict: Optional[Dict[str, str]] = None) -> str:
    """ compile formatted text block with system environment info.

    :param ind_ch:              indent character (default=" ").
    :param ind_len:             indent depths (default=12 characters).
    :param key_ch:              key-value separator character (default="=").
    :param key_len:             key-name minimum length (default=15 characters).
    :param extra_sys_env_dict:  dict with additional system info items.
    :return:                    text block with system environment info.
    """
    sed = sys_env_dict()
    if extra_sys_env_dict:
        sed.update(extra_sys_env_dict)
    key_len = max([key_len] + [len(key) + 1 for key in sed])

    ind = ""
    text = "\n".join([f"{ind:{ind_ch}>{ind_len}}{key:{key_ch}<{key_len}}{val}" for key, val in sed.items()])

    return text


def to_ascii(unicode_str: str) -> str:
    """ converts unicode string into ascii representation.

    Useful for fuzzy string compare; inspired by MiniQuark's answer
    in: https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string

    :param unicode_str:         string to convert.
    :return:                    converted string (replaced accents, diacritics, ... into normal ascii characters).
    """
    nfkd_form = unicodedata.normalize('NFKD', unicode_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])
