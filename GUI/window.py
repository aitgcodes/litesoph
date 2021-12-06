#mport the library tkinter
from tkinter import *
  
# Create a GUI app
app = Tk()
  
# Give a title to your app
app.title("LITESOPH")
  
# Constructing the first frame, frame1
frame1 = LabelFrame(app, text="Frame1", bg="gray",
                    fg="black", padx=291, pady=150)
  
# Displaying the frame1 in row 0 and column 0
frame1.grid(row=0, column=0)
  
# Constructing the button b1 in frame1
b1 = Button(frame1, text="Preprocessing")
  
# Displaying the button b1
b1.pack()
  
# Constructing the second frame, frame2
frame2 = LabelFrame(app, text="Frame2", bg="gray", padx=320, pady=149)
  
# Displaying the frame2 in row 0 and column 1
frame2.grid(row=0, column=30)
  
# Constructing the button in frame2
b2 = Button(frame2, text="ESMD")
  
# Displaying the button b2
b2.pack()
  
frame3 = LabelFrame(app, text="Frame3", bg="gray",
                    fg="black", padx=288, pady=141)

# Displaying the frame1 in row 0 and column 0
frame3.grid(row=50, column=0)

# Constructing the button b1 in frame1
b3 = Button(frame3, text="Postprocessing")

# Displaying the button b1
b3.pack()

frame4 = LabelFrame(app, text="Frame4", bg="gray",
                    fg="black", padx=307, pady=142)

# Displaying the frame1 in row 0 and column 0
frame4.grid(row=50, column=30)

# Constructing the button b1 in frame1
b4 = Button(frame4, text="Visualization")

# Displaying the button b1
b4.pack()

# Make the loop for displaying app
app.mainloop()
