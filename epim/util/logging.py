
import builtins

_tag = ""
_color_string_func = None


def print(string: str=""):
    builtins.print(_color_string_func(f"{_tag}: {string}"))

def set_tag_and_color_print_func(new_tag, color_string_func):
    global _tag
    _tag = new_tag
    
    global _color_string_func
    _color_string_func = color_string_func