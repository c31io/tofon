import bpy
from collections import defaultdict

# https://blender.stackexchange.com/questions/157828/how-to-duplicate-a-certain-collection-using-python
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
    dupe_lut = defaultdict(lambda : None) # a dict returns None if key not found
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

target_types = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'VOLUME']

def relink_objects(col, c):
    '''Relink 3D objects.'''
    if col.objects != None:
        for o in col.objects:
            if o.type in target_types:
                o.active_material = bpy.data.materials[f'ToF_{"RGB"[c]}_{o.active_material.name}']

def relink_materials(col, c):
    '''Relink materials in a collection.'''
    def _relink(col, c):
        relink_objects(col, c)
        for child in col.children:
            _relink(child, c)
    _relink(col, c)

def tofy_object(o, c, base):
    '''Add ToF nodes to material or light.'''
    #FIXME OPL = RL * IOR != RL
    o.use_nodes = True
    p, f = (c+1)%3, (c+2)%3 # path length and fall-off channels
    node_tree = o.node_tree
    nodes = node_tree.nodes
    power = nodes.new('ShaderNodeMath')
    power.operation = 'POWER'
    power.inputs[0].default_value = base
    lpath = nodes.new('ShaderNodeLightPath')
    node_tree.links.new(lpath.outputs['Ray Length'], power.inputs[1])
    for node in nodes:
        for inpt in node.inputs:
            if inpt.type == 'RGBA' and inpt.is_linked == False:
                color = inpt.default_value[c] # backup original color
                combine = nodes.new('ShaderNodeCombineXYZ')
                combine.inputs['XYZ'[c]].default_value = color
                combine.inputs['XYZ'[f]].default_value = 1.0
                node_tree.links.new(power.outputs[0], combine.inputs['XYZ'[p]])
                node_tree.links.new(combine.outputs[0], inpt)

def tofy_objects(col, c, base):
    '''Apply ToF nodes to light objects.'''
    if col.objects != None:
        for o in col.objects:
            if o.type == 'LIGHT':
                tofy_object(o.data, c, base)

def tofy_lights(col, c, base):
    '''Apply ToF nodes to collection.'''
    def _tofy(col, c, base):
        tofy_objects(col, c, base)
        for child in col.children:
            _tofy(child, c, base)
    _tofy(col, c, base)
