from typing import Union


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


def _serialize(obj):
    if type(obj) in _handlers:
        return _handlers[type(obj)](obj)
    # basic types are not tracked
    # see ext/standard/var.c, around line 610
    # if (!is_ref && Z_TYPE_P(var) != IS_OBJECT) {
	#     return 0;
	# }
    # PHP does recognize basic type implicit references though
    # php > var_dump(unserialize("a:2:{i:0;i:1;i:1;R:2;}"));
    # array(2) {
    #   [0]=>
    #   &int(1)
    #   [1]=>
    #   &int(1)
    # }
    # php > var_dump(unserialize("a:2:{i:0;i:1;i:1;r:2;}"));
    # PHP Notice:  unserialize(): Error at offset 21 of 22 bytes in php shell code on line 1
    # Notice: unserialize(): Error at offset 21 of 22 bytes in php shell code on line 1
    # bool(false)
    if (t := track.get(obj)):
        return f'r:{t};'

    if type(obj) == ref:
        if not (i := track.get(obj.obj)):
            # PHP would dereference and serialize the value normally
            # since people would want references explicitly when writing Python scripts,
            # an error is raised here.
            # though that brings up the problem of ordering, take the following example:
            # ```php
            # php > class Obj{};
            # php > $a = new Obj();
            # php > $b = &$a;
            # php > echo serialize(array($a, $b));
            # a:2:{i:0;O:3:"Obj":0:{}i:1;r:2;}
            # php > echo serialize(array($b, $a)); # this would raise an error in libphpserialize
            # a:2:{i:0;O:3:"Obj":0:{}i:1;r:2;}
            # ```
            raise SerialzeValueError("Invalid Reference")
        return f'R:{i};'
    track.put(obj)
    return _handle_attr(obj)


def serialize(obj):
    track.__init__()
    return _serialize(obj)


__all__ = ['serialize', 'register_handler', 'ref', 'SerialzeValueError', ]
