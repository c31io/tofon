import bpy
from bpy.types import Operator
from .utils import (
    copy_collection, remove_collection,
    relink_materials, tofy_object, tofy_lights,
    target_types)
from .panel import reso_max
from os import path, listdir, system
import json
import numpy as np
from collections import defaultdict
import imbuf

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
        # Render
        fpath = scene.render.filepath
        for c, b in enumerate(scene.ToF_mode):
            if b == True:
                for i in scene.collection.children:
                    if i.name[:6] == f'ToF_{"RGB"[c]}_':
                        i.hide_render = False
                    else:
                        i.hide_render = True
                scene.render.filepath = path.join(fpath, 'RGB'[c])
                #TODO scans other than normal
                bpy.ops.render.render(animation=True)
        scene.render.filepath = fpath
        # save scan information
        info = {
            'c': [i for i in scene.ToF_mode],
            'b': scene.ToF_base,
            's': scene.ToF_scan,
            'f': scene.ToF_frames,
            'm': scene.ToF_multip,
            'x': scene.ToF_reso_x,
            'y': scene.ToF_reso_y,
            'p': scene.render.filepath}
        with open(path.join(fpath, 'info.json'), 'w') as f:
            json.dump(info, f)
        return {'FINISHED'}

class TOFON_OT_synthesis_raw(Operator):
    bl_idname = 'scene.tof_synthesis_raw'
    bl_label = 'Synthesis Raw'
    @classmethod
    def poll(cls, context):
        if path.isfile(path.join(context.scene.render.filepath, 'info.json')):
            return True
        else:
            return False
    def execute(self, context):
        try:
            from .kernel import tofkernel as tk
        except ImportError:
            from .kernel import tkfallback as tk
            self.report({'WARNING'},
                '''Pybind module 'tofkernel' not found, SYNTHESIS WILL BE SLOW!!''')
        scene = context.scene
        fpath = scene.render.filepath
        with open(path.join(fpath, 'info.json'), 'r') as f:
            info = json.load(f)
        print(info)
        # cache {cpath}/{color}{frame}.exr
        cpath  = info['p']
        colors = info['c']
        frames = info['f']
        multip = info['m']
        file_found = listdir(cpath)
        cfiles = defaultdict() # the list of cached file for parallelization
        # raw(x, y, rgb, event, color&depth)
        # 3 * 2 = 6 channels: ((R, TR), (G TG), (B, TB))
        raw = np.zeros((info['x'], info['y'], 3, info['f']*info['m']**2, 2))
        for c, b in zip('RGB', colors):
            if b == False:
                continue
            cfiles[c] = [i for i in file_found
                if i[0] == c and i[-4:] == '.exr'
                and 1 <= int(i[1:-4]) <= frames]
        print(cfiles)
        # fill in data
        for c in cfiles:
            for p in cfiles[c]:
                f = np.array(imbuf.load(path.join(cpath, p)))
                frame = int(p[1:-4])
                print(f'tk.fill({raw.shape}, {p}, {c}, {frame}, {multip})')
                tk.fill(raw, f, 'RGB'.find(c), frame, multip)
        # sort raw
        tk.raw_sort(raw)
        # save raw
        np.save(path.join(scene.ToF_opath, 'raw.npy'), raw)
        return {'FINISHED'}

class TOFON_OT_bucket_sort(Operator):
    bl_idname = 'scene.tof_bucket_sort'
    bl_label = 'Bucket Sort'
    @classmethod
    def poll(cls, context):
        scene = context.scene
        if path.isfile(path.join(scene.ToF_opath, 'raw.npy')):
            return True
        else:
            return False
    def execute(self, context):
        try:
            from .kernel import tofkernel as tk
        except ImportError:
            from .kernel import tkfallback as tk
            self.report({'WARNING'},
                '''Pybind module 'tofkernel' not found, BUCKET SORT WILL BE SLOW!!''')
        scene = context.scene
        # raw(x, y, rgb, event, color&depth)
        raw = np.load(path.join(scene.ToF_opath, 'raw.npy'))
        s = raw.shape
        # bucket(t, x, y, rgb)
        bucket = np.zeros((scene.ToF_bframe, s[0], s[1], 3))
        tk.bucket_sort(bucket, raw, scene.ToF_pspf, scene.ToF_threads)
        np.save(path.join(scene.ToF_opath, 'bucket.npy'), bucket)
        return {'FINISHED'}

class TOFON_OT_render_video(Operator):
    bl_idname = 'scene.tof_render_video'
    bl_label = 'Render Video'
    @classmethod
    def poll(cls, context):
        scene = context.scene
        if path.isfile(path.join(scene.ToF_opath, 'bucket.npy')):
            return True
        else:
            return False
    def execute(self, context):
        if system('ffmpeg -version') != 0:
            self.report({'WARNING'},
                '''ffmpeg not found, aborting...''')
            return {'CANCELLED'}
        scene = context.scene
        #TODO write images from bucket
        #TODO system('ffmpeg') to render video
        return {'FINISHED'}

def register():
    bpy.utils.register_class(TOFON_OT_apply_mode)
    bpy.utils.register_class(TOFON_OT_render_scan)
    bpy.utils.register_class(TOFON_OT_synthesis_raw)
    bpy.utils.register_class(TOFON_OT_bucket_sort)
    bpy.utils.register_class(TOFON_OT_render_video)

def unregister():
    bpy.utils.unregister_class(TOFON_OT_apply_mode)
    bpy.utils.unregister_class(TOFON_OT_render_scan)
    bpy.utils.unregister_class(TOFON_OT_synthesis_raw)
    bpy.utils.unregister_class(TOFON_OT_bucket_sort)
    bpy.utils.unregister_class(TOFON_OT_render_video)
