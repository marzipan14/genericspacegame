# A GENERIC SPACE GAME
# by Mateusz Krajewski
# 04.12.2020

# Recommended screen resolution: 1920x1080
# Cheat code 1: Ctrl-x to stop taking damage
# Cheat code 2: Ctrl-y to gain one heart

from mplayer import *
from mship import *
from mscanner import *
from mbackground import *
from mforeground import *
from mmeteorite import *
from mbuttons import *
from mmenus import *
import tkinter as tk
from datetime import datetime
from time import sleep
from math import ceil


def check_status():
    """Waits for possible updates in the state of the game"""

    # accelerates the asteroids
    if(not buttons.is_pause):
        for i in range(len(mets)):
            mets[i].velocity += 1 / 57600

    # accelerates the stars in the background
    if(not buttons.is_pause):
        background.vel_constant += 1 / 57600

    # adds one heart if the scanner counter reaches 100%
    if(scanner.scanner_progr > 100):
        scanner.scanner_progr = 0
        foreground.scanner_progr = 100.00
        # unless the player already has max lives
        if(foreground.lives < foreground.max_lives):
            foreground.heart_more()
    else:
        foreground.scanner_progr = round(scanner.scanner_progr, 2)

    # if a pause button or <p> has been pressed, pauses all the objects
    if(buttons.pause_click):
        buttons.pause_click = False
        if(not buttons.is_pause):
            menus.pause()
        elif(not menus.is_main_menu_open):
            menus.unpause()

    # if a settings button or <Esc> has been pressed
    if(buttons.settings_click):
        buttons.settings_click = False
        # if a menu is open, closes it and unpauses
        if(menus.is_menu_open):
            menus.close_all()
            menus.unpause()
        # if the game is paused but the menu is not open, opens it
        elif(buttons.is_pause and not menus.is_main_menu_open):
            menus.open_menu()
        # if the game is not paused, pauses and opens menu
        elif(not menus.is_main_menu_open):
            menus.open_menu()
            menus.pause()
        # if the main menu is open, closes all other windows
        elif(menus.is_main_menu_open):
            menus.close_all()

    # if the lives counter has reached 0, the player dies
    if(foreground.lives <= 0):
        foreground.lives = 3
        menus.pause()
        menus.open_death()

    # if the first cheat code has been entered, forwards the info
    if(menus.cheat1_click):
        menus.cheat1_click = False
        if(menus.is_cheat1):
            menus.is_cheat1 = False
        else:
            menus.is_cheat1 = True

    # if the second cheat code has been entered, adds a heart
    if(menus.cheat2_click):
        menus.cheat2_click = False
        foreground.heart_more()

    # checks if the scanner covers the enemy ship
    scanner.check_collision_with_ship(
                    ship.x,
                    ship.y,
                    ship.x + ship.width,
                    ship.y + ship.height
                )

    # checks if the player has collided with an enemy ship
    if(not menus.is_cheat1 and player.check_collision_with_ship(
                                        ship.x,
                                        ship.y,
                                        ship.x + ship.width,
                                        ship.y + ship.height
                                    )):

        # shows a collision texture
        canvas.itemconfig(menus.collision, state='normal')
        canvas.lift(menus.collision)
        canvas.coords(
                    menus.collision,
                    (player.x + ship.x + ship.width) // 2,
                    (player.y + ship.y + ship.height) // 2
                )
        canvas.update()
        sleep(1)
        # restarts the game
        canvas.itemconfig(menus.collision, state='hidden')
        foreground.heart_less()
        player.set_start_position()
        ship.set_start_position()
        scanner.set_start_position()
        reset_mets()

    # checks if the player has collided with an asteroid
    met_hit = mets_collided_with_player(
                    player.x,
                    player.y,
                    player.x + player.width,
                    player.y + player.height
                )

    # if a collision with an asteroid has occurred
    if(not menus.is_cheat1 and met_hit != -1):
        # shows a collision texture
        canvas.itemconfig(menus.collision, state='normal')
        canvas.coords(menus.collision, mets[met_hit].x, mets[met_hit].y)
        canvas.lift(menus.collision)
        canvas.update()
        sleep(1)
        # restarts the game
        canvas.itemconfig(menus.collision, state='hidden')
        foreground.heart_less()
        player.set_start_position()
        ship.set_start_position()
        scanner.set_start_position()
        reset_mets()

    canvas.pack()
    root.update()
    root.update_idletasks()
    canvas.after(100 // 60, check_status)

# window size
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# window configuration
root = tk.Tk()
root.title('A generic space game')
root.attributes('-fullscreen', True)
root.geometry(str(SCREEN_WIDTH)+'x'+str(SCREEN_HEIGHT))
root.resizable(0, 0)

# canvas configuration
canvas = tk.Canvas(
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            bg='black'
        )
canvas.focus_set()
canvas.pack()
root.update()

# key elements configuration
background = Background(canvas)
player = Player(canvas)
ship = Ship(canvas)
generate_mets(canvas)
scanner = Scanner(canvas)
foreground = Foreground(canvas)
buttons = Buttons(canvas)
menus = Menus(
            root,
            canvas,
            player,
            ship,
            scanner,
            mets,
            foreground,
            background,
            buttons
        )

# ---------------
# The Game begins
# ---------------

menus.exec_main_menu()

# drawing functions
background.draw()
player.draw()
ship.draw()
scanner.draw()
foreground.draw_scanner()
check_status()
ship.random_motion()
foreground.draw_distance()
restock_mets()
draw_mets()

tk.mainloop()
