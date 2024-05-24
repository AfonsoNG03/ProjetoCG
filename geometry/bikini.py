import numpy as np
from geometry.geometry import Geometry
from core.obj_reader import my_obj_reader

class BikiniGeometry(Geometry):
    def __init__(self):
        super().__init__()

        vertices, texture = my_obj_reader('objetos/bikini.obj')

        self.add_attribute("vec3", "vertexPosition", vertices)
        self.add_attribute("vec2", "vertexUV", texture)
