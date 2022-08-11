import tkinter as tk


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

# testing ...
# if __name__ == '__main__':
#     root = tk.Tk()
#     btn1 = tk.Button(root, text="button 1")
#     btn1.pack(padx=10, pady=5)
#     button1_ttp = CreateToolTip(btn1, \
#    'Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, '
#    'consectetur, adipisci velit. Neque porro quisquam est qui dolorem ipsum '
#    'quia dolor sit amet, consectetur, adipisci velit. Neque porro quisquam '
#    'est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit.')

#     btn2 = tk.Button(root, text="button 2")
#     btn2.pack(padx=10, pady=5)
#     button2_ttp = CreateToolTip(btn2, \
#     "Hello, this is hover tooltip sample"
#     "Hello, this is hover tooltip sample"
#     "Hello, this is hover tooltip sample")
#     root.mainloop()

# dictionary for keyword explanation

hoverdict={
    
            "geometryfile": 'Please upload the geometry file i.e xyz coordinate file using "SELECT" button',
             'engine_source_doc':  'select the engine source',
             'jobtype_doc':'Jobtype description label',
             'subtask_doc':'subtask description label',

             
                }




