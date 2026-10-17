import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from blib import *
bpy.ops.wm.open_mainfile(filepath=ARBEIT + '/figur.blend')
arm = bpy.data.objects['Armature']
relaxed_pose(arm)
pose_world_rot(arm, 'Head', 'Z', 8)
setup_render((600, 900), 64)
camera((1.15, -3.0, 1.15), (0, 0, 0.92), 55); render(ARBEIT + '/r_34.png')
camera((-1.6, 2.7, 1.2), (0, 0, 0.95), 55); render(ARBEIT + '/r_back.png')
camera((0.35, -1.05, 1.58), (0, 0, 1.5), 60); render(ARBEIT + '/r_face.png')
