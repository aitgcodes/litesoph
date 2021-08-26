# code to get number of cube files (n)(an integer), rotational axes (a,b,c)(as integers) and translational axes (x,y,z)(as floats) as arguments, write a tcl script to get images of cube files and run that tcl script using python, make movies using blender

# the code requires the cube files to be named in the format $i.cube where i is 0,1,2,3. Please name your cube files accordingly or modify $i.

# usage  python3 vmd_python.py 5 0 90 90 0.0 0.0 0.0  /home/vignesh/Downloads/blender/blender-2.93.2-linux-x64/blender

# The tcl scripting for vmd is highly motivated from http://chemicaldynamicscode.blogspot.com

import os
import sys
from PIL import Image


# n is the number of cube files
n = int(sys.argv[1])

# a,b,c are ratational axes
a = int(sys.argv[2])
b = int(sys.argv[3])
c = int(sys.argv[4])

# x,y,c are translational axes
x = float(sys.argv[5])
y = float(sys.argv[6])
z = float(sys.argv[7])

blender_path = sys.argv[8]


# file to write the tcl script
f = open("vmd.tcl","w")

# decaring the lines of tcl scripts one by one
one_line   = "menu main off"
two_line  = "axes location off"
three_line   = ["for {set i 0} {$i < ",str(n),"} {incr i} {"]
four_line  = "   mol new $i.cube"
five_line  = "   if {$i == 0} {"
six_line  = "    display projection orthographic"
seven_line   = "    light 0 on"
eight_line  =  "    light 1 on"
nine_line  =  "    light 2 on"
ten_line =  "    light 3 on"
eleven_line  = "    color Display {Background} white"
twelve_line  = "    color Name {H} gray"
thirteen_line  = ["    rotate x by ",str(a)]
fourteen_line  = ["    rotate y by ",str(b)]
fifteen_line  = ["    rotate z by ",str(c)]
sixteen_line  = "    scale by 1.10"
sixteen_a_line = ["    translate by ",str(x)," ",str(y)," ",str(z)]
seventeen_line  = "    global viewpoints"
eighteen_line   ="    set viewpoints(0) [molinfo 0 get rotate_matrix]"
nineteen_line  = "    set viewpoints(1) [molinfo 0 get center_matrix]"
twenty_line   = "    set viewpoints(2) [molinfo 0 get scale_matrix]"
twentyone_line  = "    set viewpoints(3) [molinfo 0 get global_matrix]"
twentytwo_line   = "  }"
twentythree_line  = "  molinfo $i set center_matrix $viewpoints(1)"
twentyfour_line  = "  molinfo $i set rotate_matrix $viewpoints(0)"
twentyfive_line   = "  molinfo $i set scale_matrix $viewpoints(2)"
twentysix_line  = "  molinfo $i set global_matrix $viewpoints(3)"
twentyseven_line   = "  mol delrep 0 $i"
twentyeight_line  = "  mol representation CPK 0.3 0.0 100.0 100.0"
twentynine_line   = "  mol material HardPlastic"
thirty_line  = "  mol addrep $i"
thirtyone_line   = "  mol representation isosurface 0.03 0.0 0.0 0.0 1 1"
thirtytwo_line  = "  mol color ColorID 0"
thirtytwo_a_line = "  mol material HardPlastic"
thirtythree_line   = "  mol addrep $i"
thirtyfour_line  = "  mol representation isosurface 0.06 0.0 0.0 0.0 1 1"
thirtyfive_line   = "  mol color ColorID 7"
thirtysix_line  = "  mol material HardPlastic"
thirtyseven_line   = "  mol addrep $i"
thirtyeight_line  = "  mol representation isosurface 0.10 0.0 0.0 0.0 1 1"
thirtynine_line  = "  mol color ColorID 4"
fourty_line   = "  mol material HardPlastic"
fourtyone_line  = "  mol addrep $i"
fourtytwo_line   = "  mol representation isosurface 0.20 0.0 0.0 0.0 1 1"
fourtythree_line  = "  mol color ColorID 1"
fourtyfour_line   = "  mol material HardPlastic"
fourtyfive_line  = "  mol addrep $i"
fourtysix_line   = "  mol clipplane normal 0 1 $i {0.0 1.0 0.0}"
fourtyseven_line  = "  mol clipplane normal 0 2 $i {0.0 1.0 0.0}"
fourtyeight_line   = "  mol clipplane normal 0 3 $i {0.0 1.0 0.0}"
fourtynine_line  = "  mol clipplane normal 0 4 $i {0.0 1.0 0.0}"
fifty_line  = "  mol clipplane status 0 1 $i {1}"
fiftyone_line   = "  mol clipplane status 0 2 $i {1}"
fiftytwo_line  = "  mol clipplane status 0 3 $i {1}"
fiftythree_line   = "  mol clipplane status 0 4 $i {1}"
fiftyfour_line  = "  render Tachyon $i.dat"
fiftyfive_line   = "  /usr/local/lib/vmd/tachyon_LINUXAMD64 -aasamples 12 12 $i.dat -format TGA -res 1600 1200 -o $i.tga"
fiftysix_line  = "  mol delete $i"
fiftyseven_line   = "}"
fiftyeight_line = "exit"

#writing the tcl script
f.writelines(one_line)
f.write("\n")
f.writelines(two_line)
f.write("\n")
f.writelines(three_line)
f.write("\n")
f.writelines(four_line)
f.write("\n")
f.writelines(five_line)
f.write("\n")
f.writelines(six_line)
f.write("\n")
f.writelines(seven_line)
f.write("\n")
f.writelines(eight_line)
f.write("\n")
f.writelines(nine_line)
f.write("\n")
f.writelines(ten_line)
f.write("\n")
f.writelines(eleven_line)
f.write("\n")
f.writelines(twelve_line)
f.write("\n")
f.writelines(thirteen_line)
f.write("\n")
f.writelines(fourteen_line)
f.write("\n")
f.writelines(fifteen_line)
f.write("\n")
f.writelines(sixteen_line)
f.write("\n")
f.writelines(sixteen_a_line)
f.write("\n")
f.writelines(seventeen_line)
f.write("\n")
f.writelines(eighteen_line)
f.write("\n")
f.writelines(nineteen_line)
f.write("\n")
f.writelines(twenty_line)
f.write("\n")
f.writelines(twentyone_line)
f.write("\n")
f.writelines(twentytwo_line)
f.write("\n")
f.writelines(twentythree_line)
f.write("\n")
f.writelines(twentyfour_line)
f.write("\n")
f.writelines(twentyfive_line)
f.write("\n")
f.writelines(twentysix_line)
f.write("\n")
f.writelines(twentyseven_line)
f.write("\n")
f.writelines(twentyeight_line)
f.write("\n")
f.writelines(twentynine_line)
f.write("\n")
f.writelines(thirty_line)
f.write("\n")
f.writelines(thirtyone_line)
f.write("\n")
f.writelines(thirtytwo_line)
f.write("\n")
f.writelines(thirtytwo_a_line)
f.write("\n")
f.writelines(thirtythree_line)
f.write("\n")
f.writelines(thirtyfour_line)
f.write("\n")
f.writelines(thirtyfive_line)
f.write("\n")
f.writelines(thirtysix_line)
f.write("\n")
f.writelines(thirtyseven_line)
f.write("\n")
f.writelines(thirtyeight_line)
f.write("\n")
f.writelines(thirtynine_line)
f.write("\n")
f.writelines(fourty_line)
f.write("\n")
f.writelines(fourtyone_line)
f.write("\n")
f.writelines(fourtytwo_line)
f.write("\n")
f.writelines(fourtythree_line)
f.write("\n")
f.writelines(fourtyfour_line)
f.write("\n")
f.writelines(fourtyfive_line)
f.write("\n")
f.writelines(fourtysix_line)
f.write("\n")
f.writelines(fourtyseven_line)
f.write("\n")
f.writelines(fourtyeight_line)
f.write("\n")
f.writelines(fourtynine_line)
f.write("\n")
f.writelines(fifty_line)
f.write("\n")
f.writelines(fiftyone_line)
f.write("\n")
f.writelines(fiftytwo_line)
f.write("\n")
f.writelines(fiftythree_line)
f.write("\n")
f.writelines(fiftyfour_line)
f.write("\n")
f.writelines(fiftyfive_line)
f.write("\n")
f.writelines(fiftysix_line)
f.write("\n")
f.writelines(fiftyseven_line)
f.write("\n")
f.writelines(fiftyeight_line)
f.write("\n")
f.close()

#running the tcl script
os.system("vmd -e vmd.tcl")

for i in range(n):
    Image.open(str(i)+".tga").save(str(i)+".png")
os.system("mkdir image")
os.system("cp *.png image")
os.system(blender_path+" -b -P blend_vedio.py")
