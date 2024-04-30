import OpenGL.GL as GL
import numpy as np

from core_ext.object3d import Object3D


class Mesh(Object3D):
    """
    Contains geometric data that specifies vertex-related properties and material data
    that specifies the general appearance of the object
    """
    def __init__(self, geometry, material):
        super().__init__()
        self._geometry = geometry
        self._material = material
        # Should this object be rendered?
        self._visible = True
        # Set up associations between attributes stored in geometry
        # and shader program stored in material
        self._vao_ref = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self._vao_ref)
        for variable_name, attribute_object in geometry.attribute_dict.items():
            attribute_object.associate_variable(material.program_ref, variable_name)
        # Unbind this vertex array object
        GL.glBindVertexArray(0)

    @property
    def geometry(self):
        return self._geometry

    @property
    def material(self):
        return self._material

    @property
    def vao_ref(self):
        return self._vao_ref

    @property
    def visible(self):
        return self._visible
    
    def intersects(self, other):
        """
        Checks if this mesh intersects with another object based on their bounding boxes.
        """
        min_point_self, max_point_self = self.bounding_box
        min_point_other, max_point_other = other.bounding_box

        # Check for intersection along each axis
        for i in range(3):
            if max_point_self[i] < min_point_other[i] or min_point_self[i] > max_point_other[i]:
                return False  # No intersection

        return True  # Intersection detected
    
   