import tkinter as tk
import tkinter.filedialog as fd
from tkinter import messagebox, ttk
import numpy as np
from matplotlib import pyplot as plt, animation
import matplotlib.image as mpimg
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
import os,subprocess,shutil
from pathlib import Path 
from litesoph.common.utils import get_new_directory
from litesoph.common.job_submit import execute_cmd_local,execute_cmd_remote
from litesoph.gui.gui import GUIAPP
from tkinter import *

def create_directory(directory):
        absdir = os.path.abspath(directory)
        if absdir != Path.cwd and not Path.is_dir(directory):
            os.makedirs(directory)

def python_list_to_tcl_list(py_list):
    """function to convert python list to tcl list format

    Args:
        py_list (list): python list

    Returns:
        _type_: tcl list
    """        
    if type(py_list) == list:
        out_str = "{ "
        for item in py_list:
            out_str += python_list_to_tcl_list(item)
        out_str += "} "
        return out_str
    else:
        out_str = str(py_list) + " "
        for c in ["\\", "{", "}", "[", "]", "$"]:
            out_str = out_str.replace(c, "\\" + c)
        return out_str

class CollapsibleFrame(ttk.Frame):
	"""
	-----USAGE-----
	collapsiblePane = CollapsiblePane(parent,
						expanded_text =[string],
						collapsed_text =[string])

	collapsiblePane.pack()
	button = Button(collapsiblePane.frame).pack()
	"""

	def __init__(self, parent, expanded_text ="Collapse <<",
							collapsed_text ="Expand >>"):

		ttk.Frame.__init__(self, parent)

		# These are the class variable
		# see a underscore in expanded_text and _collapsed_text
		# this means these are private to class
		self.parent = parent
		self._expanded_text = expanded_text
		self._collapsed_text = collapsed_text

		# Here weight implies that it can grow it's
		# size if extra space is available
		# default weight is 0
		# self.columnconfigure(1, weight = 1)

		# Tkinter variable storing integer value
		self._variable = tk.IntVar()

		# Checkbutton is created but will behave as Button
		# cause in style, Button is passed
		# main reason to do this is Button do not support
		# variable option but checkbutton do
		self._button = ttk.Checkbutton(self, variable = self._variable,
							command = self._activate)
		self._button.grid(row = 0, column = 0)

		# This will create a separator
		# A separator is a line, we can also set thickness
		self._separator = ttk.Separator(self, orient ="horizontal")
		self._separator.grid(row = 0, column = 1, sticky ="we")

		self.frame = ttk.Frame(self)

		# This will call activate function of class
		self._activate()

	def _activate(self):
		if not self._variable.get():

			# As soon as button is pressed it removes this widget
			# but is not destroyed means can be displayed again
			self.frame.grid_forget()

			# This will change the text of the checkbutton
			self._button.configure(text = self._collapsed_text)

		elif self._variable.get():
			# increasing the frame area so new widgets
			# could reside in this container
			self.frame.grid(row = 1, column = 0, columnspan = 2)
			self._button.configure(text = self._expanded_text)

	def toggle(self):
		"""Switches the label frame to the opposite state."""
		self._variable.set(not self._variable.get())
		self._activate()
            
class GuiAppTemplate(tk.Toplevel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    # def __init__(self):
        # self.master =  tk.Tk()
        self.title("Litesoph Visualization Toolkit")
        
        # create the PanedWindow
        self.pane = tk.PanedWindow(self, orient='horizontal')        
        self.left_pane = tk.Frame(self.pane, width=150, height=400)        
        self.right_pane = tk.Frame(self.pane, width=200, height=400)
        self.pane.pack(fill=tk.BOTH, expand=1)
        self.pane.add(self.left_pane)
        self.pane.add(self.right_pane)
        self.pane.sash_place(0, 400, 0) # set the initial size of the panes | position the sash at 100 pixels from the left
        self.pane.config(sashwidth=5, sashrelief=tk.SUNKEN)  # set the sash properties
        self.pane.bind('<Button-1>', self.adjust_panes)

        # create textbox for editing script
        self.text_box = tk.Text(self.right_pane)

        # create canvas for plotting
        self.fig = plt.figure(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_pane)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas,self.right_pane)
        toolbar.update()
        toolbar.pack()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # create generate plot button
        self.generate_button = tk.Button(self.left_pane, text="Generate Plot", command=self.generate_plot)
        self.generate_button.pack(side=tk.BOTTOM, pady=10)

        self.plot_type_frame = tk.LabelFrame(self.left_pane, text="Plot Type")
        self.plot_type_frame.pack(fill=tk.X)
        self.plot_type_var = tk.StringVar(value="Line Plot")
        select_plot_label = tk.Label(self.plot_type_frame, text= "Select Plot")
        select_plot_label.pack(side=tk.LEFT)
        plot_types=['line_plot', 'contour_plot','cube']
        self.combobox = ttk.Combobox(self.plot_type_frame, values=plot_types, textvariable=self.plot_type_var)
        self.combobox.pack(side=tk.LEFT)
        self.combobox.set("select a plot")

        # self.combobox.current()
        self.combobox.bind("<<ComboboxSelected>>",self.on_plot_type_selected)  

        self.load_data_frame = tk.LabelFrame(self.left_pane, text="Load Data")
        self.load_data_frame.pack(fill=tk.X)
        
        self.graph_params_frame = tk.LabelFrame(self.left_pane, text="Graph Parameters")
        self.graph_params_frame.pack(fill=tk.X)

        # self.cf1_graph_params_frame = CollapsibleFrame(self.graph_params_frame, label="Axes")
        # self.cf1_graph_params_frame.grid(row=0, column=0, sticky="nsew")

        self.cf2_graph_params_frame = CollapsibleFrame(self.graph_params_frame,'-Details', '+Details')
        self.cf2_graph_params_frame.grid(row=1, column=0, sticky="nsew")

        self.graph_props_frame = tk.LabelFrame(self.left_pane, text="Graph Properties")
        self.graph_props_frame.pack(fill=tk.X)

        cf3 = CollapsibleFrame(self.graph_props_frame, '-Font', '+Font')
        cf3.grid(row=0, column=0, sticky="nsew")

    
    def toggle_canvas(self):
        if self.canvas.get_tk_widget().winfo_ismapped():
            # if the text box is currently displayed, switch to the canvas
            self.text_box.pack_forget()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        else:
            pass
                
    def toggle_textbox(self):
        if self.canvas.get_tk_widget().winfo_ismapped():
            self.canvas.get_tk_widget().pack_forget()
            # self.text_box.pack(side=tk.TOP, pady=5)
            self.text_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        else:
            pass
                    
    def toggle_textbox_canvas(self):
        if self.canvas.get_tk_widget().winfo_ismapped():
            # if the canvas is currently displayed, switch to the text box
            self.canvas.get_tk_widget().pack_forget()
            self.text_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            # self.toggle_button.config(text='Canvas')
        else:
            # if the text box is currently displayed, switch to the canvas
            self.text_box.pack_forget()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            # self.toggle_button.config(text='Text Box')
                
    def adjust_panes(self,event):
        """function to adjust the size of the panes"""
        self.pane.sash_place(0, event.x, event.y)

    def run(self):
        self.master.mainloop()

class CommonGraphParam(GuiAppTemplate):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


        self.project_dir='/home/anandsahu/myproject/aitg/ls/ls-testing-env/Visualization/'

    def common_graph_params(self):    
        self.title_var = tk.StringVar(value="Title")
        self.title_label = tk.Label(self.cf2_graph_params_frame.frame, text="Title:")
        self.title_entry = tk.Entry(self.cf2_graph_params_frame.frame, textvariable=self.title_var)
        self.title_label.grid(row=2, column=0, sticky=tk.E)
        self.title_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.x_axis_name_var = tk.StringVar(value="X label")
        self.x_axis_name_label = tk.Label(self.cf2_graph_params_frame.frame, text="X label:")
        self.x_axis_name_entry = tk.Entry(self.cf2_graph_params_frame.frame, textvariable=self.x_axis_name_var)
        self.x_axis_name_label.grid(row=5, column=0, sticky=tk.E)
        self.x_axis_name_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

        self.y_axis_name_var = tk.StringVar(value="Y label")
        self.y_axis_name_label = tk.Label(self.cf2_graph_params_frame.frame, text="Y label:")
        self.y_axis_name_entry = tk.Entry(self.cf2_graph_params_frame.frame, textvariable=self.y_axis_name_var)
        self.y_axis_name_label.grid(row=6, column=0, sticky=tk.E)
        self.y_axis_name_entry.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
    
    def common_graph_props(self):    
        # self.title_var = tk.StringVar(value="Title")
        # self.title_label = tk.Label(self.cf2_graph_params_frame.frame, text="Title:")
        # self.title_entry = tk.Entry(self.cf2_graph_params_frame.frame, textvariable=self.title_var)
        # self.title_label.grid(row=2, column=0, sticky=tk.E)
        # self.title_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # self.x_axis_name_var = tk.StringVar(value="X label")
        # self.x_axis_name_label = tk.Label(self.cf2_graph_params_frame.frame, text="X label:")
        # self.x_axis_name_entry = tk.Entry(self.cf2_graph_params_frame.frame, textvariable=self.x_axis_name_var)
        # self.x_axis_name_label.grid(row=5, column=0, sticky=tk.E)
        # self.x_axis_name_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

        # self.y_axis_name_var = tk.StringVar(value="Y label")
        # self.y_axis_name_label = tk.Label(self.cf2_graph_params_frame.frame, text="Y label:")
        # self.y_axis_name_entry = tk.Entry(self.cf2_graph_params_frame.frame, textvariable=self.y_axis_name_var)
        # self.y_axis_name_label.grid(row=6, column=0, sticky=tk.E)
        # self.y_axis_name_entry.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        pass
    
    def load_files(self):        
        files = fd.askopenfilename(title="Select File(s)",
                                            multiple=True,
                                            filetypes=[('all files', '.*'),
                                                        ('text files', '.txt'),
                                                        ('image files', ('.png', '.jpg')),
                                                        ('cube files', '.cube'),
                                                        ('data files', '.dat')
                                                        ])
        
        return files
        
class LinePlot(CommonGraphParam):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


    def _on_select_line_plot(self):
    
        self.load_data_button = tk.Button(self.load_data_frame, text="Load Data", command=lambda:self._on_load_lineplot_data())
        self.load_data_button.pack(side=tk.LEFT)
    
        self.x_axis_var = tk.StringVar(value="X")
        self.y_axis_var = tk.StringVar(value="Y")

        self.cf1_graph_params_frame = CollapsibleFrame(self.load_data_frame, '-Axes', '+Axes')
        self.cf1_graph_params_frame.pack(side=tk.LEFT)
        
        self.x_axis_label = tk.Label( self.cf1_graph_params_frame.frame, text="X Axis:")
        self.y_axis_label = tk.Label( self.cf1_graph_params_frame.frame, text="Y Axis:")
        
        self.x_axis_entry = tk.Entry( self.cf1_graph_params_frame.frame, textvariable=self.x_axis_var)
        self.y_axis_entry = tk.Entry( self.cf1_graph_params_frame.frame, textvariable=self.y_axis_var)

        self.x_var = tk.StringVar()
        self.x_var.set("X Axis")
        self.x_dropdown = tk.OptionMenu( self.cf1_graph_params_frame.frame, self.x_var, "")
        self.x_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.y_var = tk.StringVar()
        self.y_var.set("Y Axis")
        self.y_dropdown = tk.OptionMenu( self.cf1_graph_params_frame.frame, self.y_var, "")
        self.y_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.x_axis_label.grid(row=0, column=0, sticky=tk.E)
        self.y_axis_label.grid(row=1, column=0, sticky=tk.E)
    
    def _on_load_lineplot_data(self):
        # self.file_path = fd.askopenfilename(title="Select Data File")
        self.file_path = self.load_files()
        self.file_path=self.file_path[0]

        if self.file_path:
            data = np.loadtxt(self.file_path, comments="#")
            self.columns = [f"Column {i+1}" for i in range(data.shape[1])]
            self.x_dropdown["menu"].delete(0, tk.END)
            self.y_dropdown["menu"].delete(0, tk.END)
            for column in   self.columns:
                self.x_dropdown["menu"].add_command(label=column, command=lambda value=column: self.x_var.set(value))
                self.y_dropdown["menu"].add_command(label=column, command=lambda value=column: self.y_var.set(value))
        
    def _on_generate_line_plot(self):
        x_col = self.x_var.get()
        y_col = self.y_var.get()
        title = self.title_entry.get()

        # Generate new plot
        data = np.loadtxt(self.file_path, comments="#")
        x_data = data[:,  self.columns.index(x_col)]
        y_data = data[:,  self.columns.index(y_col)]

        # get plot parameters
        title = self.title_var.get()
        x_axis_name_var = self.x_axis_name_var.get()
        y_axis_name_var = self.y_axis_name_var.get()

        x_label = self.x_axis_entry.get()
        y_label = self.y_axis_entry.get()

        # create line plot
        plt.cla()
        plt.plot(x_data, y_data)
        plt.xlabel(x_axis_name_var)
        plt.ylabel(y_axis_name_var)
        plt.title(title)
        self.canvas.draw()

class ContourPlot(CommonGraphParam):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    
    def _on_select_contour_plot(self):

        self.load_X_data_button = tk.Button(self.load_data_frame, text="Load X Data", command=self.load_X_data)
        self.load_X_data_button.pack(side=tk.LEFT)
        self.load_Y_data_button = tk.Button(self.load_data_frame, text="Load Y Data", command=self.load_Y_data)
        self.load_Y_data_button.pack(side=tk.LEFT)
        self.load_Z_data_button = tk.Button(self.load_data_frame, text="Load Z Data", command=self.load_Z_data)
        self.load_Z_data_button.pack(side=tk.LEFT)

    def load_X_data(self):
        self.file_path = fd.askopenfilename(title="Select Data File")
        if self.file_path:
            self.contour_X_data = np.loadtxt(self.file_path, comments="#")
            
    def load_Y_data(self):
        self.file_path = fd.askopenfilename(title="Select Data File")
        if self.file_path:
            self.contour_Y_data = np.loadtxt(self.file_path, comments="#")
            
    def load_Z_data(self):
        self.file_path = fd.askopenfilename(title="Select Data File")
        if self.file_path:
            self.contour_Z_data = np.loadtxt(self.file_path, comments="#")
            
    def _on_generate_contour_plot(self):
        
        title = self.title_var.get()
        x_axis_name_var = self.x_axis_name_var.get()
        y_axis_name_var = self.y_axis_name_var.get()
        
        plt.cla()
        plt.xlabel(x_axis_name_var)
        plt.ylabel(y_axis_name_var)
        plt.title(title)
        plt.contourf( self.contour_X_data, self.contour_Y_data, self.contour_Z_data)
        
        self.canvas.draw()

class CubeFilePlot(CommonGraphParam):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        self.traj_dir=Path(self.project_dir) / 'ls_traj_anim'
        print(self.traj_dir)

    
    def _on_select_cube_file(self):

        self.load_cube_data_button = tk.Button(self.load_data_frame, text="Load Cube File(s)", command=self.load_cube_file)
        self.load_cube_data_button.pack(side=tk.LEFT)
        
        cf3 = CollapsibleFrame(self.graph_props_frame, '-Params', '+Params')
        cf3.grid(row=0, column=0, sticky="nsew")
        
        self.render_script_button = tk.Button(self.graph_props_frame, text="Render Script", command=self._on_generate_vmd_script)
        self.render_script_button.grid(row=1, column=0, sticky="nsew")

        self.edit_save_script_button = tk.Button(self.graph_props_frame, text="Save Script", command=self._on_edit_save_render_script)
        self.edit_save_script_button.grid(row=1, column=1, sticky="nsew")

        engine_types=['default','blender']
        self.render_engine_type_var = tk.StringVar()

        self.select_render_engine = ttk.Combobox(self.graph_props_frame,state = "readonly", values=engine_types, textvariable=self.render_engine_type_var)
        self.select_render_engine.grid(row=2, column=0, sticky="nsew")
        self.select_render_engine.set("select render engine")
        self.select_render_engine.current(0)

        self.render_button = tk.Button(self.graph_props_frame, text="Render", command=self._on_render_cube_movie)
        self.render_button.grid(row=2, column=1, sticky="nsew")

    def load_cube_file(self):
        cube_files = fd.askopenfilename(title="Select File(s)",
                                            multiple=True,
                                            filetypes=[('all files', '.*'),
                                                        ('text files', '.txt'),
                                                        ('image files', ('.png', '.jpg')),
                                                        ('cube files', '.cube'),
                                                        ('data files', '.dat')
                                                        ])
        self.cube_files=list(cube_files)
    
    def rewrite_file(self,file,find_text, replace_text):
        import sys
        import fileinput

        for i, line in enumerate(fileinput.input(file, inplace=1)):
            sys.stdout.write(line.replace(find_text, replace_text)) 

    def _on_generate_vmd_script(self):
        
        vmd_script_template='/home/anandsahu/myproject/aitg/ls/ls-code/litesoph/visualization/vmd_script_template.tcl'        
        # self.vmd_script='/home/anandsahu/myproject/aitg/ls/ls-testing-env/Visualization/vmd_test_lsapp.tcl'        

        # self.traj_dir=Path(self.project_dir) / 'ls_traj_anim'
        self.traj_dir=get_new_directory(self.traj_dir)

        if not self.traj_dir.exists():
            create_directory(self.traj_dir)  
            self.vmd_script= self.traj_dir/'vmd_test_lsapp.tcl'

            if os.path.isfile(self.vmd_script):
                os.remove(self.vmd_script)       
            shutil.copyfile(vmd_script_template,self.vmd_script)
            
            tcl_list=python_list_to_tcl_list(self.cube_files)
            self.rewrite_file(self.vmd_script,'[TCL_CUBE_FILES]', tcl_list)
        
        self._on_view_render_script()
        self.toggle_textbox_canvas()
    
    def _on_edit_save_render_script(self):
        
        text_file = open(self.vmd_script, "w")
        text_file.write(self.text_box.get(1.0, END))
        text_file.close()   
        self._on_view_render_script()

    def _on_view_render_script(self):
        # self.toggle_textbox_canvas()
        # self.toggle_textbox()
        
        text_file = open(self.vmd_script, "r")
        content = text_file.read()
        self.text_box.insert(END, content)
        text_file.close()
    
    def _on_render_cube_movie(self):
        self._on_generate_vmd_script()
        cmd=f'vmd -dispdev none -e {self.vmd_script}'
        result=execute_cmd_local(cmd,self.traj_dir)
        error=result[cmd]['error']    
        message=result[cmd]['output']   

        # cmd_create_gif='convert *.png output.gif'
        # result=execute_cmd_local(cmd_create_gif,project_dir)
        # error=result[cmd_create_gif]['error']    
        # message=result[cmd_create_gif]['output']  

    def _on_generate_cube_plot_blender(self):
        import bpy 
        
        ims=[]
        list_imgs = list(Path(self.traj_dir).glob('*.png'))
        file_path=list_imgs

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':

                bpy.context.scene.sequence_editor_create()

                movie = bpy.context.scene.sequence_editor.sequences.new_image(
                            name="photos", filepath=file_path[0],
                            channel=1, frame_start=1)

                for o in file_path:
                    movie.elements.append(o)
                bpy.context.scene.render.fps = 1
                bpy.context.scene.frame_end =  len(file_path)
                bpy.context.scene.render.ffmpeg.format = 'MPEG4'
                bpy.ops.render.render(animation=True)
                
    def _on_generate_cube_plot_matplotlib(self):
        
        ims=[]
        list_imgs = list(Path(self.traj_dir).glob('*.png'))
        
        for i in range(len(list_imgs)):           
            img = mpimg.imread(list_imgs[i])
            im = plt.imshow(img)
            if i == 0:
                plt.imshow(img)  # show an initial one first
            ims.append([im])
        ani = animation.ArtistAnimation(self.fig, ims, interval=50, blit=True,repeat_delay=100)
        self.canvas.draw()
    
    def _on_generate_movie(self):
        self.toggle_textbox_canvas()
        engine_type=  self.select_render_engine.get()

        if engine_type=='default':
            print(engine_type)
            self._on_generate_cube_plot_matplotlib()
        elif engine_type=='blender':
            print(engine_type)
            self._on_generate_cube_plot_blender()

class LSVizApp(LinePlot,ContourPlot,CubeFilePlot):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def destroy_frame_elements(self,list_of_frames):    
        for frame in list_of_frames:
            for widget in frame.winfo_children():
                widget.destroy()
        
    def on_plot_type_selected(self, event):
        self.plot_type = self.plot_type_var.get()
        list_of_frames=[self.load_data_frame]
        self.destroy_frame_elements(list_of_frames)
        
        if self.plot_type=="line_plot":
            self.common_graph_params()
            self._on_select_line_plot()

        elif self.plot_type=="contour_plot":
            self.common_graph_params()
            self._on_select_contour_plot()
        
        elif self.plot_type=="cube":
            self._on_select_cube_file()

    def generate_plot(self):
        # self.toggle_canvas()
        self.plot_type = self.plot_type_var.get()
        if self.plot_type=="line_plot":
            self._on_generate_line_plot()
        
        elif self.plot_type=="contour_plot":
            self._on_generate_contour_plot()
        
        elif self.plot_type=="cube":
            # self._on_generate_cube_plot()
            self._on_generate_movie()

        self.canvas.draw()

# def Run_ls_viz():
#     app=LSVizApp()
#     app.run()

# if __name__ == '__main__':
#     app=LSVizApp()
#     app.run()
#     Run_ls_viz()

# Run_ls_viz()