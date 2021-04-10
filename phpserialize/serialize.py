class SerialzeValueError(ValueError):
    pass


class ref:
    def __init__(self, obj):
        self.obj = obj


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


def _handle_array(a: [dict, list]):
    results = []
    for k in a.keys() if type(a) is dict else range(len(a)):
        results.append(_serialize(k, is_key=True) + _serialize(a[k]))
    return f'a:{len(a)}:{{{"".join(results)}}}'


def _handle_attr(attr):
    children = []
    try:
        namespace = attr.__namespace__.rstrip('\\') + '\\'
    except AttributeError:
        namespace = ''
    if type(attr) == ref:
        if not (i := track.get(attr.obj)):
            raise SerialzeValueError("Invalid Reference")
        return f'R:{i};'
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
            children.append(_serialize(i, is_key=True) + _serialize(sub))
    return f'O:{len(attr_type)}:"{attr_type}":{len(children)}:{{{"".join(children)}}}'


def _handle_number(num: [int, float]):
    # https://www.php.net/manual/en/ini.core.php#ini.serialize-precision
    # TODO: 实现此处所说的所谓 "enhanced algorithm"
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
    str: lambda x: f's:{len(x)}:"{x}";',
    int: _handle_number,
    float: _handle_number,
    list: _handle_array,
    dict: _handle_array,
    bool: lambda x: f'b:{int(x)};',
    type(None): lambda x: 'N;',
}


def register_handler(type, handler):
    _handlers[type] = handler


def _serialize(obj, is_key=False):
    if type(obj) in _handlers:
        return _handlers[type(obj)](obj)
    if not is_key:
        if (t := track.get(obj)):
            return f'r:{t};'
        track.put(obj)
    return _handle_attr(obj)


def serialize(obj):
    track.__init__()
    return _serialize(obj)


__all__ = ['serialize', 'register_handler', 'ref', 'SerialzeValueError', ]
