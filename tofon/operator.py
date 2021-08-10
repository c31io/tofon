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
    '''Copy collections (default not linked). Return the new collection with prefix ToF.'''
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

#TODO encode string ToF_mat -> the set of material names

#TODO decode the set of material names -> string ToF_mat

class TOFON_OT_apply_mode(Operator):
    '''Apply ToF mode. Create a new collection and prepare shader nodes.'''
    bl_idname = 'scene.apply_tof_mode'
    bl_label = 'Apply Mode'
    @classmethod
    def poll(cls, context):
        '''Test if a non-root collection or ToF collection is selected.'''
        if bpy.context.collection == bpy.data.scenes['Scene'].collection:
            return False
        if bpy.context.collection.name[:4] == 'ToF_':
            return False
        return True
    def execute(self, context):
        # remove the old collection
        if isinstance(bpy.types.Scene.ToF_col, str):
            old_col = bpy.data.collections.get(bpy.types.Scene.ToF_col)
            for obj in old_col.objects:
                bpy.data.objects.remove(obj)
            bpy.data.collections.remove(old_col)
        # add channel collection
        col = context.collection
        chan_col = copy_collection(context.scene.collection, col, prefix='ToF_')
        bpy.types.Scene.ToF_col = chan_col.name
        #TODO remove the old materials
        #TODO add channel materials by ToF_Mode
        return {'FINISHED'}

#TODO implement scan vector

#TODO implement data synthesis

def register():
    bpy.utils.register_class(TOFON_OT_apply_mode)
    bpy.types.Scene.ToF_col = StringProperty(name='ToF collection')
    bpy.types.Scene.ToF_mat = StringProperty(name='ToF materials')

def unregister():
    del bpy.types.Scene.ToF_mat
    del bpy.types.Scene.ToF_col
    bpy.utils.unregister_class(TOFON_OT_apply_mode)
