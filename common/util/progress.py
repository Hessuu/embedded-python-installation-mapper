from common.util.logging import print


def print_percentage(current, max):
    print(f"{100 * (current / max) : .2f} %")
