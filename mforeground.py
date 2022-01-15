import tkinter as tk


class Foreground:
    """The counters on the top of the screen"""

    def __init__(self, canvas):
        """Creates the counters"""

        self.canvas = canvas
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()
        self.padding = 10  # distance from the border of the screen
        self.is_pause = False

        # distance
        self.dist_freq = 200  # widget update frequency
        self.dist = 0
        self.dist_str = str(self.dist)
        self.dist_id = self.canvas.create_text(
                                    self.padding,
                                    self.padding,
                                    anchor='nw',
                                    text=self.dist_str.zfill(7),
                                    fill='white',
                                    font=('FreeMono', 20, 'bold'),
                                    state='hidden'
                                )

        # scanner progress
        self.scan_freq = 100 // 6  # widget update frequency
        self.scanner_progr = 0
        self.scanner_str = str(self.scanner_progr) + '%'
        self.scanner_id = self.canvas.create_text(
                                    self.canvas_width - self.padding,
                                    self.padding,
                                    anchor='ne',
                                    text=self.scanner_str,
                                    fill='white',
                                    font=('FreeMono', 20, 'bold'),
                                    state='hidden'
                                )

        # lives remaining
        self.lives = 3  # current number of lives
        self.max_lives = 5  # maximum number of lives
        self.heart_img1 = tk.PhotoImage(file='textures/heart1.png')
        self.heart_img2 = tk.PhotoImage(file='textures/heart2.png')
        self.heart_width = self.heart_img1.width()
        self.hearts = []  # list of heart textures
        self.draw_hearts()
        self.canvas.pack()

    def draw_distance(cls):
        """Updates the distance counter"""

        if(not cls.is_pause):
            cls.dist += 1
            cls.dist_str = str(cls.dist)
            cls.canvas.itemconfig(cls.dist_id, text=cls.dist_str.zfill(7))
            cls.canvas.pack()
        cls.canvas.after(cls.dist_freq, cls.draw_distance)

    def draw_scanner(cls):
        """Updates the scanner progress counter"""

        if(not cls.is_pause):
            cls.scanner_str = ('%.2f%%' % cls.scanner_progr)
            cls.canvas.itemconfig(cls.scanner_id, text=cls.scanner_str)
            cls.canvas.pack()
        cls.canvas.after(cls.scan_freq, cls.draw_scanner)

    def draw_hearts(cls):
        """Creates a list of lives remaining"""

        start_point = (cls.canvas_width - cls.max_lives * cls.heart_width) // 2
        # 'full' lives
        for i in range(cls.lives):
            cls.hearts.append(cls.canvas.create_image(
                                    start_point,
                                    cls.padding * 2,
                                    anchor='nw',
                                    image=cls.heart_img1,
                                    state='hidden'
                                ))
            start_point += cls.heart_width
        # 'empty' lives
        for i in range(cls.max_lives - cls.lives):
            cls.hearts.append(cls.canvas.create_image(
                                    start_point,
                                    cls.padding * 2,
                                    anchor='nw',
                                    image=cls.heart_img2,
                                    state='hidden'
                                ))
            start_point += cls.heart_width

    def heart_less(cls):
        """Updates the list of hearts if a heart is lost"""

        cls.lives -= 1
        cls.canvas.itemconfig(cls.hearts[cls.lives], image=cls.heart_img2)
        cls.canvas.pack()

    def heart_more(cls):
        """Updates the list of hearts if a heart is gained"""

        cls.canvas.itemconfig(cls.hearts[cls.lives], image=cls.heart_img1)
        cls.lives += 1
        cls.canvas.pack()
