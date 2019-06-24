import os, sys, time, pyglet, keyboard
import tkinter as tk  # python 3
from tkinter import font as tkfont  # python 3

pyglet.lib.load_library('avbin')
pyglet.have_avbin = True


class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="left", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (ConfigPage, TimerPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("ConfigPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class ConfigPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        addboxButton = tk.Button(self, text='<Add Timer>', command=self.addBox)
        addboxButton.pack()
        startButton = tk.Button(self, text='<Start Timer>', command=self.changePage)
        startButton.pack()
        self.errorLable = tk.Label(self, fg='red', text="Error")
        if all_entries == []:
            print("adding")
            self.addBox()

    def addBox(self):

        boxFrame = tk.Frame(root)
        boxFrame.pack()

        tk.Label(boxFrame, text='Minutes').grid(row=0, column=0)

        ent1 = tk.Entry(boxFrame)
        ent1.grid(row=1, column=0)

        tk.Label(boxFrame, text='Seconds').grid(row=0, column=1)

        ent2 = tk.Entry(boxFrame)
        ent2.grid(row=1, column=1)

        tk.Label(boxFrame, text='Sound').grid(row=0, column=2)

        ent3 = tk.Entry(boxFrame)
        ent3.grid(row=1, column=2)

        all_entries.append((ent1, ent2, ent3))

    def showEntries(self):
        all_errors = []
        self.clear = True
        for number, (ent1, ent2, ent3) in enumerate(all_entries):
            entry1 = int(ent1.get())
            if not entry1 == "" and entry1 >= 0:
                print(number, "Entry1= ", entry1)
                ent1.config(highlightcolor="black", highlightthickness=2)
                min = False
            else:
                ent1.config(highlightcolor="red", highlightthickness=2)
                min = True

            entry2 = int(ent2.get())
            if not entry2 == "" and 0 <= entry2 <= 60:
                print(number, "Entry2= ", entry2)
                ent2.config(highlightcolor="black", highlightthickness=2)
                sec = False
            else:
                ent2.config(highlightcolor="red", highlightthickness=2)
                sec = True

            entry3 = ent3.get()
            if not entry3 == "" and os.path.isfile(entry3):
                print(number, "Entry3= ", entry3)
                ent3.config(highlightcolor="black", highlightthickness=2)
                snd = False
            else:
                ent3.config(highlightcolor="red", highlightthickness=2)
                snd = True
            all_errors.append((number, min, sec, snd))
        errorText = "There are errors in:"
        for num, (number, min, sec, snd) in enumerate(all_errors):
            if min or sec or snd:
                self.clear = False
                errorText = errorText + "\n\rtimer number {timer} ".format(timer=number)
                if min:
                    errorText = errorText + "minutes"
                    if sec:
                        errorText = errorText + ", seconds"
                    if snd:
                        errorText = errorText + ", sound"
                elif sec:
                    errorText = errorText + "seconds"
                    if snd:
                        errorText = errorText + ", sound"
                elif snd:
                    errorText = errorText + "sound"
                self.errorLable.pack()
                self.errorLable.config(text=errorText)
                print(errorText)
            if errorText == "There are errors in:":
                self.clear = True
                self.errorLable.pack_forget()

    def changePage(self):
        self.showEntries()
        if self.clear == True:
            self.controller.show_frame("TimerPage")


class TimerPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.label = tk.Label(self, text="00:00", font=('Verdana', 50, 'bold'))
        self.label.pack(side="top", fill="x", pady=10)
        self.startButton = tk.Button(self, text="Start timer(s)", command=self.startTimer)
        self.startButton.pack()
        self.looper = False
        self.loopCheck = tk.Checkbutton(self, text="Loop the timer(s)", command=self.loopSet)
        self.loopCheck.pack()
        self.button = tk.Button(self, text="Go to the config page", command=lambda: controller.show_frame("ConfigPage"))
        self.button.pack()
        self.endTimer = tk.Label(self, text="To stop the timer hold 'Q'", font=('Verdana', 20))
        self.endTimer.pack()

    def loopSet(self):
        if self.looper:
            self.looper = False
        else:
            self.looper = True

    def startTimer(self):
        self.startButton.pack_forget()
        self.loopCheck.pack_forget()
        self.button.pack_forget()
        while self.looper:
            for number, (ent1, ent2, ent3) in enumerate(all_entries):
                if ent1.get and ent2.get() and ent3.get():
                    self.runTimer(ent1.get(), ent2.get(), ent3.get())
        if not self.looper:
            for number, (ent1, ent2, ent3) in enumerate(all_entries):
                if ent1.get and ent2.get() and ent3.get():
                    self.runTimer(ent1.get(), ent2.get(), ent3.get())
        self.label.config(text="00 : 00", font=('Verdana', 50, 'bold'))
        self.endTimer.pack_forget()
        self.startButton.pack()
        self.loopCheck.pack()
        self.button.pack()
        self.endTimer.pack()

    def runTimer(self, min, sec, sound):
        time_start = time.time()
        if int(sec) > 0:
            time_start -= 60
            time_start += int(sec)
        seconds = int(sec)
        minutes = int(min)
        timer = True
        while timer:
            if keyboard.is_pressed('q'):
                timer = False
                self.looper = False
                self.label.config(text="00 : 00", font=('Verdana', 50, 'bold'))
            sys.stdout.write("\r{minutes} Minutes {seconds} Seconds".format(minutes=minutes, seconds=seconds))
            sys.stdout.flush()
            if minutes <= 9:
                if seconds <= 9:
                    self.label.config(text="\r0{minutes} : 0{seconds}".format(minutes=minutes, seconds=seconds), font=('Verdana', 100, 'bold'))
                else:
                    self.label.config(text="\r0{minutes} : {seconds}".format(minutes=minutes, seconds=seconds), font=('Verdana', 100, 'bold'))
            else:
                if seconds <= 9:
                    self.label.config(text="\r{minutes} : 0{seconds}".format(minutes=minutes, seconds=seconds), font=('Verdana', 100, 'bold'))
                else:
                    self.label.config(text="\r{minutes} : {seconds}".format(minutes=minutes, seconds=seconds), font=('Verdana', 100, 'bold'))
            self.update_idletasks()
            if seconds < 0:
                minutes -= 1
                time_start = time.time()
            time.sleep(1)
            seconds = 60 - int(time.time() - time_start)
            if minutes <= 0 and seconds < 0:
                player = pyglet.media.Player()
                music_file = pyglet.media.load(sound)
                player.queue(music_file)
                player.play()
                time.sleep(1)
                break


class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master = master
        master.geometry("{0}x{1}".format(int(master.winfo_screenwidth() / 2), int(master.winfo_screenheight() / 2)))


all_entries = []
all_errors = []
root = tk.Tk()
root.title("Configurator")

if __name__ == "__main__":
    app = SampleApp()
    app.title("Timer")
    FullScreenApp(app)
    app.mainloop()
