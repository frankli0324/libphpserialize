from .unserialize import PHP_Class


def namespace(ns):
    def _namespace_decorator(cls):
        cls.__namespace__ = ns
        return cls
    return _namespace_decorator


def php_class(cls):
    return type(cls.__name__, (cls, PHP_Class), {})
