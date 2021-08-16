# copy_*s are found below:
# https://blender.stackexchange.com/questions/157828/how-to-duplicate-a-certain-collection-using-python

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from collections import  defaultdict

def copy_objects(from_col, to_col, linked, dupe_lut):
    '''Copy objects from one collection to another.'''
    for o in from_col.objects:
        dupe = o.copy()
        if not linked and o.data:
            dupe.data = dupe.data.copy()
        to_col.objects.link(dupe)
        dupe_lut[o] = dupe

def copy_collection(parent, collection, linked=False, prefix=''):
    '''Copy collection (default not linked). Return the new collection with prefix ToF.'''
    dupe_lut = defaultdict(lambda : None)
    def _copy(parent, collection, linked=False):
        cc = bpy.data.collections.new(prefix + collection.name)
        copy_objects(collection, cc, linked, dupe_lut)
        for c in collection.children:
            _copy(cc, c, linked)
        parent.children.link(cc)
        return cc
    ret = _copy(parent, collection, linked)
    for o, dupe in tuple(dupe_lut.items()):
        parent = dupe_lut[o.parent]
        if parent:
            dupe.parent = parent
    return ret

def remove_objects(col):
    '''Remove objects from one collection.'''
    if col.objects != None:
        for o in col.objects:
            bpy.data.objects.remove(o)

def remove_collection(col):
    '''Remove collection.'''
    def _remove(col):
        remove_objects(col)
        for c in col.children:
            _remove(c)
        bpy.data.collections.remove(col)
    _remove(col)

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
        cns = '__COLLECTION_NAME_SPLIT__'
        scene = context.scene
        Scene = bpy.types.Scene
        # remove the old collections
        old_cols = scene.ToF_col.split(cns)[:-1]
        for i in old_cols:
            try:
                remove_collection(bpy.data.collections.get(i))
            except AttributeError:
                print('not initialized but okay')
        # add channel collections
        col = context.collection
        mode = scene.ToF_mode
        scene.ToF_col = ''
        RGB_cols = []
        if mode[0] == True:
            chan_col = copy_collection(scene.collection, col, prefix='ToF_R_')
            scene.ToF_col = chan_col.name + cns
            RGB_cols.append(chan_col.name)
        else:
            RGB_cols.append(None)
        if mode[1] == True:
            chan_col = copy_collection(scene.collection, col, prefix='ToF_G_')
            scene.ToF_col += chan_col.name + cns
            RGB_cols.append(chan_col.name)
        else:
            RGB_cols.append(None)
        if mode[2] == True:
            chan_col = copy_collection(scene.collection, col, prefix='ToF_B_')
            scene.ToF_col += chan_col.name + cns
            RGB_cols.append(chan_col.name)
        else:
            RGB_cols.append(None)
        # enable nodes for all materials
        for i in bpy.data.materials:
            i.use_nodes = True
        #TODO create ToF twins for all materials
        '''in blender python console type
        >>> bpy.data.materials['Material'].node_tree.nodes["Principled BSDF"].inputs['Base Color'].type
        'RGBA'
        this command may help your comprehension'''
        if mode[1] == True:
            # create ToF_R_* materials
            pass
        # if mode[2] mode[3] is True
        #TODO relink materials in RGB_cols with ToF twins
        if mode[1] == True:
            # traverse & relinking
            pass
        # if mode[2] mode[3] is True
        return {'FINISHED'}

#TODO implement scan vectors: normal, confocal, non-confocal

#TODO implement data synthesis: pybind (stand-alone) & python fallback
#TODO fallback warning self.report({'WARNING'},
#                                   'Pybind module not found.
#                                       Falling back to Python implementation.
#                                       SYNTHESIS WILL BE SLOW!!')

def register():
    bpy.utils.register_class(TOFON_OT_apply_mode)
    bpy.types.Scene.ToF_col = StringProperty(name='ToF collection')
    bpy.types.Scene.ToF_mat = StringProperty(name='ToF materials')

def unregister():
    del bpy.types.Scene.ToF_mat
    del bpy.types.Scene.ToF_col
    bpy.utils.unregister_class(TOFON_OT_apply_mode)
