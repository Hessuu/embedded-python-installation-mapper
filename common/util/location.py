from enum import Enum

class Location(Enum):    
    # The developer's PC.
    HOST = "HOST"
    
    # The device under mapping.
    TARGET = "TARGET"

# Should be set when starting. Can be accessed by all to check where we are.
Location.current = None


def host_only(func):
    def wrapper(*args, **kwargs):
        assert Location.current == Location.HOST
        return func(*args, **kwargs)
    return wrapper

def target_only(func):
    def wrapper(*args, **kwargs):
        assert Location.current == Location.TARGET
        return func(*args, **kwargs)
    return wrapper

''' Technically this is useless, because we are always either on host or target.
This is provided purely so that functions can be flagged as designed
to work on both. '''
def host_and_target(func):
    def wrapper(*args, **kwargs):
        assert Location.current == Location.HOST or Location.current == Location.TARGET
        return func(*args, **kwargs)
    return wrapper