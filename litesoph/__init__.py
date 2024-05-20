


from litesoph.common.ls_manager import LSManager
from tkinter import messagebox




__version__ = '1.1'


def about_litesoph():
    about_message = "Layer Integrated Toolkit and Engine for Simulations of Photo-induced Phenomena\n" + f"Version: {__version__}"
    about_detail = ()

    messagebox.showinfo(
        title='About', message=about_message, detail=about_detail
    )
