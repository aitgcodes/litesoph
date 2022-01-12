import pathlib
from configparser import ConfigParser



def check_config(lsconfig: ConfigParser, name):
    if name == "lsroot":
        try:
            lsroot = pathlib.Path(lsconfig.get("path", "lsroot" ))
        except:
            print("Please set lsroot in ~/lsconfig.ini")
            exit()
        else:
            return lsroot
    if name == "vis":
        try:
           vis_tool = list(lsconfig.items("visualization_tools"))[0][1]
        except:
            print("Please set path to vmd or vesta in ~/lsconfig.ini and first one will be used")
        else:
            return vis_tool
        # try:
        #     vmd = lsconfig.get("visualization_tools", "vmd" )
        # try:
        #     vmd = lsconfig.get("visualization_tools", "vesta" )
        # except:
        #     print("Please set path to vmd in ~/lsconfig.ini")
        # else:
        #     return vmd