def namespace(ns):
    def _namespace_decorator(cls):
        cls.__namespace__ = ns
        return cls
    return _namespace_decorator
