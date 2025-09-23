
class ColorString(object):
    def red(string: str):
        return f"\033[91m{string}\033[00m"

    def yellow(string: str):
        return f"\033[93m{string}\033[00m"

    def green(string: str):
        return f"\033[92m{string}\033[00m"

    def purple(string: str):
        return f"\033[95m{string}\033[00m"

    def cyan(string: str):
        return f"\033[96m{string}\033[00m"

    def dark_red(string: str):
        return f"\033[31m{string}\033[00m"

    def white(string: str):
        return f"\033[97m{string}\033[00m"

    def gray(string: str):
        return f"\033[90m{string}\033[00m"

    def none(string: str):
        return string
