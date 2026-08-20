"""
basic constants, helper functions, classes and context managers
===============================================================

this module is pure python, has no external dependencies, and provides a comprehensive toolkit of base constants,
common helper functions, useful classes, and context managers for a wide variety of programming tasks.


string manipulation
-------------------

functions for converting, cleaning, normalizing, and formatting strings.

* :func:`ascii_dec_str`: decodes an ascii string literal converted by :func:`ascii_enc_lit` back to its Unicode form.
* :func:`ascii_enc_lit`: encodes a Unicode string into a reversible 7-bit ASCII representation, useful for transport
  protocol/HTTP headers.
* :func:`camel_to_snake`: converts a string from CamelCase to snake_case.
* :func:`snake_to_camel`: converts a string from snake_case to CamelCase.
* :func:`norm_name`: normalizes a string to be a valid identifier (e.g., for variable-, method-, or file-names).
* :func:`norm_line_sep`: converts all line separator combinations (CRLF, CR) in a string to a single newline (LF).
* :func:`defuse`: converts special characters in string to Unicode alternatives, making it safe for use as
  a URL slug, path or filename.
* :func:`dedefuse`: reverses the operation of :func:`defuse`, restoring the original string.
* :func:`force_encoding`: ensures text is in a specific encoding without raising errors, replacing characters as needed.
* :func:`to_ascii`: converts a Unicode string into its closest ASCII representation by removing accents and diacritics.
* :func:`format_given`: a replacement for `str.format_map` that formats a string but leaves placeholders intact if they
  are not found in the provided mapping.


data structure utilities
------------------------

helpers for working with lists, dictionaries, and other data structures.

* :func:`evaluate_literal`: replacement for :func:`ast.literal_eval` that also interprets/recognizes unquoted strings
  as `str` type.
* :func:`duplicates`: returns a list of all duplicate items found in any type of iterable.
* :func:`deep_dict_update`: recursively updates a dictionary in-place with values from another dictionary.
* :func:`mask_secrets`: hides sensitive string values (e.g., passwords, API keys) in deeply nested data structures,
  useful for logging.


file, path & I/O operations
---------------------------

simplify file system interactions with wrappers and context managers.

* :func:`extend_file`: append string to a file or create it if file not exists.
* :func:`in_wd`: a context manager to temporarily switch/change the current working directory.
* :func:`norm_path`: normalizes a path by expanding user home directories (`~`), resolving `.`, `..`, symbolic links,
  and converting between absolute and relative paths.
* :func:`read_bin_file`: reads the entire content of a binary file into a bytes object.
* :func:`read_file`: reads the entire content of a text file into a string.
* :func:`write_bin_file`: writes a bytes object to a file, overwriting existing content.
* :func:`write_file`: writes a string into a file, overwriting existing content.


networking utilities
--------------------

* :func:`mask_url`: hides or replaces the password/token portion of a URL for safe logging.
* :func:`url_failure`: determines if and why an HTTP|FTP target is unavailable.


general utilities & helpers
---------------------------

a collection of miscellaneous mathematical, date/time, and other standalone helper functions.

mathematical
^^^^^^^^^^^^

* :func:`sign`: returns the sign of a number (-1 for negative, 0 for zero, 1 for positive).
* :func:`round_traditional`: rounds a float value using traditional rounding rules (e.g., `0.5` rounds up).

date & time
^^^^^^^^^^^
* :func:`parse_date`: parse an ISO date literal string, returning the represented date/datetime.
* :func:`now_str`: creates a compact, sortable timestamp string from the current UTC time.
* :func:`utc_datetime`: Returns the current date and time as a timezone-naive `datetime` object in UTC.

miscellaneous
^^^^^^^^^^^^^
* :func:`dummy_function`: a null function that accepts any arguments and returns `None`.
* :func:`env_str`: retrieves the string value of an OS environment variable, with an option to automatically convert the
  variable name to the conventional format.
* :func:`on_ci_host`: detects if it is running on the CI of a Git repository server (GitHub or GitLab).


base types and classes
----------------------

* :class:`UnsetType`: the class for the :data:`UNSET` singleton object, useful as a sentinel value when `None` is a
  valid input.
* :class:`UnformattedValue`: a helper class for :func:`format_given` to represent a placeholder that was not found in
  the formatting map.
* :class:`GivenFormatter`: a helper class for :func:`format_given` that overrides default formatting behavior to keep
  missing placeholders.


base constants
--------------

predefined constants for defaults, project structure, file conventions, to decrease redundancy and increase performance.

project & file structure
^^^^^^^^^^^^^^^^^^^^^^^^

* :data:`CFG_EXT`: file extension for CFG/INI configuration files ('.cfg').
* :data:`DEF_PROJECT_PARENT_FOLDER`: default directory name for grouping source code projects ('src').
* :data:`DOCS_FOLDER`: default name for a project's documentation folder ('docs').
* :data:`INI_EXT`: file extension for INI configuration files ('.ini').
* :data:`PACKAGE_INCLUDE_FILES_PREFIX`: prefix for files/folders to be included in setup package data (used by
  :mod:`ae.updater` and :mod:`aedev.project_manager`)
* :data:`PY_CACHE_FOLDER`: default name for Python's cache folder (``__pycache__``).
* :data:`PY_EXT`: file extension for Python modules ('.py').
* :data:`PY_INIT`: the filename for a Python package initializer (``__init__.py``).
* :data:`PY_MAIN`: the filename for a Python executable's main module (``__main__.py``).
* :data:`TESTS_FOLDER`: default name for a project's tests folder ('tests').
* :data:`TEMPLATES_FOLDER`: default name for a folder containing file templates ('templates').


formats & default settings
^^^^^^^^^^^^^^^^^^^^^^^^^^

* :data:`DATE_ISO`: ISO format string for dates ("%Y-%m-%d").
* :data:`DATE_TIME_ISO`: ISO format string for :mod:`datetime.datetime` dates ("%Y-%m-%d %H:%M:%S.%f").
* :data:`DEF_ENCODE_ERRORS`: the default error handling strategy for encoding ('backslashreplace').
* :data:`DEF_ENCODING`: the default encoding used for string operations ('ascii').
* :data:`NAME_PARTS_SEP`: the character used as a separator in name conversions ('_').
* :data:`NOW_STR_FORMAT`: the datetime format string, used e.g. by :func:`now_str` for creating timestamps.
* :data:`UNSET`: a singleton instance of :class:`UnsetType`, used where `None` is a valid data value.


os.path shortcuts
^^^^^^^^^^^^^^^^^

the following are direct references to functions in the :mod:`os.path` module for convenient and quicker access:

* :data:`os_path_abspath`: :func:`os.path.abspath`
* :data:`os_path_basename`: :func:`os.path.basename`
* :data:`os_path_dirname`: :func:`os.path.dirname`
* :data:`os_path_expanduser`: :func:`os.path.expanduser`
* :data:`os_path_isdir`: :func:`os.path.isdir`
* :data:`os_path_isfile`: :func:`os.path.isfile`
* :data:`os_path_join`: :func:`os.path.join`
* :data:`os_path_normpath`: :func:`os.path.normpath`
* :data:`os_path_realpath`: :func:`os.path.realpath`
* :data:`os_path_relpath`: :func:`os.path.relpath`
* :data:`os_path_sep`: :data:`os.path.sep`
* :data:`os_path_splitext`: :func:`os.path.splitext`

"""
import base64
import datetime
import os
import socket
import ssl
import string
import unicodedata

from ast import literal_eval
from collections.abc import Generator, Iterable
from contextlib import contextmanager
from functools import partial
from typing import Any, Final
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen


__version__ = '0.3.93'


DOCS_FOLDER = 'docs'                            #: project documentation root folder name
TESTS_FOLDER = 'tests'                          #: name of project folder to store unit/integration tests
TEMPLATES_FOLDER = 'templates'
""" template folder name, used in template and namespace root projects to maintain and provide common file templates """

PACKAGE_INCLUDE_FILES_PREFIX = 'ae_'            #: file/folder names prefix included in setup package_data/ae_updater

PY_CACHE_FOLDER = '__pycache__'                 #: python cache folder name
PY_EXT = '.py'                                  #: file extension for modules and hooks
PY_INIT = '__init__' + PY_EXT                   #: init-module file name of a python package
PY_MAIN = '__main__' + PY_EXT                   #: main-module file name of a python executable

CFG_EXT = '.cfg'                                #: CFG config file extension
INI_EXT = '.ini'                                #: INI config file extension

DATE_ISO = "%Y-%m-%d"                           #: ISO string format for date values (e.g. in config files/variables)
DATE_TIME_ISO = "%Y-%m-%d %H:%M:%S.%f"          #: ISO string format for datetime values

DEF_PROJECT_PARENT_FOLDER = 'src'               #: default directory name to put code project roots underneath of it

DEF_ENCODE_ERRORS = 'backslashreplace'          #: default encode error handling for UnicodeEncodeErrors
DEF_ENCODING = 'ascii'
""" encoding for :func:`force_encoding` that will always work independent from destination (console, file sys, ...).
"""

NAME_PARTS_SEP = '_'                                #: name parts separator character, e.g. for :func:`norm_name`

NOW_STR_FORMAT = "{sep}%Y%m%d{sep}%H%M%S{sep}%f"    #: timestamp format of :func:`now_str`


def ascii_dec_str(encoded_str: str) -> str:
    """ convert non-ASCII chars in a string literal encoded with :func:`ascii_enc_lit` to Unicode chars.

    :param encoded_str:         string literal to decode (covert contained ASCII-encoded characters back Unicode chars).
    :return:                    decoded Unicode string.
    :raises:                    SyntaxError if invalid string literal got specified in
                                :paramref:`~ascii_dec_str.encoded_str`.
    """
    return literal_eval(encoded_str).decode()


def ascii_enc_lit(unicode_str: str) -> str:
    """ convert a Unicode string with non-ASCII chars to a revertible 7-bit/ASCII literal/representation.

    :param unicode_str:         string to encode/convert.
    :return:                    revertible representation of the specified string, using only ASCII characters,
                                e.g., to put in an http header.
    """
    return repr(unicode_str.encode())


def camel_to_snake(name: str) -> str:
    """ convert a name from CamelCase to snake_case.

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


def deep_dict_update(data: dict, update: dict, overwrite: bool = True):
    """ update the optionally nested data dict in-place with the items and subitems from the update dict.

    :param data:                dict to be updated/extended. non-existing keys of dict-subitems will be added.
    :param update:              dict with the [sub-]items to update in the :paramref:`~deep_dict_update.data` dict.
    :param overwrite:           pass `False` to not overwrite an already existing value.

    .. hint:: see the module/portion :mod:`ae.deep` for more deep update helper functions.
    """
    for upd_key, upd_val in update.items():
        if isinstance(upd_val, dict):
            if upd_key not in data:
                data[upd_key] = {}
            deep_dict_update(data[upd_key], upd_val, overwrite=overwrite)
        elif overwrite or upd_key not in data:
            data[upd_key] = upd_val


# noinspection GrazieInspection
ASCII_UNICODE = (
    ('/', '⁄'),     # U+2044: Fraction Slash; '∕' U+2215: Division Slash; '⧸' U+29F8: Big Solidus;
                    # '╱' U+FF0F: Fullwidth Solidus; '╱' U+2571: Box Drawings Light Diagonal Upper Right to Lower Left
    ('|', '।'),     # U+0964: Devanagari Danda
    ('\\', '﹨'),    # U+FE68: SMALL REVERSE SOLIDUS; '⑊' U+244A OCR DOUBLE BACKSLASH; '⧵' U+29F5 REV. SOLIDUS OPERATOR
    (':', '﹕'),     # U+FE55: Small Colon
    ('*', '﹡'),     # U+FE61: Small Asterisk
    ('?', '﹖'),     # U+FE56: Small Question Mark
    ('"', '＂'),     # U+FF02: Fullwidth Quotation Mark
    ("'", '‘'),     # U+2018: Left Single; '’' U+2019: Right Single; '‛' U+201B: Single High-Reversed-9 Quotation Mark
    ('<', '⟨'),     # U+27E8: LEFT ANGLE BRACKET; '‹' U+2039: Single Left-Pointing Angle Quotation Mark
    ('>', '⟩'),     # U+27E9: RIGHT ANGLE BRACKET; '›' U+203A: Single Right-Pointing Angle Quotation Mark
    ('(', '⟮'),     # U+27EE: MATHEMATICAL LEFT FLATTENED PARENTHESIS
    (')', '⟯'),     # U+27EF: MATHEMATICAL RIGHT FLATTENED PARENTHESIS
    ('[', '⟦'),     # U+27E6: MATHEMATICAL LEFT WHITE SQUARE BRACKET
    (']', '⟧'),     # U+27E7: MATHEMATICAL RIGHT WHITE SQUARE BRACKET
    ('{', '﹛'),     # U+FE5B: Small Left Curly Bracket
    ('}', '﹜'),     # U+FE5C: Small Right Curly Bracket
    ('#', '﹟'),     # U+FE5F: Small Number Sign
    (';', '﹔'),     # U+FE54: Small Semicolon
    ('@', '﹫'),     # U+FE6B: Small Commercial At
    ('&', '﹠'),     # U+FE60: Small Ampersand
    ('=', '﹦'),     # U+FE66: Small Equals Sign
    ('+', '﹢'),     # U+FE62: Small Plus Sign
    ('$', '﹩'),     # U+FE69: Small Dollar Sign
    ('%', '﹪'),     # U+FE6A: Small Percent Sign
    ('^', '＾'),     # U+FF3E: Fullwidth Circumflex Accent
    (',', '﹐'),     # U+FE50: Small Comma
    (' ', '␣'),     # U+2423: Open Box; more see underneath and https://unicode-explorer.com/articles/space-characters:
                    # ' ' U+00A0: No-Break Space (NBSP); ' ' U+1680 Ogham Space Mark; ' ' U+2000 En Quad;
                    # ' ' U+2001 Em Quad; ' ' U+2002 En Space; ' ' U+2003 Em Space; ' ' U+2004 Three-Per-Em
                    # ' ' U+2005 Four-Per-Em; ' ' U+2006 Six-Per-Em; ' ' U+2007 Figure Space;
                    # ' ' U+2008 Punctuation Space; ' ' U+2009 Thin; ' ' U+200A Hair Space;
                    # ' ' U+202F: Narrow No-Break Space (NNBSP); ' ' U+205F Medium Mathematical Space;
                    # '␠' U+2420 symbol for space; '␣' U+2423 Open Box; '　' U+3000: Ideographic Space
    (chr(127), '␡'),  # U+2421: DELETE SYMBOL
    # ('_', '𛲖'),     # U+1BC96: Duployan Affix Low Line; '＿' U+FF3F Fullwidth Low Line
) + tuple((chr(low_asc_ord), chr(0x2400 + low_asc_ord)) for low_asc_ord in range(32))
""" transformation table of special ASCII characters to a similar/alternative non-functional/-escaping Unicode char,
see https://www.compart.com/en/unicode/category/Po and https://xahlee.info/comp/unicode_naming_slash.html (http!) """

URI_SEP_STR = '://'             #: separator between service and address(host/path) in URIs
URI_SEP_UNICODE_CHAR = '⫻'      #: single Unicode char for :data:`URI_SEP_STR`  U+2AFB: TRIPLE SOLIDUS BINARY RELATION

ASCII_TO_UNICODE = str.maketrans(dict(ASCII_UNICODE))
""" :func:`str.translate` map to convert ASCII to an alternative defused Unicode character - used by :func:`defuse` """
UNICODE_TO_ASCII = str.maketrans({unicode_char: ascii_char for ascii_char, unicode_char in
                                  ASCII_UNICODE + ((URI_SEP_STR, URI_SEP_UNICODE_CHAR), )})
""" :func:`str.translate` Unicode to ASCII map - used by :func:`dedefuse` """


def dedefuse(value: str) -> str:
    """ convert a string that got defused with :func:`defuse` back to its original form.

    :param value:               string defused with the function :func:`defuse`.
    :return:                    re-activated form of the string (with all ASCII special characters recovered).
    """
    return value.translate(UNICODE_TO_ASCII)


def defuse(value: str) -> str:
    # noinspection GrazieInspection
    """ convert a file path or a URI into a defused/presentational form to be usable as URL slug or file/folder name.

    :param value:               any string to defuse (replace special chars with Unicode alternatives).
    :return:                    string with its special characters replaced by its pure presentational alternatives.

    the ASCII character range 0..31 gets converted to the Unicode range U+2400 + ord(char): 0==U+2400 ... 31==U+241F.

    in most unix variants only the slash and the ASCII 0 characters are not allowed in file names.

    in MS Windows are not allowed: ASCII 0..31 / | \\ : * ? ” % < > ( ). some blogs recommend also not allowing
    (convert) the characters `#` and `'`.

    only old POSIX seems to be even more restricted (only allowing alphanumeric characters plus . - and _).

    more on allowed characters in file names in the answers of RedGrittyBrick on https://superuser.com/questions/358855
    and of Christopher Oezbek on https://stackoverflow.com/questions/1976007.

    file name length is not restricted/shortened by this function, although the maximum is 255 characters on most OSs.

    .. hint:: use the :func:`dedefuse` function to convert the defused string back to the corresponding URI/file-path.

    """
    return value.replace(URI_SEP_STR, URI_SEP_UNICODE_CHAR).translate(ASCII_TO_UNICODE)  # replace makes URIs shorter


def dummy_function(*_args, **_kwargs):
    """ null function accepting any arguments and returning `None`.

    :param _args:               ignored positional arguments.
    :param _kwargs:             ignored keyword arguments.
    :return:                    always `None`.
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


def env_str(name: str, convert_name: bool = False) -> str | None:
    """ determine the string value of an OS environment variable, optionally preventing invalid variable name.

    :param name:                name of an OS environment variable.
    :param convert_name:        pass `True` to prevent invalid variable names by converting
                                CamelCase names into SNAKE_CASE, lower-case into
                                upper-case and all non-alpha-numeric characters into underscore characters.
    :return:                    string value of OS environment variable if found, else `None`.
    """
    if convert_name:
        name = norm_name(camel_to_snake(name)).upper()
    return os.environ.get(name)


def evaluate_literal(literal_string: str) -> bool | bytes | dict | complex | float | int | list | set | str | tuple:
    """ evaluates a Python expression while accepting unquoted strings as str type.

    :param literal_string:      any literal of the base types (like dict, list, set, tuple) which are recognized
                                by :func:`ast.literal_eval`.
    :return:                    an instance of the data type or the specified string, even if it is not quoted with high
                                comma characters. `None` will be returned if the specified literal is the string "None".
    """
    try:
        return literal_eval(literal_string)
    except (IndentationError, SyntaxError, TypeError, ValueError):
        return literal_string


def extend_file(file_path: str, content: str, encoding: str | None = None, make_dirs: bool = False):
    """ create/extend the text file specified by :paramref:`~extend_file.file_path` with the specified content string.

    :param file_path:           file path/name to write the passed content into (overwriting any previous content!).
    :param content:             new file content passed either as string or as `bytes`. if a byte array gets passed,
                                then this method will automatically write the content as binary.
    :param encoding:            encoding used to convert/interpret the string content to write.
    :param make_dirs:           pass `True` to create not existing parent folders of the specified file path.
    :raises IsADirectoryError:  file_path points to a directory instead of a file.
    :raises LookupError:        unknown encoding name.
    :raises NotADirectoryError: part of the path expected to be a directory is actually a file.
    :raises OSError:            disk full, filename too long, too many open files, network or device disconnected,
                                file_path is misspelled or contains invalid characters.
    :raises PermissionError:    if the current OS user account lacks permissions to write the file content.
    :raises TypeError:          content is not of type `str`.
    :raises UnicodeEncodeError: content cannot be encoded using the selected encoding.
    :raises ValueError:         other encoding errors, invalid mode or incompatible arguments.
    """
    if make_dirs and (dir_path := os_path_dirname(file_path)):
        os.makedirs(dir_path, exist_ok=True)

    with open(file_path, mode='a', encoding=encoding) as file_handle:
        file_handle.write(content)


def force_encoding(text: str | bytes, encoding: str = DEF_ENCODING, errors: str = DEF_ENCODE_ERRORS) -> str:
    """ force/ensure the encoding of text (str or bytes) without any UnicodeDecodeError/UnicodeEncodeError.

    :param text:                text as str/bytes.
    :param encoding:            encoding (def= :data:`DEF_ENCODING`).
    :param errors:              encode error handling (def= :data:`DEF_ENCODE_ERRORS`).

    :return:                    text as str (with all characters checked/converted/replaced to be encode-able).
    """
    enc_str: bytes = text.encode(encoding=encoding, errors=errors) if isinstance(text, str) else text
    return enc_str.decode(encoding=encoding)


class UnformattedValue:                     # pylint: disable=too-few-public-methods
    """ helper class for :func:`~ae.base.format_given` to keep placeholder with format unchanged if not found. """
    def __init__(self, key: int | str):
        self.key = key

    def __format__(self, format_spec: str):
        """ overriding Python object class method to return placeholder unchanged, including the curly brackets. """
        # pylint: disable=consider-using-f-string
        return "{{{}{}}}".format(self.key, ":" + format_spec if format_spec else "")


class GivenFormatter(string.Formatter):
    """ helper class for :func:`~ae.base.format_given` to keep placeholder with format unchanged if not found. """
    def get_value(self, key, args, kwargs):
        """ overriding to keep placeholder unchanged if not found """
        try:
            return super().get_value(key, args, kwargs)
        except KeyError:
            return UnformattedValue(key)


def format_given(text: str, placeholder_map: dict[str, Any], strict: bool = False):
    """ replacement for Python's str.format_map(), keeping intact placeholders that are not in the specified mapping.

    :param text:                text/template in which the given/specified placeholders will get replaced. in contrary
                                to :func:`str.format_map`, no KeyError will be raised for placeholders not specified in
                                :paramref:`~format_given.placeholder_map`.
    :param placeholder_map:     dict with placeholder keys to be replaced in :paramref:`~format_given.text` argument.
    :param strict:              pass `True` to raise an error for text templates containing unpaired curly brackets.
    :return:                    the specified :paramref:`~format_given.text` with only the placeholders specified in
                                :paramref:`~format_given.placeholder_map` replaced with their respective map value.

    inspired by the answer of CodeManX in <https://stackoverflow.com/questions/3536303>.
    """
    formatter = GivenFormatter()
    try:
        return formatter.vformat(text, (), placeholder_map)
    except (ValueError, Exception) as ex:                           # pylint: disable=broad-except
        if strict:
            raise ex
        return text


@contextmanager
def in_wd(new_cwd: str) -> Generator[None, None, None]:
    """ context manager to temporarily switch the current working directory / cwd.

    :param new_cwd:             path to the directory to switch to (within the context/with block).
                                an empty string gets interpreted as the current working directory.

    the following example demonstrates a typical usage, together with a temporary path, created with the help of Pythons
    :class:`~tempfile.TemporaryDirectory` class::

        with tempfile.TemporaryDirectory() as tmp_dir, in_wd(tmp_dir):
            # within the context the tmp_dir is set as the current working directory
            assert os.getcwd() == tmp_dir
        # here the current working directory got set back to the original path and the temporary directory got removed

    """
    cur_dir = os.getcwd()
    try:
        if new_cwd:         # empty new_cwd results in the current working folder (no dir change needed/prevent error)
            os.chdir(new_cwd)
        yield
    finally:
        os.chdir(cur_dir)


def mask_secrets(data: dict | Iterable, fragments: Iterable[str] = ('password', 'pwd')) -> dict | Iterable:
    """ partially-hide secret string values like passwords/credit-card-numbers in deeply nestable data structures.

    :param data:                iterable deep data structure wherein its item values get masked if their related dict
                                item key contains one of the fragments specified in :paramref:`~mask_secrets.fragments`.
    :param fragments:           dict key string fragments of which the related value will be masked. each fragment has
                                to be specified with lower case chars! defaults to ('password', 'pwd') if not passed.
    :return:                    specified data structure with the secrets masked (¡in-place!).
    """
    is_dict = isinstance(data, dict)

    for idx, val in tuple(data.items()) if is_dict else enumerate(data):    # type: ignore # silly mypy not sees is_dict
        val_is_str = isinstance(val, str)
        if not val_is_str and isinstance(val, Iterable):
            mask_secrets(val, fragments=fragments)
        elif is_dict and val_is_str and isinstance(idx, str):
            idx_lower = idx.lower()
            if any(_frag in idx_lower for _frag in fragments):
                data[idx] = val[:3] + "*" * 9                               # type: ignore # silly mypy not sees is_dict

    return data


def mask_url(url: str, replacement: str = "¿¿¿") -> str:
    """ hide|replace the password/token in a URL.

    :param url:                 URL in which an optional password|token will be searched and replaced.
    :param replacement:         optional replacement string, if not specified then the default value will be used.
    :return:                    URL with the credentials masked/replaced.
    """
    parts = urlparse(url)
    if parts.password is None:
        return url
    # manually split out the netloc, because using parts.hostname/,port would have to be checked for None&hostname.lower
    parts = parts._replace(netloc=f"{parts.username}:{replacement}@{parts.netloc.rpartition('@')[-1]}")
    # noinspection PyTypeChecker
    return urlunparse(parts)


def norm_line_sep(text: str) -> str:
    # noinspection GrazieInspection
    """ convert any combination of line separators in the :paramref:`~norm_line_sep.text` arg to new-line characters.

        :param text:                string containing any combination of line separators ('\\\\r\\\\n' or '\\\\r').
        :return:                    normalized/converted string with only new-line ('\\\\n') line separator characters.
        """
    return text.replace('\r\n', '\n').replace('\r', '\n')


def norm_name(name: str, allow_num_prefix: bool = False) -> str:
    """ normalize name to start with a letter/alphabetic/underscore and to contain only alphanumeric/underscore chars.

    :param name:                any string to be converted into a valid variable/method/file/... name.
    :param allow_num_prefix:    pass `True` to allow leading digits in the returned normalized name.
    :return:                    cleaned/normalized/converted name string (e.g., for a variable-/method-/file-name).
    """
    str_parts: list[str] = []
    for char in name:
        if char.isalpha() or char.isalnum() and (allow_num_prefix or str_parts):
            str_parts.append(char)
        else:
            str_parts.append('_')
    return "".join(str_parts)


def norm_path(path: str, make_absolute: bool = True, remove_base_path: str = "", remove_dots: bool = True,
              resolve_sym_links: bool = True) -> str:
    # noinspection GrazieInspection
    """ normalize a path, substituting special characters (like `..` `.` `\\` `~`) and transforming it to relative/abs.

    :param path:                path string to normalize/transform.
    :param make_absolute:       pass `False` to not convert the returned path to an absolute path.
    :param remove_base_path:    pass a valid base path to return a relative path, even if the argument values of
                                :paramref:`~norm_path.make_absolute` or :paramref:`~norm_path.resolve_sym_links` are
                                `True`.
    :param remove_dots:         pass `False` to not replace/remove the relative path placeholders `.` and `..`.
    :param resolve_sym_links:   pass `False` to not resolve symbolic links. passing `True` implies a `True` value
                                also for the :paramref:`~norm_path.make_absolute` argument.
    :return:                    normalized path string: absolute if :paramref:`~norm_path.remove_base_path` is empty and
                                either :paramref:`~norm_path.make_absolute` or :paramref:`~norm_path.resolve_sym_links`
                                is `True`; relative if :paramref:`~norm_path.remove_base_path` is a base path of
                                :paramref:`~norm_path.path` or if :paramref:`~norm_path.path` got specified as a
                                relative path and neither :paramref:`~norm_path.make_absolute` nor
                                :paramref:`~norm_path.resolve_sym_links` is `True`.
                                characters like `.` and `..` in relative paths will get replaced (to prevent this
                                specify `False` onto the :paramref:`~norm_path.remove_dots` argument).
                                if the specified path string starts with the special shortcut character `~`, it will get
                                substituted with the current users home directory (depending on the Operating System).
                                the MS Windows path seperator backslash character will always be converted into a slash.

        .. hint:: the :func:`~ae.paths.normalize` function additionally replaces :data:`~ae.paths.PATH_PLACEHOLDERS`.

        """
    path = path.replace("\\", "/") or "."
    if path[0] == "~":
        path = os_path_expanduser(path)

    if remove_dots:
        path = os_path_normpath(path)

    if resolve_sym_links:
        path = os_path_realpath(path)
    elif make_absolute:
        path = os_path_abspath(path)

    if remove_base_path:
        if remove_base_path[0] == "~":
            remove_base_path = os_path_expanduser(remove_base_path)
        path = os_path_relpath(path, remove_base_path)

    return path


def now_str(sep: str = "") -> str:
    """ return the current UTC timestamp as string (to use as suffix for file and variable/attribute names).

    :param sep:                 optional prefix and separator character (separating date from time and in time part
                                the seconds from the microseconds).
    :return:                    naive UTC timestamp (without timezone info) as string (length=20 + 3 * len(sep)).
    """
    return utc_datetime().strftime(NOW_STR_FORMAT.format(sep=sep))


def on_ci_host() -> bool:
    """ check and return `True` if it is running on the GitLab/GitHub CI host/server.

    :return:                    `True` if running on CI host, else `False`.

    .. note:: env vars always available: 'CI' on GitHub (Pre-pipeline); 'CI_PROJECT_ID' (internal ProjectId) on GitLab
    """
    return 'CI' in os.environ or 'CI_PROJECT_ID' in os.environ


os_path_abspath = os.path.abspath
os_path_basename = os.path.basename
os_path_dirname = os.path.dirname
os_path_expanduser = os.path.expanduser
os_path_isdir = os.path.isdir
os_path_isfile = os.path.isfile
os_path_join = os.path.join
os_path_normpath = os.path.normpath
os_path_realpath = os.path.realpath
os_path_relpath = os.path.relpath
os_path_sep = os.path.sep                       # pylint: disable=invalid-name
os_path_splitext = os.path.splitext


def parse_date(literal: str, ret_date: bool | None = False) -> datetime.date | datetime.datetime | None:
    """ parse an ISO date literal string, returning the represented date/datetime or `None` if date literal is invalid.

    this function extends Pythons standard function :meth:`~datetime.datetime.strptime`.
    it checks/corrects the passed date/time literals to support a wider range of ISO
    date/time formats as Pythons :func:`~datetime.datetime.strptime`.

    .. hint::
        Pythons :meth:`~datetime.datetime.strptime` to parse date and time strings into :class:`datetime.date`
        or :class:`datetime.datetime` objects is very strict and does not respect the formatting alternatives of
        ISO8601 (see https://bugs.python.org/issue15873 and https://github.com/boxed/iso8601).

    additionally a :class:`datetime.date` object can be created/returned automatically if no time info is specified
    in the date string/literal or if requested (via `False` as the :paramref:`~parse_date.ret_date` argument).

    :param literal:             date/time literal string in the format of :data:`DATE_ISO` or :data:`DATE_TIME_ISO`
                                (supporting also a "T" as separator between the date and the time literal, or
                                datetime literals without the seconds and/or the microseconds).
    :param ret_date:            request return value type: `True`=datetime.date, `False`=datetime.datetime (the default)
                                or `None`=determine type from literal (`datetime.datetime` if literal contains a time).
    :return:                    the date/datetime value of the specified literal, or `None` if the literal is invalid.
    """
    if not isinstance(literal, str):
        return None

    literal = literal.replace("T", " ")     # support "T" as alternative separator between date and time
    lit_dt_sep_pos = literal.find(" ")
    if ret_date and lit_dt_sep_pos != -1:
        literal = literal[:lit_dt_sep_pos]  # cut time part if exists caller requested return of short date
        lit_dt_sep = ""
        lit_time_sep_cnt = 0
    else:
        lit_dt_sep = literal[lit_dt_sep_pos] if lit_dt_sep_pos != -1 else ""
        lit_time_sep_cnt = literal.count(":")
        if not 0 <= lit_time_sep_cnt <= 2:
            return None

    for mask in (DATE_TIME_ISO, DATE_ISO):
        if mask == DATE_TIME_ISO:
            if not lit_dt_sep:
                continue
            if not literal.find(".") != -1 and (msk_ms_pos := mask.rfind(".")) != -1:
                mask = mask[:msk_ms_pos]    # no microseconds specified in literal, then remove ".%f" from mask
            if lit_time_sep_cnt == 1:
                mask = mask[:-3]            # no seconds specified in literal, then remove ":%S" from mask

        try:
            ret_val = datetime.datetime.strptime(literal, mask)
        except (TypeError, ValueError):
            continue

        return ret_val.date() if ret_date or ret_date is None and not lit_dt_sep else ret_val

    return None


def pep8_format(value: Any, indent_level: int = 0, debug_mode: bool = False, _printed: tuple = ()) -> str:
    """ representation code string of deep dict/list/set/tuple data structures, superseding :func:`pprint.pformat`.

    :param value:               value to format with hanging indent.
    :param indent_level:        level of indentation. pass e.g. 1 to indent the output with 4 spaces.
    :param debug_mode:          specify `True` to enable debug mode, adding key/index for list, set and tuple structures
                                to return; then no longer convertable back to its value with :func:`ast.literal_eval`.
    :param _printed:            used internally to prevent RecursionError, RuntimeError and ValueError for
                                cyclic/recursive data structures in the :paramref:`~pep8_format.value` argument.
    :return:                    value literal either in PEP-8-conform-representation or as a debug log/print string.
    """
    indent_spaces = ' ' * 4     # PEP-8: 4 spaces per indent
    level_spaces = indent_spaces * indent_level
    is_dict = isinstance(value, dict)
    show_key = debug_mode or is_dict

    beg_ch, end_ch, iter_func = (
        ('{', '}', value.items) if is_dict else
        ('[', ']', partial(enumerate, value)) if isinstance(value, list) else
        ('set(', ')', partial(enumerate, value)) if isinstance(value, set) else
        ('(', ')', partial(enumerate, value)) if isinstance(value, tuple) else
        ("", "", None))

    parts = []
    if value and iter_func:
        parts.append(beg_ch)
        for key, val in iter_func():
            key_str = repr(key) + ': ' if show_key else ""
            try:
                if value in _printed:                   # can also throw RecursionError
                    formatted = repr(value)
                else:
                    formatted = pep8_format(val, indent_level=indent_level + 1, debug_mode=debug_mode,
                                            _printed=_printed + (value, ))
            except (RecursionError, RuntimeError, ValueError):
                if not debug_mode:
                    return beg_ch + end_ch
                formatted = '......'

            parts.append(f"{level_spaces}{indent_spaces}{key_str}{formatted}" + ',')

        parts.append(level_spaces + end_ch)

    else:
        parts.append(repr(value))

    return os.linesep.join(parts)


def read_bin_file(file_path: str) -> bytes:
    """ returning the binary content of the specified by the :paramref:`~read_bin_file.file_path` argument.

    :param file_path:           path/name of the file to load the content from.
    :return:                    file content bytes array.
    :raises FileNotFoundError:  if the file to read from does not exist.
    :raises OSError:            if :paramref:`~read_bin_file.file_path` is misspelled or contains invalid characters.
    :raises PermissionError:    if the current OS user account lacks permissions to read the file content.
    """
    with open(file_path, "rb") as file_handle:
        return file_handle.read()


def read_file(file_path: str, encoding: str | None = None, error_handling: str | None = 'ignore') -> str:
    """ returning the string content of the text file specified by :paramref:`~read_file.file_path` argument.

    :param file_path:           path/name of the file to load the content from.
    :param encoding:            encoding used to load and convert/interpret the file content (passed onto the `encoding`
                                parameter of the built-in `open` function).
    :param error_handling:      pass `'strict'` or `None` to raise a `ValueError` exception on encoding errors.
                                the default value `'ignore'` will ignore any decoding errors (resulting in missing
                                characters in the return value). passed onto the `errors` parameter of the built-in
                                `open` function.
    :return:                    the content of the file as a string.
    :raises FileNotFoundError:  if the file to read from does not exist.
    :raises IsADirectoryError:  file_path points to a directory instead of a file.
    :raises LookupError:        unknown encoding name.
    :raises NotADirectoryError: part of the path expected to be a directory is actually a file.
    :raises OSError:            filename too long, too many open files, device/network error, file_path misspelled
                                or contains invalid characters.
    :raises PermissionError:    if the current OS user account lacks permissions to read the file content.
    :raises UnicodeDecodeError: file content cannot be decoded with the specified encoding or error_handling.
    :raises ValueError:         invalid error_handling argument.
    """
    with open(file_path, "r", encoding=encoding, errors=error_handling) as file_handle:
        return file_handle.read()


def round_traditional(num_value: float, num_digits: int = 0) -> float:
    """ round numeric value traditional.

    needed because python round() is working differently, e.g., round(0.075, 2) == 0.07 instead of 0.08
    inspired by https://stackoverflow.com/questions/31818050/python-2-7-round-number-to-nearest-integer.

    :param num_value:           float value to be round.
    :param num_digits:          number of digits to be round (def=0 - rounds to an integer value).

    :return:                    rounded value.
    """
    return round(num_value + 10 ** (-len(str(num_value)) - 1), num_digits)


def sign(number: float) -> int:
    """ return ths sign (-1, 0, 1) of a number.

    :param number:              any number of type float or int.
    :return:                    -1 if the number is negative, 0 if it is zero, or 1 if it is positive.
    """
    return (number > 0) - (number < 0)


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


def to_ascii(unicode_str: str) -> str:
    """ converts Unicode string into ascii representation.

    useful for fuzzy string compare; inspired by MiniQuark's answer
    in: https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string

    :param unicode_str:         string to convert.
    :return:                    converted string (replaced accents, diacritics, ... into normal ascii characters).
    """
    nfkd_form = unicodedata.normalize('NFKD', unicode_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('ß', "ss").replace('€', "Euro")


# pylint: disable-next=too-many-arguments,too-many-positional-arguments,too-many-return-statements
def url_failure(url: str, token: str = "", username: str = "", password: str = "",
                git_repo: bool = False, timeout: float | None = None) -> str:
    """ determine if and why an FTP or HTTP[S] target is not available via a GET request.

    :param url:                 URL of a target|page|file to check (not downloaded, fetching only the header).
    :param token:               optional bearer token to authenticate (only for HTTPS protocol).
    :param username:            optional username to authenticate (for HTTPS, together with the password argument).
    :param password:            optional password to authenticate (for HTTPS, together with the username argument).
    :param git_repo:            optimized check for Git repository HTTP servers/sites (like GitHub, GitLab, Bitbucket,
                                Gitea, SourceHut, Mercury, etc. as long as they implement Smart HTTP). if specified
                                then the :paramref:`~url_failure.url` has to point to a repository.
    :param timeout:             connection timeout in seconds (see :func:`urllib.request.urlopen`).
    :return:                    empty string if target header is available, else an error description. if an
                                FTP|HTTP response error occurred then the error/status code
                                will be returned in the first 3 characters.

    .. note::
        credentials for server authentication can be specified either (1) embedded into the specified url argument,
        (2) as bearer token in the token argument or (3) via the username/password arguments. in all cases the
        functino will remove these secrets from the returned error description string.
    """
    if git_repo:
        if not url.endswith(".git"):
            url += ".git"
        url += "/info/refs?service=git-upload-pack"

    headers = {}
    if token:
        assert not username and not password, "url_failure accepts either a token or username/password, not both"
        headers['Authorization'] = "Bearer " + token
    elif username or password:
        creds = f"{username}:{password}".encode('utf-8')
        headers['Authorization'] = "Basic " + base64.b64encode(creds).decode('utf-8')

    # noinspection PyBroadException
    try:
        request = Request(url, method='GET', headers=headers)
        with urlopen(request, timeout=timeout) as response:         # open connection and only read the header
            status = response.getcode()                             # no need to call response.read()
            return "" if 200 <= status < 300 else f"{status} {mask_url(url)} {response.reason=}"

    except HTTPError as exception:
        return f"{exception.code} {mask_url(url)} raised HTTPError {exception.reason=}"

    except URLError as exception:
        err_msg = f" {mask_url(url)} raised {exception.errno=} {exception.reason=};"
        if isinstance(exception.reason, socket.gaierror):
            return '995' + f"{err_msg} could not resolve hostname"
        if isinstance(exception.reason, ssl.SSLCertVerificationError):
            return '996' + f"{err_msg} SSL certificate verification failed"
        if isinstance(exception.reason, socket.timeout):
            return '997' + f"{err_msg} connection timed out after {timeout} seconds"
        return '998' + f"{err_msg} could not reach the server"

    except socket.timeout as _exception:    # noqa: F841 # str(_exception) could contain password|token
        return '997' + f" {mask_url(url)} raised socket-timeout exception after {timeout} seconds"

    except Exception as _exception:         # noqa: F841 # pylint: disable=broad-exception-caught
        return '999' + f" {mask_url(url)} raised unexpected exception"   # str(_exception) COULD contain password


def utc_datetime() -> datetime.datetime:
    """ return the current UTC timestamp as string (to use as suffix for file and variable/attribute names).

    :return:                    timestamp string of the actual UTC date and time.
    """
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def write_bin_file(file_path: str, content: bytes, make_dirs: bool = False):
    """ (over)write the file specified by :paramref:`~write_bin_file.file_path` with the specified binary/bytes content.

    :param file_path:           file path/name to write the passed content into (overwriting any previous content!).
    :param content:             new file content specified as `bytes`.
    :param make_dirs:           pass `True` to automatically create not existing folders of the file path.
    :raises FileExistsError:    if the file to write to exists already and is write-protected.
    :raises FileNotFoundError:  if parts of the file path do not exist.
    :raises IsADirectoryError:  file_path points to a directory instead of a file.
    :raises NotADirectoryError: part of the path expected to be a directory is actually a file.
    :raises OSError:            disk full, filename too long, too many open files, network or device disconnected,
                                file_path is misspelled or contains invalid characters.
    :raises PermissionError:    if the current OS user account lacks permissions to write the file content.
    :raises TypeError:          content is not of type `bytes`.
    """
    if make_dirs and (dir_path := os_path_dirname(file_path)):
        os.makedirs(dir_path, exist_ok=True)

    with open(file_path, mode='wb') as file_handle:
        file_handle.write(content)


def write_file(file_path: str, content: str, encoding: str | None = None, make_dirs: bool = False):
    """ (over)write the file specified by :paramref:`~write_file.file_path` with the specified string content.

    :param file_path:           file path/name to write the passed content into (overwriting any previous content!).
    :param content:             new file content passed as string.
    :param encoding:            encoding used to write/convert/interpret the file content to write (defaults to utf-8).
    :param make_dirs:           pass `True` to automatically create not existing folders of the file path (specified in
                                :paramref:`~write_file.file_path`).
    :raises FileExistsError:    if the file to write to exists already and is write-protected.
    :raises FileNotFoundError:  if parts of the file path do not exist.
    :raises IsADirectoryError:  file_path points to a directory instead of a file.
    :raises LookupError:        unknown encoding name.
    :raises NotADirectoryError: part of the path expected to be a directory is actually a file.
    :raises OSError:            disk full, filename too long, too many open files, network or device disconnected,
                                file_path is misspelled or contains invalid characters.
    :raises PermissionError:    if the current OS user account lacks permissions to write the file content.
    :raises TypeError:          content is not of type `str`.
    :raises UnicodeEncodeError: content cannot be encoded using the selected encoding.
    :raises ValueError:         other encoding errors, invalid mode or incompatible arguments.

    to extend this function for Android 14+, see <https://github.com/beeware/toga/pull/1158#issuecomment-2254564657>
    and <https://gist.github.com/neonankiti/05922cf0a44108a2e2732671ed9ef386>
    Yes, to use ACTION_CREATE_DOCUMENT, you don't supply a URI in the intent. You wait for the intent result, and that
    will contain a URI which you can write to.
    See #1158 (comment - <https://github.com/beeware/toga/pull/1158#issuecomment-2254564657>) for a link to a Java
    example, and #1158 (comment - <https://github.com/beeware/toga/pull/1158#issuecomment-1446196973>) for how to
    wait for an intent result.
    Related german docs: <https://developer.android.com/training/data-storage/shared/media?hl=de>.
    """
    if make_dirs and (dir_path := os_path_dirname(file_path)):
        os.makedirs(dir_path, exist_ok=True)

    with open(file_path, mode='w', encoding=encoding) as file_handle:
        file_handle.write(content)


class UnsetType:
    """ (singleton) UNSET (type) object class. """
    def __bool__(self):
        """ ensure to be evaluated as `False`, like `None`. """
        return False

    def __len__(self):
        """ ensure to be evaluated as empty. """
        return 0


UNSET: Final = UnsetType()     #: pseudo value used for attributes/arguments if `None` is needed as a valid value
