import copy

from enum import Enum
from intbase import InterpreterBase


# Enumerated type for our different language data types
class Type(Enum):
    INT = 1
    BOOL = 2
    STRING = 3
    CLOSURE = 4
    NIL = 5
    OBJECT = 6


class Closure:
    def __init__(self, func_ast, env):
        if env is None:
            self.captured_env = {}
        else:
            self.captured_env = {}
            for key, value in env:
                if value.type() == Type.OBJECT:
                    self.captured_env[key] = value
                elif value.type() == Type.CLOSURE:
                    self.captured_env[key] = value 
                else:
                    self.captured_env[key] = copy.deepcopy(value)
        self.func_ast = func_ast
        self.type = Type.CLOSURE

class Object:
    def __init__(self, expr_ast):
        self.expr_ast = expr_ast
        self.type = Type.OBJECT
        self.dict = {}
        self.proto = None

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name
    
    def set_thing(self, name, thing):
        self.dict[name] = thing

    def get_thing(self, name):
        if self.dict.get(name) is None:
            prototype = self.get_proto()
            while prototype is not None:
                val = prototype.get_thing(name)
                if val is not None:
                    return val
                prototype = prototype.get_proto()
        else:
            return self.dict.get(name)
    
    def get_dict(self):
        return self.dict

    def set_proto(self, parent_obj):
        self.proto = parent_obj

    def get_proto(self):
        return self.proto



# Represents a value, which has a type and its value
class Value:
    def __init__(self, t, v=None):
        self.t = t
        self.v = v

    def value(self):
        return self.v

    def type(self):
        return self.t

    def set(self, other):
        self.t = other.t
        self.v = other.v

def create_value(val):
    if val == InterpreterBase.TRUE_DEF:
        return Value(Type.BOOL, True)
    elif val == InterpreterBase.FALSE_DEF:
        return Value(Type.BOOL, False)
    elif isinstance(val, int):
        return Value(Type.INT, val)
    elif val == InterpreterBase.NIL_DEF:
        return Value(Type.NIL, None)
    elif isinstance(val, str):
        return Value(Type.STRING, val)


def get_printable(val):
    if val.type() == Type.INT:
        return str(val.value())
    if val.type() == Type.STRING:
        return val.value()
    if val.type() == Type.BOOL:
        if val.value() is True:
            return "true"
        return "false"
    return None
