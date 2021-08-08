import bpy
from bpy.types import Panel
from bpy.props import BoolVectorProperty

class TOFON_PT_para_setter(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ToF'
    bl_label = 'ToF Settings'
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        row.label (text='Mode:')
        col = row.column()
        col.prop(scene, 'ToF_Mode', index=0, text='R')
        col = row.column()
        col.prop(scene, 'ToF_Mode', index=1, text='G')
        col = row.column()
        col.prop(scene, 'ToF_Mode', index=2, text='B')
        row = layout.row()
        row.operator('scene.apply_tof_mode')

def register():
    bpy.utils.register_class(TOFON_PT_para_setter)
    bpy.types.Scene.ToF_Mode = BoolVectorProperty(name='Mode', size=3)

def unregister():
    del bpy.types.Scene.ToF_Mode
    bpy.utils.unregister_class(TOFON_PT_para_setter)
