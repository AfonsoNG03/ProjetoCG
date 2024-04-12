from geometry.geometry import Geometry
from core.obj_reader import my_obj_reader

class OculosGeometry(Geometry):
    def __init__(self):
        super().__init__()

        position_data = my_obj_reader('oculos3.obj')
        default_color = [1, 1, 1]  
        color_data = [default_color for _ in range(len(position_data))]
        self.add_attribute("vec3", "vertexPosition", position_data)
        self.add_attribute("vec3", "vertexColor", color_data)
        self.add_attribute("vec2", "vertexUV", position_data)
        #self.count_vertices()
