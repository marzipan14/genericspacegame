import tkinter as tk


class Buttons:
    """The buttons in the bottom right of the screen"""

    def __init__(self, canvas):
        """Creates button textures and places them on the screen"""

        self.canvas = canvas
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()
        self.padding = 10
        self.is_volatile_open = False  # True when some keys are prohibited
        self.is_menu_open = False  # True when an in-game menu is open
        self.isMainMenuOpen = False
        self.settings_click = False  # True when a settings button is clicked
        self.is_pause = False
        self.pause_click = False  # True when a pause button is clicked

        # settings button
        self.settings1 = tk.PhotoImage(file='textures/settings1.png')
        self.settings2 = tk.PhotoImage(file='textures/settings2.png')
        self.settings_id = self.canvas.create_image(
                                    self.padding,
                                    self.canvas_height - self.padding,
                                    anchor='sw',
                                    image=self.settings1,
                                    activeimage=self.settings2,
                                    state='hidden'
                                )
        self.canvas.tag_bind(
                                    self.settings_id,
                                    '<Button-1>',
                                    lambda e: self.menu()
                                )
        self.canvas.bind_all('<Escape>', lambda e: self.menu())

        # pause button
        self.pause1 = tk.PhotoImage(file='textures/pause1.png')
        self.pause2 = tk.PhotoImage(file='textures/pause2.png')
        self.nopause1 = tk.PhotoImage(file='textures/no_pause1.png')
        self.nopause2 = tk.PhotoImage(file='textures/no_pause2.png')
        self.pause_id = self.canvas.create_image(
                                    self.padding + self.settings1.width(),
                                    self.canvas_height - self.padding,
                                    anchor='sw',
                                    image=self.pause1,
                                    activeimage=self.pause2,
                                    state='hidden'
                                )
        self.canvas.tag_bind(
                                    self.pause_id,
                                    '<Button-1>',
                                    lambda e: self.change_pause()
                                )
        self.canvas.bind_all('<p>', lambda e: self.change_pause())
        self.canvas.pack()

    def menu(cls):
        """Runs when an <Esc> or a settings button is clicked"""

        if(not cls.is_volatile_open):
            cls.settings_click = True

    def change_pause(cls):
        """Runs when a <p> or a pause button is clicked"""

        if(not cls.is_volatile_open):
            cls.pause_click = True
