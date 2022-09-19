from typing import List
from .unserialize import PHP_Class


def namespace(*decls: List[str]):
    def _namespace_decorator(cls):
        if not hasattr(cls, '__namespace__'):
            cls.__namespace__ = list()
        for ns in decls:
            cls.__namespace__.extend(ns.split('\\'))
        return cls
    return _namespace_decorator


def php_class(cls):
    return type(cls.__name__, (cls, PHP_Class), {})
