from typing import Union

from .types import *


class UnserializeTypeError(TypeError):
    pass


class UnserializeFormatError(SyntaxError):
    pass


def _handle_int(sg):
    s = '0'
    while s[-1] != ';' and s[-1] != ':':
        s += chr(next(sg))
    return int(s[1:-1])


def _handle_double(sg):
    s = '0'
    while s[-1] != ';' and s[-1] != ':':
        s += chr(next(sg))
    return float(s[1:-1])


def _handle_str(sg) -> bytes:
    # in php, strings are regarded as raw bytes
    # so a `bytes` object is returned here.
    cnt = int(_handle_int(sg))
    assert chr(next(sg)) == '"'
    s = bytes((next(sg) for _ in range(cnt)))
    assert chr(next(sg)) == '"'
    next(sg)  # ; or :
    return s


def _handle_array(sg):
    result = {}
    cnt = int(_handle_int(sg))
    assert chr(next(sg)) == '{'
    for _ in range(cnt):
        k = _handle(sg)
        v = _handle(sg)
        result[k] = v
    if all((isinstance(i, int) for i in result.keys())):
        result = [v for v in result.values()]
    assert chr(next(sg)) == '}'
    return result


def _get_attr_type(name: str):
    if not name.startswith('\0'):
        return 'public', name
    end = name[1:].find('\0') + 1
    sli, varname = name[1:end], name[end + 1:]
    if sli == '*':
        return 'protected', varname
    else:
        return 'private', (sli, varname)


def _handle_object(sg):
    class_name = _handle_str(sg).decode('utf-8')
    property_cnt = _handle_int(sg)
    assert chr(next(sg)) == '{'
    for cls in PHP_Class.__subclasses__():
        if cls.__name__ == class_name:
            # __init__ not called
            obj = PHP_Class.__new__(cls)
            break
    else:
        obj = __PHP_Incomplete_Class(class_name)
    for _ in range(property_cnt):
        assert chr(next(sg)) == 's' and chr(next(sg)) == ':'
        # property names must be string
        var_type, var_name = _get_attr_type(_handle_str(sg).decode('utf-8'))
        var_value = _handle(sg)
        if var_type == 'public':
            if hasattr(obj, f'{var_type}_{var_name}'):
                var_name = f'{var_type}_{var_name}'
        elif var_type == 'protected':
            var_name = f'{var_type}_{var_name}'
        elif var_type == 'private':
            var_name = f'{var_type}_{var_name[1]}'
        setattr(obj, var_name, var_value)
    assert chr(next(sg)) == '}'
    return obj


_handlers = {
    'b': lambda sg: [chr(next(sg)), next(sg)][0] == '1',
    'i': _handle_int,
    'd': _handle_double,
    'a': _handle_array,
    's': _handle_str,
    'O': _handle_object,
}


def _handle(sg):
    x = chr(next(sg))
    try:
        assert chr(next(sg)) == ':'
        if x not in _handlers:
            raise UnserializeTypeError('Invalid Type')
        return _handlers[x](sg)
    except AssertionError:
        if x == 'N':
            return None
        raise UnserializeFormatError()


def unserialize(s: Union[str, bytes]):
    if type(s) is str:
        s = s.encode('utf-8')
    return _handle((c for c in s))


__all__ = ['unserialize', 'UnserializeTypeError', 'UnserializeFormatError', ]
