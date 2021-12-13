import pathlib
import os
import litesoph

class LSCONFIG:
    
    def __init__(self) -> None:
        
        lsroot = pathlib.Path.home() / "litesoph"
        try:
            lsroot = pathlib.Path(litesoph.__file__)
            lsroot = lsroot.parent.parent
        except:
            print("Please add path of litesoph to PYTHONPATH environment variable.")
            exit()
        else:
            print("litesoph is located at {}".format(str(lsroot)))

        self.lsroot = lsroot
        self.configs = self.read_configs()

    def read_configs(self):

        lsproject = pathlib.Path.home() / "Litesoph_Projects"
        vistool = None
        p = pathlib.Path.home() / 'lsconfig.in'
        with p.open() as f:
            lines = f.readlines()
            for line in lines:
                if 'vistool' in line:
                    vistool = line.strip().split("=")[1]
                elif 'LSPROJECT' in line:
                    lsproject = line.strip().split("=")[1]
        
        configs = {}
        configs['vistool'] = vistool
        configs['lsproject'] = lsproject

        return configs
