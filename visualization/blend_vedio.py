import os
import bpy 
import sys

n = int(sys.argv[4]) 
dir_path = os.path.dirname(os.path.realpath(__file__))
path = dir_path+"/image"
file_path = os.listdir(path)
file_path.sort()
for area in bpy.context.screen.areas:
  if area.type == 'VIEW_3D':

       bpy.context.scene.sequence_editor_create()

       movie = bpy.context.scene.sequence_editor.sequences.new_image(
                  name="photos", filepath=os.path.join(path, file_path[0]),
                  channel=1, frame_start=1)

       for o in file_path:
           movie.elements.append(o)
       bpy.context.scene.render.fps = 1
       bpy.context.scene.frame_end = n
       bpy.context.scene.render.image_settings.file_format = 'FFMPEG' 
       bpy.context.scene.render.ffmpeg.format = 'MPEG4'
       bpy.ops.render.render(animation=True)
