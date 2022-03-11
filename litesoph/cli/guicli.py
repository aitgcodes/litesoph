import subprocess
import os 
import pathlib
from configparser import ConfigParser


filename = pathlib.Path.home() / "lsconfig.ini"

class CLICommand:
    """LITESOPH's graphical user interface.

    """

    @staticmethod
    def add_arguments(parser):
        pass

    @staticmethod
    def run(args):

        
        lsconfig = ConfigParser()
        lsconfig.read(filename)
        
        from litesoph.gui.gui import AITG
        app = AITG(lsconfig)
        app.title("AITG - LITESOPH")
        app.resizable(True,True)
        app.mainloop()
    