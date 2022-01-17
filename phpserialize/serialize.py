from typing import Iterable, Union, Callable
from string import printable


class SerialzeValueError(ValueError):
    pass


class ref:
    def __init__(self, obj):
        self.obj = obj


class S:
    'See https://github.com/frankli0324/libphpserialize/wiki/PHP-String-and-Binary-Data'
    def __init__(self, s: Union[str, bytes, Iterable[int]],
                 encode_chars: Union[str, bytes, Callable[[int], bool]] = None,
                 encode_all=False,
                 format='02x'):
        if type(encode_chars) == str:
            encode_chars = encode_chars.encode()
        if type(encode_chars) == bytes:
            self.encode_chars = lambda x: x in encode_chars
        elif not encode_chars:
            self.encode_chars = lambda x: x not in bytes(printable, 'utf-8')
        else:
            self.encode_chars = encode_chars
        self.encode_all = encode_all
        self.format = format
        if type(s) == str:
            s = s.encode('utf-8')
        self.s = s

    def __getitem__(self, item):
        if type(item) != int or item < 0 or item > 256:
            raise SerialzeValueError()
        if self.encode_all or self.encode_chars(item) or item == 92:
            return '\\' + format(item, self.format)
        else:
            return chr(item)

    def encode(self):
        return ''.join(self[c] for c in self.s)

    def __str__(self):
        return f'S:{len(self.s)}:"{self.encode()}";'


class __empty__:
    __namespace__ = None
    pass


blacklist = set(dir(__empty__))


class __track__:
    def __init__(self):
        self.t, self.c = {}, 0

    def get(self, obj):
        return self.t.get(id(obj), None)

    def put(self, obj):
        self.c += 1
        self.t[id(obj)] = self.c


track = __track__()


def _handle_array(a: Union[dict, list]):
    results = []
    for k in a.keys() if type(a) is dict else range(len(a)):
        if type(k) is int or type(k) is float:
            results.append(_handlers[int](int(k)) + _serialize(a[k]))
        elif type(k) is str:
            if k.isdigit():
                results.append(_handlers[int](int(k)) + _serialize(a[k]))
            else:
                results.append(_handlers[str](k) + _serialize(a[k]))
        else:
            # https://www.php.net/manual/en/language.types.array.php
            raise SerialzeValueError('Illegal offset type')
    return f'a:{len(a)}:{{{"".join(results)}}}'


def _handle_attr(attr):
    children = []
    try:
        namespace = attr.__namespace__.rstrip('\\') + '\\'
    except AttributeError:
        namespace = ''
    attr_type = namespace + type(attr).__name__
    for i in dir(attr):
        if i in blacklist:
            continue
        sub = getattr(attr, i)
        if not callable(sub):
            if i.startswith('private_'):
                i = f'\0{attr_type}\0{i[8:]}'
            if i.startswith('protected_'):
                i = f'\0*\0{i[10:]}'
            if i.startswith('public_'):
                i = i[7:]
            children.append(_handlers[str](i) + _serialize(sub))
    return f'O:{len(attr_type)}:"{attr_type}":{len(children)}:{{{"".join(children)}}}'


def _handle_number(num: Union[int, float]):
    # https://www.php.net/manual/en/ini.core.php#ini.serialize-precision
    # TODO: implement "enhanced algorithm"
    # php_gcvt(Z_DVAL_P(struc), (int)PG(serialize_precision), '.', 'E', tmp_str);
    if num > 9223372036854775807:
        result = f'd:{num:.15E};'.split('E')
        stripped = result[0].rstrip('0')
        if stripped[-1] == '.':
            stripped += '0'
        # is there a better way?
        return f'{stripped}E{result[1]}'
    if type(num) is float:
        return f'd:{num};'
    return f'i:{num};'


_handlers = {
    str: lambda x: f's:{len(x.encode("utf-8"))}:"{x}";',
    S: lambda x: str(x),
    int: _handle_number,
    float: _handle_number,
    list: _handle_array,
    dict: _handle_array,
    bool: lambda x: f'b:{int(x)};',
    type(None): lambda x: 'N;',
}


def register_handler(type, handler):
    _handlers[type] = handler


def _serialize(obj):
    if type(obj) in _handlers:
        return _handlers[type(obj)](obj)
    # wiki/Handling-Reference-Types#tracking-objects
    if (t := track.get(obj)):
        return f'r:{t};'

    if type(obj) == ref:
        if not (i := track.get(obj.obj)):
            # wiki/Handling-Reference-Types#serialzevalueerror-invalid-reference
            raise SerialzeValueError("Invalid Reference")
        return f'R:{i};'
    track.put(obj)
    return _handle_attr(obj)


def serialize(obj):
    track.__init__()
    return _serialize(obj)


__all__ = ['serialize', 'register_handler', 'ref', 'S', 'SerialzeValueError', ]
