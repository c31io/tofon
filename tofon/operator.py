import bpy
from bpy.types import Operator
from .utils import (
    copy_collection, remove_collection,
    relink_materials, target_types
    )

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
        # enable nodes for all materials
        materials = bpy.data.materials
        for i in materials:
            i.use_nodes = True
        # remove obsolete materials
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
                    p, f = (c+1)%3, (c+2)%3 # path length and fall-off channels
                    node_tree = tof_mat.node_tree
                    nodes = node_tree.nodes
                    power = nodes.new('ShaderNodeMath')
                    power.operation = 'POWER'
                    power.inputs[0].default_value = scene.ToF_base
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
                # relink materials in RGB collections with ToF twins
                relink_materials(chan_cols[c], c)
                #TODO ToF twins for all lights
        return {'FINISHED'}

#TODO
class TOFON_OT_scan(Operator):
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
    pass

#TODO implement data synthesis: pybind (stand-alone) & python fallback
#TODO fallback warning self.report({'WARNING'},
#                                   'Pybind module not found.
#                                       Falling back to Python implementation.
#                                       SYNTHESIS WILL BE SLOW!!')
class TOFON_OT_synthesis(Operator):
    pass

def register():
    bpy.utils.register_class(TOFON_OT_apply_mode)

def unregister():
    bpy.utils.unregister_class(TOFON_OT_apply_mode)
