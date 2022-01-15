import tkinter as tk
import random

# direction vectors
DX = [0, -1, 0, 1]
DY = [-1, 0, 1, 0]

# direction aliases
UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3

# direction list
DIRECTIONS = [
                [UP],
                [UP, LEFT],
                [LEFT],
                [LEFT, DOWN],
                [DOWN],
                [DOWN, RIGHT],
                [RIGHT],
                [RIGHT, UP]
            ]


class Ship:
    """A ship navigated by the computer"""

    def __init__(self, canvas):
        """Creates the ship"""

        self.canvas = canvas
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()
        self.is_pause = False

        self.velocity = 3
        self.frequency = 100 // 6
        self.change_frequency = 1300  # frequency of changing direction
        self.x = 0
        self.y = 0
        # the direction of current motion
        self.moves = [False, False, False, False]
        # three textures depending on the direction
        self.img_up = tk.PhotoImage(file='textures/ship_up.png')
        self.img_down = tk.PhotoImage(file='textures/ship_down.png')
        self.img_default = tk.PhotoImage(file='textures/ship_default.png')
        self.id = self.canvas.create_image(
                                    0,
                                    0,
                                    image=self.img_default,
                                    anchor='nw',
                                    state='hidden'
                                )
        self.width = self.img_default.width()
        self.height = self.img_default.height()

        self.set_start_position()
        self.canvas.pack()

    def change_direction(cls):
        """Updates the object's direction in a random manner"""

        # clears the previous direction
        for i in range(len(cls.moves)):
            cls.moves[i] = False

        # determines a new direction
        direction = random.choice(DIRECTIONS)
        for i in range(len(direction)):
            cls.moves[direction[i]] = True

    def random_motion(cls):
        """Allows the object to move if the game is not paused"""

        if(not cls.is_pause):
            cls.change_direction()
        cls.canvas.after(cls.change_frequency, cls.random_motion)

    def draw(cls):
        """Updates the position of the object"""

        if(not cls.is_pause):
            # update the position
            for i in range(4):
                cls.canvas.move(
                            cls.id,
                            cls.velocity * DX[i] * cls.moves[i],
                            cls.velocity * DY[i] * cls.moves[i]
                        )
                cls.x += cls.velocity * DX[i] * cls.moves[i]
                cls.y += cls.velocity * DY[i] * cls.moves[i]

            # update the texture
            if(cls.moves[UP] and not cls.moves[DOWN]):
                cls.canvas.itemconfig(cls.id, image=cls.img_up)
            elif(cls.moves[DOWN] and not cls.moves[UP]):
                cls.canvas.itemconfig(cls.id, image=cls.img_down)
            else:
                cls.canvas.itemconfig(cls.id, image=cls.img_default)

            # check collisions
            cls.check_collision_with_wall()
            cls.canvas.pack()
        cls.canvas.after(cls.frequency, cls.draw)

    def set_start_position(cls):
        """Places the object on a starting position"""

        cls.x = cls.canvas_width - cls.width - 128
        cls.y = (cls.canvas_height - cls.height) // 2
        cls.canvas.coords(cls.id, cls.x, cls.y)
        cls.canvas.pack()

    def check_collision_with_wall(cls):
        """Updates the position if a collision with a wall occurs"""

        # left wall
        if(cls.x < 2 * cls.canvas_width // 3):
            cls.canvas.move(cls.id, cls.velocity, 0)
            cls.x += cls.velocity
            cls.change_direction()
        # right wall
        if(cls.x + cls.width > cls.canvas_width):
            cls.canvas.move(cls.id, -cls.velocity, 0)
            cls.x -= cls.velocity
            cls.change_direction()
        # top wall
        if(cls.y < 0):
            cls.canvas.move(cls.id, 0, cls.velocity)
            cls.y += cls.velocity
            cls.change_direction()
        # bottom wall
        if(cls.y + cls.height > cls.canvas_height):
            cls.canvas.move(cls.id, 0, -cls.velocity)
            cls.y -= cls.velocity
            cls.change_direction()
