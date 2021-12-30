import pathlib
from configparser import ConfigParser



def check_config(lsconfig: ConfigParser, name):
    if name == "lsroot":
        try:
            lsroot = pathlib.Path(lsconfig.get("project_path", "lsroot" ))
        except:
            print("Please set lsroot in ~/lsconfig.ini")
            exit()
        else:
            return lsroot
    if name == "vmd":
        try:
            vmd = lsconfig.get("visualization_tools", "vmd" )
        except:
            print("Please set path to vmd in ~/lsconfig.ini")
        else:
            return vmd