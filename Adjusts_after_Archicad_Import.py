bl_info = {
    "name": "Archicad Import Adjustments",
    "author": "Leandro Paganelli",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "category": "Scene",
    "description": "Efetua ajustes após importação do Archicad. Licença: MIT",
    "location": "Propriedades > Cena",
#    "warning": "",
#    "doc_url": "https://seusite.com/doc",
#    "tracker_url": "https://seusite.com/bugtracker",
}

import bpy
from mathutils import Vector

# First operator: Add Gamma Node
class SimpleOperator1(bpy.types.Operator):
    bl_idname = "scene.add_gamma_node"
    bl_label = "Correct Colors"
    
    def execute(self, context):
        materials = bpy.data.materials
        for material in materials:
            if material.use_nodes and material.node_tree.nodes.get("Principled BSDF"):
                principled_node = material.node_tree.nodes.get("Principled BSDF")
                if not principled_node.inputs['Base Color'].is_linked and not principled_node.inputs['Base Color'].links:
                    gamma_node = material.node_tree.nodes.new('ShaderNodeGamma')
                    gamma_node.location = principled_node.location - Vector((300, 0))
                    gamma_node.inputs[1].default_value = 2
                    gamma_node.inputs[0].default_value = principled_node.inputs['Base Color'].default_value
                    material.node_tree.links.new(gamma_node.outputs[0], principled_node.inputs['Base Color'])
        return {'FINISHED'}

# Second operator: Set Metallic to Zero
class SimpleOperator2(bpy.types.Operator):
    bl_idname = "scene.set_metallic_to_zero"
    bl_label = "Correct Metallic, Roughness and Specular"
    
    def execute(self, context):
        for material in bpy.data.materials:
            if material.use_nodes and material.node_tree.nodes.get("Principled BSDF"):
                principled_bsdf_node = material.node_tree.nodes.get("Principled BSDF")
                principled_bsdf_node.inputs["Metallic"].default_value = 0.0
                principled_bsdf_node.inputs["Roughness"].default_value = 0.5
                principled_bsdf_node.inputs["Specular IOR Level"].default_value = 0.5
        return {'FINISHED'}

# Third operator: Remove Duplicate Vertices
class RemoveDuplicateVerticesOperator(bpy.types.Operator):
    bl_idname = "scene.remove_duplicate_vertices"
    bl_label = "Remove Duplicate Vertices"
    
    def execute(self, context):
        # Save current active object
        active_object = bpy.context.view_layer.objects.active

        # Create a list to hold mesh objects
        mesh_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        # If there are mesh objects, make the first one the active object
        if mesh_objects:
            bpy.context.view_layer.objects.active = mesh_objects[0]
        
        # Select all mesh objects
        for obj in mesh_objects:
            obj.select_set(True)
        
        # Enter Multi-Object Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Select All Vertices
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Run the "Merge by Distance" command
        bpy.ops.mesh.remove_doubles()
        
        # Return to Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Restore the active object
        bpy.context.view_layer.objects.active = active_object
        
        return {'FINISHED'}

# Panel to hold the buttons
class OBJECT_PT_SimplePanel(bpy.types.Panel):  # Renamed to follow convention
    bl_label = "Adjusts after Archicad import"
    bl_idname = "OBJECT_PT_SimplePanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("scene.add_gamma_node")
        layout.operator("scene.set_metallic_to_zero")
        layout.operator("scene.remove_duplicate_vertices")

# Register and Unregister functions
def register():
    bpy.utils.register_class(SimpleOperator1)
    bpy.utils.register_class(SimpleOperator2)
    bpy.utils.register_class(RemoveDuplicateVerticesOperator)
    bpy.utils.register_class(OBJECT_PT_SimplePanel)  # Renamed to follow convention
    
def unregister():
    bpy.utils.unregister_class(OBJECT_PT_SimplePanel)  # Renamed to follow convention
    bpy.utils.unregister_class(RemoveDuplicateVerticesOperator)
    bpy.utils.unregister_class(SimpleOperator2)
    bpy.utils.unregister_class(SimpleOperator1)

if __name__ == "__main__":
    register()
