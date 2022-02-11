from main import win_width, win_height

X_ORIGIN = win_width / 2
Y_ORIGIN = win_height / 2


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.conv_x = x + X_ORIGIN
        self.conv_y = y + Y_ORIGIN

    def __repr__(self):
        return repr((self.conv_x, self.conv_y))
