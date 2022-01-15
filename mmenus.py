import tkinter as tk
from mplayer import *
from mship import *
from mscanner import *
from mmeteorite import *
from mforeground import *
from mbackground import *
from math import ceil
from os import listdir
from datetime import datetime
from random import randint
from re import search

# direction aliases
UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3


class Menus():
    def __init__(
                    cls,
                    root,
                    canvas,
                    player,
                    ship,
                    scanner,
                    mets,
                    foreground,
                    background,
                    buttons
                ):
        """Initialises all menu elements"""

        cls.root = root
        cls.canvas = canvas
        cls.canvas_width = cls.canvas.winfo_width()
        cls.canvas_height = cls.canvas.winfo_height()
        cls.player = player
        cls.ship = ship
        cls.scanner = scanner
        cls.mets = mets
        cls.foreground = foreground
        cls.background = background
        cls.active = active
        cls.inactive = inactive
        cls.buttons = buttons
        cls.player.is_volatile_open = False  # True if some keys are disabled
        cls.buttons.is_volatile_open = False  # True if some keys are disabled

        cls.init_common()
        cls.init_boss()
        cls.init_menu()
        cls.init_main_menu()
        cls.init_load()
        cls.init_save()
        cls.init_confirm()
        cls.init_settings()
        cls.init_help()
        cls.init_death()
        cls.init_lead()

        # Initialises the 'boss key'
        cls.is_boss = False  # True if a boss window is open
        cls.canvas.bind_all('<b>', lambda e: cls.exec_boss())

        # Initialises the first cheat code
        cls.cheat1_click = False  # True if a cheat code 1 is entered
        cls.is_cheat1 = False  # True if a cheat code 1 is active
        cls.canvas.bind_all('<Control-x>', lambda e: cls.cheat1_exec())

        # Initialises the second cheat code
        cls.cheat2_click = False  # True if a cheat code 2 is entered
        cls.canvas.bind_all('<Control-y>', lambda e: cls.cheat2_exec())

    def cheat1_exec(cls):
        """Activates the first cheat code"""

        cls.cheat1_click = True

    def cheat2_exec(cls):
        """Activates the second cheat code"""

        cls.cheat2_click = True

    def pause(cls):
        """Pauses the game"""

        cls.buttons.is_pause = True
        cls.canvas.itemconfig(
                            cls.buttons.pause_id,
                            image=cls.buttons.nopause1,
                            activeimage=cls.buttons.nopause2
                        )
        cls.canvas.itemconfig(cls.shroud, state='normal')
        cls.player.is_pause = True
        cls.ship.is_pause = True
        cls.scanner.is_pause = True
        cls.background.is_pause = True
        cls.foreground.is_pause = True
        pause_mets()

    def unpause(cls):
        """Unpauses the game"""

        cls.buttons.is_pause = False
        cls.canvas.itemconfig(
                            cls.buttons.pause_id,
                            image=cls.buttons.pause1,
                            activeimage=cls.buttons.pause2
                        )
        cls.canvas.itemconfig(cls.shroud, state='hidden')
        cls.player.is_pause = False
        cls.ship.is_pause = False
        cls.scanner.is_pause = False
        cls.background.is_pause = False
        cls.foreground.is_pause = False
        unpause_mets()
        cls.close_all()

    def close_all(cls):
        """Closes all active windows"""

        cls.close_lead()
        cls.close_death()
        cls.close_help()
        cls.close_settings()
        cls.close_save()
        cls.close_confirm()
        cls.close_load()
        cls.close_menu()

    def init_common(cls):
        """Initialises textures common for multiple events"""

        # a pause shroud
        cls.shr = tk.PhotoImage(file='textures/shroud.png')
        cls.shroud = cls.canvas.create_image(
                                    0,
                                    0,
                                    image=cls.shr,
                                    state='hidden',
                                    anchor='nw'
                                )

        # a collision texture
        cls.coll_img = tk.PhotoImage(file='textures/collision.png')
        cls.collision = cls.canvas.create_image(
                                    0,
                                    0,
                                    image=cls.coll_img,
                                    state='hidden'
                                )

        # a warning message
        cls.warning_text = cls.canvas.create_text(
                                    cls.canvas_width // 2,
                                    450,
                                    fill='red',
                                    state='hidden',
                                    font=('FreeMono', 22, 'bold')
                                )

        # an in-game menu background
        cls.menu3 = tk.PhotoImage(file='textures/local_menu.png')
        cls.local_menu = cls.canvas.create_image(
                                    cls.canvas_width // 2,
                                    cls.canvas_height // 2,
                                    image=cls.menu3,
                                    state='hidden'
                                )

        # a left arrow
        cls.menu7 = tk.PhotoImage(file='textures/arrow_left.png')
        cls.menu8 = tk.PhotoImage(file='textures/arrow_left2.png')
        cls.arrow_left = cls.canvas.create_image(
                                    800,
                                    820,
                                    image=cls.menu7,
                                    activeimage=cls.menu8,
                                    state='hidden'
                                )

        # a right arrow
        cls.menu9 = tk.PhotoImage(file='textures/arrow_right.png')
        cls.menu10 = tk.PhotoImage(file='textures/arrow_right2.png')
        cls.arrow_right = cls.canvas.create_image(
                                    1110,
                                    820,
                                    image=cls.menu9,
                                    activeimage=cls.menu10,
                                    state='hidden'
                                )

        # an exit button
        cls.menu5 = tk.PhotoImage(file='textures/exit_button1.png')
        cls.menu6 = tk.PhotoImage(file='textures/exit_button2.png')
        cls.exit_button = cls.canvas.create_image(
                                    1270,
                                    420,
                                    image=cls.menu5,
                                    activeimage=cls.menu6,
                                    state='hidden',
                                    anchor='nw'
                                )

        # a horizontal message window
        cls.menu4 = tk.PhotoImage(file='textures/message_window.png')
        cls.mess_window = cls.canvas.create_image(
                                    cls.canvas_width // 2,
                                    cls.canvas_height // 2,
                                    image=cls.menu4,
                                    state='hidden'
                                )

    def init_menu(cls):
        """Initialises the in-game menu"""

        cls.is_menu_open = False  # True if the in-game menu is open

        # button textures
        cls.l_menu = []  # The list of buttons
        cls.l_menu_text = [
                        'Resume',
                        'Save Game',
                        'Load Game',
                        'Settings',
                        'Main Menu'
                    ]  # The list of button contents
        cls.l_button1 = tk.PhotoImage(file='textures/l_button1.png')
        cls.l_button2 = tk.PhotoImage(file='textures/l_button2.png')
        for i in range(len(cls.l_menu_text)):
            cls.l_menu_text[i] = cls.canvas.create_text(
                                    cls.canvas_width // 2,
                                    280 + 120*i,
                                    text=cls.l_menu_text[i],
                                    font=('FreeMono', 22, 'bold'),
                                    state='hidden',
                                    fill='white',
                                    anchor='n'
                                )
            cls.l_menu.append(cls.canvas.create_image(
                                    cls.canvas_width // 2,
                                    245 + 120*i,
                                    image=cls.l_button1,
                                    activeimage=cls.l_button2,
                                    state='hidden',
                                    anchor='n'
                                ))

        # button bindings
        cls.canvas.tag_bind(
                            cls.l_menu[0],
                            '<Button-1>',
                            lambda e: cls.exec_resume()
                        )
        cls.canvas.tag_bind(
                            cls.l_menu[1],
                            '<Button-1>',
                            lambda e: cls.open_save()
                        )
        cls.canvas.tag_bind(
                            cls.l_menu[2],
                            '<Button-1>',
                            lambda e: cls.open_load(1)
                        )
        cls.canvas.tag_bind(
                            cls.l_menu[3],
                            '<Button-1>',
                            lambda e: cls.open_settings()
                        )
        cls.canvas.tag_bind(
                            cls.l_menu[4],
                            '<Button-1>',
                            lambda e: cls.exec_main_menu()
                        )

    def open_menu(cls):
        """Opens the in-game menu"""

        cls.is_menu_open = True
        # the background
        cls.canvas.lift(cls.local_menu)
        cls.canvas.itemconfig(cls.local_menu, state='normal')
        # the text on the buttons
        for i in range(len(cls.l_menu_text)):
            cls.canvas.lift(cls.l_menu_text[i])
            cls.canvas.itemconfig(cls.l_menu_text[i], state='normal')
        # the buttons
        for i in range(len(cls.l_menu)):
            cls.canvas.lift(cls.l_menu[i])
            cls.canvas.itemconfig(cls.l_menu[i], state='normal')

    def close_menu(cls):
        """Closes the in-game menu"""

        cls.is_menu_open = False
        # the background
        cls.canvas.itemconfig(cls.local_menu, state='hidden')
        # the text on the buttons
        for i in range(len(cls.l_menu)):
            cls.canvas.itemconfig(cls.l_menu[i], state='hidden')
        # the buttons
        for i in range(len(cls.l_menu_text)):
            cls.canvas.itemconfig(cls.l_menu_text[i], state='hidden')

    def init_main_menu(cls):
        """Initialises the main menu"""

        cls.is_main_menu_open = False  # True if the main menu is open

        # the background
        cls.menu1 = tk.PhotoImage(file='textures/menu_background.png')
        cls.menu_background = cls.canvas.create_image(
                                    0,
                                    0,
                                    image=cls.menu1,
                                    state='hidden',
                                    anchor='nw'
                                )

        # the title
        cls.menu2 = tk.PhotoImage(file='textures/game_title.png')
        cls.game_title = cls.canvas.create_image(
                                    cls.canvas_width // 2,
                                    60,
                                    image=cls.menu2,
                                    state='hidden',
                                    anchor='n'
                                )

        # button textures
        cls.g_menu = []  # the list of buttons
        cls.g_menu_text = [
                        'New Game',
                        'Load Game',
                        'Leaderboard',
                        'Help',
                        'Settings',
                        'Exit'
                    ]  # the list of button contents
        cls.g_button1 = tk.PhotoImage(file='textures/g_button1.png')
        cls.g_button2 = tk.PhotoImage(file='textures/g_button2.png')
        for i in range(len(cls.g_menu_text)):
            cls.g_menu_text[i] = cls.canvas.create_text(
                                    cls.canvas_width // 2,
                                    395 + 110 * i,
                                    text=cls.g_menu_text[i],
                                    font=('FreeMono', 22, 'bold'),
                                    state='hidden',
                                    fill='white',
                                    anchor='n'
                                )
            cls.g_menu.append(cls.canvas.create_image(
                                    cls.canvas_width // 2,
                                    365 + 110 * i,
                                    image=cls.g_button1,
                                    activeimage=cls.g_button2,
                                    state='hidden',
                                    anchor='n'
                                ))

        # button bindings
        cls.canvas.tag_bind(
                            cls.g_menu[0],
                            '<Button-1>',
                            lambda e: cls.exec_new_game()
                        )
        cls.canvas.tag_bind(
                            cls.g_menu[1],
                            '<Button-1>',
                            lambda e: cls.open_load(1)
                        )
        cls.canvas.tag_bind(
                            cls.g_menu[2],
                            '<Button-1>',
                            lambda e: cls.open_lead(1)
                        )
        cls.canvas.tag_bind(
                            cls.g_menu[3],
                            '<Button-1>',
                            lambda e: cls.open_help()
                        )
        cls.canvas.tag_bind(
                            cls.g_menu[4],
                            '<Button-1>',
                            lambda e: cls.open_settings()
                        )
        cls.canvas.tag_bind(
                            cls.g_menu[5],
                            '<Button-1>',
                            lambda e: cls.exec_exit()
                        )

    def open_main_menu(cls):
        """Opens the main menu"""

        cls.is_main_menu_open = True
        # the background
        cls.canvas.lift(cls.menu_background)
        cls.canvas.itemconfig(cls.menu_background, state='normal')
        # the title
        cls.canvas.lift(cls.game_title)
        cls.canvas.itemconfig(cls.game_title, state='normal')
        # the text on the buttons
        for i in range(len(cls.g_menu_text)):
            cls.canvas.lift(cls.g_menu_text[i])
            cls.canvas.itemconfig(cls.g_menu_text[i], state='normal')
        # the buttons
        for i in range(len(cls.g_menu)):
            cls.canvas.lift(cls.g_menu[i])
            cls.canvas.itemconfig(cls.g_menu[i], state='normal')

    def close_main_menu(cls):
        """Closes the main menu"""

        cls.is_main_menu_open = False
        # the background
        cls.canvas.itemconfig(cls.menu_background, state='hidden')
        # the title
        cls.canvas.itemconfig(cls.game_title, state='hidden')
        # the text on the buttons
        for i in range(len(cls.g_menu_text)):
            cls.canvas.itemconfig(cls.g_menu_text[i], state='hidden')
        # the buttons
        for i in range(len(cls.g_menu)):
            cls.canvas.itemconfig(cls.g_menu[i], state='hidden')

    def exec_main_menu(cls):
        """Runs when the 'main menu' button is clicked"""

        # closes all windows, closes the game, pauses, and opens main menu
        cls.close_all()
        cls.open_main_menu()
        cls.close_game()
        cls.pause()

    def init_load(cls):
        """Initialises the 'load game' menu"""

        # already saved games, sorted by date
        cls.load_saves = []  # saved games in the form (save time, filename)
        for file in listdir('saved_games'):
            if(file.endswith('.txt')):
                f = open('saved_games/' + file)
                save_date = f.readline()
                cls.load_saves.append((
                    datetime.strptime(save_date, '%Y-%m-%d %H:%M:%S.%f\n'),
                    file[:-4]
                ))
                f.close()
        cls.load_saves.sort(reverse=1)

        # title text
        cls.load_text = cls.canvas.create_text(
                                    cls.canvas_width // 2,
                                    270,
                                    text="Choose a game",
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden'
                                )

        # page number
        cls.load_page = cls.canvas.create_text(
                    cls.canvas_width // 2,
                    500,
                    text='1 / ' + str(max(ceil(len(cls.load_saves) / 4), 1)),
                    font=('FreeMono', 22, 'bold'),
                    fill='white',
                    state='hidden'
                )

        # buttons
        cls.load_buttons = []  # button textures
        cls.load_buttons_text = []  # the text on the buttons (filenames)
        cls.load_buttons_text2 = []  # the text on the buttons (dates)
        for i in range(4):
            cls.load_buttons.append(cls.canvas.create_image(
                                cls.canvas_width // 2,
                                360 + 120*i,
                                image=cls.l_button1,
                                activeimage=cls.l_button2,
                                state='hidden'
                            ))
            cls.load_buttons_text.append(cls.canvas.create_text(
                                    955,
                                    335 + 120*i,
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden'
                                ))
            cls.load_buttons_text2.append(cls.canvas.create_text(
                                    955,
                                    375 + 120*i,
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden'
                                ))

    def open_load(cls, page):
        """Opens the 'load game' menu"""

        # if the in-game menu is open, close it and open this one instead
        if(cls.is_menu_open):
            cls.close_menu()
            cls.is_menu_open = True
        # if the main menu is open, temporarily disable its buttons
        elif(cls.is_main_menu_open):
            for i in range(len(cls.g_menu)):
                cls.canvas.itemconfig(cls.g_menu[i], state='disabled')

        # background
        cls.canvas.lift(cls.local_menu)
        cls.canvas.itemconfig(cls.local_menu, state='normal')

        # exit button
        cls.canvas.lift(cls.exit_button)
        cls.canvas.coords(cls.exit_button, 1170, 230)
        cls.canvas.tag_unbind(cls.exit_button, '<Button-1>')
        cls.canvas.tag_bind(
                            cls.exit_button,
                            '<Button-1>',
                            lambda e: cls.close_load()
                        )
        cls.canvas.itemconfig(cls.exit_button, state='normal')

        # title
        cls.canvas.lift(cls.load_text)
        cls.canvas.itemconfig(cls.load_text, state='normal')

        # left arrow
        cls.canvas.lift(cls.arrow_left)
        cls.canvas.tag_unbind(cls.arrow_left, '<Button-1>')
        cls.canvas.tag_bind(
                                    cls.arrow_left,
                                    '<Button-1>',
                                    lambda e: cls.open_load(page-1)
                                )
        # disables the arrow when the first page is reached
        if(page == 1):
            cls.canvas.itemconfig(cls.arrow_left, state='disabled')
        else:
            cls.canvas.itemconfig(cls.arrow_left, state='normal')

        # right arrow
        cls.canvas.lift(cls.arrow_right)
        cls.canvas.tag_unbind(cls.arrow_right, '<Button-1>')
        cls.canvas.tag_bind(
                                    cls.arrow_right,
                                    '<Button-1>',
                                    lambda e: cls.open_load(page+1)
                                )
        # disables the arrow when the last page is reached
        if(page == max(ceil(len(cls.load_saves) / 4), 1)):
            cls.canvas.itemconfig(cls.arrow_right, state='disabled')
        else:
            cls.canvas.itemconfig(cls.arrow_right, state='normal')

        # page counter
        cls.canvas.lift(cls.load_page)
        cls.canvas.coords(cls.load_page, cls.canvas_width // 2, 820)
        num = max(ceil(len(cls.load_saves) / 4), 1)
        cls.canvas.itemconfig(
            cls.load_page,
            text=str(page) + ' / ' + str(num),
            state='normal'
        )

        # buttons and text on buttons
        for i in range(len(cls.load_buttons)):
            # if the number of games is not divisible by 4, hide the rest
            if(4*(page-1)+i >= len(cls.load_saves)):
                cls.canvas.itemconfig(
                                    cls.load_buttons[i],
                                    state='hidden'
                                )
                cls.canvas.itemconfig(
                                    cls.load_buttons_text[i],
                                    state='hidden'
                                )
                cls.canvas.itemconfig(
                                    cls.load_buttons_text2[i],
                                    state='hidden'
                                )
            else:
                # button text - the name of the game
                cls.canvas.lift(cls.load_buttons_text[i])
                cls.game_name = cls.load_saves[4*(page-1)+i][1]
                cls.canvas.itemconfig(
                                    cls.load_buttons_text[i],
                                    text=cls.game_name,
                                    state='normal'
                                )

                # button text - the time when the game was saved
                cls.canvas.lift(cls.load_buttons_text2[i])
                cls.game_time = \
                    cls.load_saves[4*(page-1)+i][0].strftime('%d/%m/%Y %H:%M')
                cls.canvas.itemconfig(
                                    cls.load_buttons_text2[i],
                                    text=cls.game_time,
                                    state='normal'
                                )

                # button textures
                cls.canvas.lift(cls.load_buttons[i])
                cls.canvas.itemconfig(cls.load_buttons[i], state='normal')

                # button bindings
                cls.canvas.tag_unbind(cls.load_buttons[i], '<Button-1>')
                cls.canvas.tag_bind(
                                    cls.load_buttons[i],
                                    '<Button-1>',
                                    lambda e, gn=cls.game_name:
                                    cls.exec_load(gn)
                                )

    def close_load(cls):
        """Closes the 'load game' menu"""

        # background
        cls.canvas.itemconfig(cls.local_menu, state='hidden')

        # exit button
        cls.canvas.itemconfig(cls.exit_button, state='hidden')

        # title
        cls.canvas.itemconfig(cls.load_text, state='hidden')

        # arrows
        cls.canvas.itemconfig(cls.arrow_left, state='hidden')
        cls.canvas.itemconfig(cls.arrow_right, state='hidden')

        # page counter
        cls.canvas.itemconfig(cls.load_page, state='hidden')

        # buttons
        for i in range(len(cls.load_buttons)):
            cls.canvas.itemconfig(cls.load_buttons[i], state='hidden')
            cls.canvas.itemconfig(
                                    cls.load_buttons_text[i],
                                    state='hidden'
                                )
            cls.canvas.itemconfig(
                                    cls.load_buttons_text2[i],
                                    state='hidden'
                                )

        # if the in-game menu was closed, reopen it
        if(cls.is_menu_open):
            cls.open_menu()
        # if the main menu was disabled, reenable it
        elif(cls.is_main_menu_open):
            for i in range(len(cls.g_menu)):
                cls.canvas.itemconfig(cls.g_menu[i], state='normal')

    def exec_load(cls, path):
        """Runs when the 'load game' button is clicked"""

        file = open('saved_games/' + path + '.txt')
        file.readline()

        # reads foreground info and updates the lives counter
        cls.foreground.dist = int(file.readline())
        cls.foreground.lives = int(file.readline())
        for i in range(cls.foreground.lives):
            cls.canvas.itemconfig(
                            cls.foreground.hearts[i],
                            image=cls.foreground.heart_img1
                        )
        for i in range(cls.foreground.lives, cls.foreground.max_lives):
            cls.canvas.itemconfig(
                            cls.foreground.hearts[i],
                            image=cls.foreground.heart_img2
                        )

        # reads the player info
        cls.player.x = int(file.readline())
        cls.player.y = int(file.readline())
        cls.canvas.coords(cls.player.id, cls.player.x, cls.player.y)

        # reads the enemy ship info
        cls.ship.x = int(file.readline())
        cls.ship.y = int(file.readline())
        cls.canvas.coords(cls.ship.id, cls.ship.x, cls.ship.y)

        # reads the scanner info and updates the counter accordingly
        cls.scanner.scanner_progr = float(file.readline())
        cls.scanner.x = float(file.readline())
        cls.scanner.y = float(file.readline())
        cls.canvas.coords(cls.scanner.id, cls.scanner.x, cls.scanner.y)

        # reads the background info
        cls.background.vel_constant = float(file.readline())

        # deletes the current asteroids
        for i in range(len(cls.mets)):
            cls.canvas.delete(cls.mets[i].met_id)
        cls.mets.clear()

        # reads the active asteroids info and updates them accordingly
        cls.active.clear()
        active_no = int(file.readline())
        for i in range(active_no):
            temp = Meteorite(cls.canvas)
            temp.velocity = float(file.readline())
            temp.radius = float(file.readline())
            temp.vertices = int(file.readline())
            temp.x = float(file.readline())
            temp.y = float(file.readline())
            temp.dest = (float(file.readline()), float(file.readline()))
            for j in range(temp.vertices):
                angle = float(file.readline())
                arm = float(file.readline())
                temp.angles.append((angle, arm))
            temp.met_id = cls.canvas.create_polygon(
                                    temp.translate(),
                                    fill='gray42',
                                    state='normal'
                                )
            cls.active.append(len(cls.mets))
            cls.mets.append(temp)

        # reads the inactive asteroids info and updates them accordingly
        cls.inactive.clear()
        inactive_no = int(file.readline())
        for i in range(inactive_no):
            temp = Meteorite(cls.canvas)
            temp.velocity = float(file.readline())
            temp.radius = float(file.readline())
            temp.vertices = int(file.readline())
            temp.x = float(file.readline())
            temp.y = float(file.readline())
            temp.dest = (float(file.readline()), float(file.readline()))
            for j in range(temp.vertices):
                angle = float(file.readline())
                arm = float(file.readline())
                temp.angles.append((angle, arm))
            temp.met_id = cls.canvas.create_polygon(
                                    temp.translate(),
                                    fill='gray42',
                                    state='hidden'
                                )
            cls.inactive.append(len(mets))
            cls.mets.append(temp)
        file.close()

        # ensures the layers are in the correct order
        cls.canvas.lift(cls.scanner.id)
        cls.canvas.lift(cls.foreground.dist_id)
        cls.canvas.lift(cls.foreground.scanner_id)
        cls.canvas.lift(cls.buttons.pause_id)
        cls.canvas.lift(cls.buttons.settings_id)
        for i in range(cls.foreground.max_lives):
            cls.canvas.lift(cls.foreground.hearts[i])

        # closes all windows and starts the game anew
        cls.unpause()
        cls.close_all()
        cls.close_main_menu()
        cls.open_game()

        cls.canvas.pack()
        cls.canvas.update()
        cls.root.update()

    def open_game(cls):
        """Opens the game window"""

        cls.canvas.itemconfig(cls.player.id, state='normal')
        cls.canvas.itemconfig(cls.ship.id, state='normal')
        cls.canvas.itemconfig(cls.scanner.id, state='normal')
        cls.canvas.itemconfig(cls.buttons.settings_id, state='normal')
        cls.canvas.itemconfig(cls.buttons.pause_id, state='normal')
        cls.canvas.itemconfig(cls.foreground.dist_id, state='normal')
        cls.canvas.itemconfig(cls.foreground.scanner_id, state='normal')
        for i in cls.foreground.hearts:
            cls.canvas.itemconfig(i, state='normal')
        for i in range(len(cls.background.star_list)):
            cls.canvas.itemconfig(
                                    cls.background.star_list[i][0],
                                    state='normal'
                                )

    def close_game(cls):
        """Closes the game window"""

        # hides the textures
        cls.canvas.itemconfig(cls.player.id, state='hidden')
        cls.canvas.itemconfig(cls.ship.id, state='hidden')
        cls.canvas.itemconfig(cls.scanner.id, state='hidden')
        cls.canvas.itemconfig(cls.buttons.settings_id, state='hidden')
        cls.canvas.itemconfig(cls.buttons.pause_id, state='hidden')
        cls.canvas.itemconfig(cls.local_menu, state='hidden')
        cls.canvas.itemconfig(cls.foreground.dist_id, state='hidden')
        cls.canvas.itemconfig(cls.foreground.scanner_id, state='hidden')
        for i in cls.foreground.hearts:
            cls.canvas.itemconfig(i, state='hidden')
        for i in range(len(cls.background.star_list)):
            cls.canvas.itemconfig(
                                    cls.background.star_list[i][0],
                                    state='hidden'
                                )
        # resets the counters
        cls.foreground.dist = 0
        cls.foreground.scanner_progr = 0
        cls.background.vel_constant = 0.8
        cls.scanner.scanner_progr = 0
        cls.foreground.lives = 3

        # resets the textures
        for i in range(cls.foreground.lives):
            cls.canvas.itemconfig(
                                    cls.foreground.hearts[i],
                                    image=cls.foreground.heart_img1
                                )
        for i in range(cls.foreground.lives, cls.foreground.max_lives):
            cls.canvas.itemconfig(
                                    cls.foreground.hearts[i],
                                    image=cls.foreground.heart_img2
                                )
        cls.background.reset()
        reset_mets()

    def init_save(cls):
        """Initialises the 'save game' menu"""

        # title
        cls.save_text = cls.canvas.create_text(
                                    800,
                                    500,
                                    text="Enter the name:",
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden'
                                )

        # input box
        cls.game_name = tk.StringVar()  # the name entered by the user
        cls.save_prompt = tk.Entry(
                                    cls.canvas,
                                    state='normal',
                                    font=('FreeMono', 22, 'bold'),
                                    textvariable=cls.game_name,
                                    background='white',
                                    width=15
                                )

        # save button
        cls.save_button = cls.canvas.create_image(
                                    cls.canvas_width // 2,
                                    600,
                                    image=cls.l_button1,
                                    activeimage=cls.l_button2,
                                    state='hidden'
                                )
        cls.canvas.tag_bind(
                                    cls.save_button,
                                    '<Button-1>',
                                    lambda e: cls.exec_save()
                                )

        # the text on the save button
        cls.save_button_text = cls.canvas.create_text(
                                    cls.canvas_width // 2,
                                    595,
                                    text='Save',
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden'
                                )

    def open_save(cls):
        """Opens the 'save game' menu"""

        # input is now active - disable any key bindings
        cls.player.is_volatile_open = True
        cls.buttons.is_volatile_open = True

        # background
        cls.canvas.lift(cls.mess_window)
        cls.canvas.itemconfig(cls.mess_window, state='normal')

        # exit button
        cls.canvas.lift(cls.exit_button)
        cls.canvas.coords(cls.exit_button, 1270, 420)
        cls.canvas.tag_unbind(cls.exit_button, '<Button-1>')
        cls.canvas.tag_bind(
                            cls.exit_button,
                            '<Button-1>',
                            lambda e: cls.close_save()
                        )
        cls.canvas.itemconfig(cls.exit_button, state='normal')

        # title
        cls.canvas.lift(cls.save_text)
        cls.canvas.itemconfig(cls.save_text, state='normal')

        # button text
        cls.canvas.lift(cls.save_button_text)
        cls.canvas.itemconfig(cls.save_button_text, state='normal')

        # button
        cls.canvas.lift(cls.save_button)
        cls.canvas.itemconfig(cls.save_button, state='normal')

        # input box
        cls.save_prompt.config(state='normal')
        cls.save_prompt.delete(0, 'end')
        cls.save_prompt.place(x=980, y=485)

        # disable the in-game menu temporarily
        for i in range(len(cls.l_menu)):
            cls.canvas.itemconfig(cls.l_menu[i], state='disabled')

    def close_save(cls):
        """Closes the 'save game' menu"""

        # enables all the key bindings back
        cls.player.is_volatile_open = False
        cls.buttons.is_volatile_open = False

        # background
        cls.canvas.itemconfig(cls.mess_window, state='hidden')

        # exit button
        cls.canvas.itemconfig(cls.exit_button, state='hidden')

        # title
        cls.canvas.itemconfig(cls.save_text, state='hidden')

        # button text
        cls.canvas.itemconfig(cls.save_button_text, state='hidden')

        # button
        cls.canvas.itemconfig(cls.save_button, state='hidden')

        # warning text
        cls.canvas.itemconfig(cls.warning_text, state='hidden')

        # input box
        cls.save_prompt.config(state='disabled')
        cls.save_prompt.place(x=cls.canvas_width, y=cls.canvas_height)

        # enable the in-game menu back
        for i in range(len(cls.l_menu)):
            cls.canvas.itemconfig(cls.l_menu[i], state='normal')

    def exec_save(cls):
        """Runs when the 'save game' button is pressed"""

        name = cls.save_prompt.get()  # the name given
        regex = '^[a-zA-Z0-9_]+$'  # the pattern required

        # if the name does not match a pattern, show a warning message
        if(not search(regex, name)):
            cls.canvas.lift(cls.warning_text)
            cls.canvas.itemconfig(
                                    cls.warning_text,
                                    text='Use letters, numbers or an "_"!',
                                    state='normal'
                                )
            cls.save_prompt.delete(0, 'end')
            return

        # if the name already exists, show a warning message
        if(any(name == y for (x, y) in cls.load_saves)):
            cls.canvas.lift(cls.warning_text)
            cls.canvas.itemconfig(
                                    cls.warning_text,
                                    text='This name already exists!',
                                    state='normal'
                                )
            cls.save_prompt.delete(0, 'end')
            return

        # if the name is longer than 16 chars, show a warning message
        if(len(name) > 16):
            cls.canvas.lift(cls.warning_text)
            cls.canvas.itemconfig(
                                    cls.warning_text,
                                    text='Use a maximum of 16 characters!',
                                    state='normal'
                                )
            cls.save_prompt.delete(0, 'end')
            return

        file = open('saved_games/' + name + '.txt', 'x')
        dt = datetime.now()
        cls.load_saves.append((dt, name))
        cls.load_saves.sort(reverse=1)
        file.write(str(dt) + '\n')

        # write the foreground info
        file.write(str(cls.foreground.dist) + '\n')
        file.write(str(cls.foreground.lives) + '\n')

        # write the player info
        file.write(str(cls.player.x) + '\n')
        file.write(str(cls.player.y) + '\n')

        # write the enemy ship info
        file.write(str(cls.ship.x) + '\n')
        file.write(str(cls.ship.y) + '\n')

        # write the scanner info
        file.write(str(cls.scanner.scanner_progr) + '\n')
        file.write(str(cls.scanner.x) + '\n')
        file.write(str(cls.scanner.y) + '\n')

        # write the background info
        file.write(str(cls.background.vel_constant) + '\n')

        # write the active asteroids info
        file.write(str(len(cls.active)) + '\n')
        for i in cls.active:
            file.write(str(cls.mets[i].velocity) + '\n')
            file.write(str(cls.mets[i].radius) + '\n')
            file.write(str(cls.mets[i].vertices) + '\n')
            file.write(str(cls.mets[i].x) + '\n')
            file.write(str(cls.mets[i].y) + '\n')
            file.write(str(cls.mets[i].dest[0]) + '\n')
            file.write(str(cls.mets[i].dest[1]) + '\n')
            for j in range(cls.mets[i].vertices):
                file.write(str(cls.mets[i].angles[j][0]) + ' \n')
                file.write(str(cls.mets[i].angles[j][1]) + '\n')

        # write the inactive asteroids info
        file.write(str(len(cls.inactive)) + '\n')
        for i in inactive:
            file.write(str(cls.mets[i].velocity) + '\n')
            file.write(str(cls.mets[i].radius) + '\n')
            file.write(str(cls.mets[i].vertices) + '\n')
            file.write(str(cls.mets[i].x) + '\n')
            file.write(str(cls.mets[i].y) + '\n')
            file.write(str(cls.mets[i].dest[0]) + '\n')
            file.write(str(cls.mets[i].dest[1]) + '\n')
            for j in range(cls.mets[i].vertices):
                file.write(str(cls.mets[i].angles[j][0]) + '\n')
                file.write(str(cls.mets[i].angles[j][1]) + '\n')
        file.close()

        # if everything is ok, show a confirmation menu
        cls.close_save()
        cls.window_confirm_open()

    def init_confirm(cls):
        """Initialises the confirmation menu (after the game is saved)"""

        # title
        cls.confirm_text = cls.canvas.create_text(
                                    cls.canvas_width // 2,
                                    500,
                                    text="The game has been saved!",
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden'
                                )

        # the text on the button
        cls.confirm_button_text = cls.canvas.create_text(
                                    cls.canvas_width // 2,
                                    595,
                                    text='OK',
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden'
                                )

        # button
        cls.confirm_button = cls.canvas.create_image(
                                    cls.canvas_width // 2,
                                    600,
                                    image=cls.l_button1,
                                    activeimage=cls.l_button2,
                                    state='hidden'
                                )
        cls.canvas.tag_bind(
                                    cls.confirm_button,
                                    '<Button-1>',
                                    lambda e: cls.close_confirm()
                                )

    def window_confirm_open(cls):
        """Opens the confirmation menu (after the game is saved)"""

        # background
        cls.canvas.lift(cls.mess_window)
        cls.canvas.itemconfig(cls.mess_window, state='normal')

        # exit button
        cls.canvas.lift(cls.exit_button)
        cls.canvas.tag_unbind(cls.exit_button, '<Button-1>')
        cls.canvas.tag_bind(
                                    cls.exit_button,
                                    '<Button-1>',
                                    lambda e: cls.close_confirm()
                                )
        cls.canvas.itemconfig(cls.exit_button, state='normal')

        # title
        cls.canvas.lift(cls.confirm_text)
        cls.canvas.itemconfig(cls.confirm_text, state='normal')

        # the text on the button
        cls.canvas.lift(cls.confirm_button_text)
        cls.canvas.itemconfig(cls.confirm_button_text, state='normal')

        # button
        cls.canvas.lift(cls.confirm_button)
        cls.canvas.itemconfig(cls.confirm_button, state='normal')

        # temporarily disables the in-game menu
        for i in range(len(cls.l_menu)):
            cls.canvas.itemconfig(cls.l_menu[i], state='disabled')

    def close_confirm(cls):
        """Closes the confirmation menu (after the game is saved)"""

        # background
        cls.canvas.itemconfig(cls.mess_window, state='hidden')

        # exit button
        cls.canvas.itemconfig(cls.exit_button, state='hidden')

        # title
        cls.canvas.itemconfig(cls.confirm_text, state='hidden')

        # the text on the button
        cls.canvas.itemconfig(cls.confirm_button_text, state='hidden')

        # button
        cls.canvas.itemconfig(cls.confirm_button, state='hidden')

        # enable the in-game menu back
        for i in range(len(cls.l_menu)):
            cls.canvas.itemconfig(cls.l_menu[i], state='normal')

    def clicked(cls, i):
        """Runs when the user chooses a key binding to change"""

        # prohibit all other key actions
        cls.player.is_volatile_open = True
        cls.buttons.is_volatile_open = True

        # color the text
        cls.canvas.itemconfig(cls.settings_buttons[i], fill='red')

        # wait for input
        cls.canvas.bind_all('<Key>', lambda e, i=i: cls.change(i, e))

    def change(cls, i, event):
        """Runs when the user changes the key binding"""

        # other key actions are now enabled
        cls.player.is_volatile_open = False
        cls.buttons.is_volatile_open = False
        cls.canvas.unbind_all('<Key>')

        # if there is already such a binding, do nothing
        if(event.keysym in cls.settings_def):
            cls.canvas.itemconfig(cls.settings_buttons[i], fill='white')
            return

        # delete the previous bindings
        cls.canvas.unbind_all('<'+cls.settings_def[i]+'>')

        # the actual changing process
        if(cls.settings_def_text[i] == 'Pause'):
            cls.canvas.bind_all(
                                    '<'+event.keysym+'>',
                                    lambda e: cls.buttons.change_pause()
                                )
        elif(cls.settings_def_text[i] == 'Open settings'):
            cls.canvas.bind_all(
                                    '<'+event.keysym+'>',
                                    lambda e: cls.buttons.menu()
                                )
        elif(cls.settings_def_text[i] == 'Boss key'):
            cls.canvas.bind_all(
                                    '<'+event.keysym+'>',
                                    lambda e: cls.exec_boss()
                                )
        elif(cls.settings_def_text[i] == 'Player up'):
            cls.canvas.unbind_all('<KeyRelease-' + cls.settings_def[i] + '>')
            cls.canvas.bind_all(
                                    '<'+event.keysym+'>',
                                    lambda e: cls.player.motion(UP)
                                )
            cls.canvas.bind_all(
                                    '<KeyRelease-' + event.keysym + '>',
                                    lambda e: cls.player.no_motion(UP)
                                )
        elif(cls.settings_def_text[i] == 'Player left'):
            cls.canvas.unbind_all('<KeyRelease-' + cls.settings_def[i] + '>')
            cls.canvas.bind_all(
                                    '<' + event.keysym + '>',
                                    lambda e: cls.player.motion(LEFT)
                                )
            cls.canvas.bind_all(
                                    '<KeyRelease-' + event.keysym + '>',
                                    lambda e: cls.player.no_motion(LEFT)
                                )
        elif(cls.settings_def_text[i] == 'Player down'):
            cls.canvas.unbind_all('<KeyRelease-' + cls.settings_def[i] + '>')
            cls.canvas.bind_all(
                                    '<' + event.keysym + '>',
                                    lambda e: cls.player.motion(DOWN)
                                )
            cls.canvas.bind_all(
                                    '<KeyRelease-' + event.keysym + '>',
                                    lambda e: cls.player.no_motion(DOWN)
                                )
        elif(cls.settings_def_text[i] == 'Player right'):
            cls.canvas.unbind_all('<KeyRelease-' + cls.settings_def[i] + '>')
            cls.canvas.bind_all(
                                    '<' + event.keysym + '>',
                                    lambda e: cls.player.motion(RIGHT)
                                )
            cls.canvas.bind_all(
                                    '<KeyRelease-' + event.keysym + '>',
                                    lambda e: cls.player.no_motion(RIGHT)
                                )
        elif(cls.settings_def_text[i] == 'Scanner up'):
            cls.canvas.unbind_all('<KeyRelease-' + cls.settings_def[i] + '>')
            cls.canvas.bind_all(
                                    '<' + event.keysym + '>',
                                    lambda e: cls.scanner.motion(UP)
                                )
            cls.canvas.bind_all(
                                    '<KeyRelease-' + event.keysym + '>',
                                    lambda e: cls.scanner.no_motion(UP)
                                )
        elif(cls.settings_def_text[i] == 'Scanner left'):
            cls.canvas.unbind_all('<KeyRelease-' + cls.settings_def[i] + '>')
            cls.canvas.bind_all(
                                    '<' + event.keysym + '>',
                                    lambda e: cls.scanner.motion(LEFT)
                                )
            cls.canvas.bind_all(
                                    '<KeyRelease-' + event.keysym + '>',
                                    lambda e: cls.scanner.no_motion(LEFT)
                                )
        elif(cls.settings_def_text[i] == 'Scanner down'):
            cls.canvas.unbind_all('<KeyRelease-' + cls.settings_def[i] + '>')
            cls.canvas.bind_all(
                                    '<' + event.keysym + '>',
                                    lambda e: cls.scanner.motion(DOWN)
                                )
            cls.canvas.bind_all(
                                    '<KeyRelease-' + event.keysym + '>',
                                    lambda e: cls.scanner.no_motion(DOWN)
                                )
        elif(cls.settings_def_text[i] == 'Scanner right'):
            cls.canvas.unbind_all('<KeyRelease-' + cls.settings_def[i] + '>')
            cls.canvas.bind_all(
                                    '<' + event.keysym + '>',
                                    lambda e: cls.scanner.motion(RIGHT)
                                )
            cls.canvas.bind_all(
                                    '<KeyRelease-' + event.keysym + '>',
                                    lambda e: cls.scanner.no_motion(RIGHT)
                                )
        # update the text
        cls.settings_def[i] = event.keysym
        cls.canvas.itemconfig(
                                    cls.settings_buttons[i],
                                    fill='white',
                                    text=event.keysym
                                )

    def init_settings(cls):
        """Initialises the settings menu"""

        # the titles of the key bindings
        cls.settings_def_text = [
                        'Pause',
                        'Boss key',
                        'Player up',
                        'Player left',
                        'Player down',
                        'Player right',
                        'Scanner up',
                        'Scanner left',
                        'Scanner down',
                        'Scanner right',
                        'Open settings'
                    ]

        # the names of the key bindings
        cls.settings_def = [
                        'p',
                        'b',
                        'w',
                        'a',
                        's',
                        'd',
                        'Up',
                        'Left',
                        'Down',
                        'Right',
                        'Escape'
                    ]

        # the titles that appear on the screen
        cls.settings_text = []

        # the names that appear on the screen
        cls.settings_buttons = []

        # generate and bind the text
        for i in range(len(cls.settings_def)):
            cls.settings_text.append(cls.canvas.create_text(
                                770,
                                255 + 55*i,
                                fill='white',
                                font=('FreeMono', 22, 'bold'),
                                text=cls.settings_def_text[i],
                                state='hidden',
                                anchor='nw'
                            ))
            cls.settings_buttons.append(cls.canvas.create_text(
                                    1070,
                                    255 + 55*i,
                                    fill='white',
                                    font=('FreeMono', 22, 'bold'),
                                    text=cls.settings_def[i],
                                    state='hidden',
                                    anchor='nw'
                                ))
            cls.canvas.tag_bind(
                                    cls.settings_buttons[i],
                                    '<Button-1>',
                                    lambda e, i=i: cls.clicked(i)
                                )

    def open_settings(cls):
        """Opens the settings menu"""

        # if the in-game menu is open, temporarily close it
        if(cls.is_menu_open):
            cls.close_menu()
            cls.is_menu_open = True
        # if the main menu is open, temporarily disable it
        elif(cls.is_main_menu_open):
            for i in range(len(cls.g_menu)):
                cls.canvas.itemconfig(cls.g_menu[i], state='disabled')

        # background
        cls.canvas.lift(cls.local_menu)
        cls.canvas.itemconfig(cls.local_menu, state='normal')

        # exit button
        cls.canvas.lift(cls.exit_button)
        cls.canvas.coords(cls.exit_button, 1170, 230)
        cls.canvas.tag_unbind(cls.exit_button, '<Button-1>')
        cls.canvas.tag_bind(
                                    cls.exit_button,
                                    '<Button-1>',
                                    lambda e: cls.close_settings()
                                )
        cls.canvas.itemconfig(cls.exit_button, state='normal')

        # titles
        for i in range(len(cls.settings_text)):
            cls.canvas.lift(cls.settings_text[i])
            cls.canvas.itemconfig(cls.settings_text[i], state='normal')

        # names
        for i in range(len(cls.settings_buttons)):
            cls.canvas.lift(cls.settings_buttons[i])
            cls.canvas.itemconfig(cls.settings_buttons[i], state='normal')
        cls.canvas.pack()

    def close_settings(cls):
        """Closes the settings menu"""

        # other key bindings can be used again
        cls.player.is_volatile_open = False
        cls.buttons.is_volatile_open = False
        cls.canvas.unbind('<Key>')

        # background
        cls.canvas.itemconfig(cls.local_menu, state='hidden')

        # exit button
        cls.canvas.itemconfig(cls.exit_button, state='hidden')

        # titles
        for i in range(len(cls.settings_buttons)):
            cls.canvas.itemconfig(
                                    cls.settings_buttons[i],
                                    state='hidden',
                                    fill='white'
                                )

        # names
        for i in range(len(cls.settings_text)):
            cls.canvas.itemconfig(cls.settings_text[i], state='hidden')

        # if the in-game menu was closed, open it again
        if(cls.is_menu_open):
            cls.open_menu()
        # if the main menu is open, enable it back
        elif(cls.is_main_menu_open):
            for i in range(len(cls.g_menu)):
                cls.canvas.itemconfig(cls.g_menu[i], state='normal')
        cls.canvas.pack()

    def init_help(cls):
        """Initialises the help menu"""

        cls.lore = cls.canvas.create_text(
                                    cls.canvas_width // 2,
                                    260,
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden',
                                    anchor='n',
                                    justify='center',
                                    text='[Captain log, 17/12/2321]\n\
The chase after an alien\n\
vessel of unknown origin\n\
continues. Our ship, ORP\n\
Trzcina, seems to have\n\
been lured into an\n\
asteroid belt. I will pay\n\
for this mistake with my\n\
head, surely. The only\n\
chance to get out now\n\
is to use our scanning\n\
devices, analyse the\n\
alien ship\'s hull, and\n\
modify ours accordingly.\n\
Despite sustaining\n\
numerous collisions with\n\
asteroids, their vessel\n\
seems to remain intact.\n\
Unlike, sadly, ours.'
                                )

    def open_help(cls):
        """Opens the help menu"""

        # if the main menu is open, temporarily disable it
        if(cls.is_main_menu_open):
            for i in range(len(cls.g_menu)):
                cls.canvas.itemconfig(cls.g_menu[i], state='disabled')

        # background
        cls.canvas.lift(cls.local_menu)
        cls.canvas.itemconfig(cls.local_menu, state='normal')

        # exit button
        cls.canvas.lift(cls.exit_button)
        cls.canvas.coords(cls.exit_button, 1170, 230)
        cls.canvas.tag_unbind(cls.exit_button, '<Button-1>')
        cls.canvas.tag_bind(
                                    cls.exit_button,
                                    '<Button-1>',
                                    lambda e: cls.close_help()
                                )
        cls.canvas.itemconfig(cls.exit_button, state='normal')

        # text
        cls.canvas.lift(cls.lore)
        cls.canvas.itemconfig(cls.lore, state='normal')

    def close_help(cls):
        """Closes the help menu"""

        # background
        cls.canvas.itemconfig(cls.local_menu, state='hidden')

        # exit button
        cls.canvas.itemconfig(cls.exit_button, state='hidden')

        # text
        cls.canvas.itemconfig(cls.lore, state='hidden')

        # if the main menu is open, reenable it
        if(cls.is_main_menu_open):
            for i in range(len(cls.g_menu)):
                cls.canvas.itemconfig(cls.g_menu[i], state='normal')

    def init_death(cls):
        """Initialises the death menu"""

        # the title
        cls.death_text = cls.canvas.create_text(
                                    cls.canvas_width // 2,
                                    450,
                                    text='You have died!',
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden'
                                )

        # the text next to the input box
        cls.death_text2 = cls.canvas.create_text(
                                    800,
                                    500,
                                    text='Enter Your name:',
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden'
                                )

        # the button
        cls.death_button = cls.canvas.create_image(
                                    cls.canvas_width // 2,
                                    600,
                                    image=cls.l_button1,
                                    activeimage=cls.l_button2,
                                    state='hidden'
                                )
        cls.canvas.tag_bind(
                                    cls.death_button,
                                    '<Button-1>',
                                    lambda e: cls.exec_death()
                                )

        # the texton the button
        cls.death_button_text = cls.canvas.create_text(
                                    cls.canvas_width // 2,
                                    595,
                                    text='Damn!',
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden'
                                )
        # user input
        cls.player_name = tk.StringVar()
        cls.death_prompt = tk.Entry(
                                    cls.root,
                                    state='normal',
                                    font=('FreeMono', 22, 'bold'),
                                    textvariable=cls.player_name,
                                    background='white',
                                    width=15
                                )
        cls.death_prompt.place(x=980, y=485)
        cls.death_prompt.lower()

    def open_death(cls):
        """Opens the death menu"""

        # user input active - other key functions prohibited
        cls.player.is_volatile_open = True
        cls.buttons.is_volatile_open = True

        # background
        cls.canvas.lift(cls.mess_window)
        cls.canvas.itemconfig(cls.mess_window, state='normal')

        # title
        cls.canvas.lift(cls.death_text)
        cls.canvas.itemconfig(cls.death_text, state='normal')

        # the text next to the input box
        cls.canvas.lift(cls.death_text2)
        cls.canvas.itemconfig(cls.death_text2, state='normal')

        # the text on the button
        cls.canvas.lift(cls.death_button_text)
        cls.canvas.itemconfig(cls.death_button_text, state='normal')

        # the button
        cls.canvas.lift(cls.death_button)
        cls.canvas.itemconfig(cls.death_button, state='normal')

        # input box
        cls.death_prompt.lift()
        cls.death_prompt.config(state='normal')

    def close_death(cls):
        """Closes the death menu"""

        # reenables other key bindings
        cls.player.is_volatile_open = False
        cls.buttons.is_volatile_open = False

        # background
        cls.canvas.itemconfig(cls.mess_window, state='hidden')

        # title
        cls.canvas.itemconfig(cls.death_text, state='hidden')

        # the text next to the input box
        cls.canvas.itemconfig(cls.death_text2, state='hidden')

        # the text on the button
        cls.canvas.itemconfig(cls.death_button_text, state='hidden')

        # the button
        cls.canvas.itemconfig(cls.death_button, state='hidden')

        # warning text
        cls.canvas.itemconfig(cls.warning_text, state='hidden')

        # input box
        cls.death_prompt.lower()
        cls.death_prompt.config(state='disabled')

    def exec_death(cls):
        """Runs when the player dies"""

        cls.player_name = cls.death_prompt.get()  # the player name
        regex = '^[a-z_A-Z0-9_]+$'  # the regular expression

        # if the name does not math the regular expression, show a warning
        if(not search(regex, cls.player_name)):
            cls.canvas.itemconfig(cls.death_text, state='hidden')
            cls.canvas.lift(cls.warning_text)
            cls.canvas.itemconfig(
                                    cls.warning_text,
                                    text='Use letters, numbers or an "_"!',
                                    state='normal'
                                )
            cls.death_prompt.delete(0, 'end')
            return

        # if the player name already exists, show a warning
        if(any(cls.player_name == y for (x, y) in cls.lead_saves)):
            cls.canvas.itemconfig(cls.death_text, state='hidden')
            cls.canvas.lift(cls.warning_text)
            cls.canvas.itemconfig(
                                    cls.warning_text,
                                    text='This name already exists!',
                                    state='normal'
                                )
            cls.death_prompt.delete(0, 'end')
            return

        # if the name is longer than 12 chars, show a warning message
        if(len(cls.player_name) > 12):
            cls.canvas.itemconfig(cls.death_text, state='hidden')
            cls.canvas.lift(cls.warning_text)
            cls.canvas.itemconfig(
                                    cls.warning_text,
                                    text='Use a maximum of 12 characters!',
                                    state='normal'
                                )
            cls.death_prompt.delete(0, 'end')
            return

        # if everything is ok, create a new saved player
        file = open('leaderboard/' + cls.player_name + '.pl', 'x')
        file.write(str(cls.foreground.dist))
        file.close()
        cls.lead_saves.append((cls.foreground.dist, cls.player_name))
        cls.lead_saves.sort(reverse=1)
        cls.death_prompt.delete(0, 'end')

        # return to main menu
        cls.exec_main_menu()

    def init_lead(cls):
        """Initialises the leaderboard menu"""

        # already saved players, sorted by distance
        cls.lead_saves = []  # saved players in the form (distance, name)
        for file in listdir('leaderboard'):
            if(file.endswith('.pl')):
                f = open('leaderboard/' + file)
                save_dist = f.readline()
                cls.lead_saves.append((int(save_dist), file[:-3]))
                f.close()
        cls.lead_saves.sort(reverse=1)

        # title text
        cls.lead_text = cls.canvas.create_text(
                                    cls.canvas_width // 2,
                                    270,
                                    text="Leaderboard",
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden'
                                )

        # page number
        cls.lead_page = cls.canvas.create_text(
                    cls.canvas_width // 2,
                    500,
                    text='1 / ' + str(max(ceil(len(cls.lead_saves) / 4), 1)),
                    font=('FreeMono', 22, 'bold'),
                    fill='white',
                    state='hidden'
                )

        # buttons
        cls.lead_buttons = []  # button textures
        cls.lead_buttons_text = []  # the text on the buttons (place number)
        cls.lead_buttons_text2 = []  # the text on the buttons (player name)
        cls.lead_buttons_text3 = []  # the text on the buttons (distance)
        for i in range(4):
            cls.lead_buttons.append(cls.canvas.create_image(
                                cls.canvas_width // 2,
                                360 + 120*i,
                                image=cls.l_button1,
                                state='hidden'
                            ))
            cls.lead_buttons_text.append(cls.canvas.create_text(
                                    835,
                                    330 + 120*i,
                                    font=('FreeMono', 44, 'bold'),
                                    fill='white',
                                    state='hidden',
                                    width='80',
                                    anchor='n'
                                ))
            cls.lead_buttons_text2.append(cls.canvas.create_text(
                                    890,
                                    325 + 120*i,
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden',
                                    anchor='nw'
                                ))
            cls.lead_buttons_text3.append(cls.canvas.create_text(
                                    890,
                                    360 + 120*i,
                                    font=('FreeMono', 22, 'bold'),
                                    fill='white',
                                    state='hidden',
                                    anchor='nw'
                                ))

    def open_lead(cls, page):
        """Open the leaderboard menu"""

        # if the in-game menu is open, close it and open this one instead
        if(cls.is_main_menu_open):
            for i in range(len(cls.g_menu)):
                cls.canvas.itemconfig(cls.g_menu[i], state='disabled')

        # background
        cls.canvas.lift(cls.local_menu)
        cls.canvas.itemconfig(cls.local_menu, state='normal')

        # exit button
        cls.canvas.lift(cls.exit_button)
        cls.canvas.coords(cls.exit_button, 1170, 230)
        cls.canvas.tag_unbind(cls.exit_button, '<Button-1>')
        cls.canvas.tag_bind(
                            cls.exit_button,
                            '<Button-1>',
                            lambda e: cls.close_lead()
                        )
        cls.canvas.itemconfig(cls.exit_button, state='normal')

        # title
        cls.canvas.lift(cls.lead_text)
        cls.canvas.itemconfig(cls.lead_text, state='normal')

        # left arrow
        cls.canvas.lift(cls.arrow_left)
        cls.canvas.tag_unbind(cls.arrow_left, '<Button-1>')
        cls.canvas.tag_bind(
                                    cls.arrow_left,
                                    '<Button-1>',
                                    lambda e: cls.open_lead(page-1)
                                )
        # disables the arrow when the first page is reached
        if(page == 1):
            cls.canvas.itemconfig(cls.arrow_left, state='disabled')
        else:
            cls.canvas.itemconfig(cls.arrow_left, state='normal')

        # right arrow
        cls.canvas.lift(cls.arrow_right)
        cls.canvas.tag_unbind(cls.arrow_right, '<Button-1>')
        cls.canvas.tag_bind(
                                    cls.arrow_right,
                                    '<Button-1>',
                                    lambda e: cls.open_lead(page+1)
                                )
        # disables the arrow when the last page is reached
        if(page == max(ceil(len(cls.lead_saves) / 4), 1)):
            cls.canvas.itemconfig(cls.arrow_right, state='disabled')
        else:
            cls.canvas.itemconfig(cls.arrow_right, state='normal')

        # page counter
        cls.canvas.lift(cls.lead_page)
        cls.canvas.coords(cls.lead_page, cls.canvas_width // 2, 820)
        num = max(ceil(len(cls.lead_saves) / 4), 1)
        cls.canvas.itemconfig(
                cls.lead_page,
                text=str(page) + ' / ' + str(num),
                state='normal'
            )

        # buttons and text on buttons
        for i in range(len(cls.lead_buttons)):
            # if the number of games is not divisible by 4, hide the rest
            if(4*(page-1)+i >= len(cls.lead_saves)):
                cls.canvas.itemconfig(
                                    cls.lead_buttons[i],
                                    state='hidden'
                                )
                cls.canvas.itemconfig(
                                    cls.lead_buttons_text[i],
                                    state='hidden'
                                )
                cls.canvas.itemconfig(
                                    cls.lead_buttons_text2[i],
                                    state='hidden'
                                )
                cls.canvas.itemconfig(
                                    cls.lead_buttons_text3[i],
                                    state='hidden'
                                )
            else:
                # colors the first three places
                if(page == 1 and i == 0):
                    cls.canvas.itemconfig(
                                    cls.lead_buttons_text[i],
                                    fill='gold'
                                )
                elif(page == 1 and i == 1):
                    cls.canvas.itemconfig(
                                    cls.lead_buttons_text[i],
                                    fill='grey42'
                                )
                elif(page == 1 and i == 2):
                    cls.canvas.itemconfig(
                                    cls.lead_buttons_text[i],
                                    fill='saddlebrown'
                                )
                else:
                    cls.canvas.itemconfig(
                                    cls.lead_buttons_text[i],
                                    fill='white'
                                )

                # place number
                cls.canvas.lift(cls.lead_buttons_text[i])
                cls.canvas.itemconfig(
                                    cls.lead_buttons_text[i],
                                    text=str(4*(page-1)+i+1),
                                    state='normal'
                                )

                # player name
                cls.canvas.lift(cls.lead_buttons_text2[i])
                cls.lead_name = cls.lead_saves[4*(page-1)+i][1]
                cls.canvas.itemconfig(
                                    cls.lead_buttons_text2[i],
                                    text=cls.lead_name,
                                    state='normal'
                                )

                # distance
                cls.canvas.lift(cls.lead_buttons_text3[i])
                cls.lead_dist = str(cls.lead_saves[4*(page-1)+i][0])
                cls.canvas.itemconfig(
                                    cls.lead_buttons_text3[i],
                                    text='Score: ' + cls.lead_dist,
                                    state='normal'
                                )

                # button textures
                cls.canvas.lift(cls.lead_buttons[i])
                cls.canvas.itemconfig(
                                    cls.lead_buttons[i],
                                    state='normal'
                                )

    def close_lead(cls):
        """Closes the leaderboard menu"""

        # background
        cls.canvas.itemconfig(cls.local_menu, state='hidden')

        # exit button
        cls.canvas.itemconfig(cls.exit_button, state='hidden')

        # title
        cls.canvas.itemconfig(cls.lead_text, state='hidden')

        # arrows
        cls.canvas.itemconfig(cls.arrow_left, state='hidden')
        cls.canvas.itemconfig(cls.arrow_right, state='hidden')

        # page counter
        cls.canvas.itemconfig(cls.lead_page, state='hidden')

        # buttons
        for i in range(len(cls.lead_buttons)):
            cls.canvas.itemconfig(cls.lead_buttons[i], state='hidden')
            cls.canvas.itemconfig(
                                    cls.lead_buttons_text[i],
                                    state='hidden'
                                )
            cls.canvas.itemconfig(
                                    cls.lead_buttons_text2[i],
                                    state='hidden'
                                )
            cls.canvas.itemconfig(
                                    cls.lead_buttons_text3[i],
                                    state='hidden'
                                )

        # if the main menu was disabled, reenable it
        if(cls.is_main_menu_open):
            for i in range(len(cls.g_menu)):
                cls.canvas.itemconfig(cls.g_menu[i], state='normal')

    def init_boss(cls):
        """Initialises the boss menu"""

        cls.boss_paused = False  # True if the game is paused
        cls.boss_volatile = False  # True if boss menu is open

        cls.boss_src = []  # menu images
        for file in listdir('boss_imgs'):
            cls.boss_src.append(tk.PhotoImage(file='boss_imgs/' + file))

        cls.boss_img = []  # menu textures
        for i in range(len(cls.boss_src)):
            cls.boss_img.append(cls.canvas.create_image(
                                    0,
                                    0,
                                    image=cls.boss_src[i],
                                    state='hidden',
                                    anchor='nw'
                                ))

    def open_boss(cls):
        """Opens the boss menu"""

        # prohibits any other key bindings
        cls.player.is_volatile_open = True
        cls.buttons.is_volatile_open = True

        # if the game is not paused, pauses it
        if(not cls.buttons.is_pause):
            cls.pause()
            cls.boss_paused = True

        # opens the image
        cls.chosen_boss = randint(0, len(cls.boss_img)-1)
        cls.canvas.lift(cls.boss_img[cls.chosen_boss])
        cls.canvas.itemconfig(cls.boss_img[cls.chosen_boss], state='normal')

    def close_boss(cls):
        """Closes the boss menu"""

        cls.canvas.itemconfig(cls.boss_img[cls.chosen_boss], state='hidden')

        # re-enables key bindings
        cls.player.is_volatile_open = False
        cls.buttons.is_volatile_open = False

        # unpauses the game, unless it was paused prior
        if(cls.boss_paused):
            cls.unpause()
            cls.boss_paused = False

    def exec_boss(cls):
        """Runs when the boss key is pressed"""

        # if the input is active, does nothing
        if(
            cls.player.is_volatile_open and
            cls.buttons.is_volatile_open and
            not cls.is_boss
        ):
            return

        # if the boss menu is closed, opens it
        if(not cls.is_boss):
            cls.is_boss = True
            cls.open_boss()

        # if the boss menu is open, closes it
        else:
            cls.close_boss()
            cls.is_boss = False

    def exec_resume(cls):
        """Runs when the 'resume' button is clicked"""

        cls.buttons.settings_click = True
        cls.buttons.is_settings = False

    def exec_new_game(cls):
        """Runs when the 'new game' button is clicked"""

        cls.close_all()
        cls.close_main_menu()
        cls.open_game()
        cls.player.set_start_position()
        cls.ship.set_start_position()
        cls.scanner.set_start_position()
        cls.unpause()

    def exec_exit(cls):
        """Runs when the 'exit' button is clicked"""

        cls.root.destroy()
