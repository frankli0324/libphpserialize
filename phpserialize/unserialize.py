from typing import Union


class UnserializeTypeError(TypeError):
    pass


class UnserializeFormatError(SyntaxError):
    pass


class PHP_Class:
    pass


class __PHP_Incomplete_Class(PHP_Class):
    def __init__(self, name: str):
        self.__PHP_Incomplete_Class_Name = name


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


def _handle_object(sg):
    class_name = _handle_str(sg).decode('utf-8')
    property_cnt = _handle_int(sg)
    assert chr(next(sg)) == '{'
    class_type = __PHP_Incomplete_Class
    for cls in PHP_Class.__subclasses__():
        if cls.__name__ == class_name:
            class_type = cls
    # __init__ not called
    obj = PHP_Class.__new__(class_type)
    for _ in range(property_cnt):
        assert chr(next(sg)) == 's' and chr(next(sg)) == ':'
        # property names must be string
        name = _handle_str(sg).decode('utf-8')
        value = _handle(sg)
        setattr(obj, name, value)
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
