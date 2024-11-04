
import bpy
import math
import sys
import os
from . import interpola
from bpy.props import FloatVectorProperty
from mathutils import noise

# Añadir la ruta donde se encuentran tus módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

bpy.types.Scene.tension = bpy.props.FloatProperty(
    name="Tension",
    description="Tensión para Catmull-Rom",
    default=0.5,
    min=0.0  # Sin límite superior
)

enum_items = [
    ('LINEAL', "Interpolacion lineal", "Interpola linealmente"),
    ('CATMULL-ROM', "Interpolacion Catmull-Rom", "Interpola usando Catmull-Rom"),
    ('HERMITE', "Interpolacion Hermite", "Interpola usando Hermite")
]

bpy.types.Scene.selected_shape = bpy.props.EnumProperty(
    name="Tipo de interpolación",
    description="Selecciona la interpolación",
    items=enum_items,
    default='LINEAL'
)

# Añadir una propiedad personalizada de velocidad a todos los objetos
bpy.types.Object.velocity = FloatVectorProperty(
    name="Velocity",
    description="Velocidad en el keyframe como un vector 3D",
    default=(0.0, 0.0, 0.0),  # Valor por defecto si no se especifica
    size=3  # Tamaño del vector (x, y, z)
)

def get_random_oscillation(frame, frequency, amplitude, axes):
    """
    Genera una oscilación aleatoria en los ejes especificados utilizando ruido.
    """
    t = frame * frequency
    osc_values = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
    
    # Genera el valor de ruido para cada eje especificado en `axes`
    if 'X' in axes:
        osc_values['X'] = amplitude * noise.noise([t, 0.0, 0.0])  # Ruido en el eje X
    if 'Y' in axes:
        osc_values['Y'] = amplitude * noise.noise([0.0, t, 0.0])  # Ruido en el eje Y
    if 'Z' in axes:
        osc_values['Z'] = amplitude * noise.noise([0.0, 0.0, t])  # Ruido en el eje Z
    
    return osc_values

# Ejercicio 2
def get_posicion_x_loop(frame):
    t = frame / 24.0  
    return 5 * math.cos(t)  # Radio de 5, centrado en el origen

def get_posicion_y_loop(frame):
    t = frame / 24.0
    return 5 * math.sin(t)  # Radio de 5, centrado en el origen

# Ejercicio 1
def get_posicion1(frm: float):
    t = frm / 24.0
    if t <= 0:
        posx = 0.0
    elif t <= 5.0:
        posx = 10.0 * t / 5.0
    else:
        posx = 10.0
    print(f"Frame: {frm}, Posición X: {posx}")
    return posx

# Ejercicio 3
def get_posicion2(frm, obj, coord):
    """Obtiene la posición interpolada según el frame y la interpolación seleccionada"""

    # Obtiene la curva de animación
    c = obj.animation_data.action.fcurves.find('location', index=coord)

    if not c:
        #print("Curva de animación no encontrada.")
        return 0.0

    # Si hay menos de dos keyframes, devolver la posición del único keyframe
    if len(c.keyframe_points) == 1:
        return c.keyframe_points[0].co[1]

    # Si el frame es menor que el primer keyframe, devolver el valor del primer keyframe
    if frm < c.keyframe_points[0].co[0]:
        #print("El frame está antes del primer keyframe.")
        return c.keyframe_points[0].co[1]

    # Si el frame es mayor que el último keyframe, devolver el valor del último keyframe
    if frm > c.keyframe_points[-1].co[0]:
        #print("El frame está después del último keyframe.")
        return c.keyframe_points[-1].co[1]

    prev_kf = None
    next_kf = None

    # Encontrar los dos keyframes entre los que se encuentra el frame actual
    for i in range(len(c.keyframe_points) - 1):
        kf1 = c.keyframe_points[i]
        kf2 = c.keyframe_points[i + 1]

        if kf1.co[0] <= frm <= kf2.co[0]:
            anterior_kf = c.keyframe_points[i - 1] if i > 0 else None
            prev_kf = kf1
            next_kf = kf2
            posterior_kf = c.keyframe_points[i + 2] if i + 2 < len(c.keyframe_points) else None
            break

    # Manejo de casos fuera de los keyframes
    if prev_kf is None or next_kf is None:
        print("El frame está fuera de los keyframes")
        return None  # Retornar None si el frame está fuera de los keyframes

    # Dependiendo del método de interpolación seleccionado, se elige el algoritmo
    selected_interpolation = bpy.context.scene.selected_shape

    if selected_interpolation == 'LINEAL':
        pos = interpola.lineal(frm, prev_kf.co[0], next_kf.co[0], prev_kf.co[1], next_kf.co[1])

    elif selected_interpolation == 'CATMULL-ROM':
        tension = bpy.context.scene.tension  # Obtener la tensión desde el panel
       
        if len(c.keyframe_points) >= 2:
            # Estos pueden ser keyframes anteriores y siguientes a los actuales
            p0 = anterior_kf.co[1] if anterior_kf is not None else prev_kf.co[1]
            p1 = prev_kf.co[1]
            p2 = next_kf.co[1]
            p3 = posterior_kf.co[1] if posterior_kf is not None else next_kf.co[1]

            # Lo mismo con los tiempos
            t0 = anterior_kf.co[0] if anterior_kf is not None else prev_kf.co[0]
            t1 = prev_kf.co[0]
            t2 = next_kf.co[0]
            t3 = posterior_kf.co[0] if posterior_kf is not None else next_kf.co[0]
           
            # Realizar la interpolación
            pos = interpola.catmull_rom(frm, t0, t1, t2, t3, p0, p1, p2, p3, tension)

    elif selected_interpolation == 'HERMITE':
        # Buscar la fCurve de velocidad del objeto
        velocity_fcurve = None
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                if fcurve.data_path == 'velocity':
                    velocity_fcurve = fcurve
                    break

        # Evaluar las velocidades en los keyframes previos y siguientes
        if velocity_fcurve is not None:
            v0 = velocity_fcurve.evaluate(prev_kf.co[0])  # Evaluar la velocidad en t0
            v1 = velocity_fcurve.evaluate(next_kf.co[0])  # Evaluar la velocidad en t1
        else:
            v0 = 0.0
            v1 = 0.0

        # Asegurarse de que t0 y t1 no son iguales para evitar división por cero en Hermite
        if prev_kf.co[0] != next_kf.co[0]:
            # Llamar a la función Hermite con las velocidades adecuadas
            pos = interpola.hermite(
                frm,                    # El tiempo del frame actual
                prev_kf.co[0],          # t0: tiempo del keyframe previo
                next_kf.co[0],          # t1: tiempo del keyframe siguiente
                prev_kf.co[1],          # p0: valor en el keyframe previo
                next_kf.co[1],          # p1: valor en el keyframe siguiente
                v0 * (next_kf.co[0] - prev_kf.co[0]),  # v0 ajustado al intervalo de tiempo entre t0 y t1
                v1 * (next_kf.co[0] - prev_kf.co[0])   # v1 ajustado al intervalo de tiempo entre t0 y t1
            )
            print("111111")

        else:
            # Si t0 y t1 son iguales, devuelve el valor del keyframe sin interpolación
            pos = prev_kf.co[1]

     # Obtener los valores de las propiedades de oscilación
    frecuencia = bpy.context.scene.oscillation_frequency
    amplitud = bpy.context.scene.oscillation_amplitude
    axis = bpy.context.scene.oscillation_axes

    osc_values = get_random_oscillation(frm, frecuencia, amplitud, axis)
    if coord == 0:  # Eje X
        pos += osc_values['X']
    elif coord == 1:  # Eje Y
        pos += osc_values['Y']
    elif coord == 2:  # Eje Z
        pos += osc_values['Z']

    return pos

def sincronizar_keyframes_velocidad(obj):
    """Sincroniza la velocidad con los keyframes de posición del objeto solo una vez para asignar valores iniciales."""
    # Comprobar si el objeto tiene datos de animación
    if not obj.animation_data or not obj.animation_data.action:
        print("El objeto no tiene datos de animación.")
        return

    # Recorrer todas las fCurves para encontrar las que son de 'location'
    fcurves_location = [fcurve for fcurve in obj.animation_data.action.fcurves if "location" in fcurve.data_path]
    
    if not fcurves_location:
        print("No se encontraron fCurves de ubicación.")
        return

    # Asumimos que tenemos las fcurves para x, y, z en la lista
    for i, fcurve in enumerate(fcurves_location):
        keyframes = fcurve.keyframe_points
        
        for k in range(len(keyframes) - 1):
            kf1 = keyframes[k]
            kf2 = keyframes[k + 1]
            
            frame1 = kf1.co[0]
            frame2 = kf2.co[0]
            
            pos1 = kf1.co[1]
            pos2 = kf2.co[1]
            
            # Calcular la velocidad como el cambio de posición dividido por el tiempo entre los keyframes
            tiempo = frame2 - frame1
            if tiempo != 0:
                velocidad = (pos2 - pos1) / tiempo
            else:
                velocidad = 0.0

            # Solo asignar la velocidad inicial al objeto
            obj.velocity[i] = velocidad

            # Insertar un keyframe para la propiedad de velocidad en el frame inicial
            obj.keyframe_insert(data_path="velocity", index=i, frame=frame1)

            print(f"Keyframe de velocidad insertado en frame {frame1}, velocidad: {velocidad} en coordenada {i}")


# Ejercicio 4
def asigna_driver_posicion(obj):
    for coord in range(3):
        print("coordenada:", coord)
        drv = obj.driver_add('location', coord).driver
        drv.use_self = True
        drv.expression = f"get_pos2(frame, self, {coord})"
       
        # Añadir una variable de dependencia para el driver, para que se actualice con selected_shape
        var = drv.variables.new()
        var.name = 'selected_shape'
        var.targets[0].id_type = 'SCENE'
        var.targets[0].id = bpy.context.scene
        var.targets[0].data_path = 'selected_shape'


# Panel personalizado
class OBJECT_PT_CustomPanel(bpy.types.Panel):
    bl_label = "Drivers Control"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Drivers Control"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Generación trayectoria interpolada")
        layout.prop(context.scene, "selected_shape", text="Elige una forma")

        if context.scene.selected_shape == 'CATMULL-ROM':
            layout.prop(context.scene, "tension", text="Tensión Catmull-Rom")

        if context.scene.selected_shape == 'HERMITE':
            obj = context.object
            if obj and hasattr(obj, "velocity"):
                layout.prop(obj, "velocity", text="Velocidad Hermite")


        layout.operator("object.create_trayectoria", text="Crear trayectoria")


class OBJECT_OT_CreateTrayectoria(bpy.types.Operator):
    bl_idname = "object.create_trayectoria"
    bl_label = "Crear Trayectoria"


    shape = bpy.props.EnumProperty(
        name="Tipo de interpolación",
        description="Selecciona la interpolación",
        items=enum_items,
        default='LINEAL'
    )
   
    def invoke(self, context, event):
        asigna_driver_posicion(context.object)
        sincronizar_keyframes_velocidad(context.object)
        bpy.ops.object.paths_calculate(display_type='RANGE', range='SCENE')
        bpy.ops.object.paths_update_visible()
        self.report({'INFO'}, "Trayectoria creada exitosamente")
        return {'FINISHED'}
   
    def execute(self, context):
        asigna_driver_posicion(context.object)
        sincronizar_keyframes_velocidad(context.object)
        bpy.ops.object.paths_calculate(display_type='RANGE', range='SCENE')
        bpy.ops.object.paths_update_visible()
        self.report({'INFO'}, "Trayectoria creada exitosamente")
        return {'FINISHED'}



class OBJECT_PT_VelocityPanel(bpy.types.Panel):
    bl_label = "Control de Velocidad"
    bl_idname = "OBJECT_PT_velocity_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'


    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj:
            layout.prop(obj, "velocity")


def register():
    bpy.app.driver_namespace['get_pos2'] = get_posicion2
    bpy.app.driver_namespace['get_pos1'] = get_posicion1
    bpy.app.driver_namespace['get_posicion_x_loop'] = get_posicion_x_loop
    bpy.app.driver_namespace['get_posicion_y_loop'] = get_posicion_y_loop

    bpy.utils.register_class(OBJECT_PT_CustomPanel)
    bpy.utils.register_class(OBJECT_OT_CreateTrayectoria)
    bpy.utils.register_class(OBJECT_PT_VelocityPanel)


    bpy.types.Scene.selected_shape = bpy.props.EnumProperty(
        name="Tipo de interpolación",
        description="Selecciona la interpolación",
        items=enum_items,
        default='LINEAL'
    )
    bpy.types.Scene.tension = bpy.props.FloatProperty(
        name="Tension",
        description="Tensión para Catmull-Rom",
        default=0.5,
        min=0.0
    )
    print("Definimos Drivers")

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_CustomPanel)
    bpy.utils.unregister_class(OBJECT_OT_CreateTrayectoria)
    bpy.utils.unregister_class(OBJECT_PT_VelocityPanel)
   
    # Desregistrar propiedades de Scene
    if hasattr(bpy.types.Scene, "selected_shape"):
        del bpy.types.Scene.selected_shape
    if hasattr(bpy.types.Scene, "tension"):
        del bpy.types.Scene.tension


if __name__ == "__main__":
    register()

    obj_activo = bpy.context.view_layer.objects.active

    if obj_activo:
        asigna_driver_posicion(obj_activo)
        print("drivers asignados")
    else:
        print("No hay obj activo / driver no asignado")
