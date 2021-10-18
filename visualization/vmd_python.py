# code to get number of cube files (n)(an integer), rotational axes (a,b,c)(as integers) and translational axes (x,y,z)(as floats) as arguments, write a tcl script to get images of cube files and run that tcl script using python, make movies using blender

# the code requires the cube files to be named in the format $i.cube where i is 0,1,2,3. Please name your cube files accordingly or modify $i.

# usage  python3 vmd_python.py 5 0.0001  /home/vignesh/Downloads/blender/blender-2.93.2-linux-x64/blender

# The tcl scripting for vmd is highly motivated from http://chemicaldynamicscode.blogspot.com

import os
import sys
from PIL import Image


# n is the number of cube files
n = int(sys.argv[1])
l_n = "{:04d}".format(n)
# a,b,c are ratational axes
iso = float(sys.argv[2])

blender_path = sys.argv[3]

rot1 = 0
rot2 = 90
rot3 = 90

argm = sys.argv
if "-t" in argm:
  rot1 = int(sys.argv[5])
  rot2 = int(sys.argv[6])
  rot3 = int(sys.argv[7])

t = False

# file to write the tcl script
f = open("vmd.tcl","w")

# decaring the lines of tcl scripts one by one
one_line   = "menu main off"
two_line  = "axes location off"
two_a_line = ["lappend isoval"," ",str(iso)," ","-",str(iso)]
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
thirteen_line  = ["    rotate x by "+str(rot1)]
fourteen_line  = ["    rotate y by  "+str(rot2)]
fifteen_line  = ["    rotate z by "+str(rot3)]
sixteen_line  = "    scale by 0.6"
sixteen_a_line = ["    translate by 0 0 0 "]
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
thirtyone_line   = "  set iso 0"
thirtytwo_line  = "  foreach val $isoval {"
thirtytwo_a_line = "  mol representation isosurface ${val} 0.0 0.0 0.0 1 1"
thirtythree_line   = "  mol color ColorID $iso"
thirtyfour_line  = "  incr iso"
thirtyfive_line   = '  puts "iso ${iso}"'
thirtysix_line  = "  mol addrep $i"
thirtyseven_line   = "  }"
thirtyeight_line  = "  render Tachyon $i.dat " 
thirtynine_line  = "  /usr/local/lib/vmd/tachyon_LINUXAMD64 -aasamples 12 12 $i.dat -format TGA -res 1600 1200 -o $i.tga" 
fourty_line   = "  mol delete $i "
fourtyone_line  = "}"  
fourtytwo_line   = "exit"  

#writing the tcl script
f.writelines(one_line)
f.write("\n")
f.writelines(two_line)
f.write("\n")
f.writelines(two_a_line)
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
f.close()

#running the tcl script
os.system("vmd -e vmd.tcl")

for i in range(n):
    Image.open(str(i)+".tga").save(str(i)+".png")
os.system("mkdir image")
os.system("cp *.png image")
os.system(blender_path+" -b -P blend_vedio.py"+" "+str(n))
os.system("cp /tmp/0001-"+str(l_n)+".mp4 .")
