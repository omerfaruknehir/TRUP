import inspect
from functools import wraps
import traceback
from types import TracebackType

import sys
from contextlib import contextmanager
from typing import Iterable

@contextmanager
def except_handler(exc_handler):
    sys.excepthook = exc_handler
    yield
    sys.excepthook = sys.__excepthook__

def my_exchandler(type, value, traceback):
    print(value)

class ParamError(ValueError):
    def __init__(self, *args: object) -> None:
        stack = traceback.extract_stack()[:-2]
        caller_frame = stack[-1]
        caller_func_name = caller_frame.name
        
        # Raise a custom error with a custom message and formatted traceback
        error_message = f"ParamError(ValueError): {', '.join([str(i) for i in args])}"
        formatted_traceback = '\n'.join(traceback.format_list(stack))
        lastline = formatted_traceback.split('\n')[-2]
        space = len(lastline) - len(lastline.lstrip(' '))
        highlight = len(lastline.strip(' '))
        self.args = [f"Traceback (most recent call last):\n{formatted_traceback}{' ' * space + '^' * highlight}\n{error_message}"] # type: ignore
    
    def __str__(self):
        return self.args[0]
    
    def with_traceback(self, __tb: TracebackType | None):
        return super().with_traceback(__tb)

def type_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)

        for param_name, param_value in bound_args.arguments.items():
            param_type = sig.parameters[param_name].annotation
            if param_type is not inspect.Parameter.empty:
                if '|' in str(param_type):  # Check if the type is a union type
                    expected_types = [t.strip() for t in str(param_type).split('|')]
                    if not any(isinstance(param_value, eval(t)) for t in expected_types):
                        type_names = ', '.join(expected_types)
                        with except_handler(my_exchandler):
                            raise ParamError(f"Parameter '{param_name}' should be one of the following types: [{type_names}], but got {type(param_value).__name__}")
                elif not isinstance(param_value, param_type):
                    with except_handler(my_exchandler):
                        raise ParamError(f"Parameter '{param_name}' should be of type {param_type.__name__}, but got {type(param_value).__name__}")

        return func(*args, **kwargs)
    return wrapper