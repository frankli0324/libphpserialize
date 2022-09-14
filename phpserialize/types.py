# serveral PHP internal types

class PHP_Class:
    pass


class __PHP_Incomplete_Class(PHP_Class):
    def __init__(self, name: str):
        self.__PHP_Incomplete_Class_Name = name

    def __repr__(self):
        return f'<{self.__PHP_Incomplete_Class_Name}>'


class Error(PHP_Class):
    protected_code: int
    protected_file: bytes
    protected_line: int
    protected_message: bytes
    private_previous: any
    private_str: bytes
    private_trace: list[dict]


class SoapClient(PHP_Class):
    uri: str = ''
    location: str
    _user_agent: str
    _stream_context: int = 0
    _soap_version: int = 1


__all__ = [
    'PHP_Class',
    '__PHP_Incomplete_Class',
    'Error',
    'SoapClient'
]
