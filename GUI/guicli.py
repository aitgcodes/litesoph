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

        import litesoph

        lsroot = litesoph.__file__
        lsroot = pathlib.Path(lsroot) 
        lsroot = lsroot.parent.parent
       
        from litesoph.GUI.gui import AITG
        app = AITG(lsroot)
        app.title("AITG - LITESOPH")
        app.resizable(True,True)
        app.mainloop()
    