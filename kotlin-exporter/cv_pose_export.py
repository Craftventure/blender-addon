def writeString(file, string):
    file.write(bytes(string, 'UTF-8'))


def do_export(context, props, filepath):
    file = open(filepath, "wb")

    DEG2RAD = 57.29577951

    for current_obj in context.selected_objects:
        if current_obj.type == 'CURVE':
            writeString(file,
                        "SplinedTrackSegment " + current_obj.data.name + " = SplinedTrackSegment(trackedRide);\n")

            xOffset = current_obj.matrix_world.to_translation().x
            yOffset = current_obj.matrix_world.to_translation().y
            zOffset = current_obj.matrix_world.to_translation().z

            writeString(file, current_obj.data.name + ".add(offset")

            for spline in current_obj.data.splines:
                for bezier_point in spline.bezier_points:
                    writeString(file, ",\n  SplineNode(SplineHandle(%f, %f, %f),\n" % (
                        bezier_point.handle_left[0] + xOffset, bezier_point.handle_left[2] + zOffset,
                        -bezier_point.handle_left[1] + yOffset))
                    writeString(file, "     SplineHandle(%f, %f, %f),\n" % (
                        bezier_point.co[0] + xOffset, bezier_point.co[2] + zOffset, -bezier_point.co[1] + yOffset))
                    writeString(file, "     SplineHandle(%f, %f, %f), %f)" % (
                        bezier_point.handle_right[0] + xOffset, bezier_point.handle_right[2] + zOffset,
                        -bezier_point.handle_right[1] + yOffset, -(bezier_point.tilt * DEG2RAD)))

            writeString(file, ");\n")

            writeString(file, "\n")

    file.flush()
    file.close()
    return True

bl_info = {
    'name': 'Craftventure Exporter',
    'author': 'Joeywp',
    'version': (1, 0, 0),
    'blender': (2, 80, 0),
    'location': 'File > Export > Craftventure.kotlin (.kt)',
    'description': 'Export Craftventure.kotlin scenes (.kt)',
    'category': 'Import-Export'}

# if "bpy" in locals():
#     import importlib
#
#     if "import_obj" in locals():
#         importlib.reload(import_obj)
#     if "export_kt" in locals():
#         importlib.reload(export_obj)

import bpy
from bpy_extras.io_utils import (
    ExportHelper,
    orientation_helper,
    path_reference_mode,
    axis_conversion,
)
import time
import bpy


@orientation_helper(axis_forward='-Z', axis_up='Y')
class ExportKT(bpy.types.Operator, ExportHelper):
    """Save a Craftventure Kotlin File"""

    bl_idname = "export_scene.kt"
    bl_label = 'Export KT'
    bl_options = {'PRESET'}

    filename_ext = ".kt"

    def execute(self, context):
        start_time = time.time()
        print('\n_____START_____')
        props = self.properties
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        exported = do_export(context, props, filepath)

        if exported:
            print('finished export in %s seconds' % ((time.time() - start_time)))
            print(filepath)

        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(ExportKT.bl_idname, text="Kotlin (.kt)")


classes = (
    ExportKT,
)


def writeString(file, string):
    file.write(bytes(string, 'UTF-8'))


def do_export(context, props, filepath):
    file = open(filepath, "wb")

    DEG2RAD = 57.29577951

    for current_obj in context.selected_objects:
        if current_obj.type == 'CURVE':
            writeString(file,
                        "SplinedTrackSegment " + current_obj.data.name + " = SplinedTrackSegment(trackedRide)\n")

            xOffset = current_obj.matrix_world.to_translation().x
            yOffset = current_obj.matrix_world.to_translation().y
            zOffset = current_obj.matrix_world.to_translation().z

            writeString(file, current_obj.data.name + ".add(offset")

            for spline in current_obj.data.splines:
                for bezier_point in spline.bezier_points:
                    writeString(file, ",\n  SplineNode(SplineHandle(%f, %f, %f),\n" % (
                        bezier_point.handle_left[0] + xOffset, bezier_point.handle_left[2] + zOffset,
                        -bezier_point.handle_left[1] + yOffset))
                    writeString(file, "     SplineHandle(%f, %f, %f),\n" % (
                        bezier_point.co[0] + xOffset, bezier_point.co[2] + zOffset, -bezier_point.co[1] + yOffset))
                    writeString(file, "     SplineHandle(%f, %f, %f), %f)" % (
                        bezier_point.handle_right[0] + xOffset, bezier_point.handle_right[2] + zOffset,
                        -bezier_point.handle_right[1] + yOffset, -(bezier_point.tilt * DEG2RAD)))

            writeString(file, ")\n")

            writeString(file, "\n")

    file.flush()
    file.close()
    return True


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
