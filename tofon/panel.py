import bpy
from bpy.types import Panel
from bpy.props import (
    BoolVectorProperty,
    FloatProperty,
    EnumProperty,
    IntProperty,
    StringProperty)

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
        row.prop(scene, 'ToF_mpath')
        row = layout.row()
        row.prop(scene, 'ToF_opath')
        row = layout.row()
        row.operator('scene.tof_synthesis_raw')
        row = layout.row()
        row.prop(scene, 'ToF_bframe', emboss=False)
        row = layout.row()
        row.prop(scene, 'ToF_pspf', emboss=False)
        row = layout.row()
        row.operator('scene.tof_bucket_sort')
        row = layout.row()
        row.prop(scene, 'ToF_brightness', emboss=False)
        row = layout.row()
        row.prop(scene, 'ToF_contrast', emboss=False)
        row = layout.row()
        row.prop(scene, 'ToF_gamma', emboss=False)
        row = layout.row()
        row.prop(scene, 'ToF_vfps', emboss=False)
        row = layout.row()
        row.operator('scene.tof_render_video')

frame_max = 1048574
reso_max = 65536

def register():
    bpy.utils.register_class(TOFON_PT_para_setter)
    bpy.types.Scene.ToF_mode = BoolVectorProperty(
        name='Mode', default=(True,True,True))
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
        default=512, min=1, max=reso_max)
    bpy.types.Scene.ToF_opath = StringProperty(
        name='Output', subtype='FILE_PATH',
        default='/tmp/')
    bpy.types.Scene.ToF_bframe = IntProperty(
        name='Bucket frames',
        default=100, min=1)
    bpy.types.Scene.ToF_pspf = FloatProperty(
        name='Picoseconds per frame', precision=3,
        default=1000, min=0.001)
    bpy.types.Scene.ToF_mpath = StringProperty(
        name='Module Path', subtype='FILE_PATH',
        default='/home/user/.local/lib/python3.9/site-packages/')
    bpy.types.Scene.ToF_brightness = FloatProperty(
        name='Brightness', precision=6,
        default=0, min=0)
    bpy.types.Scene.ToF_contrast = FloatProperty(
        name='Contrast', precision=6,
        default=10, min=0.000001)
    bpy.types.Scene.ToF_gamma = FloatProperty(
        name='Gamma', precision=6,
        default=1, min=0.000001)
    bpy.types.Scene.ToF_vfps = IntProperty(
        name='Frame Per Second',
        default=24, min=1)

def unregister():
    del bpy.types.Scene.ToF_mode
    del bpy.types.Scene.ToF_base
    del bpy.types.Scene.ToF_scan
    del bpy.types.Scene.ToF_frames
    del bpy.types.Scene.ToF_multip
    del bpy.types.Scene.ToF_reso_x
    del bpy.types.Scene.ToF_reso_y
    del bpy.types.Scene.ToF_opath
    del bpy.types.Scene.ToF_bframe
    del bpy.types.Scene.ToF_pspf
    del bpy.types.Scene.ToF_mpath
    del bpy.types.Scene.ToF_brightness
    del bpy.types.Scene.ToF_contrast
    del bpy.types.Scene.ToF_gamma
    del bpy.types.Scene.ToF_vfps
    bpy.utils.unregister_class(TOFON_PT_para_setter)
