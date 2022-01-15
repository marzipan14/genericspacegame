import tkinter as tk

# direction vectors
DX = [0, -1, 0, 1]
DY = [-1, 0, 1, 0]

# direction aliases
UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3


class Player:
    """A ship navigated by the player"""

    def __init__(self, canvas):
        """Creates the ship"""

        self.canvas = canvas
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()
        self.is_pause = False
        self.is_volatile_open = False  # True when some keys are prohibited

        self.velocity = 7
        self.freq = 100 // 6  # ship update frequency
        self.x = 0
        self.y = 0
        # the direction of current motion
        self.moves = [False, False, False, False]
        # three textures depending on the direction
        self.img_up = tk.PhotoImage(file='textures/player_up.png')
        self.img_down = tk.PhotoImage(file='textures/player_down.png')
        self.img_default = tk.PhotoImage(file='textures/player_default.png')
        self.id = self.canvas.create_image(
                                    0,
                                    0,
                                    image=self.img_default,
                                    state='hidden',
                                    anchor='nw'
                                )
        self.width = self.img_default.width()
        self.height = self.img_default.height()

        # key bindings
        self.canvas.bind_all(
                            '<KeyPress-w>',
                            lambda e: self.motion(UP)
                        )
        self.canvas.bind_all(
                            '<KeyPress-a>',
                            lambda e: self.motion(LEFT)
                        )
        self.canvas.bind_all(
                            '<KeyPress-s>',
                            lambda e: self.motion(DOWN)
                        )
        self.canvas.bind_all(
                            '<KeyPress-d>',
                            lambda e: self.motion(RIGHT)
                        )
        self.canvas.bind_all(
                            '<KeyRelease-w>',
                            lambda e: self.no_motion(UP)
                        )
        self.canvas.bind_all(
                            '<KeyRelease-a>',
                            lambda e: self.no_motion(LEFT)
                        )
        self.canvas.bind_all(
                            '<KeyRelease-s>',
                            lambda e: self.no_motion(DOWN)
                        )
        self.canvas.bind_all(
                            '<KeyRelease-d>',
                            lambda e: self.no_motion(RIGHT)
                        )

        self.set_start_position()
        self.canvas.pack()

    def motion(cls, direction):
        """Updates the current direction if a key is pressed"""

        if(not cls.is_pause and not cls.is_volatile_open):
            cls.moves[direction] = True

    def no_motion(cls, direction):
        """Updates the current direction if a key is released"""

        cls.moves[direction] = False

    def draw(cls):
        """Updates the position the object"""

        if(not cls.is_pause):
            # update the position
            for i in range(4):
                cls.canvas.move(
                            cls.id,
                            cls.velocity*DX[i]*cls.moves[i],
                            cls.velocity*DY[i]*cls.moves[i]
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
        cls.canvas.after(cls.freq, cls.draw)

    def set_start_position(cls):
        """Places the object on a starting position"""

        cls.x = 128
        cls.y = cls.canvas_height // 2
        cls.canvas.coords(cls.id, cls.x, cls.y)
        cls.canvas.pack()

    def check_collision_with_wall(cls):
        """Updates the position if a collision with a wall occurs"""

        # left wall
        if(cls.x < 0):
            cls.canvas.move(cls.id, cls.velocity, 0)
            cls.x += cls.velocity
        # right wall
        if(cls.x + cls.width > cls.canvas_width):
            cls.canvas.move(cls.id, -cls.velocity, 0)
            cls.x -= cls.velocity
        # top wall
        if(cls.y < 0):
            cls.canvas.move(cls.id, 0, cls.velocity)
            cls.y += cls.velocity
        # bottom wall
        if(cls.y + cls.height > cls.canvas_height):
            cls.canvas.move(cls.id, 0, -cls.velocity)
            cls.y -= cls.velocity

    def within(cls, x0, y0, x1, y1, xc, yc):
        """Checks whether a collision with an enemy ship occurs (one side)"""

        return (xc >= x0 and xc <= x1 and yc >= y0 and yc <= y1)

    def check_collision_with_ship(cls, x0, y0, x1, y1):
        """Checks whether a collision with an enemy ship occurs"""

        if(
            cls.within(x0, y0, x1, y1, cls.x, cls.y) or
            cls.within(x0, y0, x1, y1, cls.x + cls.width, cls.y) or
            cls.within(x0, y0, x1, y1, cls.x, cls.y + cls.height) or
            cls.within(x0, y0, x1, y1, cls.x + cls.width, cls.y + cls.height)
        ):
            return True
        else:
            return False
