import subprocess
import os 
import pathlib
from litesoph.GUI.gui import AITG

class CLICommand:
    """LITESOPH's graphical user interface.

    """

    @staticmethod
    def add_arguments(parser):
        pass

    @staticmethod
    def run(args):
        
        app = AITG()
        app.title("AITG - LITESOPH")
        app.resizable(True,True)
        app.mainloop()
    