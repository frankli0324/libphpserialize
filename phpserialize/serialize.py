class __empty__:
    __namespace__ = None
    pass


blacklist = set(dir(__empty__))


def _handle_array(a: [dict, list]):
    results = []
    for k in a.keys() if type(a) is dict else range(len(a)):
        results.append(serialize(k) + serialize(a[k]))
    return f'a:{len(a)}:{{{"".join(results)}}}'


def _handle_attr(attr):
    children = []
    try:
        namespace = attr.__namespace__
    except AttributeError:
        namespace = ''
    attr_type = namespace.rstrip('\\') + '\\' + type(attr).__name__
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
            children.append(serialize(i) + serialize(sub))
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


def serialize(obj):
    if type(obj) in _handlers:
        return _handlers[type(obj)](obj)
    return _handle_attr(obj)
