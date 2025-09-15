from epim.application import *


from typing import Any, Callable, Generic, TypeVar
'''
def classproperty(func: Callable[[type], Any]) -> property:
    """A decorator that combines @classmethod and @property."""
    return property(classmethod(func).__get__)
'''

T = TypeVar("T")
R = TypeVar("R")

class classproperty(Generic[T, R]):
    def __init__(self, func: Callable[[type[T]], R]) -> None:
        self.func = func

    def __get__(self, obj: Any, cls: type[T]) -> R:
        return self.func(cls)

'''
class classproperty:
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, owner):
        return self.func(owner)
'''

def host_only(func):
    def wrapper(*args, **kwargs):
        from epim.application import Application, Location

        assert Application.location == Location.HOST
        return func(*args, **kwargs)
    return wrapper

def target_only(func):
    def wrapper(*args, **kwargs):
        from epim.application import Application, Location

        assert Application.location == Location.TARGET
        return func(*args, **kwargs)
    return wrapper

''' Technically this is useless, because we are always either on host or target.
This is provided purely so that functions can be flagged to work on both. '''
def host_and_target(func):
    def wrapper(*args, **kwargs):
        from epim.application import Application, Location

        assert Application.location == Location.HOST or Application.location == Location.TARGET
        return func(*args, **kwargs)
    return wrapper
