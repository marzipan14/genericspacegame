import tkinter as tk
from random import random, randint


class Background:
    """The stars moving in the background"""

    def __init__(self, canvas):
        """Creates the stars in the background"""

        self.canvas = canvas
        self.canvas_width = canvas.winfo_width()
        self.canvas_height = canvas.winfo_height()
        self.freq = 100 // 6  # background update frequency
        self.max_stars = 50
        self.max_size = 3
        self.size_constant = 5  # constant when determining size
        self.vel_constant = 0.8  # constant when determining velocity
        self.star_list = []
        self.is_pause = False

        # random generation
        for i in range(self.max_stars):
            x = randint(0, self.canvas_width)
            y = randint(0, self.canvas_height)
            size = self.max_size * max(random(), 0.1)
            id_num = self.canvas.create_line(
                                x,
                                y,
                                x + size * size * size * self.size_constant,
                                y,
                                width=size,
                                fill='white',
                                state='hidden',
                            )
            self.star_list.append((id_num, size))
        self.canvas.pack()

    def draw(self):
        """Moves the stars in the background"""

        if(not self.is_pause):
            for i in range(len(self.star_list)):
                id_num = self.star_list[i][0]
                size = self.star_list[i][1]
                # move the star
                self.canvas.move(
                                id_num,
                                -size * size * size * self.vel_constant,
                                0
                            )
                width = size * size * size * self.size_constant
                coord = self.canvas.coords(id_num)
                # if the star is off screen
                if(coord[0] + width < 0):
                    new_y = randint(0, self.canvas_height)
                    self.canvas.coords(
                                    id_num,
                                    self.canvas_width,
                                    new_y,
                                    self.canvas_width + width,
                                    new_y
                                )
                self.star_list[i] = (id_num, size)
            self.canvas.pack()
        self.canvas.after(self.freq, self.draw)

    def reset(cls):
        """Resets the stars in the background"""

        for i in range(len(cls.star_list)):
            id_num = cls.star_list[i][0]
            size = cls.star_list[i][1]
            width = size * size * size * cls.size_constant
            new_x = randint(0, cls.canvas_width)
            new_y = randint(0, cls.canvas_height)
            cls.canvas.coords(id_num, new_x, new_y, new_x + width, new_y)
            cls.star_list[i] = (id_num, size)
