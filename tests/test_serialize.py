from phpserialize import serialize, ref, SerialzeValueError
from phpserialize import namespace


class Test2:
    d = {3: 4}
    e = [5, 6]
    f = None
    g = True


class Test:
    a = 1
    b = '2'
    c = Test2()


class TestRecursion:
    def __init__(self):
        self.a = object()
        self.b = self.a
        assert (id(self.b) == id(self.a))
        self.c = ref(self.a)


@namespace('axqJ', 'zjUw')
@namespace('qwer\\zxcv')
class TestNamespace:
    pass


objects = [
    (None, 'N;'),
    (True, 'b:1;'),
    ('te"st', 's:5:"te"st";'),
    ('啊啊啊', 's:9:"啊啊啊";'),
    ('✈️', 's:6:"✈️";'),
    (213412, 'i:213412;'),
    (213.412, 'd:213.412;'),
    (Test(), ('O:4:"Test":3:{s:1:"a";i:1;s:1:"b";s:1:"2";s:1:"c";O:5:"Test2":4:{s:1:"d";a:1:{'
              'i:3;i:4;}s:1:"e";a:2:{i:0;i:5;i:1;i:6;}s:1:"f";N;s:1:"g";b:1;}}')),
    (['a', '423', 234], 'a:3:{i:0;s:1:"a";i:1;s:3:"423";i:2;i:234;}'),
    ({'a': 1, '8': 'b'}, 'a:2:{s:1:"a";i:1;i:8;s:1:"b";}'),
    ({'test': 1, 2: 'test3'}, 'a:2:{s:4:"test";i:1;i:2;s:5:"test3";}'),
    ({'test': 1, Test(): 1}, SerialzeValueError('Illegal offset type')),
    (TestRecursion(),'O:13:"TestRecursion":3:{s:1:"a";O:6:"object":0:{}s:1:"b";r:2;s:1:"c";R:2;}'),
    (TestNamespace(), 'O:33:"qwer\\zxcv\\axqJ\\zjUw\\TestNamespace":0:{}'),
    # 9223372036854775808: 'd:9.223372036854776E+18;',
    # 10023372036854775808.1234: 'd:1.0023372036854776E+19;',
    # 10000000000000000000: 'd:1.0E+19;'
]


def test_serialize():
    for k, v in objects:
        try:
            result = serialize(k)
            if result != v:
                raise AssertionError(f'serialize({k}) != "{v}" ("{result}")')
        except SerialzeValueError as e:
            if type(e) != type(v) or e.args != v.args:
                raise


if __name__ == '__main__':
    test_serialize()
