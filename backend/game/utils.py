def __get_height(height):
    return height / 2


def get_paddle_top(y, height):
    return y - __get_height(height)


def get_paddle_bottom(y, height):
    return y + __get_height(height)
