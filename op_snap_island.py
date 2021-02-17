import bpy
import bmesh
from mathutils import Vector

from . import utilities_uv

_LOCATIONS = [
    'TOPLEFT',
    'TOPCENTER',
    'TOPRIGHT',
    'CENTERLEFT',
    'CENTER',
    'CENTERRIGHT',
    'BOTTOMLEFT',
    'BOTTOMCENTER',
    'BOTTOMRIGHT'
    ]

_SNAP_POINTS = {
    'LEFTTOP': ['min', 'max', Vector((0, 1))],
    'CENTERTOP': ['center', 'max', Vector((.5, 1))],
    'RIGHTTOP': ['max', 'max', Vector((1, 1))],
    'LEFTCENTER': ['min', 'center', Vector((0, .5))],
    'CENTER': ['center', 'center', Vector((.5, .5))],
    'RIGHTCENTER': ['max', 'center', Vector((1, .5))],
    'LEFTBOTTOM': ['min', 'min', Vector((0, 0))],
    'CENTERBOTTOM': ['center', 'min', Vector((.5, 0))],
    'RIGHTBOTTOM': ['max', 'min', Vector((1, 0))]
}

def GetIslandBoundingBox(uvIsland):
    """ Return the bounding box coords with extra tests for single island selection
    """

    if not uvIsland:
        print("Select a UV island!")
        return None

    if len(uvIsland) > 1:
        print("Too many islands selected!")
        return None

    return utilities_uv.getSelectionBBox()


class IslandSnap(bpy.types.Operator):
    bl_idname = "uv.be_textools_snap_island"
    bl_label = "Snap Islands"
    bl_description = "Snap islands to different positions on the grid"
    bl_options = {'REGISTER', 'UNDO'}

    direction : bpy.props.StringProperty(
        name='Direction',
        default='TOPLEFT'
        )

    @classmethod
    def poll(cls, context):
        if not bpy.context.active_object:
            return False
        #Only in Edit mode
        if bpy.context.active_object.mode != 'EDIT':
            return False
        #Requires UV map
        if not bpy.context.object.data.uv_layers:
            return False
        if bpy.context.scene.tool_settings.use_uv_select_sync:
            return False
        #Only in UV editor mode
        if bpy.context.area.type != 'IMAGE_EDITOR':
            return False
        return True

    def execute(self, context):

        print("Snap point is {}".format(self.direction))

        island = utilities_uv.getSelectionIslands()

        if not island:
            return {'FINISHED'}

        bounds = GetIslandBoundingBox(island)

        """
        {'min': Vector((0.36108651757240295, -0.009061867371201515)),
        'max': Vector((0.5110875964164734, 4.390938758850098)),
        'width': 0.15000107884407043,
        'height': 4.40000057220459,
        'center': Vector((0.436087042093277, 2.1909382343292236)),
        'area': 0.6600048327452157,
        'minLength': 0.15000107884407043}
        """

        x = _SNAP_POINTS.get(self.direction)[0]
        y = _SNAP_POINTS.get(self.direction)[1]
        target = _SNAP_POINTS.get(self.direction)[2]

        xDelta = target.x-bounds.get(x).x
        yDelta = target.y-bounds.get(y).y

        bpy.ops.transform.translate(
            value=(xDelta, yDelta, 0),
            orient_type='GLOBAL',
            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            orient_matrix_type='GLOBAL',
            mirror=True,
            use_proportional_edit=False,
            proportional_edit_falloff='SMOOTH',
            proportional_size=1,
            use_proportional_connected=False,
            use_proportional_projected=False,
            release_confirm=True
            )

        return {'FINISHED'}

bpy.utils.register_class(IslandSnap)
