bl_info = {
    'name': 'Craftventure Exporter',
    'author': 'Joeywp',
    'version': (1, 0, 0),
    'blender': (2, 93, 4),
    'location': 'File > Export > Craftventure.json (.json)',
    'description': 'Export Craftventure JSON (.json)',
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
    """Save a Craftventure Json File"""

    export_type: bpy.props.EnumProperty(
        name="Export type",
        default="JSON",
        items=(
            ("JSON", "JSON", "JSON"),
            ("Kotlin", "Kotlin", "Kotlin")
        ),
        options=set()
    )

    max_dimensions: bpy.props.FloatProperty(
        name="Max dimensions for nodes",
        default=0.1,
        min=0.0,
        max=1000.0,
        options=set()
    )

    bl_idname = "export_scene.json"
    bl_label = 'Export JSON'
    bl_options = {'PRESET'}

    filename_ext = ".json"

    def execute(self, context):
        start_time = time.time()
        print('\n_____START KOTLIN_____')
        props = self.properties
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        if self.export_type == "JSON":
            exported = do_export_json(context, props, filepath, self.max_dimensions)
        else:
            exported = do_export_kotlin(context, props, filepath)

        if exported:
            print('finished export in %s seconds' % ((time.time() - start_time)))
            print(filepath)

        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(ExportKT.bl_idname, text="Craftventure (.json)")


class OBJECT_PT_craftventure(bpy.types.Panel):
    bl_idname = "DATA_PT_craftventure"
    bl_label = 'Craftventure Panel'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object.type == 'CURVE'

    def draw(self, context):
        ob = context.object
        print(ob.type)
        if ob.type == 'CURVE':
            layout = self.layout
            # row = layout.row()
            # row.label(text=str("Tracked ride spline type"))
            row = layout.row()
            # row.label(text="Segment type")
            row.prop(data=ob.data, property='cv_tracked_ride_spline_type')


classes = (
    ExportKT,
    OBJECT_PT_craftventure,
)


def remove_prefix(text, prefix):
    return text[len(prefix):] if text.startswith(prefix) else text


def writeString(file, string):
    file.write(bytes(string, 'UTF-8'))


def do_export_kotlin(context, props, filepath):
    file = open(filepath, "wb")

    DEG2RAD = 57.29577951

    for current_obj in context.selected_objects:
        if current_obj.type == 'CURVE':
            # current_obj["custom_tracked_ride_spline_type"] = "SplinedTrackSegment"
            # print(current_obj.data.custom_tracked_ride_spline_type)

            # current_obj.data.custom_tracked_ride_spline_type = "StationSegment"

            # current_obj.trackedRideSplineType = "SplinedTrackSegment"
            writeString(file, "val " + current_obj.data.name + " = SplinedTrackSegment(trackedRide)\n")

            xOffset = current_obj.matrix_world.to_translation().x
            yOffset = current_obj.matrix_world.to_translation().y
            zOffset = current_obj.matrix_world.to_translation().z

            writeString(file, current_obj.data.name + ".add(offset")

            for spline in current_obj.data.splines:
                for bezier_point in spline.bezier_points:
                    writeString(file, ",\n  SplineNode(SplineHandle(%f, %f, %f),\n" % (
                        bezier_point.handle_left[0] + xOffset,
                        bezier_point.handle_left[2] + zOffset,
                        -bezier_point.handle_left[1] + yOffset))
                    writeString(file, "     SplineHandle(%f, %f, %f),\n" % (
                        bezier_point.co[0] + xOffset,
                        bezier_point.co[2] + zOffset,
                        -bezier_point.co[1] + yOffset))
                    writeString(file, "     SplineHandle(%f, %f, %f), %f)" % (
                        bezier_point.handle_right[0] + xOffset,
                        bezier_point.handle_right[2] + zOffset,
                        -bezier_point.handle_right[1] + yOffset,
                        -(bezier_point.tilt * DEG2RAD)))
            writeString(file, ")\n")
            writeString(file, "\n")

    writeString(file, "\n")

    file.flush()
    file.close()
    return True


def do_export_json(context, props, filepath, max_dimensions):
    file = open(filepath, "wb")

    DEG2RAD = 57.29577951

    export = {}

    # bpy.data.curves[0].custom_tracked_ride_spline_type = "SplinedTrackSegment"

    # for current_obj in context.selected_objects:
    #     if current_obj.type == 'CURVE':
    #         # current_obj["custom_tracked_ride_spline_type"] = "SplinedTrackSegment"
    #         print(current_obj.data.custom_tracked_ride_spline_type)
    #
    #         current_obj.data.custom_tracked_ride_spline_type = "StationSegment"
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

                export["nodes"].append({
                    "id": remove_prefix(current_obj.name, "node_"),
                    "location": {
                        "x": current_obj.location.x,
                        "y": current_obj.location.z,
                        "z": -current_obj.location.y,
                    },
                    "dimensions": {
                        "x": round(min(max_dimensions, current_obj.dimensions.x), 3),
                        "y": round(min(max_dimensions, current_obj.dimensions.z), 3),
                        "z": round(min(max_dimensions, current_obj.dimensions.y), 3),
                    },
                })

    for current_obj in context.selected_objects:
        if current_obj.type == 'CURVE':
            if current_obj.name.startswith("BezierCurve") and not current_obj.data.name.startswith("BezierCurve"):
                current_obj.name = current_obj.data.name

            export.setdefault("parts", [])
            name = current_obj.name.replace(".", "_")

            xOffset = current_obj.matrix_world.to_translation().x
            yOffset = current_obj.matrix_world.to_translation().y
            zOffset = current_obj.matrix_world.to_translation().z

            part = {
                "type": "bezier",
                "id": name,
                "nodes": []
            }

            for spline in current_obj.data.splines:
                for bezier_point in spline.bezier_points:
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

    writeString(file, json.dumps(export, indent=2))

    file.flush()
    file.close()
    return True


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    bpy.types.Scene.cv_scene_type = bpy.props.EnumProperty(
        name="Scene Type",
        default="Tracked",
        items=(
            ("Tracked", "Tracked", "Tracked"),
            ("Trackless", "Trackless", "Trackless")
        ),
        options=set()
    )

    bpy.types.Curve.cv_tracked_ride_spline_type = bpy.props.EnumProperty(
        name="Segment Type",
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

    # del bpy.types.Scene.cv_tracked_ride_spline_type


if __name__ == "__main__":
    register()
