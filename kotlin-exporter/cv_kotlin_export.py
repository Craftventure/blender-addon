bl_info = {
    'name': 'Craftventure Exporter',
    'author': 'Joeywp',
    'version': (1, 0, 0),
    'blender': (2, 90, 1),
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

import json
import time

import bpy
from bpy_extras.io_utils import (
    ExportHelper,
    orientation_helper,
)


@orientation_helper(axis_forward='-Z', axis_up='Y')
class ExportKT(bpy.types.Operator, ExportHelper):
    """Save a Craftventure Kotlin File"""

    bl_idname = "export_scene.kt"
    bl_label = 'Export KT'
    bl_options = {'PRESET'}

    filename_ext = ".kt"

    def execute(self, context):
        start_time = time.time()
        print('\n_____START KOTLIN_____')
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


def remove_prefix(text, prefix):
    return text[len(prefix):] if text.startswith(prefix) else text


def writeString(file, string):
    file.write(bytes(string, 'UTF-8'))


def do_export(context, props, filepath):
    file = open(filepath, "wb")

    DEG2RAD = 57.29577951

    export = {}

    # bpy.data.curves[0].custom_tracked_ride_spline_type = "SplinedTrackSegment"

    # for current_obj in context.selected_objects:
    #     if current_obj.type == 'CURVE':
    #         # current_obj["custom_tracked_ride_spline_type"] = "SplinedTrackSegment"
    #         print(current_obj.data.custom_tracked_ride_spline_type)
    #
    #         # current_obj.trackedRideSplineType = "SplinedTrackSegment"
    #         writeString(file, "val " + current_obj.data.name + " = SplinedTrackSegment(trackedRide)\n")
    #
    #         xOffset = current_obj.matrix_world.to_translation().x
    #         yOffset = current_obj.matrix_world.to_translation().y
    #         zOffset = current_obj.matrix_world.to_translation().z
    #
    #         writeString(file, current_obj.data.name + ".add(offset")
    #
    #         for spline in current_obj.data.splines:
    #             for bezier_point in spline.bezier_points:
    #                 writeString(file, ",\n  SplineNode(SplineHandle(%f, %f, %f),\n" % (
    #                     bezier_point.handle_left[0] + xOffset, bezier_point.handle_left[2] + zOffset,
    #                     -bezier_point.handle_left[1] + yOffset))
    #                 writeString(file, "     SplineHandle(%f, %f, %f),\n" % (
    #                     bezier_point.co[0] + xOffset, bezier_point.co[2] + zOffset, -bezier_point.co[1] + yOffset))
    #                 writeString(file, "     SplineHandle(%f, %f, %f), %f)" % (
    #                     bezier_point.handle_right[0] + xOffset, bezier_point.handle_right[2] + zOffset,
    #                     -bezier_point.handle_right[1] + yOffset, -(bezier_point.tilt * DEG2RAD)))
    #         writeString(file, ")\n")
    #         writeString(file, "\n")

    # for current_obj in context.selected_objects:
    #     if current_obj.type == 'MESH':
    #         if (current_obj.name.startswith("node")):
    #             writeString(file, "val %s = SimpleArea(\"world\", %f, %f, %f, %f, %f, %f) // node\n" % (
    #                 remove_prefix(current_obj.name, "node_"),
    #                 current_obj.location.x - (current_obj.dimensions.x * 0.5),
    #                 current_obj.location.z - (current_obj.dimensions.z * 0.5),
    #                 current_obj.location.y - (current_obj.dimensions.y * 0.5),
    #                 current_obj.location.x + (current_obj.dimensions.x * 0.5),
    #                 current_obj.location.z + (current_obj.dimensions.z * 0.5),
    #                 current_obj.location.y + (current_obj.dimensions.y * 0.5)
    #             ))
    #
    # writeString(file, "\n")

    for current_obj in context.selected_objects:
        if current_obj.type == 'MESH':
            if (current_obj.name.startswith("node")):
                export.setdefault("nodes", [])
                # writeString(file,
                #             "val %s = navigation.createNode(where = Vector(%f, %f, %f), dimensions = Vector(%f, %f, %f), id = \"%s\")\n" % (
                #                 remove_prefix(current_obj.name, "node_"),
                #                 current_obj.location.x,
                #                 current_obj.location.z,
                #                 -current_obj.location.y,
                #                 current_obj.dimensions.x,
                #                 current_obj.dimensions.z,
                #                 current_obj.dimensions.y,
                #                 remove_prefix(current_obj.name, "node_"),
                #             ))

                export["nodes"].append({
                    "id": remove_prefix(current_obj.name, "node_"),
                    "location": {
                        "x": current_obj.location.x,
                        "y": current_obj.location.z,
                        "z": -current_obj.location.y,
                    },
                    "dimensions": {
                        "x": current_obj.dimensions.x,
                        "y": current_obj.dimensions.z,
                        "z": current_obj.dimensions.y,
                    },
                })

    for current_obj in context.selected_objects:
        if current_obj.type == 'CURVE':
            export.setdefault("parts", [])
            name = current_obj.name.replace(".", "_")
            # writeString(file, "val " + name + " = SplinedPathPart(\"%s\")\n" % name)

            xOffset = current_obj.matrix_world.to_translation().x
            yOffset = current_obj.matrix_world.to_translation().y
            zOffset = current_obj.matrix_world.to_translation().z

            # writeString(file, name + ".add(")

            part = {
                "type": "bezier",
                "id": name,
                "nodes": []
            }

            for spline in current_obj.data.splines:
                for bezier_point in spline.bezier_points:
                    # writeString(file, ",\n  SplineNode(SplineHandle(%f, %f, %f),\n" % (
                    #     bezier_point.handle_left[0] + xOffset, bezier_point.handle_left[2] + zOffset,
                    #     -bezier_point.handle_left[1] + yOffset))
                    # writeString(file, "     SplineHandle(%f, %f, %f),\n" % (
                    #     bezier_point.co[0] + xOffset, bezier_point.co[2] + zOffset, -bezier_point.co[1] + yOffset))
                    # writeString(file, "     SplineHandle(%f, %f, %f), %f)" % (
                    #     bezier_point.handle_right[0] + xOffset, bezier_point.handle_right[2] + zOffset,
                    #     -bezier_point.handle_right[1] + yOffset, -(bezier_point.tilt * DEG2RAD)))

                    part["nodes"].append({
                        "in": {
                            "x": bezier_point.handle_left[0] + xOffset,
                            "y": bezier_point.handle_left[2] + zOffset,
                            "z": -bezier_point.handle_left[1] + yOffset,
                        },
                        "knot": {
                            "x": bezier_point.co[0] + xOffset,
                            "y": bezier_point.co[2] + zOffset,
                            "z": -bezier_point.co[1] + yOffset,
                        },
                        "out": {
                            "x": bezier_point.handle_right[0] + xOffset,
                            "y": bezier_point.handle_right[2] + zOffset,
                            "z": -bezier_point.handle_right[1] + yOffset,
                        },
                        "banking": -(bezier_point.tilt * DEG2RAD),
                    })

            export["parts"].append(part)

            # writeString(file, ")\n")
            # writeString(file, "navigation.addPathPart(%s)\n\n" % name)

    writeString(file, json.dumps(export, indent=2))

    file.flush()
    file.close()
    return True


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    bpy.types.Material.custom_float = bpy.props.FloatProperty(name="Test Property 1")
    bpy.types.Curve.custom_float = bpy.props.FloatProperty(name="Test Property 2")

    bpy.types.Curve.custom_tracked_ride_spline_type = bpy.props.EnumProperty(
        name="Tracked Ride Spline Type",
        default="SplinedTrackSegment",
        items=(
            ("StationSegment", "StationSegment", "StationSegment"),
            ("SplinedTrackSegment", "SplinedTrackSegment", "SplinedTrackSegment")
        ),
        options=set()
    )


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
