class Position:
    def __init__(self, position):
        from main import win_width, win_height

        X_ORIGIN = win_width / 2
        Y_ORIGIN = win_height / 2

        self.x = position[0]
        self.y = position[1]
        self.conv_x = self.x + X_ORIGIN
        self.conv_y = self.y + Y_ORIGIN

    def __repr__(self):
        return repr((self.conv_x, self.conv_y))

    def get_position(self):
        return (self.conv_x, self.conv_y)
