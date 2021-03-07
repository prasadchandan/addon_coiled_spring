from mathutils import Vector
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty
from bpy.types import Operator
import numpy as np
import math
import bpy
bl_info = {
    "name": "Coiled Spring",
    "author": "Chandan Prasad M",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds a new coiled spring mesh object",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}


def dist(x, y):
    return np.sqrt(np.sum((x - y)**2))


def normalize(a):
    return (a / np.linalg.norm(a))


class OBJECT_OT_add_coiled_spring(Operator, AddObjectHelper):
    """Create a new coiled spring mesh object"""
    bl_idname = "mesh.add_object"
    bl_label = "Add coiled spring mesh object"
    bl_options = {'REGISTER', 'UNDO'}

    helix_radius: FloatProperty(
        name="Spring Radius",
        default=2.0,
        description="Helix spring radius"
    )

    profile_radius: FloatProperty(
        name="Spring profile radius",
        default=0.3,
        description="Radius of the spring profile"
    )

    num_turns: IntProperty(
        name="Number of turns",
        default=5,
        description="Number of coils in the spring"
    )

    helix_resolution: IntProperty(
        name="Coil Resolution",
        default=512,
        description="Resolution of the coil spring"
    )

    profile_resolution: IntProperty(
        name="Profile Resolution",
        default=16,
        description="Resolution of the coil profile"
    )

    length: FloatProperty(
        name="Spring Length",
        default=10.0,
        description="Length of the spring"
    )

    def CreateHelixVertices(self):
        start_point = np.array([0.0, 0.0, 0.0])
        end_point = np.array([0.0, 0.0, self.length])
        distance = dist(start_point, end_point)

        # 2 * pi * pitch_b => Pitch
        pitch_b = distance / (self.num_turns * math.pi * 2)
        t_max = distance / pitch_b  # => distance * pi

        t = list(np.linspace(0.0, t_max, self.helix_resolution))
        x = [self.helix_radius * math.sin(it) for it in t]
        y = [self.helix_radius * math.cos(it) for it in t]
        z = [pitch_b * it for it in t]

        self.verts = [np.array((x[i], y[i], z[i]))
                      for i in range(self.helix_resolution)]

    def get_profile_circle_vertices(self, center, prev_vec):
        r = self.profile_radius
        s = self.profile_resolution + 1  # Is the +1 required?

        helix_center_at_z = np.array((0.0, 0.0, center[2]))
        b = normalize(helix_center_at_z - center)
        c = normalize(center - prev_vec)
        a = normalize(np.cross(b, c))

        t = np.linspace(0, 2 * math.pi, s)
        x = [(center[0] + (r * math.cos(it) * a[0]) +
              (r * math.sin(it) * b[0])) for it in t[0:-1]]
        y = [(center[1] + (r * math.cos(it) * a[1]) +
              (r * math.sin(it) * b[1])) for it in t[0:-1]]
        z = [(center[2] + (r * math.cos(it) * a[2]) +
              (r * math.sin(it) * b[2])) for it in t[0:-1]]

        return [(x[i], y[i], z[i]) for i in range(s - 1)]

    def GenerateCircleVertices(self):
        for i in range(self.helix_resolution):
            center = self.verts[i]
            prev_vec = self.verts[i-1] if i > 0 else -self.verts[1]
            self.verts += self.get_profile_circle_vertices(center, prev_vec)

    def CreateFacets(self):
        self.facets = []
        start_vertex_id = self.helix_resolution
        num_vtx_per_circle = self.profile_resolution
        for i in range(self.helix_resolution):
            if i > 0:
                start_prev_vtx = start_vertex_id - num_vtx_per_circle
                for j in range(num_vtx_per_circle):
                    ctr = 0 if j + 1 >= num_vtx_per_circle else j + 1
                    self.facets.append((start_prev_vtx + j,
                                        start_prev_vtx + ctr,
                                        start_vertex_id + ctr,
                                        start_vertex_id + j))
            start_vertex_id += num_vtx_per_circle

    def execute(self, context):
        self.CreateHelixVertices()
        self.GenerateCircleVertices()
        self.CreateFacets()

        edges = []

        mesh = bpy.data.meshes.new(name="Spring")
        mesh.from_pydata(self.verts, edges, self.facets)
        # useful for development when the mesh may be invalid.
        # mesh.validate(verbose=True)
        spring_ob = object_data_add(context, mesh, operator=self)

        return {'FINISHED'}


def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_coiled_spring.bl_idname,
        text="Add Coiled Spring",
        icon='GP_SELECT_STROKES')


# This allows you to right click on a button and link to documentation
def add_object_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/latest/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "scene_layout/object/types.html"),
    )
    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(OBJECT_OT_add_coiled_spring)
    bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_coiled_spring)
    bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)


if __name__ == "__main__":
    register()
