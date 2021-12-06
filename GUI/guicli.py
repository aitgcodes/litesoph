import subprocess
import os 
import pathlib


class CLICommand:
    """LITESOPH's graphical user interface.

    """

    @staticmethod
    def add_arguments(parser):
        pass

    @staticmethod
    def run(args):

        lsroot = os.environ.get('LS_ROOT')
        lsroot = lsroot.replace(':','')
        lsroot = pathlib.Path(lsroot) 

        from litesoph.GUI.gui import AITG
        app = AITG(lsroot)
        app.title("AITG - LITESOPH")
        app.resizable(True,True)
        app.mainloop()
    