# a shared model for all the various clients in chime

class Model:

    rows = 6
    columns = 8

    def __init__(self):
        self.leds = []
        for row in range(0, Model.rows):
            self.leds.append([])
            for column in range(0, Model.columns):
                self.leds[row].append(False)

    def flip(self, x, y):
        self.leds[y][x] = not self.leds[y][x]

    def zero(self):
        for row in range(0, Model.rows):
            for column in range(0, Model.columns):
                self.leds[row][column] = False
