import bpy
import random  
import mathutils

def CrearEdificio(altura, pos_x, pos_y, n_cube, sx, sy, sz):

    cubes = []

    for edif in range(n_cube):
        scale_x = random.uniform(min_scale, max_scale)
        scale_y = random.uniform(min_scale, max_scale)
        scale_z = random.uniform(min_scale, max_scale)
        
        shift_x = random.uniform(-scale_x/2, scale_x/2)
        shift_y = random.uniform(-scale_y/2, scale_y/2)
        shift_z = random.uniform(0.0, building_height - scale_z/2)

        
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            enter_editmode=False,
            align='WORLD',
            location=(shift_x, shift_y, shift_z),
            scale=(scale_x, scale_y, scale_z)
        )
               
        cubes.append(bpy.context.active_object)
        bpy.ops.transform.translate(value=(pos_x, pos_y, 0),
                                    orient_type='GLOBAL', 
                                    orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                    orient_matrix_type='GLOBAL',
                                    constraint_axis=(True, False, False),
                                    mirror=False,
                                    use_proportional_edit=False,
                                    proportional_edit_falloff='SMOOTH',
                                    proportional_size=1, use_proportional_connected=False,
                                    use_proportional_projected=False,
                                    snap=False, snap_elements={'INCREMENT'},
                                    use_snap_project=False,
                                    snap_target='CLOSEST',
                                    use_snap_self=True,
                                    use_snap_edit=True,
                                    use_snap_nonedit=True,
                                    use_snap_selectable=False)
                                    
        bpy.ops.transform.resize(value=(sx, sy, 1),
                                 orient_type='GLOBAL',
                                 orient_matrix=((1, 0, 0), (0, 1, 0),
                                 (0, 0, 1)),
                                 orient_matrix_type='GLOBAL',
                                 mirror=False,
                                 use_proportional_edit=False,
                                 proportional_edit_falloff='SMOOTH',
                                 proportional_size=1,
                                 use_proportional_connected=False,
                                 use_proportional_projected=False,
                                 snap=False,
                                 snap_elements={'INCREMENT'},
                                 use_snap_project=False,
                                 snap_target='CLOSEST', 
                                 use_snap_self=True, 
                                 use_snap_edit=True, 
                                 use_snap_nonedit=True, 
                                 use_snap_selectable=False)
                                 
        bpy.ops.transform.resize(value=(1, 1, sz), 
                                 orient_type='GLOBAL', 
                                 orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                                 orient_matrix_type='GLOBAL', 
                                 constraint_axis=(False, False, True), 
                                 mirror=False, 
                                 use_proportional_edit=False,
                                 proportional_edit_falloff='SMOOTH',
                                 proportional_size=1,
                                 use_proportional_connected=False, 
                                 use_proportional_projected=False, 
                                 snap=False, 
                                 snap_elements={'INCREMENT'}, 
                                 use_snap_project=False, 
                                 snap_target='CLOSEST', 
                                 use_snap_self=True, 
                                 use_snap_edit=True, 
                                 use_snap_nonedit=True, 
                                 use_snap_selectable=False)
                                 
        bpy.ops.transform.translate(value=(0, 0, sz/2),
                                   orient_type='GLOBAL', 
                                   orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                                   orient_matrix_type='GLOBAL', 
                                   constraint_axis=(False, False, True), 
                                   mirror=False, 
                                   use_proportional_edit=False, 
                                   proportional_edit_falloff='SMOOTH', 
                                   proportional_size=1, 
                                   use_proportional_connected=False, 
                                   use_proportional_projected=False, 
                                   snap=False, 
                                   snap_elements={'INCREMENT'}, 
                                   use_snap_project=False, 
                                   snap_target='CLOSEST', 
                                   use_snap_self=True, 
                                   use_snap_edit=True, 
                                   use_snap_nonedit=True, 
                                   use_snap_selectable=False)

    bpy.ops.object.select_all(action='DESELECT')

    for ob in cubes:
        ob.select_set(True)

    bpy.ops.object.join()
    
    return cubes
 
building_height = 10

min_scale = 0.8
max_scale = 1.5

tam_edif = 4
tam_calle = 2

sx = 1
sy = 1

n_cubes = 30

suma_pos_x = 0
suma_pos_y = 0
total_cubos = 0

numero_calles_x = 7
numero_calles_y = 7

#posiciones_edificios = []

centro_ciudad_x_y = (numero_calles_x * (tam_calle + tam_edif))/2 

def register():
    for i in range(numero_calles_x):
        for j in range(numero_calles_y):
            pos_x = i*(tam_edif + tam_calle) + (tam_edif/2)
            pos_y = j*(tam_edif + tam_calle) + (tam_edif/2)

            pos_x_y = mathutils.Vector((pos_x, pos_y))

            #posiciones_edificios.append(mathutils.Vector((pos_x, pos_y)))

            sz = random.uniform(5, 15)
            cubosLista = CrearEdificio(building_height, pos_x, pos_y, n_cubes, sx, sy, sz)

    velocidad = 1

    # Colocar un cubo en la posición central calculada
    bpy.ops.mesh.primitive_cube_add(
        enter_editmode=False, 
        align='WORLD', 
        location=(centro_ciudad_x_y, centro_ciudad_x_y, 0),  # Posición central
        scale=(30, 30, 4)  # Tamaño del cubo en el centro
    )      

def Borrar_Ciudad():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    print('BORRADA TODA LA CIUDAD')

if __name__ == "__main__":
    register()
    

