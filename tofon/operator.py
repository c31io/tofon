import bpy
from bpy.types import Operator
from collections import  defaultdict

def copy_objects(from_col, to_col, linked, dupe_lut):
    for o in from_col.objects:
        dupe = o.copy()
        if not linked and o.data:
            dupe.data = dupe.data.copy()
        to_col.objects.link(dupe)
        dupe_lut[o] = dupe

def copy(parent, collection, linked=False):
    dupe_lut = defaultdict(lambda : None)
    def _copy(parent, collection, linked=False):
        cc = bpy.data.collections.new(collection.name)
        copy_objects(collection, cc, linked, dupe_lut)
        for c in collection.children:
            _copy(cc, c, linked)
        parent.children.link(cc)
    _copy(parent, collection, linked)
    print(dupe_lut)
    for o, dupe in tuple(dupe_lut.items()):
        parent = dupe_lut[o.parent]
        if parent:
            dupe.parent = parent

class TOFON_OT_apply_mode(Operator):
    bl_idname = 'scene.apply_tof_mode'
    bl_label = 'Apply Mode'
    @classmethod
    def poll(cls, context): #TODO check context
        coll = context.collection
        return True
    def execute(self, context):
        #TODO add channel collections
        #TODO manage color inputs of nodes
        return {'FINISHED'}

#TODO implement scan vector

#TODO implement data synthesis

def register():
    bpy.utils.register_class(TOFON_OT_apply_mode)

def unregister():
    bpy.utils.unregister_class(TOFON_OT_apply_mode)
