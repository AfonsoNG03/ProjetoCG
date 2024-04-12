import numpy as np
from geometry.geometry import Geometry
from core.obj_reader import my_obj_reader

class ToalhaGeometry(Geometry):
    def __init__(self):
        super().__init__()

        """position_data = my_obj_reader('toalha.obj')
        #default_color = [1, 1, 1]
        #color_data = [default_color for  in range(len(position_data))]
        self.add_attribute("vec3", "vertexPosition", position_data)
        #self.add_attribute("vec3", "vertexColor", color_data)
        self.add_attribute("vec2", "vertexUV", position_data)
        self.count_vertices()
        """
        # Carregar vértices do arquivo .obj
        vertices = my_obj_reader('toalha.obj')

        # Adicionar vértices e cores à geometria do objeto
        position_data = vertices
        self.add_attribute("vec3", "vertexPosition", position_data)
        #self.count_vertices()