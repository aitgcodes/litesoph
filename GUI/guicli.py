import subprocess
import os 
import pathlib
from litesoph.config import SETUPS

class CLICommand:
    """LITESOPH's graphical user interface.

    """

    @staticmethod
    def add_arguments(parser):
        pass

    @staticmethod
    def run(args):

        import litesoph
        setup = SETUPS()
        lsroot = litesoph.__file__
        lsroot = pathlib.Path(lsroot) 
        setup.lsroot = lsroot.parent.parent
       
        from litesoph.GUI.gui import AITG
        app = AITG(setup.lsroot)
        app.title("AITG - LITESOPH")
        app.resizable(True,True)
        app.mainloop()
    