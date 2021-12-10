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
    while s[-1].isnumeric():
        s += next(sg)
    return int(s[1:-1])


def _handle_str(sg):
    cnt = int(_handle_int(sg))
    assert next(sg) == '"'
    s = ''
    skip = False
    for _ in range(cnt):
        if skip:
            continue
        next_char = next(sg)
        if next_char.isascii():
            skip = False
        else:
            skip = True
        s += next_char
    assert(next(sg)) == '"'
    next(sg)  # ; or :
    return s


def _handle_array(sg):
    result = {}
    cnt = int(_handle_int(sg))
    assert next(sg) == '{'
    for _ in range(cnt):
        k = _handle(sg)
        v = _handle(sg)
        result[k] = v
    if all((isinstance(i, int) for i in result.keys())):
        result = [v for v in result.values()]
    assert next(sg) == '}'
    return result


def _handle_object(sg):
    class_name = _handle_str(sg)
    property_cnt = _handle_int(sg)
    assert next(sg) == '{'
    class_type = __PHP_Incomplete_Class
    for cls in PHP_Class.__subclasses__():
        if cls.__name__ == class_name:
            class_type = cls
    # __init__ not called
    obj = PHP_Class.__new__(class_type)
    for _ in range(property_cnt):
        name = _handle(sg)
        value = _handle(sg)
        setattr(obj, name, value)
    assert next(sg) == '}'
    return obj


_handlers = {
    'b': lambda sg: [next(sg), next(sg)][0] == '1',
    'i': _handle_int,
    'a': _handle_array,
    's': _handle_str,
    'O': _handle_object,
}


def _handle(sg):
    x = next(sg)
    try:
        assert next(sg) == ':'
        if x not in _handlers:
            raise UnserializeTypeError('Invalid Type')
        return _handlers[x](sg)
    except AssertionError:
        raise UnserializeFormatError()


def unserialize(s: str):
    return _handle((c for c in s))


__all__ = ['unserialize', 'UnserializeTypeError', 'UnserializeFormatError', ]
