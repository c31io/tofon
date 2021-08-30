import bpy
from bpy.types import Panel
from bpy.props import (
    BoolVectorProperty,
    FloatProperty,
    EnumProperty,
    IntProperty)

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
        col.prop(scene, 'ToF_mode', index=0, text='R')
        col = row.column()
        col.prop(scene, 'ToF_mode', index=1, text='G')
        col = row.column()
        col.prop(scene, 'ToF_mode', index=2, text='B')
        row = layout.row()
        row.prop(scene, 'ToF_base', emboss=False, slider=True)
        row = layout.row()
        row.operator('scene.apply_tof_mode')
        row = layout.row()
        row.operator('OUTLINER_OT_orphans_purge', text='Clear Orphaned Data')
        row = layout.row()
        row.prop(scene, 'ToF_scan')
        row = layout.row()
        row.prop(scene, 'ToF_frames', emboss=False)
        row = layout.row()
        row.prop(scene, 'ToF_multip', emboss=False)
        row = layout.row()
        row.prop(scene, 'ToF_reso_x', emboss=False)
        row = layout.row()
        row.prop(scene, 'ToF_reso_y', emboss=False)
        row = layout.row()
        row.prop(scene.render, 'filepath', text='Cache')
        row = layout.row()
        row.operator('scene.render_tof_scan')
        row = layout.row()
        row.operator('scene.tof_synthesis')

frame_max = 1048574
reso_max = 65536

def register():
    bpy.utils.register_class(TOFON_PT_para_setter)
    bpy.types.Scene.ToF_mode = BoolVectorProperty(
        name='Mode')
    bpy.types.Scene.ToF_base = FloatProperty(
        name='Logarithmic Base', precision=3,
        default=0.950, min=0.001, max=0.999,
        description='Turn multiplication to addition.' )
    bpy.types.Scene.ToF_scan = EnumProperty(items=[
        ('NORMAL', 'Normal', 'f many (x*m)*(y*m) images present a x*y image with f*m*m samples.'),
        ('CONFOC', 'Confocal', 'f*p many x*y images present f*x*y samples at p many points.'),
        ('NONCOF', 'Non-confocal', 'Same as confocal except that the location of emitter is fixed.')],
        name='Scan',
        default='NORMAL')
    bpy.types.Scene.ToF_frames = IntProperty(
        name='Frames',
        default=16, min=1, max=frame_max)
    bpy.types.Scene.ToF_multip = IntProperty(
        name='Multiplier',
        default=2, min=1, max=reso_max)
    bpy.types.Scene.ToF_reso_x = IntProperty(
        name='Resolution X',
        default=1024, min=1, max=reso_max)
    bpy.types.Scene.ToF_reso_y = IntProperty(
        name='Resolution Y',
        default=1024, min=1, max=reso_max)

def unregister():
    del bpy.types.Scene.ToF_mode
    del bpy.types.Scene.ToF_base
    del bpy.types.Scene.ToF_scan
    del bpy.types.Scene.ToF_frames
    del bpy.types.Scene.ToF_multip
    del bpy.types.Scene.ToF_reso_x
    del bpy.types.Scene.ToF_reso_y
    bpy.utils.unregister_class(TOFON_PT_para_setter)
