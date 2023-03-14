#!/usr/bin/tclsh

set cube_file_list [TCL_CUBE_FILES]
set len_list [llength $cube_file_list] 

menu main off
axes location off

for {set i 0} {$i < $len_list} {incr i} {
    puts $i
    # put llength cube_file_list
    puts [lindex $cube_file_list  $i]
  
    mol new [lindex $cube_file_list  $i]
  
  if {$i == 0} {
    display projection orthographic
    light 0 on
    light 1 on
    light 2 on
    light 3 on
    color Display {Background} white
    color Name {H} gray
    rotate x by 0
    rotate y by 90
    rotate z by 90
    scale by 1.10
    translate by 0.0 0.0 0.0
    global viewpoints
    set viewpoints(0) [molinfo 0 get rotate_matrix]
    set viewpoints(1) [molinfo 0 get center_matrix]
    set viewpoints(2) [molinfo 0 get scale_matrix]
    set viewpoints(3) [molinfo 0 get global_matrix]
  }
  molinfo $i set center_matrix $viewpoints(1)
  molinfo $i set rotate_matrix $viewpoints(0)
  molinfo $i set scale_matrix $viewpoints(2)
  molinfo $i set global_matrix $viewpoints(3)
  mol delrep 0 $i
  mol representation CPK 0.3 0.0 100.0 100.0
  mol material HardPlastic
  mol addrep $i
  mol representation isosurface 0.03 0.0 0.0 0.0 1 1
  mol color ColorID 0
  mol material HardPlastic
  mol addrep $i
  mol representation isosurface 0.06 0.0 0.0 0.0 1 1
  mol color ColorID 7
  mol material HardPlastic
  mol addrep $i
  mol representation isosurface 0.10 0.0 0.0 0.0 1 1
  mol color ColorID 4
  mol material HardPlastic
  mol addrep $i
  mol representation isosurface 0.20 0.0 0.0 0.0 1 1
  mol color ColorID 1
  mol material HardPlastic
  mol addrep $i
  mol clipplane normal 0 1 $i {0.0 1.0 0.0}
  mol clipplane normal 0 2 $i {0.0 1.0 0.0}
  mol clipplane normal 0 3 $i {0.0 1.0 0.0}
  mol clipplane normal 0 4 $i {0.0 1.0 0.0}
  mol clipplane status 0 1 $i {1}
  mol clipplane status 0 2 $i {1}
  mol clipplane status 0 3 $i {1}
  mol clipplane status 0 4 $i {1}
  render Tachyon ls_cube_$i.dat
  /usr/local/lib/vmd/tachyon_LINUXAMD64 -aasamples 12 12 ls_cube_$i.dat -format TGA -res 1600 1200 -o ls_cube_$i.tga
  exec convert ls_cube_$i.tga ls_cube_$i.png
  mol delete $i

}
exit
