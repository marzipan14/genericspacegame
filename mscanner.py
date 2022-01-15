import tkinter as tk

# direction vectors
DX = [0, -1, 0, 1]
DY = [-1, 0, 1, 0]

# direction aliases
UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3


class Scanner:
    """The scanner navigated by the player"""

    def __init__(self, canvas):
        """Creates the scanner"""

        self.canvas = canvas
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()
        self.is_pause = False
        self.scanner_progr = 0
        self.scanner_tick = 0.2  # how much to increment in a single tick

        self.velocity = 7
        self.freq = 100 // 6  # scanner update frequency
        self.x = 0
        self.y = 0
        # the direction of current motion
        self.moves = [False, False, False, False]
        # two textures depending on the state of the scanner
        self.img_green = tk.PhotoImage(file='textures/scanner_green.png')
        self.img_red = tk.PhotoImage(file='textures/scanner_red.png')
        self.id = self.canvas.create_image(
                                    0,
                                    0,
                                    image=self.img_green,
                                    anchor='nw',
                                    state='hidden'
                                )
        self.width = self.img_green.width()
        self.height = self.img_red.height()

        # key bindings
        self.canvas.bind_all(
                            '<KeyPress-Up>',
                            lambda e: self.motion(UP)
                        )
        self.canvas.bind_all(
                            '<KeyPress-Left>',
                            lambda e: self.motion(LEFT)
                        )
        self.canvas.bind_all(
                            '<KeyPress-Down>',
                            lambda e: self.motion(DOWN)
                        )
        self.canvas.bind_all(
                            '<KeyPress-Right>',
                            lambda e: self.motion(RIGHT)
                        )
        self.canvas.bind_all(
                            '<KeyRelease-Up>',
                            lambda e: self.no_motion(UP)
                        )
        self.canvas.bind_all(
                            '<KeyRelease-Left>',
                            lambda e: self.no_motion(LEFT)
                        )
        self.canvas.bind_all(
                            '<KeyRelease-Down>',
                            lambda e: self.no_motion(DOWN)
                        )
        self.canvas.bind_all(
                            '<KeyRelease-Right>',
                            lambda e: self.no_motion(RIGHT)
                        )

        self.set_start_position()
        self.canvas.pack()

    def motion(cls, direction):
        """Updates the current direction if a key is pressed"""

        if(not cls.is_pause):
            cls.moves[direction] = True

    def no_motion(cls, direction):
        """Updates the current direction if a key is released"""

        cls.moves[direction] = False

    def draw(cls):
        """Updating the position of the object"""

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
            cls.check_collision_with_wall()
            cls.canvas.pack()
        cls.canvas.after(cls.freq, cls.draw)

    def set_start_position(cls):
        """Places the object on a starting position"""

        cls.x = (cls.canvas_width - cls.width) // 2
        cls.y = (cls.canvas_height - cls.height) // 2
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

        # the coordinates of the middle of the ship
        xm = (x0 + x1) // 2
        ym = (y0 + y1) // 2

        if(
            cls.within(x0, y0, xm, ym, cls.x, cls.y) or
            cls.within(xm, y0, x1, ym, cls.x + cls.width, cls.y) or
            cls.within(x0, ym, xm, y1, cls.x, cls.y + cls.height) or
            cls.within(xm, ym, x1, y1, cls.x + cls.width, cls.y + cls.height)
        ):
            # activate
            cls.canvas.itemconfig(cls.id, image=cls.img_red)
            cls.scanner_progr += cls.scanner_tick
        else:
            # deactivate
            cls.canvas.itemconfig(cls.id, image=cls.img_green)

        cls.canvas.pack()
