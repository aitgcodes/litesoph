import subprocess
import os 
import pathlib
from litesoph.config import LSCONFIG

class CLICommand:
    """LITESOPH's graphical user interface.

    """

    @staticmethod
    def add_arguments(parser):
        pass

    @staticmethod
    def run(args):

        
        lsconfig = LSCONFIG()
        lsconfig.configs['lsproject'] = pathlib.Path.cwd()
        
        from litesoph.GUI.gui import AITG
        app = AITG(lsconfig)
        app.title("AITG - LITESOPH")
        app.resizable(0,0)
        app.mainloop()
    