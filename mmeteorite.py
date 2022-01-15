import tkinter as tk
from math import pi, sin, cos, atan
from random import randint, uniform, choice

active = []  # asteroids currently on the screen
inactive = []  # asteroids currently off screen
mets = []  # the list of asteroids
max_visible = 30  # maximum number of asteroids on the screen
max_total = 30  # maximum number of asteroids in total
max_vertices = 4
min_vertices = 6  # max and min number of asteroid vertices
min_radius = 20
max_radius = 30  # max and min asteroid radius
min_velocity = 15
max_velocity = 20  # max and min asteroid velocity
freq = 100 // 6  # asteroids update frequency
restock_freq = 200  # asteroids restock frequency
canvas = None
canvas_width = 0
canvas_height = 0
is_pause = False


def pause_mets():
    """Pauses the asteroids"""

    global is_pause
    is_pause = True


def unpause_mets():
    """Unpauses the asteroids"""

    global is_pause
    is_pause = False


def draw_mets():
    """Updates the positions of the asteroids"""

    if(not is_pause):
        for i in active:
            mets[i].x -= mets[i].velocity
            canvas.move(mets[i].met_id, -mets[i].velocity, 0)
            # if the asteroid is off screen
            if(mets[i].x <= mets[i].dest[0]):
                active.remove(i)
                inactive.append(i)
                canvas.itemconfig(mets[i].met_id, state='hidden')
    canvas.after(freq, draw_mets)


def generate_mets(canv):
    """Generates a list of asteroids"""

    global canvas
    global canvas_width
    global canvas_height
    canvas = canv
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    for i in range(max_total):
        met = Meteorite(canvas)
        met.generate_verts()
        mets.append(met)
        # at first all asteroids are off screen
        inactive.append(i)


def reset_mets():
    """Resets the positions of asteroids"""

    while(len(active) > 0):
        i = active.pop()
        inactive.append(i)
        canvas.itemconfig(mets[i].met_id, state='hidden')
        canvas.move(mets[i].met_id, -mets[i].x, -mets[i].y)
        canvas.move(mets[i].met_id, mets[i].dest[0], mets[i].dest[1])
        mets[i].x = mets[i].dest[0]
        mets[i].y = mets[i].dest[1]


def restock_mets():
    """Checks if the number of on-screen asteroids is as high as possible"""

    if(not is_pause):
        if(len(active) < max_visible):
            # choose a random inactive asteroid
            poss = choice(inactive)
            inactive.remove(poss)
            active.append(poss)

            # choose its new source, destination, and velocity
            mets[poss].src = roll_source(
                        mets[poss].radius,
                        canvas_width,
                        canvas_height
                    )
            mets[poss].dest = (-mets[poss].radius, mets[poss].src[1])

            # place it on the screen
            canvas.move(mets[poss].met_id, -mets[poss].x, -mets[poss].y)
            canvas.move(
                        mets[poss].met_id,
                        mets[poss].src[0],
                        mets[poss].src[1]
                    )
            mets[poss].x = mets[poss].src[0]
            mets[poss].y = mets[poss].src[1]
            canvas.itemconfig(mets[poss].met_id, state='normal')
    canvas.after(restock_freq, restock_mets)


def roll_source(radius, width, height):
    """Chooses a random starting point for the asteroid"""

    x = width + radius
    y = uniform(radius, height - radius)
    return (x, y)


def mets_collided_with_player(x0, y0, x1, y1):
    """Checks if a collision with player has occurred"""

    for i in active:
        test_x = mets[i].x
        test_y = mets[i].y
        if(mets[i].x < x0):
            test_x = x0
        elif(mets[i].x > x1):
            test_x = x1
        if(mets[i].y < y0):
            test_y = y0
        elif(mets[i].y > y1):
            test_y = y1
        dist_x = mets[i].x - test_x
        dist_y = mets[i].y - test_y

        # if a collision has occured, return the number of the asteroid
        if(dist_x*dist_x + dist_y*dist_y <= mets[i].radius*mets[i].radius):
            return i
    return -1


class Meteorite:
    """A single asteroid (or meteorite)"""

    def __init__(self, canvas):
        """Creates an asteroid"""

        self.canvas = canvas
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()
        self.x = 0
        self.y = 0
        self.radius = 0
        self.velocity = uniform(min_velocity, max_velocity)
        # the number of vertices
        self.vertices = randint(max_vertices, min_vertices)
        # the list of vertex positions in the form (arm, angle)
        self.angles = []
        self.dest = (0, 0)  # the destination
        self.src = (0, 0)  # the source

    def generate_verts(cls):
        """Randomises the vertices and places the object on screen"""

        cls.radius = 0  # the max distance from the vertex to the middle
        # randomise the vertices
        for i in range(cls.vertices):
            angle = i * 2 * pi / cls.vertices
            arm = uniform(min_radius, max_radius)
            cls.angles.append((angle, arm))
            cls.radius = max(cls.radius, arm)
        # place the asteroid on the screen
        cls.met_id = cls.canvas.create_polygon(
                                    cls.translate(),
                                    fill='gray42',
                                    state='hidden'
                                )

    def translate(cls):
        """Translates the list of (arm, angle) into (x, y)"""

        result = []
        for i in range(cls.vertices):
            angle = cls.angles[i][0]
            arm = cls.angles[i][1]
            x = arm * cos(angle) + cls.x
            y = arm * sin(angle) + cls.y
            result.append(x)
            result.append(y)
        return result
