import bpy
from collections import defaultdict

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

def relink_materials(col_name, prefix):
    return NotImplemented

def relink_lights(col_name, prefix):
    return NotImplemented
