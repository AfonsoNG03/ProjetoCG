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
        self._heightMesh = 1.0
        self._radiusMesh = 1.0
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
        self.heightMesh()
        self.radiusMesh()

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
    
    
    def heightMesh(self):
        position_data = self._geometry._attribute_dict["vertexPosition"].data
        minY = 0
        maxY = 0
        for pos in position_data:
            if pos[1] < minY:
                minY = pos[1]
            if pos[1] > maxY:
                maxY = pos[1]
        self._heightMesh = maxY - minY
        return self._heightMesh
    
    
    def radiusMesh(self):
        position_data = self._geometry._attribute_dict["vertexPosition"].data
        minX = 0
        maxX = 0
        for pos in position_data:
            if pos[0] < minX:
                minX = pos[0]
            if pos[0] > maxX:
                maxX = pos[0]
        radiusMeshX = (maxX - minX) / 2
        minZ = 0
        maxZ = 0
        for pos in position_data:
            if pos[1] < minZ:
                minZ = pos[1]
            if pos[1] > maxZ:
                maxZ = pos[1]
        radiusMeshZ = (maxZ - minZ) / 2
        if radiusMeshX > radiusMeshZ:
            self._radiusMesh = radiusMeshX
        else:
            self._radiusMesh = radiusMeshZ
        return self._radiusMesh
    
   