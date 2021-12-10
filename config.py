import pathlib
import os

class SETUPS:
    
    def __init__(self) -> None:
        
        lsroot = pathlib.Path.home() / "litesoph"
        try:
            lsroot = os.environ['LSROOT']
            lsroot = pathlib.Path(lsroot) / "litesoph"
        except:
            print("Please set LSROOT environment variable.")
            exit()
        else:
            print("LSROOT points to {}".format(str(lsroot)))

        self.lsroot = lsroot
        self.setups = self.read_setups()

    def read_setups(self):

        lsproject = pathlib.Path.home() / "Litesoph_Projects"
        vistool = None
        p = self.lsroot / 'setups.in'
        with p.open() as f:
            lines = f.readlines()
            for line in lines:
                if 'vistool' in line:
                    vistool = line.strip().split("=")[1]
                elif 'LSPROJECT' in line:
                    lsproject = line.strip().split("=")[1]
        
        setups = {}
        setups['vistool'] = vistool
        setups['lsproject'] = lsproject

        return setups
