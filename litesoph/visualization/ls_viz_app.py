import tkinter as tk
import tkinter.filedialog as fd
from tkinter import messagebox, ttk
import numpy as np
from matplotlib import pyplot as plt, animation
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import os
from pathlib import Path 
from litesoph.common.utils import get_new_directory
from litesoph.common.job_submit import execute_cmd_local
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

		self.parent = parent
		self._expanded_text = expanded_text
		self._collapsed_text = collapsed_text
		self._variable = tk.IntVar()
		self._button = ttk.Checkbutton(self, variable = self._variable,command = self._activate)
		self._button.grid(row = 0, column = 0)
		self._separator = ttk.Separator(self, orient ="horizontal")
		self._separator.grid(row = 0, column = 1, sticky ="we")
		self.frame = ttk.Frame(self)
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

    def __init__(self, parent,project_dir, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)

        self.title("Litesoph Visualization Toolkit")

        self.project_dir=project_dir
        
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
        self.text_box = tk.Text(self.right_pane,font= ('Sans Serif', 13, 'bold'))

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
        plot_types=['line_plot','scatter_plot','histogram_plot', 'contour_plot','cube']
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

        # cf3 = CollapsibleFrame(self.graph_props_frame, '-Font', '+Font')
        # cf3.grid(row=0, column=0, sticky="nsew")

    def toggle_canvas(self):
        
        self.text_box.pack_forget()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                
    def toggle_textbox(self):
        if self.canvas.get_tk_widget().winfo_ismapped():
            self.canvas.get_tk_widget().pack_forget()
            self.text_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                    
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
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

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

        pass
    
    def load_files(self):        
        files = fd.askopenfilename(title="Select File(s)",
                                            multiple=True,
                                            initialdir=self.project_dir,
                                            filetypes=[('all files', '*'),
                                                        ('text files', '.txt'),
                                                        ('image files', ('.png', '.jpg')),
                                                        ('cube files', '.cube'),
                                                        ('data files', '.dat')
                                                        ])
        
        return files
        
class LinePlot(CommonGraphParam):
    
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
        
    def _on_generate_line_plot(self,plot_type):
        x_col = self.x_var.get()
        y_col = self.y_var.get()
        title = self.title_entry.get()
        
        # get plot parameters
        title = self.title_var.get()
        x_axis_name_var = self.x_axis_name_var.get()
        y_axis_name_var = self.y_axis_name_var.get()

        x_label = self.x_axis_entry.get()
        y_label = self.y_axis_entry.get()
        
        # Generate new plot
        data = np.loadtxt(self.file_path, comments="#")
        try:
            x_data = data[:,  self.columns.index(x_col)]
            y_data = data[:,  self.columns.index(y_col)]

            # create line plot
            plt.cla()
            plt.xlabel(x_axis_name_var)
            plt.ylabel(y_axis_name_var)
            plt.title(title)
        
            if plot_type=='line':
                plt.plot(x_data, y_data)
            elif plot_type=='scatter':
                plt.scatter(x_data, y_data)
            elif plot_type=='histogram':
                plt.hist2d(x_data, y_data)

            self.canvas.draw()

        except ValueError:
            messagebox.showinfo(title='Info', message="First Select the Axes") 

class ContourPlot(CommonGraphParam):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.colorBarPresent=False
    
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

        if self.colorBarPresent==True:
                plt.colorbar().remove()
        else:
            pass
        
        plt.cla()
        plt.xlabel(x_axis_name_var)
        plt.ylabel(y_axis_name_var)
        plt.title(title)
        plt.contourf( self.contour_X_data, self.contour_Y_data, self.contour_Z_data)
        plt.colorbar()
        self.colorBarPresent=True
        self.canvas.draw()

class CubeFilePlot(CommonGraphParam):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.traj_dir=Path(self.project_dir) /'plots'/ 'trajectory_animation'

    def _on_select_cube_file(self):

        self.load_cube_data_button = tk.Button(self.load_data_frame, text="Load Cube File(s)", command=self.load_cube_file)
        self.load_cube_data_button.pack(side=tk.LEFT)
        
        cf3 = CollapsibleFrame(self.graph_props_frame, '-Params', '+Params')
        cf3.grid(row=0, column=0, sticky="nsew")
        
        self.render_script_button = tk.Button(self.graph_props_frame, text="Render Script", command=self._on_generate_vmd_script)
        self.render_script_button.grid(row=1, column=0, sticky="nsew")

        self.edit_save_script_button = tk.Button(self.graph_props_frame, text="Save Script", command=self._on_edit_save_render_script)
        self.edit_save_script_button.grid(row=1, column=1, sticky="nsew")

        self.render_button = tk.Button(self.graph_props_frame, text="Render Frames", command=self._on_render_cube_frames)
        self.render_button.grid(row=1, column=2, sticky="nsew")

        engine_types=['default','blender']
        self.render_engine_type_var = tk.StringVar()

        self.select_render_engine = ttk.Combobox(self.graph_props_frame,state = "readonly", values=engine_types, textvariable=self.render_engine_type_var)
        self.select_render_engine.grid(row=2, column=0, sticky="nsew")
        self.select_render_engine.set("select render engine")
        self.select_render_engine.current(0)

        self.generate_movie_button = tk.Button(self.graph_props_frame, text="Generate Movie", command=self._on_generate_movie)
        self.generate_movie_button.grid(row=2, column=1, sticky="nsew")

        self.render_progress = tk.Label(self.graph_props_frame, bg='gray', fg='black')
        self.render_progress.grid(row=1, column=3, sticky="nsew")


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
    
    def vmd_template_script(self):
        script='''
            
        #!/usr/bin/tclsh

        menu main off
        axes location off
        lappend isoval 0.003 -0.003


        set cube_file_list [TCL_CUBE_FILES]
        
        set len_list [llength $cube_file_list] 

        for {set i 0} {$i < $len_list} {incr i} {
        

        mol new [lindex $cube_file_list  $i]

        if {$i == 0} {
            display projection orthographic
            light 0 on
            light 1 on
            light 2 on
            light 3 on
            color Display {Background} white
            color Name {H} gray
            rotate x by 0
            rotate y by 90
            rotate z by 90
            scale by 1.10
            translate by 0.0 0.0 0.0
            global viewpoints
            set viewpoints(0) [molinfo 0 get rotate_matrix]
            set viewpoints(1) [molinfo 0 get center_matrix]
            set viewpoints(2) [molinfo 0 get scale_matrix]
            set viewpoints(3) [molinfo 0 get global_matrix]
        }
    
        molinfo $i set center_matrix $viewpoints(1)
        molinfo $i set rotate_matrix $viewpoints(0)
        molinfo $i set scale_matrix $viewpoints(2)
        molinfo $i set global_matrix $viewpoints(3)
        mol delrep 0 $i
        mol representation CPK 1.2 0.0 100.0 100.0
        mol material HardPlastic
        mol addrep $i
        set iso 0
        foreach val $isoval {
        mol representation isosurface ${val} 0.0 0.0 0.0 1 1
        mol color ColorID $iso
        incr iso
        puts "iso ${iso}"
        mol addrep $i
        }

        # do not edit below this
        render Tachyon $i.dat
        /usr/local/lib/vmd/tachyon_LINUXAMD64 -aasamples 12 12 $i.dat -format TGA -res 1600 1200 -o $i.tga
        exec convert $i.tga $i.png
        mol delete $i

        }
        exit
            
        '''
        return script
    
    def rewrite_script(self,template_script,find_text, replace_text):        
        rescripted = template_script.replace(find_text, replace_text)
        return rescripted
    
    def _on_generate_vmd_script(self):
        self.toggle_textbox()
        self.text_box.delete("1.0",END)
                
        vmd_script_template=self.vmd_template_script()
        self.traj_dir=get_new_directory(self.traj_dir)

        if not self.traj_dir.exists():
            create_directory(self.traj_dir)  
            
            tcl_list=python_list_to_tcl_list(self.cube_files)
            self.final_vmd_script=self.rewrite_script(vmd_script_template,'[TCL_CUBE_FILES]', tcl_list)
            self.text_box.insert(END, self.final_vmd_script)
    
    def _on_edit_save_render_script(self):

        self.vmd_script= self.traj_dir/'vmd_test_lsapp.tcl'  
        text_file = open(self.vmd_script, "w")
        text_file.write(self.text_box.get(1.0, END))
        text_file.close()   
    
    def _on_render_cube_frames(self):

        self.render_progress.configure(text= "Frame Rendering") 
        
        cmd=f'vmd -dispdev none -e {self.vmd_script}'
        result=execute_cmd_local(cmd,self.traj_dir)
        error=result[cmd]['error']    
        message=result[cmd]['output']   

        self.render_progress.configure(text= "Frame Rendered") 
 
    def _on_generate_cube_plot_blender(self):
        try:
            import bpy 
        
            # Set the path to the input and output directories
            input_dir = self.traj_dir
            output_dir = self.traj_dir

            # Set the file format and output file name
            file_format = "AVI_JPEG"
            output_file = "output.avi"

            self.output_file_path=str(output_dir) + "/" + output_file

            # Set the frame rate and number of frames
            frame_rate = 24
            num_frames = len(list(Path(input_dir).glob('*.png')))

            # Set the render settings
            bpy.context.scene.render.resolution_x = 1920
            bpy.context.scene.render.resolution_y = 1080
            bpy.context.scene.render.resolution_percentage = 100
            bpy.context.scene.render.fps = frame_rate
            bpy.context.scene.frame_start = 1
            bpy.context.scene.frame_end = num_frames

            # Set the input and output directories
            bpy.context.scene.render.filepath =  self.output_file_path
            bpy.context.scene.render.image_settings.file_format = file_format

            # Iterate over the input directory and add the images to the sequence editor
            for i in range(0, num_frames):
                image_path = os.path.join(input_dir, f"{i}.png")
                image = bpy.data.images.load(image_path)
                bpy.data.scenes["Scene"].sequence_editor_create()
                bpy.context.scene.sequence_editor.sequences.new_image(
                    name=f"{i}",
                    filepath=image_path,
                    channel=1,
                    frame_start=i
                )
                bpy.context.scene.render.fps = 1

            # Render the animation
            bpy.ops.render.render(animation=True)
            self.play_video_canvas()
        except ImportError:
            messagebox.showinfo(title= "Warning", message="Blender not found !! Install Blender in your Environment or select default")
    
    def play_video_canvas(self):
        try:
            import cv2

            video = cv2.VideoCapture(self.output_file_path)
            def update_video_frame():
                ret, frame = video.read()

                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    plt.axis('off')
                    plt.imshow(frame)
                    self.canvas.draw()
                    self.after(10, update_video_frame)
                else:
                    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    update_video_frame()
            update_video_frame()
        except ImportError:
            messagebox.showinfo(title= "Warning", message="cv2 package not found !! Video generated through blender cannot be played on canvas. Install cv2 to play")
                    
    def _on_generate_cube_plot_matplotlib(self):
        
        ims=[]
        list_imgs = list(Path(self.traj_dir).glob('*.png'))
        
        for i in range(len(list_imgs)):           
            img = mpimg.imread(list_imgs[i])
            plt.axis('off')
            im = plt.imshow(img)
            if i == 0:
                plt.imshow(img)  # show an initial one first
            ims.append([im])
        ani = animation.ArtistAnimation(self.fig, ims, interval=50, blit=True,repeat_delay=100)
        self.canvas.draw()
    
    def _on_generate_movie(self):
        self.toggle_canvas()
        engine_type=  self.select_render_engine.get()

        if engine_type=='default':
            self._on_generate_cube_plot_matplotlib()
        elif engine_type=='blender':
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
        
        elif self.plot_type=="scatter_plot":
            self.common_graph_params()
            self._on_select_line_plot()
        
        elif self.plot_type=="histogram_plot":
            self.common_graph_params()
            self._on_select_line_plot()

        elif self.plot_type=="contour_plot":
            self.common_graph_params()
            self._on_select_contour_plot()
        
        elif self.plot_type=="cube":
            self._on_select_cube_file()

    def generate_plot(self):
        self.toggle_canvas()

        try:
            self.plot_type = self.plot_type_var.get()
            if self.plot_type=="line_plot":
                self._on_generate_line_plot('line')
            
            elif self.plot_type=="scatter_plot":
                self._on_generate_line_plot('scatter')
            
            elif self.plot_type=="histogram_plot":
                self._on_generate_line_plot('histogram')
            
            elif self.plot_type=="contour_plot":
                self._on_generate_contour_plot()
            
            elif self.plot_type=="cube":
                self._on_generate_movie()            
            
            self.canvas.draw()

        except AttributeError:
            messagebox.showinfo(title='Info', message="First load the Data") 

