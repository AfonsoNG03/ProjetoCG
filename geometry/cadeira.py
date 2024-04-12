from geometry.geometry import Geometry
from core.obj_reader import my_obj_reader


class CadeiraGeometry(Geometry):
    def __init__(self):  # Por padrão, estamos configurando a cor para branco
        super().__init__()

        # Carregar vértices do arquivo .obj
        vertices = my_obj_reader('cadeira.obj')

        # Adicionar vértices e cores à geometria do objeto
        position_data = vertices
        self.add_attribute("vec3", "vertexPosition", position_data)
        self.add_attribute("vec2", "vertexUV", position_data)
        #self.count_vertices()