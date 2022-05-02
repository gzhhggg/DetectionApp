import cv2
import tkinter as tk
from PIL import Image, ImageTk
import tkinter.ttk as ttk

# define valiable
width = 640
height = 480

class SsFrame(ttk.LabelFrame):
    def __init__(self, master=None, text=None):
        super(SsFrame, self).__init__(master, text=text)
        self.start_b = ttk.Button(self, text="start", command=master.start_cap)
        self.stop_b = ttk.Button(self, text="stop", command=master.stop_cap)

        self.start_b.grid(row=0, column=0)
        self.stop_b.grid(row=0, column=1)

class App(tk.Tk):
    def __init__(self):
        super(App, self).__init__()
        # root configuration
        self.title("VideoCapture")
        self.resizable(width=False, height=False)

        # valiables configuration
        self.capture_flag = False

        # canvas configuration
        self.canvas = tk.Canvas(self, width=width, height=height)
        self.canvas.create_rectangle(0, 0, 640, 480, fill="black")
        self.canvas.pack()

        # ss_frame configuration
        self.ss_frame = SsFrame(self, text="start_stop_buttons")
        self.ss_frame.pack()

    def start_cap(self):
        if not self.capture_flag:
            self.capture_flag = True
            self.capture = cv2.VideoCapture(0)
            self.after_id = self.after(10, self.update_cap)

    def update_cap(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.resize(frame, (width, height))
            self.tk_frame = ImageTk.PhotoImage(
                Image.fromarray(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                )
            )
            self.canvas.create_image(0, 0, image=self.tk_frame, anchor='nw')
        else:
            self.canvas.create_text(width/2, height/2, text="None")

        self.after_id = self.after(10, self.update_cap)

    def stop_cap(self):
        self.after_cancel(self.after_id)
        self.capture.release()
        cv2.destroyAllWindows()
        self.capture_flag = False

    def start(self):
        self.mainloop()


if __name__ == "__main__":

    app = App()
    app.start()