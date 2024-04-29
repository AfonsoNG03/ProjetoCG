from geometry.geometry import Geometry
from core.obj_reader import my_obj_reader

class OculosGeometry(Geometry):
    def __init__(self):
        super().__init__()

        vertices, texture = my_obj_reader('oculos.obj')


        self.add_attribute("vec3", "vertexPosition", vertices)
        self.add_attribute("vec2", "vertexUV", texture)
        #self.count_vertices()
