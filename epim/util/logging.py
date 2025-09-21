
import builtins
import sys

from epim.util.color_string import ColorString

_tag = "UNK" # Unknown
_color_string_func = ColorString.none


def print(string: str=""):
    builtins.print(_color_string_func(f"{_tag}: {string}"))
    sys.stdout.flush()

def set_tag_and_color_print_func(new_tag, color_string_func):
    global _tag
    _tag = new_tag
    
    global _color_string_func
    _color_string_func = color_string_func