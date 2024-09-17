"""
basic constants, helper functions and context manager
=====================================================

this module is pure python, has no external dependencies, and is providing base constants, common helper
functions and context managers.


base constants
--------------

ISO format strings for `date` and `datetime` values are provided by the constants :data:`DATE_ISO` and
:data:`DATE_TIME_ISO`.

the :data:`UNSET` constant is useful in cases where `None` is a valid data value and another special value is needed
to specify that e.g. an argument or attribute has no (valid) value or did not get specified/passed.

default values to compile file and folder names for a package or an app project are provided by the constants:
:data:`DOCS_FOLDER`, :data:`TESTS_FOLDER`, :data:`TEMPLATES_FOLDER`, :data:`BUILD_CONFIG_FILE`,
:data:`PACKAGE_INCLUDE_FILES_PREFIX`, :data:`PY_EXT`, :data:`PY_INIT`, :data:`PY_MAIN`, :data:`CFG_EXT`
and :data:`INI_EXT`.

the constants :data:`PACKAGE_NAME`, :data:`PACKAGE_DOMAIN` and :data:`PERMISSIONS` are mainly used for apps running
on mobile devices. to avoid redundancies, these values get loaded from the
:data:`build config file <BUILD_CONFIG_FILE>` - if it exists in the current working directory.


base helper functions
---------------------

to write more compact and readable code for the most common file I/O operations, the helper functions :func:`read_file`
and :func:`write_file` are wrapping Python's built-in :func:`open` function and its context manager.

the function :func:`duplicates` returns the duplicates of an iterable type.

:func:`norm_line_sep` is converting any combination of line separators of a string to a single new-line character.

:func:`norm_name` converts any string into a name that can be used e.g. as file name or as method/attribute name.

to normalize a file path, in order to remove `.`, `..` placeholders, to resolve symbolic links or to make it relative or
absolute, call the function :func:`norm_path`.

:func:`camel_to_snake` and :func:`snake_to_camel` providing name conversions of class and method names.

to encode Unicode strings to other codecs the functions :func:`force_encoding` and :func:`to_ascii` can be used.

the :func:`round_traditional` function get provided by this module for traditional rounding of float values. the
function signature is fully compatible to Python's :func:`round` function.

the function :func:`instantiate_config_parser` ensures that the :class:`~configparser.ConfigParser` instance is
correctly configured, e.g. to support case-sensitive config variable names and to use :class:`ExtendedInterpolation` for
the interpolation argument.

:func:`app_name_guess` guesses the name of o running Python application from the application environment, with the help
of :func:`build_config_variable_values`, which determines config-variable-values from the build spec file of an app
project.


operating system constants and helpers
--------------------------------------

the string :data:`os_platform` provides the OS where your app is running, extending Python's :func:`sys.platform`
for mobile platforms like Android and iOS.

:func:`os_host_name`, :func:`os_local_ip` and :func:`os_user_name` are determining machine and user information from
the OS.

use :func:`env_str` to determine the value of an OS environment variable with automatic variable name conversion. other
helper functions provided by this namespace portion to determine the values of the most important system environment
variables for your application are :func:`sys_env_dict` and :func:`sys_env_text`.

to integrate system environment variables from ``.env`` files into :data:`os.environ` the helper functions
:func:parse_dotenv`, :func:`load_env_var_defaults` and :func:`load_dotenvs` are provided.


android-specific constants and helper functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

some helper functions of this module are provided to be used for the Android OS.

the helper function :func:`start_app_service` is starting a service in its own, separate thread.
with the function :func:`request_app_permissions` you can ensure that all your Android permissions will be
requested. the module :mod:`ae.kivy.apps` does this automatically on app startup. on other platforms than
Android it will have no effect to call these functions.

.. note:: importing this module on an Android OS, it is monkey patching the :mod:`shutil` module to prevent crashes.

links to other android code and service examples and documentation:

    * `https://python-for-android.readthedocs.io/en/latest/`__
    * `https://github.com/kivy/python-for-android/tree/develop/pythonforandroid/recipes/android/src/android`__
    * `https://github.com/tshirtman/kivy_service_osc/blob/master/src/main.py`__
    * `https://blog.kivy.org/2014/01/building-a-background-application-on-android-with-kivy/`__
    * `https://github.com/Android-for-Python/Android-for-Python-Users`__
    * `https://github.com/Android-for-Python/INDEX-of-Examples`__

big thanks to `Robert Flatt <https://github.com/RobertFlatt>`_ for his investigations, findings and documentations to
code and build Kivy apps for the Android OS, and to `Gabriel Pettier <https://github.com/tshirtman>`_ for his service
osc example.


generic context manager
-----------------------

the context manager :func:`in_wd` allows to switch the current working directory temporarily. the following
example demonstrates a typical usage, together with a temporary path, created with the help of Pythons
:class:`~tempfile.TemporaryDirectory` class::

    with tempfile.TemporaryDirectory() as tmp_dir, in_wd(tmp_dir):
        # within the context the tmp_dir is set as the current working directory
        assert os.getcwd() == tmp_dir
    # current working directory set back to the original path and the temporary directory got removed


call stack inspection
---------------------

:func:`module_attr` dynamically determines a reference to an attribute (variable, function, class, ...) in a module.

:func:`module_name`, :func:`stack_frames`, :func:`stack_var` and :func:`stack_vars` are inspecting the call stack frames
to determine e.g. variable values of the callers of a function/method.

.. hint::
    the :class:`AppBase` class uses these helper functions to determine the :attr:`version <AppBase.app_version>` and
    :attr:`title <AppBase.app_title>` of an application, if these values are not specified in the instance initializer.

another useful helper function provided by this portion to inspect and debug your code is :func:`full_stack_trace`.
"""
import datetime
import getpass
import importlib.abc
import importlib.util
import os
import platform
import re
import shutil
import socket
import sys
import unicodedata
import urllib.parse
import warnings

from configparser import ConfigParser, ExtendedInterpolation
from contextlib import contextmanager
from importlib.machinery import ModuleSpec
from inspect import getinnerframes, getouterframes, getsourcefile
from types import ModuleType
from typing import Any, Callable, Dict, Generator, Iterable, List, Optional, Tuple, Union, cast


__version__ = '0.3.39'


DOCS_FOLDER = 'docs'                            #: project documentation root folder name
TESTS_FOLDER = 'tests'                          #: name of project folder to store unit/integration tests
TEMPLATES_FOLDER = 'templates'
""" template folder name, used in template and namespace root projects to maintain and provide common file templates """

BUILD_CONFIG_FILE = 'buildozer.spec'            #: gui app build config file
PACKAGE_INCLUDE_FILES_PREFIX = 'ae_'            #: file/folder names prefix included into setup package_data/ae_updater

PY_CACHE_FOLDER = '__pycache__'                 #: python cache folder name
PY_EXT = '.py'                                  #: file extension for modules and hooks
PY_INIT = '__init__' + PY_EXT                   #: init-module file name of a python package
PY_MAIN = '__main__' + PY_EXT                   #: main-module file name of a python executable

CFG_EXT = '.cfg'                                #: CFG config file extension
INI_EXT = '.ini'                                #: INI config file extension

DATE_ISO = "%Y-%m-%d"                           #: ISO string format for date values (e.g. in config files/variables)
DATE_TIME_ISO = "%Y-%m-%d %H:%M:%S.%f"          #: ISO string format for datetime values

DEF_ENCODE_ERRORS = 'backslashreplace'          #: default encode error handling for UnicodeEncodeErrors
DEF_ENCODING = 'ascii'
""" encoding for :func:`force_encoding` that will always work independent from destination (console, file sys, ...).
"""

DOTENV_FILE_NAME = '.env'                       #: name of the file containing console/shell environment variables
_env_line = re.compile(r"""
    ^
    (?:export\s+)?      # optional export
    ([\w.]+)            # key
    (?:\s*=\s*|:\s+?)   # separator
    (                   # optional value begin
        '(?:\'|[^'])*'  #   single quoted value
        |               #   or
        "(?:\"|[^"])*"  #   double quoted value
        |               #   or
        [^#\n]+         #   unquoted value
    )?                  # value end
    (?:\s*\#.*)?        # optional comment
    $
    """, re.VERBOSE)
_env_variable = re.compile(r"""
    (\\)?               # is it escaped with a backslash?
    (\$)                # literal $
    (                   # collect braces with var for sub
        \{?             #   allow brace wrapping
        ([A-Z0-9_]+)    #   match the variable
        }?              #   closing brace
    )                   # braces end
    """, re.IGNORECASE | re.VERBOSE)


NAME_PARTS_SEP = '_'                            #: name parts separator character, e.g. for :func:`norm_name`

SKIPPED_MODULES = ('ae.base', 'ae.paths', 'ae.dynamicod', 'ae.core', 'ae.console', 'ae.gui_app', 'ae.gui_help',
                   'ae.kivy', 'ae.kivy.apps', 'ae.kivy.behaviors', 'ae.kivy.i18n', 'ae.kivy.tours', 'ae.kivy.widgets',
                   'ae.enaml_app', 'ae.beeware_app', 'ae.pyglet_app', 'ae.pygobject_app', 'ae.dabo_app',
                   'ae.qpython_app', 'ae.appjar_app',   # removed in V 0.1.4: 'ae.lisz_app_data',
                   'importlib._bootstrap', 'importlib._bootstrap_external')
""" skipped modules used as default by :func:`module_name`, :func:`stack_var` and :func:`stack_vars` """


# using only object() does not provide proper representation string
class UnsetType:
    """ (singleton) UNSET (type) object class. """
    def __bool__(self):
        """ ensure to be evaluated as False, like None. """
        return False

    def __len__(self):
        """ ensure to be evaluated as empty. """
        return 0


UNSET = UnsetType()     #: pseudo value used for attributes/arguments if `None` is needed as a valid value


def app_name_guess() -> str:
    """ guess/try to determine the name of the currently running app (w/o assessing not yet initialized app instance).

    :return:                    application name/id or "unguessable" if not guessable.
    """
    app_name = build_config_variable_values(('package.name', ""))[0]
    if not app_name:
        unspecified_app_names = ('ae_base', 'app', '_jb_pytest_runner', 'main', '__main__', 'pydevconsole', 'src')
        path = sys.argv[0]
        app_name = os.path.splitext(os.path.basename(path))[0]
        if app_name.lower() in unspecified_app_names:
            path = os.getcwd()
            app_name = os.path.basename(path)
            if app_name.lower() in unspecified_app_names:
                app_name = "unguessable"
    return app_name


def build_config_variable_values(*names_defaults: Tuple[str, Any], section: str = 'app') -> Tuple[Any, ...]:
    """ determine build config variable values from the ``buildozer.spec`` file in the current directory.

    :param names_defaults:      tuple of tuples of build config variable names and default values.
    :param section:             name of the spec file section, using 'app' as default.
    :return:                    tuple of build config variable values (using the passed default value if not specified
                                in the :data:`BUILD_CONFIG_FILE` spec file or if the spec file does not exist in cwd).
    """
    if not os.path.exists(BUILD_CONFIG_FILE):
        return tuple(def_val for name, def_val in names_defaults)

    config = instantiate_config_parser()
    config.read(BUILD_CONFIG_FILE, 'utf-8')

    return tuple(config.get(section, name, fallback=def_val) for name, def_val in names_defaults)


def camel_to_snake(name: str) -> str:
    """ convert name from CamelCase to snake_case.

    :param name:                name string in CamelCaseFormat.
    :return:                    name in snake_case_format.
    """
    str_parts = []
    for char in name:
        if char.isupper():
            str_parts.append(NAME_PARTS_SEP + char)
        else:
            str_parts.append(char)
    return "".join(str_parts)


def deep_dict_update(data: dict, update: dict):
    """ update the optionally nested data dict in-place with the items and sub-items from the update dict.

    :param data:                dict to be updated/extended. non-existing keys of dict-sub-items will be added.
    :param update:              dict with the [sub-]items to update in the :paramref:`~deep_dict_update.data` dict.

    .. hint:: the module/portion :mod:`ae.deep` is providing more deep update helper functions.

    """
    for upd_key, upd_val in update.items():
        if isinstance(upd_val, dict):
            if upd_key not in data:
                data[upd_key] = {}
            deep_dict_update(data[upd_key], upd_val)
        else:
            data[upd_key] = upd_val


def dummy_function(*_args, **_kwargs):
    """ null function accepting any arguments and returning None.

    :param _args:               ignored positional arguments.
    :param _kwargs:             ignored keyword arguments.
    :return:                    always None.
    """


def duplicates(values: Iterable) -> list:
    """ determine all duplicates in the iterable specified in the :paramref:`~duplicates.values` argument.

    inspired by Ritesh Kumars answer to https://stackoverflow.com/questions/9835762.

    :param values:              iterable (list, tuple, str, ...) to search for duplicate items.
    :return:                    list of the duplicate items found (can contain the same duplicate multiple times).
    """
    seen_set: set = set()
    seen_add = seen_set.add
    dup_list: list = []
    dup_add = dup_list.append
    for item in values:
        if item in seen_set:
            dup_add(item)
        else:
            seen_add(item)
    return dup_list


def env_str(name: str, convert_name: bool = False) -> Optional[str]:
    """ determine the string value of an OS environment variable, optionally preventing invalid variable name.

    :param name:                name of an OS environment variable.
    :param convert_name:        pass True to prevent invalid variable names by converting
                                CamelCase names into SNAKE_CASE, lower-case into
                                upper-case and all non-alpha-numeric characters into underscore characters.
    :return:                    string value of OS environment variable if found, else None.
    """
    if convert_name:
        name = norm_name(camel_to_snake(name)).upper()
    return os.environ.get(name)


def force_encoding(text: Union[str, bytes], encoding: str = DEF_ENCODING, errors: str = DEF_ENCODE_ERRORS) -> str:
    """ force/ensure the encoding of text (str or bytes) without any UnicodeDecodeError/UnicodeEncodeError.

    :param text:                text as str/bytes.
    :param encoding:            encoding (def= :data:`DEF_ENCODING`).
    :param errors:              encode error handling (def= :data:`DEF_ENCODE_ERRORS`).

    :return:                    text as str (with all characters checked/converted/replaced to be encode-able).
    """
    enc_str: bytes = text.encode(encoding=encoding, errors=errors) if isinstance(text, str) else text
    return enc_str.decode(encoding=encoding)


def full_stack_trace(ex: Exception) -> str:
    """ get full stack trace from an exception.

    :param ex:                  exception instance.
    :return:                    str with stack trace info.
    """
    ret = f"Exception {ex!r}. Traceback:" + os.linesep
    trace_back = sys.exc_info()[2]
    if trace_back:
        def ext_ret(item):
            """ process traceback frame and add as str to ret """
            nonlocal ret
            ret += f'File "{item[1]}", line {item[2]}, in {item[3]}' + os.linesep
            lines = item[4]  # mypy does not detect item[]
            if lines:
                for line in lines:
                    ret += ' ' * 4 + line.lstrip()

        for frame in reversed(getouterframes(trace_back.tb_frame)[1:]):
            ext_ret(frame)
        for frame in getinnerframes(trace_back):
            ext_ret(frame)
    return ret


def import_module(import_name: str, path: Optional[Union[str, UnsetType]] = UNSET) -> Optional[ModuleType]:
    """ search, import and execute a Python module dynamically without adding it to sys.modules.

    :param import_name:         dot-name of the module to import.
    :param path:                optional file path of the module to import. if this arg is not specified or has the
                                default value (:data:`UNSET`), then the path will be determined from the import name.
                                specify ``None`` to prevent the module search.
    :return:                    a reference to the loaded module or ``None`` if module could not be imported.
    """
    if path is UNSET:
        path = import_name.replace('.', os.path.sep)
        path += PY_EXT if os.path.isfile(path + PY_EXT) else os.path.sep + PY_INIT
    mod_ref = None

    spec = importlib.util.spec_from_file_location(import_name, path)    # type: ignore # silly mypy
    if isinstance(spec, ModuleSpec):
        mod_ref = importlib.util.module_from_spec(spec)
        # added isinstance and imported importlib.abc to suppress PyCharm+mypy inspections
        if isinstance(spec.loader, importlib.abc.Loader):
            try:
                spec.loader.exec_module(mod_ref)
            except FileNotFoundError:
                mod_ref = None

    return mod_ref


def instantiate_config_parser() -> ConfigParser:
    """ instantiate and prepare config file parser. """
    cfg_parser = ConfigParser(allow_no_value=True, interpolation=ExtendedInterpolation())
    # set optionxform to have case-sensitive var names (or use 'lambda option: option')
    # mypy V 0.740 bug - see mypy issue #5062: adding pragma "type: ignore" breaks PyCharm (showing
    # .. inspection warning "Non-self attribute could not be type-hinted"), but
    # .. also cast(Callable[[Arg(str, 'option')], str], str) and # type: ... is not working
    # .. (because Arg is not available in plain mypy, only in the extra mypy_extensions package)
    setattr(cfg_parser, 'optionxform', str)
    return cfg_parser


@contextmanager
def in_wd(new_cwd: str) -> Generator[None, None, None]:
    """ context manager to temporary switch the current working directory / cwd.

    :param new_cwd:             path to the directory to switch to (within the context/with block).
                                an empty string gets interpreted as the current working directory.
    """
    cur_dir = os.getcwd()
    try:
        if new_cwd:             # empty new_cwd results in current working folder (no dir change needed/prevent error)
            os.chdir(new_cwd)
        yield
    finally:
        os.chdir(cur_dir)


def load_dotenvs():
    """ detect and load multiple ``.env`` files in/above the current working directory and the calling module folder.

    .. hint:: call from main module of project/app in order to also load ``.env`` files in/above the project folder.
    """
    load_env_var_defaults(os.getcwd())
    if file_name := stack_var('__file__'):
        load_env_var_defaults(os.path.dirname(os.path.abspath(file_name)))


def load_env_var_defaults(start_dir: str):
    """ detect and load chain of ``.env`` files starting in the specified folder or one above.

    :param start_dir:           folder to start search of an ``.env`` file, if not found then checks the parent folder.
                                if a first ``.env`` file got found, then load their console/shell environment variables
                                into Python's :data:`os.environ`. after loading the first one, repeat to check for
                                further ``.env`` files in the parent folder to load them too, until either detecting
                                a folder without an ``.env`` file or until an ``.env`` got loaded from the root folder.

    .. note::
        only variables that are not declared in :data:`os.environ` will be added (with the
        value specified in the ``.env`` file to be loaded).
    """
    file_path = os.path.abspath(os.path.join(start_dir, DOTENV_FILE_NAME))
    if not os.path.isfile(file_path):
        file_path = os.path.join(os.path.dirname(start_dir), DOTENV_FILE_NAME)

    while os.path.isfile(file_path):
        for var_nam, var_val in parse_dotenv(file_path).items():
            if var_nam not in os.environ:
                os.environ[var_nam] = var_val

        if os.sep not in file_path:
            break           # pragma: no cover # prevent endless-loop for ``.env`` file in root dir (os.sep == '/')
        file_path = os.path.join(os.path.dirname(os.path.dirname(file_path)), DOTENV_FILE_NAME)


def main_file_paths_parts(portion_name: str) -> Tuple[Tuple[str, ...], ...]:
    """ determine tuple of supported main/version file name path part tuples.

    :param portion_name:        portion or package name.
    :return:                    tuple of tuples of main/version file name path parts.
    """
    return (
        ('main' + PY_EXT, ),
        (PY_MAIN, ),
        (PY_INIT, ),
        ('main', PY_INIT),          # django main project
        (portion_name + PY_EXT, ),
        (portion_name, PY_INIT),
    )


def module_attr(import_name: str, attr_name: str = "") -> Optional[Any]:
    """ determine dynamically a reference to a module or to any attribute (variable/func/class) declared in the module.

    :param import_name:         import-/dot-name of the distribution/module/package to load/import.
    :param attr_name:           name of the attribute declared within the module. do not specify or pass an empty
                                string to get/return a reference to the imported module instance.
    :return:                    module instance or module attribute value
                                or None if module not found
                                or UNSET if module attribute doesn't exist.

    .. note:: a previously not imported module will *not* be added to `sys.modules` by this function.

    """
    mod_ref = sys.modules.get(import_name, None) or import_module(import_name)
    return getattr(mod_ref, attr_name, UNSET) if mod_ref and attr_name else mod_ref


def module_file_path(local_object: Optional[Callable] = None) -> str:
    """ determine the absolute path of the module from which this function got called.

    :param local_object:        optional local module, class, method, function, traceback, frame, or code object of the
                                calling module (passing `lambda: 0` also works). omit to use instead the `__file__`
                                module variable (which will not work if the module is frozen by ``py2exe`` or
                                ``PyInstaller``).
    :return:                    module path (inclusive module file name) or empty string if path not found/determinable.
    """
    if local_object:
        file_path = getsourcefile(local_object)
        if file_path:
            return norm_path(file_path)

    file_path = stack_var('__file__')
    if not file_path:                                   # pragma: no cover
        try:
            # noinspection PyProtectedMember,PyUnresolvedReferences
            file_path = sys._getframe().f_back.f_code.co_filename   # type: ignore # pylint: disable=protected-access
        except (AttributeError, Exception):                         # pylint: disable=broad-except # pragma: no cover
            file_path = ""
    return file_path


def module_name(*skip_modules: str, depth: int = 0) -> Optional[str]:
    """ find the first module in the call stack that is *not* in :paramref:`~module_name.skip_modules`.

    :param skip_modules:        module names to skip (def=this ae.core module).
    :param depth:               the calling level from which on to search. the default value 0 refers the frame and
                                the module of the caller of this function.
                                pass 1 or an even higher value if you want to get the module name of a function/method
                                in a deeper level in the call stack.
    :return:                    the module name of the call stack level specified by :paramref:`~module_name.depth`.
    """
    if not skip_modules:
        skip_modules = SKIPPED_MODULES
    return stack_var('__name__', *skip_modules, depth=depth + 1)


def norm_line_sep(text: str) -> str:
    """ convert any combination of line separators in the :paramref:`~norm_line_sep.text` arg to new-line characters.

    :param text:                string containing any combination of line separators ('\\\\r\\\\n' or '\\\\r').
    :return:                    normalized/converted string with only new-line ('\\\\n') line separator characters.
    """
    return text.replace('\r\n', '\n').replace('\r', '\n')


def norm_name(name: str, allow_num_prefix: bool = False) -> str:
    """ normalize name to start with a letter/alphabetic/underscore and to contain only alphanumeric/underscore chars.

    :param name:                any string to be converted into a valid variable/method/file/... name.
    :param allow_num_prefix:    pass True to allow leading digits in the returned normalized name.
    :return:                    cleaned/normalized/converted name string (e.g. for a variable-/method-/file-name).
    """
    str_parts: List[str] = []
    for char in name:
        if char.isalpha() or char.isalnum() and (allow_num_prefix or str_parts):
            str_parts.append(char)
        else:
            str_parts.append('_')
    return "".join(str_parts)


def norm_path(path: str, make_absolute: bool = True, remove_base_path: str = "", remove_dots: bool = True,
              resolve_sym_links: bool = True) -> str:
    """ normalize path, replacing `..`/`.` parts or the tilde character (for home folder) and transform to relative/abs.

    :param path:                path string to normalize/transform.
    :param make_absolute:       pass False to not convert path to an absolute path.
    :param remove_base_path:    pass a valid base path to return a relative path, even if the argument values of
                                :paramref:`~norm_path.make_absolute` or :paramref:`~norm_path.resolve_sym_links` are
                                `True`.
    :param remove_dots:         pass False to not replace/remove the `.` and `..` placeholders.
    :param resolve_sym_links:   pass False to not resolve symbolic links, passing True implies a `True` value also for
                                the :paramref:`~norm_path.make_absolute` argument.
    :return:                    normalized path string: absolute if :paramref:`~norm_path.remove_base_path` is empty and
                                either :paramref:`~norm_path.make_absolute` or :paramref:`~norm_path.resolve_sym_links`
                                is `True`; relative if :paramref:`~norm_path.remove_base_path` is a base path of
                                :paramref:`~norm_path.path` or if :paramref:`~norm_path.path` got specified as relative
                                path and neither :paramref:`~norm_path.make_absolute` nor
                                :paramref:`~norm_path.resolve_sym_links` is `True`.

    .. hint:: the :func:`~ae.paths.normalize` function additionally replaces :data:`~ae.paths.PATH_PLACEHOLDERS`.

    """
    path = path or "."
    if path[0] == "~":
        path = os.path.expanduser(path)

    if remove_dots:
        path = os.path.normpath(path)

    if resolve_sym_links:
        path = os.path.realpath(path)
    elif make_absolute:
        path = os.path.abspath(path)

    if remove_base_path:
        if remove_base_path[0] == "~":
            remove_base_path = os.path.expanduser(remove_base_path)
        path = os.path.relpath(path, remove_base_path)

    return path


def now_str(sep: str = "") -> str:
    """ return the current UTC timestamp as string (to use as suffix for file and variable/attribute names).

    :param sep:                 optional prefix and separator character (separating date from time and in time part
                                the seconds from the microseconds).
    :return:                    UTC timestamp as string (length=20 + 3 * len(sep)).
    """
    return datetime.datetime.utcnow().strftime("{sep}%Y%m%d{sep}%H%M%S{sep}%f".format(sep=sep))


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
    if env_str('ANDROID_ARGUMENT') is not None:     # p4a env variable; alternatively use ANDROID_PRIVATE
        return 'android'
    return env_str('KIVY_BUILD') or sys.platform    # KIVY_BUILD == 'android'/'ios' on Android/iOS


os_platform = _os_platform()
""" operating system / platform string (see :func:`_os_platform`).

this string value gets determined for most of the operating systems with the help of Python's :func:`sys.platform`
function and additionally detects the operating systems iOS and Android (not supported by Python).
"""


def os_user_name() -> str:
    """ determine the operating system username.

    :return:                    username string.
    """
    return getpass.getuser()


def parse_dotenv(file_path: str) -> Dict[str, str]:
    """ parse ``.env`` file content and return environment variable names as dict keys and values as dict values.

    :param file_path:           string with the name/path of an existing ``.env``/:data:`DOTENV_FILE_NAME` file.
    :return:                    dict with environment variable names and values
    """
    env_vars: Dict[str, str] = {}
    for line in cast(str, read_file(file_path)).splitlines():
        match = _env_line.search(line)
        if not match:
            if not re.search(r'^\s*(?:#.*)?$', line):  # not comment or blank
                warnings.warn(f"'{line!r}' in '{file_path}' doesn't match {DOTENV_FILE_NAME} format", SyntaxWarning)
            continue

        var_nam, var_val = match.groups()
        var_val = "" if var_val is None else var_val.strip()

        # remove surrounding quotes, unescape all chars except $ so variables can be escaped properly
        match = re.match(r'^([\'"])(.*)\1$', var_val)
        if match:
            delimiter, var_val = match.groups()
            if delimiter == '"':
                var_val = re.sub(r'\\([^$])', r'\1', var_val)
        else:
            delimiter = None
        if delimiter != "'":
            for parts in _env_variable.findall(var_val):
                if parts[0] == '\\':
                    replace = "".join(parts[1:-1])          # don't replace escaped variables
                else:
                    # substitute variables in a value, replace it with the value from the environment
                    replace = env_vars.get(parts[-1], os.environ.get(parts[-1], ""))
                var_val = var_val.replace("".join(parts[0:-1]), replace)

        env_vars[var_nam] = var_val

    return env_vars


def project_main_file(import_name: str, project_path: str = "") -> str:
    """ determine the main module file path of a project package, containing the project __version__ module variable.

    :param import_name:         import name of the module/package (including namespace prefixes for namespace packages).
    :param project_path:        optional path where the project of the package/module is situated. not needed if the
                                current working directory is the root folder of either the import_name project or of a
                                sister project (under the same project parent folder).
    :return:                    absolute file path/name of main module or empty string if no main/version file found.
    """
    join = os.path.join
    *namespace_dirs, portion_name = import_name.split('.')
    project_name = ('_'.join(namespace_dirs) + '_' if namespace_dirs else "") + portion_name
    paths_parts = main_file_paths_parts(portion_name)

    project_path = norm_path(project_path)
    module_paths = []
    if os.path.basename(project_path) != project_name:
        module_paths.append(join(os.path.dirname(project_path), project_name, *namespace_dirs))
    if namespace_dirs:
        module_paths.append(join(project_path, *namespace_dirs))
    module_paths.append(project_path)

    for module_path in module_paths:
        for path_parts in paths_parts:
            main_file = join(module_path, *path_parts)
            if os.path.isfile(main_file):
                return main_file
    return ""


def read_file(file_path: str, extra_mode: str = "", encoding: Optional[str] = None, error_handling: str = 'ignore'
              ) -> Union[str, bytes]:
    """ returning content of the text/binary file specified by file_path argument as string.

    :param file_path:           file path/name to load into a string or a bytes array.
    :param extra_mode:          extra open mode flag characters appended to "r" onto open() mode argument. pass "b" to
                                read the content of a binary file returned as bytes array. in binary mode the argument
                                passed in :paramref:`~read_file.error_handling` will be ignored.
    :param encoding:            encoding used to load and convert/interpret the file content.
    :param error_handling:      for files opened in text mode pass `'strict'` or `None` to return `None` (instead of an
                                empty string) for the cases where either a decoding `ValueError` exception or any
                                `OSError`, `FileNotFoundError` or `PermissionError` exception got raised.
                                the default value `'ignore'` will ignore any decoding errors (missing some characters)
                                and will return an empty string on any file/os exception. this parameter will be ignored
                                if the :paramref:`~read_file.extra_mode` argument contains the 'b' character (to read
                                the file content as binary/bytes-array).
    :return:                    file content string or bytes array.
    :raises FileNotFoundError:  if file does not exist.
    :raises OSError:            if :paramref:`~read_file.file_path` is misspelled or contains invalid characters.
    :raises PermissionError:    if current OS user account lacks permissions to read the file content.
    :raises ValueError:         on decoding errors.
    """
    extra_kwargs = {} if "b" in extra_mode else {'errors': error_handling}
    with open(file_path, "r" + extra_mode, encoding=encoding, **extra_kwargs) as file_handle:           # type: ignore
        return file_handle.read()


def round_traditional(num_value: float, num_digits: int = 0) -> float:
    """ round numeric value traditional.

    needed because python round() is working differently, e.g. round(0.075, 2) == 0.07 instead of 0.08
    inspired by https://stackoverflow.com/questions/31818050/python-2-7-round-number-to-nearest-integer.

    :param num_value:           float value to be round.
    :param num_digits:          number of digits to be round (def=0 - rounds to an integer value).

    :return:                    rounded value.
    """
    return round(num_value + 10 ** (-len(str(num_value)) - 1), num_digits)


def snake_to_camel(name: str, back_convertible: bool = False) -> str:
    """ convert name from snake_case to CamelCase.

    :param name:                name string composed of parts separated by an underscore character
                                (:data:`NAME_PARTS_SEP`).
    :param back_convertible:    pass `True` to get the first character of the returned name in lower-case
                                if the snake name has no leading underscore character (and to allow
                                the conversion between snake and camel case without information loss).
    :return:                    name in camel case.
    """
    ret = "".join(part.capitalize() for part in name.split(NAME_PARTS_SEP))
    if back_convertible and name[0] != NAME_PARTS_SEP:
        ret = ret[0].lower() + ret[1:]
    return ret


def stack_frames(depth: int = 1) -> Generator:  # Generator[frame, None, None]
    """ generator returning the call stack frame from the level given in :paramref:`~stack_frames.depth`.

    :param depth:               the stack level to start; the first returned frame by this generator. the default value
                                (1) refers the next deeper stack frame, respectively the one of the caller of this
                                function. pass 2 or a higher value if you want to start with an even deeper frame/level.
    :return:                    generated frames of the call stack.
    """
    try:
        while True:
            depth += 1
            # noinspection PyProtectedMember,PyUnresolvedReferences
            yield sys._getframe(depth)          # pylint: disable=protected-access
    except (TypeError, AttributeError, ValueError):
        pass


def stack_var(name: str, *skip_modules: str, scope: str = '', depth: int = 1) -> Optional[Any]:
    """ determine variable value in calling stack/frames.

    :param name:                variable name to search in the calling stack frames.
    :param skip_modules:        module names to skip (def=see :data:`SKIPPED_MODULES` module constant).
    :param scope:               pass 'locals' to only check for local variables (ignoring globals) or
                                'globals' to only check for global variables (ignoring locals). the default value (an
                                empty string) will not restrict the scope, returning either a local or global value.
    :param depth:               the calling level from which on to search. the default value (1) refers the next
                                deeper stack frame, which is the caller of the function. pass 2 or an even higher
                                value if you want to start the variable search from a deeper level in the call stack.
    :return:                    the variable value of a deeper level within the call stack or UNSET if the variable was
                                not found.
    """
    glo, loc, _deep = stack_vars(*skip_modules, find_name=name, min_depth=depth + 1, scope=scope)
    variables = glo if name in glo and scope != 'locals' else loc
    return variables.get(name, UNSET)


def stack_vars(*skip_modules: str,
               find_name: str = '', min_depth: int = 1, max_depth: int = 0, scope: str = ''
               ) -> Tuple[Dict[str, Any], Dict[str, Any], int]:
    """ determine all global and local variables in a calling stack/frames.

    :param skip_modules:        module names to skip (def=see :data:`SKIPPED_MODULES` module constant).
    :param find_name:           if passed then the returned stack frame must contain a variable with the passed name.
    :param scope:               scope to search the variable name passed via :paramref:`~stack_vars.find_name`. pass
                                'locals' to only search for local variables (ignoring globals) or 'globals' to only
                                check for global variables (ignoring locals). passing an empty string will find the
                                variable within either locals and globals.
    :param min_depth:           the call stack level from which on to search. the default value (1) refers the next
                                deeper stack frame, respectively to the caller of this function. pass 2 or a higher
                                value if you want to get the variables from a deeper level in the call stack.
    :param max_depth:           the maximum depth in the call stack from which to return the variables. if the specified
                                argument is not zero and no :paramref:`~stack_vars.skip_modules` are specified then the
                                first deeper stack frame that is not within the default :data:`SKIPPED_MODULES` will be
                                returned. if this argument and :paramref:`~stack_var.find_name` get not passed then the
                                variables of the top stack frame will be returned.
    :return:                    tuple of the global and local variable dicts and the depth in the call stack.
    """
    if not skip_modules:
        skip_modules = SKIPPED_MODULES
    glo = loc = {}
    depth = min_depth + 1   # +1 for stack_frames()
    for frame in stack_frames(depth=depth):
        depth += 1
        glo, loc = frame.f_globals, frame.f_locals

        if glo.get('__name__') in skip_modules:
            continue
        if find_name and (find_name in glo and scope != 'locals' or find_name in loc and scope != 'globals'):
            break
        if max_depth and depth > max_depth:
            break
    # experienced strange overwrites of locals (e.g. self) when returning f_locals directly (adding .copy() fixed it)
    # check if f_locals is a dict (because enaml is using their DynamicScope object which is missing a copy method)
    if isinstance(loc, dict):
        loc = loc.copy()
    return glo.copy(), loc, depth - 1


def sys_env_dict() -> Dict[str, Any]:
    """ returns dict with python system run-time environment values.

    :return:                    python system run-time environment values like python_ver, argv, cwd, executable,
                                frozen and bundle_dir (if bundled with pyinstaller).

    .. hint:: see also https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
    """
    sed: Dict[str, Any] = {
        'python_ver': sys.version.replace('\n', ' '),
        'platform': os_platform,
        'argv': sys.argv,
        'executable': sys.executable,
        'cwd': os.getcwd(),
        'frozen': getattr(sys, 'frozen', False),
        'user_name': os_user_name(),
        'host_name': os_host_name(),
        'app_name_guess': app_name_guess(),
    }

    if sed['frozen']:
        sed['bundle_dir'] = getattr(sys, '_MEIPASS', '*#ERR#*')

    return sed


def sys_env_text(ind_ch: str = " ", ind_len: int = 12, key_ch: str = "=", key_len: int = 15,
                 extra_sys_env_dict: Optional[Dict[str, str]] = None) -> str:
    """ compile formatted text block with system environment info.

    :param ind_ch:              indent character (defaults to " ").
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
    """ converts Unicode string into ascii representation.

    useful for fuzzy string compare; inspired by MiniQuark's answer
    in: https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string

    :param unicode_str:         string to convert.
    :return:                    converted string (replaced accents, diacritics, ... into normal ascii characters).
    """
    nfkd_form = unicodedata.normalize('NFKD', unicode_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('ß', "ss").replace('€', "Euro")


def uri2filename(uri: str) -> str:
    """ convert a URI to be usable as name of a file or folder

    :param uri:                 URI to convert to a corresponding file name, that will be revertible back to this URI.
    :return:                    name of a file/folder representing the specified URI.

    in *nix only / and \0 are not allowed characters in file names.
    in MS Windows are not allowed: ASCII 0...31): / \\ : * ? ” < > | (). some blogs recommend to also not allow
    (convert) the characters # and '.
    only old POSIX seems to be even more restricted (only allowing alphanumeric characters plus . - and _).

    file name length is not restricted/shortened by this function, although the maximum is 255 characters on most OSs.

    more on allowed characters in file names in the answers of RedGrittyBrick on https://superuser.com/questions/358855
    and of Christopher Oezbek on https://stackoverflow.com/questions/1976007.
    """
    # using urllib.parse.quote(uri, safe="") instead would convert also any non-ascii (e.g. umlaut) characters into hex
    # added [] to str.join() argument because List comprehensions are faster than generator expressions
    return "".join([f"%{hex(ord(_))[2:].upper()}" if _ in '/|\\:*?"<>%' else _ for _ in uri])


def filename2uri(file_name: str) -> str:
    """ convert a file name converted by :func:`uri2filename` back to its representation as a URI

    :param file_name:           name of the file/folder to convert back to its URI representation.
    :return:                    URI string.
    """
    return urllib.parse.unquote(file_name)


def write_file(file_path: str, content: Union[str, bytes], extra_mode: str = "", encoding: Optional[str] = None):
    """ (over)write the file specified by :paramref:`~write_file.file_path` with text or binary/bytes content.

    :param file_path:           file path/name to write the passed content into (overwriting any previous content!).
    :param content:             new file content either passed as string or list of line strings (will be
                                concatenated with the line separator of the current OS: os.linesep).
    :param extra_mode:          open mode flag characters. passed unchanged to the `mode` argument of :func:`open` if
                                this argument starts with 'a', else this argument value will be appended to 'w'.
    :param encoding:            encoding used to write/convert/interpret the file content to write.
    :raises FileExistsError:    if file exists already and is write-protected.
    :raises FileNotFoundError:  if parts of the file path do not exist.
    :raises OSError:            if :paramref:`~read_file.file_path` is misspelled or contains invalid characters.
    :raises PermissionError:    if current OS user account lacks permissions to read the file content.
    :raises ValueError:         on decoding errors.

    to extend this function for Android 14+ see https://github.com/beeware/toga/pull/1158#issuecomment-2254564657
    and https://gist.github.com/neonankiti/05922cf0a44108a2e2732671ed9ef386
    Yes, to use ACTION_CREATE_DOCUMENT, you don't supply a URI in the intent. You wait for the intent result, and that
    will contain a URI which you can write to.
    See #1158 (comment - https://github.com/beeware/toga/pull/1158#issuecomment-2254564657) for a link to a Java
    example, and #1158 (comment - https://github.com/beeware/toga/pull/1158#issuecomment-1446196973) for how to wait
    for an intent result.
    Related german docs: https://developer.android.com/training/data-storage/shared/media?hl=de
    """
    with open(file_path, ('' if extra_mode.startswith('a') else 'w') + extra_mode, encoding=encoding) as file_handle:
        file_handle.write(content)


class ErrorMsgMixin:
    """ mixin class providing error message """
    _err_msg: str = ""

    @property
    def error_message(self) -> str:
        """ error message string if an error occurred or an empty string if not.

        :getter:                return the accumulated error message of the recently occurred error(s).
        :setter:                any assigned error message will be accumulated to recent error messages.
                                pass an empty string to reset the error message.
        """
        return self._err_msg

    @error_message.setter
    def error_message(self, next_err_msg: str):
        if next_err_msg:
            self._err_msg += ("\n\n" if self._err_msg else "") + next_err_msg
        else:
            self._err_msg = ""


PACKAGE_NAME = stack_var('__name__') or 'unspecified_package'
PACKAGE_DOMAIN = 'org.test'
PERMISSIONS = "INTERNET, VIBRATE, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE"
if os.path.exists(BUILD_CONFIG_FILE):                           # pragma: no cover
    PACKAGE_NAME, PACKAGE_DOMAIN, PERMISSIONS = build_config_variable_values(
        ('package.name', PACKAGE_NAME),
        ('package.domain', PACKAGE_DOMAIN),
        ('android.permissions', PERMISSIONS))
elif os_platform == 'android':                                  # pragma: no cover
    _importing_package = norm_path(stack_var('__file__') or 'empty_package' + PY_EXT)
    if os.path.basename(_importing_package) in (PY_INIT, PY_MAIN):
        _importing_package = os.path.dirname(_importing_package)
    _importing_package = os.path.splitext(os.path.basename(_importing_package))[0]
    write_file(f'{_importing_package}_debug.log', f"{BUILD_CONFIG_FILE} not bundled - using defaults\n", extra_mode='a')


if os_platform == 'android':                                    # pragma: no cover
    # monkey patch the :func:`shutil.copystat` and :func:`shutil.copymode` helper functions, which are crashing on
    # 'android' (see # https://bugs.python.org/issue28141 and https://bugs.python.org/issue32073). these functions are
    # used by shutil.copy2/copy/copytree/move to copy OS-specific file attributes.
    # although shutil.copytree() and shutil.move() are copying/moving the files correctly when the copy_function
    # arg is set to :func:`shutil.copyfile`, they will finally also crash afterward when they try to set the attributes
    # on the destination root directory.
    shutil.copymode = dummy_function
    shutil.copystat = dummy_function

    # import permissions module from python-for-android (recipes/android/src/android/permissions.py)
    # noinspection PyUnresolvedReferences
    from android.permissions import request_permissions, Permission     # type: ignore # pylint: disable=import-error
    from jnius import autoclass                                         # type: ignore

    def request_app_permissions(callback: Optional[Callable[[List[Permission], List[bool]], None]] = None):
        """ request app/service permissions on Android OS.

        :param callback:        optional callback receiving two list arguments with identical length,
                                the 1st with the requested permissions and
                                the 2nd with booleans stating if the permission got granted (True) or rejected (False).
        """
        permissions = []
        for permission_str in PERMISSIONS.split(','):
            permission = getattr(Permission, permission_str.strip(), None)
            if permission:
                permissions.append(permission)
        request_permissions(permissions, callback=callback)

    def start_app_service(service_arg: str = "") -> Any:
        """ start service.

        :param service_arg:     string value to be assigned to environment variable PYTHON_SERVICE_ARGUMENT on start.
        :return:                service instance.

        see https://github.com/tshirtman/kivy_service_osc/blob/master/src/main.py
        and https://python-for-android.readthedocs.io/en/latest/services/#arbitrary-scripts-services
        """
        service_instance = autoclass(f"{PACKAGE_DOMAIN}.{PACKAGE_NAME}.Service{PACKAGE_NAME.capitalize()}")
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        service_instance.start(activity, service_arg)        # service_arg will be in env var PYTHON_SERVICE_ARGUMENT

        return service_instance

else:
    request_app_permissions = dummy_function
    start_app_service = dummy_function
