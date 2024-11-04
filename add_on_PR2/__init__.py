bl_info = {
    "name": "Control Velocidad Esfera",
    "blender": (2, 93, 0),
    "category": "Object",
    "author": "Grupo 05",
    "description": "Panel para controlar la velocidad de la esfera",
    "version": (1, 0, 0),
    "location": "View3D > Tool Shel7f > Control de Esfera",
}

import bpy
import random
from . import generar_ciudad
from . import posicion
from . import interpola


# Definir propiedad para controlar la velocidad de la esfera
bpy.types.Scene.velocidad_esfera = bpy.props.FloatProperty(
    name="Velocidad de la Esfera",
    description="Controla la velocidad a la que se mueve la esfera",
    default=1.0,
    min=0.1,
    max=20.0
)

# Registrar la propiedad de número de esferas
bpy.types.Scene.num_esferas = bpy.props.IntProperty(
    name="Número de Esferas",
    description="Define el número de esferas a crear",
    default=1,
    min=1,
    max=10
)

bpy.types.Scene.nturns = bpy.props.IntProperty(
    name="Número de giros ",
    description="Define el número de giros en la ruta",
    default=1,
    min=1,
    max=10
)

bpy.types.Scene.apply_random_oscillation = bpy.props.BoolProperty(
    name="Aplicar Oscilación Aleatoria",
    description="Activar o desactivar oscilación aleatoria",
    default=False
)

bpy.types.Scene.oscillation_axes = bpy.props.EnumProperty(
    name="Ejes de Oscilación",
    description="Selecciona los ejes de aplicación de la oscilación",
    items=[('X', "Eje X", ""), ('Y', "Eje Y", ""), ('Z', "Eje Z", "")],
    options={'ENUM_FLAG'}
)

bpy.types.Scene.oscillation_amplitude = bpy.props.FloatProperty(
    name="Amplitud de Oscilación",
    description="Define la amplitud de la oscilación aleatoria",
    default=1.0,
    min=0.0,
    max=10.0
)

bpy.types.Scene.oscillation_frequency = bpy.props.FloatProperty(
    name="Frecuencia de Oscilación",
    description="Define la frecuencia de la oscilación aleatoria",
    default=0.1,
    min=0.0,
    max=5.0
)
bpy.types.Scene.numero_calles_x_y = bpy.props.IntProperty(
    name="Calles en X",
    description="Número de calles en el eje X",
    default=7,
    min=1,
    max=20
)

bpy.types.Scene.numero_calles_y = bpy.props.IntProperty(
    name="Calles en Y",
    description="Número de calles en el eje Y",
    default=7,
    min=1,
    max=20
)

def crea_ruta(nturns: int, N: int):
    """ Crea una ruta aleatoria de nturns giros en una cuadrícula de NxN """
    # Listado de calles a elegir
    calles = set(range(N+1))

    i = 0
    j = 0
    posns = []

    # Elegimos al azar si la primera posición es en fila o columna
    fila = random.choice([True, False])
    for turn in range(nturns + 1):
        if fila:
            fila = False
            # Elección aleatoria de la siguiente calle
            i = random.choice(list(calles - {i}))
        else:
            fila = True
            # Elección aleatoria de la siguiente calle
            j = random.choice(list(calles - {j}))
        posns.append([i, j])

    # Forzamos que acabe en la última calle
    if fila:
        i = N
    else:
        j = N

    posns.append([i, j])

    return posns

def aplicar_configuracion_ciudad():
    generar_ciudad.numero_calles_x = bpy.context.scene.numero_calles_x_y
    generar_ciudad.numero_calles_y = bpy.context.scene.numero_calles_x_y
    generar_ciudad.Borrar_Ciudad()  # Genera la ciudad con los nuevos valores
    generar_ciudad.register()  # Genera la ciudad con los nuevos valores

def CrearEsferas(velocidad, nturns):
    fps = bpy.context.scene.render.fps  # Obtener la cantidad de frames por segundo (FPS)
    tiempo_por_calle = fps / velocidad  # Calcular el tiempo en frames para recorrer una calle
    posiciones = []
    
    direccion = random.randint(0, 3) #harexmos 0 N-S y 1 E-O

    if direccion == 0:
        calle_x = random.randint(0, generar_ciudad.numero_calles_x)

        # Calcular la posición de la esfera entre dos valores consecutivos de X
        pos_esfera_x = -2 + (calle_x * generar_ciudad.tam_calle) + (calle_x * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)
        pos_esfera_fin = -2 + (generar_ciudad.numero_calles_y * generar_ciudad.tam_calle) + (generar_ciudad.numero_calles_y * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)

        altura = random.uniform(5, 15)

        # Crear esfera
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1,
                                            enter_editmode=False, 
                                            align='WORLD',
                                            location=(pos_esfera_x, 0, altura),  # Posición inicial
                                            scale=(1, 1, 1))
        
        print('Esfera creada en X -->', pos_esfera_x)
        
        esfera = bpy.context.active_object

        # Redimensionar la esfera
        bpy.ops.transform.resize(value=(generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75),
                                orient_type='GLOBAL',
                                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                orient_matrix_type='GLOBAL',
                                mirror=False, 
                                use_proportional_edit=False,
                                proportional_edit_falloff='SMOOTH',
                                proportional_size=1,
                                use_proportional_connected=False,
                                use_proportional_projected=False,
                                snap=False)

        # Añadir el modificador de Subdivision Surface
        mod = esfera.modifiers.new(name="Subdivision", type='SUBSURF')
        mod.levels = 2  # Nivel de subdivisión en la vista
        mod.render_levels = 3  # Nivel de subdivisión en el render

      # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier="Subdivision")
        posiciones = crea_ruta( nturns ,generar_ciudad.numero_calles_x)
        # Insertar fotogramas clave en cada posición de posns
        for index, pos in enumerate(posiciones):
            frame = 1 + int(index * tiempo_por_calle)  # Calcular el frame para cada punto en la ruta
            bpy.context.scene.frame_set(frame)
            esfera.location = (pos[0] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, pos[1] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, altura)  # Configurar la posición de la esfera en el punto actual
            
            print('Pos_X -->', pos[0] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2)
            print('Pos_Y -->', pos[1] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2)

            esfera.keyframe_insert(data_path="location", index=-1)  # Insertar fotograma clave para la posición

        bpy.context.view_layer.objects.active = esfera  
        bpy.ops.object.create_trayectoria()  # Llama al operador


    
    elif direccion == 1:
        calle_y = random.randint(0, generar_ciudad.numero_calles_y)

        # Calcular la posición de la esfera entre dos valores consecutivos de X
        pos_esfera_y = -2 + (calle_y * generar_ciudad.tam_calle) + (calle_y * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)
        pos_esfera_fin = -2 + (generar_ciudad.numero_calles_x * generar_ciudad.tam_calle) + (generar_ciudad.numero_calles_x * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)

        altura = random.uniform(5, 15)

        # Crear esfera
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1,
                                            enter_editmode=False, 
                                            align='WORLD',
                                            location=(0, pos_esfera_y, altura),  # Posición inicial
                                            scale=(1, 1, 1))
        
        print('Esfera creada en X -->', pos_esfera_y)
        
        esfera = bpy.context.active_object

        # Redimensionar la esfera
        bpy.ops.transform.resize(value=(generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75),
                                orient_type='GLOBAL',
                                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                orient_matrix_type='GLOBAL',
                                mirror=False, 
                                use_proportional_edit=False,
                                proportional_edit_falloff='SMOOTH',
                                proportional_size=1,
                                use_proportional_connected=False,
                                use_proportional_projected=False,
                                snap=False)

        # Añadir el modificador de Subdivision Surface
        mod = esfera.modifiers.new(name="Subdivision", type='SUBSURF')
        mod.levels = 2  # Nivel de subdivisión en la vista
        mod.render_levels = 3  # Nivel de subdivisión en el render

        # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier="Subdivision")

         # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier="Subdivision")
        posiciones = crea_ruta( nturns ,generar_ciudad.numero_calles_x)        # Insertar fotogramas clave en cada posición de posns
        for index, pos in enumerate(posiciones):
            frame = 1 + int(index * tiempo_por_calle)  # Calcular el frame para cada punto en la ruta
            bpy.context.scene.frame_set(frame)
            esfera.location = (pos[0] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, pos[1] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, altura)  # Configurar la posición de la esfera en el punto actual
            
            print('Pos_X -->', pos[0] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2)
            print('Pos_Y -->', pos[1] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2)

            esfera.keyframe_insert(data_path="location", index=-1)  # Insertar fotograma clave para la posición

        bpy.context.view_layer.objects.active = esfera  
        bpy.ops.object.create_trayectoria()  # Llama al operador


    #O-E
    elif direccion == 2:
        calle_y = random.randint(0, generar_ciudad.numero_calles_y)

        # Calcular la posición de la esfera entre dos valores consecutivos de X
        pos_esfera_y = -2 + (calle_y * generar_ciudad.tam_calle) + (calle_y * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)
        pos_esfera_fin = (generar_ciudad.numero_calles_x * generar_ciudad.tam_calle) + (generar_ciudad.numero_calles_x * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)

        altura = random.uniform(5, 15)

        # Crear esfera
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1,
                                            enter_editmode=False, 
                                            align='WORLD',
                                            location=(0, pos_esfera_y, altura),  # Posición inicial
                                            scale=(1, 1, 1))
        
        print('Esfera creada en X -->', pos_esfera_y)
        
        esfera = bpy.context.active_object

        # Redimensionar la esfera
        bpy.ops.transform.resize(value=(generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75),
                                orient_type='GLOBAL',
                                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                orient_matrix_type='GLOBAL',
                                mirror=False, 
                                use_proportional_edit=False,
                                proportional_edit_falloff='SMOOTH',
                                proportional_size=1,
                                use_proportional_connected=False,
                                use_proportional_projected=False,
                                snap=False)

        # Añadir el modificador de Subdivision Surface
        mod = esfera.modifiers.new(name="Subdivision", type='SUBSURF')
        mod.levels = 2  # Nivel de subdivisión en la vista
        mod.render_levels = 3  # Nivel de subdivisión en el render

        # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier="Subdivision")

        # Establecer el frame a 50 y agregar el fotograma clave al final de la calle
       # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier="Subdivision")
        posiciones = crea_ruta( nturns ,generar_ciudad.numero_calles_x)
        # Insertar fotogramas clave en cada posición de posns
        for index, pos in enumerate(posiciones):
            frame = 1 + int(index * tiempo_por_calle)  # Calcular el frame para cada punto en la ruta
            bpy.context.scene.frame_set(frame)
            esfera.location = (pos[0] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, pos[1] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, altura)  # Configurar la posición de la esfera en el punto actual
            
            print('Pos_X -->', pos[0] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2)
            print('Pos_Y -->', pos[1] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2)

            esfera.keyframe_insert(data_path="location", index=-1)  # Insertar fotograma clave para la posición

        bpy.context.view_layer.objects.active = esfera  
        bpy.ops.object.create_trayectoria()  # Llama al operador

    elif direccion == 3:
        calle_x = random.randint(0, generar_ciudad.numero_calles_x)

        # Calcular la posición de la esfera entre dos valores consecutivos de X
        pos_esfera_x = -2 + (calle_x * generar_ciudad.tam_calle) + (calle_x * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)
        pos_esfera_fin = -2 + (generar_ciudad.numero_calles_y * generar_ciudad.tam_calle) + (generar_ciudad.numero_calles_y * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)

        altura = random.uniform(5, 15)

        # Crear esfera
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1,
                                            enter_editmode=False, 
                                            align='WORLD',
                                            location=(pos_esfera_x, 0, altura),  # Posición inicial
                                            scale=(1, 1, 1))
        
        print('Esfera creada en X -->', pos_esfera_x)
        
        esfera = bpy.context.active_object

        # Redimensionar la esfera
        bpy.ops.transform.resize(value=(generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75),
                                orient_type='GLOBAL',
                                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                orient_matrix_type='GLOBAL',
                                mirror=False, 
                                use_proportional_edit=False,
                                proportional_edit_falloff='SMOOTH',
                                proportional_size=1,
                                use_proportional_connected=False,
                                use_proportional_projected=False,
                                snap=False)

        # Añadir el modificador de Subdivision Surface
        mod = esfera.modifiers.new(name="Subdivision", type='SUBSURF')
        mod.levels = 2  # Nivel de subdivisión en la vista
        mod.render_levels = 3  # Nivel de subdivisión en el render

        # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier="Subdivision")

        # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier="Subdivision")
        posiciones = crea_ruta( nturns ,generar_ciudad.numero_calles_x)
        # Insertar fotogramas clave en cada posición de posns
        for index, pos in enumerate(posiciones):
            frame = 1 + int(index * tiempo_por_calle)  # Calcular el frame para cada punto en la ruta
            bpy.context.scene.frame_set(frame)
            esfera.location = (pos[0] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, pos[1] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, altura)  # Configurar la posición de la esfera en el punto actual
            
            print('Pos_X -->', pos[0] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2)
            print('Pos_Y -->', pos[1] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2)

            esfera.keyframe_insert(data_path="location", index=-1)  # Insertar fotograma clave para la posición

        bpy.context.view_layer.objects.active = esfera  
        bpy.ops.object.create_trayectoria()  # Llama al operador

class OBJECT_OT_Crear_Mov_Esfera(bpy.types.Operator):
    bl_idname = "object.crear_mov_esfera"
    bl_label = "Crear Trayectoria"

    def invoke(self, context, event):
        velocidad = bpy.context.scene.velocidad_esfera
        num_esferas = bpy.context.scene.num_esferas
        nturns =  bpy.context.scene.nturns

        # Crear esferas en un bucle
        for i in range(num_esferas):
            CrearEsferas(velocidad, nturns)
            print(f"Esfera {i+1} creada")

        self.report({'INFO'}, f"{num_esferas} esferas creadas exitosamente")
        return {'FINISHED'}


# Operador para borrar todas las esferas
class OBJECT_OT_Borrar_Esferas(bpy.types.Operator):
    bl_idname = "object.borrar_esferas"
    bl_label = "Borrar Todas las Esferas"

    def execute(self, context):
        # Recorrer todos los objetos de la escena y eliminar las esferas
        for obj in bpy.context.scene.objects:
            if obj.name.startswith("Sphere"):
                bpy.data.objects.remove(obj, do_unlink=True)
        
        self.report({'INFO'}, "Todas las esferas han sido borradas")
        return {'FINISHED'}

# Panel personalizado para controlar las esferas
class OBJECT_PT_VelocidadEsferaPanel(bpy.types.Panel):
    bl_label = "Control de Esfera"
    bl_idname = "OBJECT_PT_velocidad_esfera_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Control de Esfera"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Configuración de la ciudad
        layout.label(text="Configuración de la Ciudad")
        layout.prop(scene, "numero_calles_x_y", text="Número de Calles")
        layout.operator("object.aplicar_configuracion_ciudad", text="Aplicar Configuración de Ciudad")

        # Control de las esferas existente
        layout.label(text="Controlador de las Esferas")
        layout.prop(scene, "velocidad_esfera", text="Velocidad")
        layout.prop(scene, "num_esferas", text="Número de Esferas")
        layout.prop(scene, "nturns", text="Número de Giros")
        layout.prop(scene, "apply_random_oscillation", text="Oscilación Aleatoria")

        if scene.apply_random_oscillation:
            layout.prop(scene, "oscillation_axes", text="Ejes")
            layout.prop(scene, "oscillation_amplitude", text="Amplitud")
            layout.prop(scene, "oscillation_frequency", text="Frecuencia")

        layout.operator("object.crear_mov_esfera", text="Crear Esferas")
        layout.operator("object.borrar_esferas", text="Borrar Todas las Esferas")

# Operador para aplicar la configuración de la ciudad
class OBJECT_OT_AplicarConfiguracionCiudad(bpy.types.Operator):
    bl_idname = "object.aplicar_configuracion_ciudad"
    bl_label = "Aplicar Configuración de Ciudad"

    def execute(self, context):
        aplicar_configuracion_ciudad()
        self.report({'INFO'}, "Ciudad configurada con éxito")
        return {'FINISHED'}
    
def register():
    # Registra solo las clases específicas de __init__.py
    bpy.utils.register_class(OBJECT_PT_VelocidadEsferaPanel)
    bpy.utils.register_class(OBJECT_OT_Crear_Mov_Esfera)
    bpy.utils.register_class(OBJECT_OT_Borrar_Esferas)
    bpy.utils.register_class(OBJECT_OT_AplicarConfiguracionCiudad)

    # Registra el módulo posicion
    posicion.register()


def unregister():
    # Desregistra clases específicas de __init__.py
    try:
        bpy.utils.unregister_class(OBJECT_PT_VelocidadEsferaPanel)
    except RuntimeError:
        pass
    try:
        bpy.utils.unregister_class(OBJECT_OT_AplicarConfiguracionCiudad)
    except RuntimeError:
        pass
    try:
        bpy.utils.unregister_class(OBJECT_OT_Crear_Mov_Esfera)
    except RuntimeError:
        pass

    try:
        bpy.utils.unregister_class(OBJECT_OT_Borrar_Esferas)
    except RuntimeError:
        pass

    try:
        posicion.unregister()    
    except RuntimeError:
        pass
    

if __name__ == "__main__":
    unregister()
    register()
