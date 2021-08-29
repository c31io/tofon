import bpy
from bpy.types import Operator
from .utils import (
    copy_collection, remove_collection,
    relink_materials, tofy_object, tofy_lights,
    target_types)
from .panel import reso_max

class TOFON_OT_apply_mode(Operator):
    '''Apply ToF mode. Create a new collection and prepare shader nodes.'''
    bl_idname = 'scene.apply_tof_mode'
    bl_label = 'Apply Mode'
    @classmethod
    def poll(cls, context):
        '''Test if a non-first-order collection or ToF collection is selected.'''
        if context.collection == bpy.data.scenes['Scene'].collection:
            return False
        if context.collection.name not in bpy.data.scenes['Scene'].collection.children.keys():
            return False
        if context.collection.name[:4] == 'ToF_':
            return False
        return True
    def execute(self, context):
        '''Create ToF collections.'''
        cns = '__COLLECTION_NAME_SPLIT__'
        scene = context.scene
        # light nodes are only available in Cycles
        scene.render.engine = 'CYCLES'
        # remove the old collections
        to_remove = [i.name for i in bpy.data.collections if i.name[:4] == 'ToF_']
        for i in to_remove:
            remove_collection(bpy.data.collections.get(i))
        # add channel collections
        col = context.collection
        chan_cols = []
        for c, b in enumerate(scene.ToF_mode):
            if b == True:
                new_col = copy_collection(scene.collection, col, prefix=f'ToF_{"RGB"[c]}_')
                chan_cols.append(new_col)
            else:
                chan_cols.append(None)
        # remove world light
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 0.0
        # add material for all objects
        for o in bpy.data.objects:
            if o.type in target_types and o.active_material == None:
                o.active_material = bpy.data.materials.new(name="NoMaterial")
        # remove obsolete materials
        materials = bpy.data.materials
        to_remove = [i.name for i in materials if i.name[:4] == 'ToF_']
        for i in to_remove:
            materials.remove(materials[i])
        # create ToF twins for all materials
        '''in blender python console type
        >>> bpy.data.materials['Material'].node_tree.nodes["Principled BSDF"].inputs['Base Color'].type
        'RGBA'
        >>> list(D.materials['Material'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value)
        [0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0]
        these commands may help your comprehension'''
        to_copy = [i.name for i in materials if i.is_grease_pencil == False]
        for c, b in enumerate(scene.ToF_mode):
            if b == True: # if channel[c] is active
                # create material ToF twins
                for i in to_copy:
                    tof_mat = materials[i].copy()
                    tof_mat.name = f'ToF_{"RGB"[c]}_{i}'
                    tofy_object(tof_mat, c, scene.ToF_base)
                # relink materials in RGB collections with ToF twins
                relink_materials(chan_cols[c], c)
                # ToF twins for all lights (unlike materials, lights are not shared via links)
                tofy_lights(chan_cols[c], c, scene.ToF_base)
        return {'FINISHED'}

#TODO
class TOFON_OT_render_scan(Operator):
    '''
    normal: reso = (x*m)*(y*m)*f
      internally use f many (x*m)*(y*m) images to present a x*y image with f*m*m samples.
    confocal:
      internally use f*p many x*y images to present f*x*y samples at p many points.
    non-confocal:
      the same as confocal except that the location of emitter is fixed.
    
    scan array (confocal & non-confocal):
      square (x * y array with dx * dy step) or custom (get from a csv file).
    
    There is no simple way to read a rendered image without writing it to disk first,
        https://blender.stackexchange.com/questions/2170/how-to-access-render-result-pixels-from-python-script
    but you can use a ram-disk, e.g. tmpfs on Linux platforms.
    '''
    bl_idname = 'scene.render_tof_scan'
    bl_label = 'Render Scan'
    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene.render.engine != 'CYCLES':
            return False
        if scene.ToF_multip * max(scene.ToF_reso_x, scene.ToF_reso_y) > reso_max:
            return False
        return True
    def execute(self, context):
        scene = context.scene
        # Cycle
        scene.cycles.samples = 1 # prevent overwrite
        # Saving
        scene.render.use_file_extension = True
        scene.render.use_render_cache = False
        # Format
        scene.render.image_settings.file_format = 'OPEN_EXR'
        scene.render.image_settings.color_mode = 'RGB'
        scene.render.image_settings.color_depth = '32'
        scene.render.image_settings.exr_codec = 'ZIP'
        scene.render.image_settings.use_zbuffer = False
        scene.render.image_settings.use_preview = False
        scene.render.use_overwrite = True
        scene.render.use_placeholder = True
        # Post Processing
        scene.render.use_compositing = False
        scene.render.use_sequencer = False
        scene.render.dither_intensity = 0
        # ToF
        scene.frame_start = 1
        scene.frame_end = scene.ToF_frames
        scene.render.resolution_x = scene.ToF_reso_x * scene.ToF_multip
        scene.render.resolution_y = scene.ToF_reso_y * scene.ToF_multip
        scene.render.resolution_percentage = 100
        #TODO Render
        fpath = scene.render.filepath
        for c, b in enumerate(scene.ToF_mode):
            pass
        scene.render.path = fpath
        return {'FINISHED'}

#TODO implement data synthesis: pybind (stand-alone) & python fallback
#TODO fallback warning self.report({'WARNING'},
#                                   'Pybind module not found.
#                                       Falling back to Python implementation.
#                                       SYNTHESIS WILL BE SLOW!!')
class TOFON_OT_synthesis(Operator):
    pass

def register():
    bpy.utils.register_class(TOFON_OT_apply_mode)
    bpy.utils.register_class(TOFON_OT_render_scan)

def unregister():
    bpy.utils.unregister_class(TOFON_OT_apply_mode)
    bpy.utils.unregister_class(TOFON_OT_render_scan)
