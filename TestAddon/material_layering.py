import bpy
import os

def create_logistic_function_node_group():

    # Check if the node group already exists
    node_group = bpy.data.node_groups.get("LST_LogisticFunction", None)
    if node_group != None:
        return node_group

    # Define a new node group
    node_group = bpy.data.node_groups.new("LST_LogisticFunction", "ShaderNodeTree")
    nodes = node_group.nodes

    # Add inputs and outputs to that node group
    node_group.inputs.new("NodeSocketFloat", "Value")
    node_group.inputs.new("NodeSocketFloat", "Midpoint")
    node_group.inputs.new("NodeSocketFloat", "Scale")
    node_group.outputs.new("NodeSocketFloat", "Value")

    # Create nodes in the node group
    group_inputs = nodes.new("NodeGroupInput")
    group_outputs = nodes.new("NodeGroupOutput")
    
    subtract_node = nodes.new("ShaderNodeMath")
    subtract_node.operation = "SUBTRACT"

    multiply_node = nodes.new("ShaderNodeMath")
    multiply_node.operation = "MULTIPLY"

    power_node = nodes.new("ShaderNodeMath")
    power_node.operation = "POWER"
    power_node.inputs[0].default_value = 2.71828

    add_node = nodes.new("ShaderNodeMath")
    add_node.operation = "ADD"
    add_node.inputs[0].default_value = 1

    divide_node = nodes.new("ShaderNodeMath")
    divide_node.operation = "DIVIDE"
    divide_node.inputs[0].default_value = 1

    # Connect the nodes in the node group
    node_group.links.new(group_inputs.outputs[0], subtract_node.inputs[1])
    node_group.links.new(group_inputs.outputs[1], subtract_node.inputs[0])
    node_group.links.new(group_inputs.outputs[2], multiply_node.inputs[1])

    node_group.links.new(subtract_node.outputs[0], multiply_node.inputs[0])
    node_group.links.new(multiply_node.outputs[0], power_node.inputs[1])
    node_group.links.new(power_node.outputs[0], add_node.inputs[1])
    node_group.links.new(add_node.outputs[0], divide_node.inputs[1])

    node_group.links.new(divide_node.outputs[0], group_outputs.inputs[0])

    return node_group

def create_landscape_material(depth, texture_scale):

    # Check if mat already exists
    material = bpy.data.materials.get("LST_LandscapeMaterial")
    if material != None:
        return material
    
    # Create a new material
    material = bpy.data.materials.new("LST_LandscapeMaterial")
    material.use_nodes = True
    node_tree = material.node_tree
    nodes = node_tree.nodes
    nodes.remove(nodes.get("Diffuse BSDF"))

    texture_coordinate = nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "LST_TexCoord"

    separate_xyz_generated = nodes.new("ShaderNodeSeparateXYZ")
    x_scaling = nodes.new("ShaderNodeMath")
    x_scaling.name = "LST_ScaleX"
    x_scaling.operation = "MULTIPLY"
    x_scaling.inputs[1].default_value = texture_scale
    y_scaling = nodes.new("ShaderNodeMath")
    y_scaling.name = "LST_ScaleY"
    y_scaling.operation = "MULTIPLY"
    y_scaling.inputs[1].default_value = texture_scale
    combine_xyz_generated = nodes.new("ShaderNodeCombineXYZ")
    combine_xyz_generated.name = "LST_UV_Input"

    separate_xyz_object = nodes.new("ShaderNodeSeparateXYZ")
    separate_xyz_object.name = "LST_SepXYZObject"

    divide_node = nodes.new("ShaderNodeMath")
    divide_node.name = "LST_Normalize"
    divide_node.operation = "DIVIDE"
    divide_node.inputs[1].default_value = depth

    ocean_node = nodes.new("ShaderNodeBsdfDiffuse")
    ocean_node.name = "LST_Ocean"
    ocean_node.inputs[0].default_value = (0,0,1,1)

    # Link nodes in material
    node_tree.links.new(texture_coordinate.outputs[0], separate_xyz_generated.inputs[0])
    node_tree.links.new(separate_xyz_generated.outputs[0], x_scaling.inputs[0])
    node_tree.links.new(separate_xyz_generated.outputs[1], y_scaling.inputs[0])

    node_tree.links.new(x_scaling.outputs[0], combine_xyz_generated.inputs[0])
    node_tree.links.new(y_scaling.outputs[0], combine_xyz_generated.inputs[1])
    node_tree.links.new(separate_xyz_generated.outputs[2], combine_xyz_generated.inputs[2])

    node_tree.links.new(texture_coordinate.outputs[3], separate_xyz_object.inputs[0])
    node_tree.links.new(separate_xyz_object.outputs[2], divide_node.inputs[0])

    return material

def create_layer_material(name, base_color_map=None, metallic_map=None, specular_map=None, roughness_map=None, normal_map=None):
    
    node_group = bpy.data.node_groups.get("LST_M_" + name)
    if node_group == None:
    
        # Define a new node group
        node_group = bpy.data.node_groups.new("LST_M_" + name, "ShaderNodeTree")
        nodes = node_group.nodes

        # Add inputs and outputs to that node group
        node_group.inputs.new("NodeSocketVector", "UV")
        node_group.outputs.new("NodeSocketShader", name + " Shader")

        # Create nodes in the node group
        group_inputs = nodes.new("NodeGroupInput")
        group_outputs = nodes.new("NodeGroupOutput")
        texture_base_color = nodes.new("ShaderNodeTexImage")
        if (base_color_map != None):
            texture_base_color.image = bpy.data.images.get(base_color_map)
        texture_metallic = nodes.new("ShaderNodeTexImage")
        if (metallic_map != None):
            texture_metallic.image = bpy.data.images.get(metallic_map)
        texture_specular = nodes.new("ShaderNodeTexImage")
        if (specular_map != None):
            texture_specular.image = bpy.data.images.get(specular_map)
        texture_roughness = nodes.new("ShaderNodeTexImage")
        if (roughness_map != None):
            texture_roughness.image = bpy.data.images.get(roughness_map)
        texture_normal = nodes.new("ShaderNodeTexImage")
        if (normal_map != None):
            texture_normal.image = bpy.data.images.get(normal_map)
        principled_shader = nodes.new("ShaderNodeBsdfPrincipled")

        # Connect the nodes in the node group
        node_group.links.new(group_inputs.outputs[0], texture_base_color.inputs[0])
        node_group.links.new(group_inputs.outputs[0], texture_metallic.inputs[0])
        node_group.links.new(group_inputs.outputs[0], texture_specular.inputs[0])
        node_group.links.new(group_inputs.outputs[0], texture_roughness.inputs[0])
        node_group.links.new(group_inputs.outputs[0], texture_normal.inputs[0])

        node_group.links.new(texture_base_color.outputs[0], principled_shader.inputs[0])
        node_group.links.new(texture_metallic.outputs[0], principled_shader.inputs[4])
        node_group.links.new(texture_specular.outputs[0], principled_shader.inputs[5])
        node_group.links.new(texture_roughness.outputs[0], principled_shader.inputs[7])
        node_group.links.new(texture_normal.outputs[0], principled_shader.inputs[17])

        node_group.links.new(principled_shader.outputs[0], group_outputs.inputs[0])

    material = bpy.data.materials.get("LST_M_" + name)
    if material == None:
        # Make a new material
        material = bpy.data.materials.new(name)
        material.use_nodes = True
        nodes = material.node_tree.nodes

        # Add the node group to the material
        group_node = nodes.new("ShaderNodeGroup")
        group_node.node_tree = node_group

    # Return the node group
    return node_group

def create_landscape_layer(index, name, start_height, end_height, blend_top=.05, blend_bottom=.05):

    material = bpy.data.materials.get("LST_LandscapeMaterial")
    if material == None:
        return -1
    
    nodes = material.node_tree.nodes
    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.name = "LST_Layer" + str(index) + "_ColorRamp"
    
    color_ramp.color_ramp.elements[0].position = clip(start_height - blend_bottom, 0, 1)
    color_ramp.color_ramp.elements[0].color = (1,1,1,0)
    color_ramp.color_ramp.elements[1].position = clip(start_height + blend_bottom, 0, 1)
    color_ramp.color_ramp.elements[1].color = (1,1,1,1)
    color_ramp.color_ramp.elements.new(clip(end_height + blend_top, 0, 1))
    color_ramp.color_ramp.elements[2].color = (1,1,1,1)
    color_ramp.color_ramp.elements.new(clip(end_height + blend_top, 0, 1))
    color_ramp.color_ramp.elements[3].color=(1,1,1,0)

    group_node = nodes.new("ShaderNodeGroup")
    group_node.name = "LST_Layer" + str(index) + "_Shader"
    material_group = bpy.data.node_groups.get("LST_M_" + name)
    if material_group == None:
        material_group = create_layer_material(name)
    group_node.node_tree = material_group

def update_landscape_layer(index, name, start_height, end_height, blend_top, blend_bottom):
    print("Update Landscape Layer...")
    material = bpy.data.materials.get("LST_LandscapeMaterial")
    if material == None:
        return -1
    
    nodes = material.node_tree.nodes
    group_node = nodes.get("LST_Layer" + str(index) + "_Shader")
    material_group = bpy.data.node_groups.get("LST_M_" + name)
    if material_group == None:
        material_group = create_layer_material(name)
    group_node.node_tree = material_group

    color_ramp = nodes.get("LST_Layer" + str(index) + "_ColorRamp")
    color_ramp.color_ramp.elements[0].position = clip(start_height - blend_bottom, 0, 1)
    color_ramp.color_ramp.elements[1].position = clip(start_height + blend_bottom, 0, 1)
    color_ramp.color_ramp.elements[2].position = clip(end_height - blend_top, 0, 1)
    color_ramp.color_ramp.elements[3].position = clip(end_height + blend_top, 0, 1)

def delete_landscape_layer(index, old_max_index):
    material = bpy.data.materials.get("LST_LandscapeMaterial")
    if material == None:
        return -1
    
    nodes = material.node_tree.nodes
    nodes.remove(nodes.get("LST_Layer" + str(index) + "_Shader"))
    nodes.remove(nodes.get("LST_Layer" + str(index) + "_ColorRamp"))
    nodes.remove(nodes.get("LST_Layer" + str(index) + "_MixShader"))

    for i in range(index, old_max_index):
        nodes.get("LST_Layer" + str(i + 1) + "_Shader").name="LST_Layer" + str(i) + "_Shader"
        nodes.get("LST_Layer" + str(i + 1) + "_ColorRamp").name="LST_Layer" + str(i) + "_ColorRamp"
        nodes.get("LST_Layer" + str(i + 1) + "_MixShader").name="LST_Layer" + str(i) + "_MixShader"
    
    link_landscape_layers(old_max_index)

def create_steepness_layer(name, threshold):
    material = bpy.data.materials.get("LST_LandscapeMaterial")
    if material == None:
        return -1
    
    node_tree = material.node_tree
    nodes = node_tree.nodes

    # Generate nodes in the material
    separate_xyz_generated = nodes.new("ShaderNodeSeparateXYZ")

    arccos_node = nodes.new("ShaderNodeMath")
    arccos_node.operation = "ARCCOSINE"
    arccos_node.inputs[1].default_value = 0.5

    multiply_node = nodes.new("ShaderNodeMath")
    multiply_node.operation = "MULTIPLY"
    multiply_node.name = "LST_Steepness_Multiply"
    multiply_node.inputs[0].default_value = threshold
    multiply_node.inputs[1].default_value = 0.017453

    logistic_node = nodes.new("ShaderNodeGroup")
    logistic_function = bpy.data.node_groups.get("LST_LogisticFunction")
    if logistic_function == None:
        logistic_function = create_logistic_function_node_group()
    logistic_node.node_tree = logistic_function
    logistic_node.inputs[2].default_value = 7.5

    material_node = nodes.new("ShaderNodeGroup")
    material_node.name = "LST_Steepness_Shader"
    material_group = bpy.data.node_groups.get("LST_M_" + name)
    if material_group == None:
        material_group = create_layer_material(name)
    material_node.node_tree = material_group

    mix_shader = nodes.new("ShaderNodeMixShader")
    mix_shader.name = "LST_Steepness_Mix_Shader"

    # Link the nodes
    node_tree.links.new(nodes.get("LST_TexCoord").outputs[1], separate_xyz_generated.inputs[0])
    node_tree.links.new(nodes.get("LST_UV_Input").outputs[0], material_node.inputs[0])
    node_tree.links.new(separate_xyz_generated.outputs[2], arccos_node.inputs[0])
    node_tree.links.new(arccos_node.outputs[0], logistic_node.inputs[0])
    node_tree.links.new(multiply_node.outputs[0], logistic_node.inputs[1])
    node_tree.links.new(logistic_node.outputs[0], mix_shader.inputs[0])
    node_tree.links.new(material_node.outputs[0], mix_shader.inputs[2])
    node_tree.links.new(mix_shader.outputs[0], nodes.get("Material Output").inputs[0])
    
def update_steepness_layer(name, threshold):
    print("Update Steepness Layer...")
    material = bpy.data.materials.get("LST_LandscapeMaterial")
    if material == None:
        return -1
    
    nodes = material.node_tree.nodes
    multiply_node = nodes.get("LST_Steepness_Multiply")
    multiply_node.inputs[0].default_value = threshold

    group_node = nodes.get("LST_Steepness_Shader")
    material_group = bpy.data.node_groups.get("LST_M_" + name)
    if material_group == None:
        material_group = create_layer_material(name)
    group_node.node_tree = material_group

def update_landscape_textures(texture_scale):
    material = bpy.data.materials.get("LST_LandscapeMaterial")
    if material == None:
        return -1
    
    nodes = material.node_tree.nodes
    scale_x = nodes.get("LST_ScaleX")
    scale_x.inputs[1].default_value = texture_scale
    scale_y = nodes.get("LST_ScaleY")
    scale_y.inputs[1].default_value = texture_scale

def link_landscape_layers(num_layers):
    for layer in range(num_layers):
        material = bpy.data.materials.get("LST_LandscapeMaterial")
        node_tree = material.node_tree
        nodes = node_tree.nodes
        node_tree.links.new(nodes.get("LST_Normalize").outputs[0], nodes.get("LST_Layer" + str(layer) + "_ColorRamp").inputs[0])
        node_tree.links.new(nodes.get("LST_UV_Input").outputs[0], nodes.get("LST_Layer" + str(layer) + "_Shader").inputs[0])
        
        mix_shader = nodes.get("LST_Layer" + str(layer) + "_MixShader")
        if mix_shader == None:
            mix_shader = nodes.new("ShaderNodeMixShader")
            mix_shader.name = "LST_Layer" + str(layer) + "_MixShader"
        
        node_tree.links.new(nodes.get("LST_Layer" + str(layer) + "_Shader").outputs[0], mix_shader.inputs[2])
        node_tree.links.new(nodes.get("LST_Layer" + str(layer) + "_ColorRamp").outputs[1], mix_shader.inputs[0])

        if layer == 0:
            node_tree.links.new(nodes.get("LST_Ocean").outputs[0], mix_shader.inputs[1])
        if layer != 0:
            node_tree.links.new(nodes.get("LST_Layer" + str(layer - 1) + "_MixShader").outputs[0], mix_shader.inputs[1])
        if layer == num_layers - 1:
            node_tree.links.new(mix_shader.outputs[0], nodes.get("LST_Steepness_Mix_Shader").inputs[1])

def load_default_layer_materials():
    filepath = os.path.dirname(os.path.abspath(__file__)) + "\\tex\\"
    for filename in [
        "grass\\lst_grass_albedo.png", "grass\\lst_grass_normal.png", "grass\\lst_grass_roughness.png",
        "rock\\lst_rock_albedo.png", "rock\\lst_rock_metallic.png", "rock\\lst_rock_normal.png", "rock\\lst_rock_roughness.png",
        "sand\\lst_sand_albedo.png", "sand\\lst_sand_normal.png", "sand\\lst_sand_specular.png",
        "snow\\lst_snow_albedo.jpg", "snow\\lst_snow_normal.jpg", "snow\\lst_snow_roughness.jpg",
        "gravel\\lst_gravel_albedo.png", "gravel\\lst_gravel_metallic.png", "gravel\\lst_gravel_normal.png", "gravel\\lst_gravel_roughness.png"]:
        bpy.ops.image.open(filepath=filepath+filename)
        trunc = filename.split("\\")[1]
        img = bpy.data.images.get(trunc)
        tex = bpy.data.textures.new(trunc, "IMAGE")
        tex.image = img
    create_layer_material("Snow", base_color_map="lst_snow_albedo.jpg", normal_map="lst_snow_normal.jpg", roughness_map="lst_snow_roughness.jpg")
    create_layer_material("Grass", base_color_map="lst_grass_albedo.png", normal_map="lst_grass_normal.png", roughness_map="lst_grass_roughness.png")
    create_layer_material("Rock", base_color_map="lst_rock_albedo.png", metallic_map="lst_rock_metallic.png", normal_map="lst_rock_normal.png", roughness_map="lst_rock_roughness.png")
    create_layer_material("Sand", base_color_map="lst_sand_albedo.png", normal_map="lst_sand_normal.png", specular_map="lst_sand_specular.png")
    create_layer_material("Gravel", base_color_map="lst_gravel_albedo.png", metallic_map="lst_gravel_metallic.png", normal_map="lst_gravel_normal.png", roughness_map="lst_gravel_roughness.png")

def link_selection_to_material(context):
    active_object = context.active_object
    material = bpy.data.materials.get("LST_LandscapeMaterial")
    if material == None:
        return -1
    
    if active_object.data.materials:
        active_object.data.materials[0] = material
    else:
        active_object.data.materials.append(material)

def clip(val, mini, maxi):
    return min(maxi, max(mini, val))