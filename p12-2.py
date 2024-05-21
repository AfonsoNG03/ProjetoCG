import numpy as np
import math
import pathlib
import sys

from core.base import Base
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from core_ext.renderer2 import Renderer
from core_ext.scene import Scene
from extras.movement_rig import MovementRig
from extras.movement_rig2 import MovementRig2
from extras.movement_rig3 import MovementRig3
from geometry.animal import animalGeometry
from geometry.arvore import ArvoreGeometry
from geometry.arbusto import arbustoGeometry
from geometry.bola import bolaGeometry
from geometry.bikini import BikiniGeometry
from geometry.cadeira import CadeiraGeometry
from geometry.golfinho import golfinhoGeometry
from geometry.jetski import JetskiGeometry
from geometry.modelo import ModeloGeometry
from geometry.oculos import OculosGeometry
from geometry.cubo import CuboGeometry
from geometry.passa import passaGeometry
from geometry.placa import placaGeometry
from geometry.portal import portalGeometry
from geometry.stand import standGeometry
from geometry.pokeball import pokeballGeometry
from geometry.rocks import rocksGeometry
from geometry.yatch import YatchGeometry
from geometry.warship import warshipGeometry
from geometry.warship2 import warship2Geometry
from geometry.rectangle import RectangleGeometry
from geometry.sphere import SphereGeometry
from geometry.toalha import ToalhaGeometry
from light.ambient import AmbientLight
from light.directional import DirectionalLight
from material.material import Material
from material.phong import PhongMaterial
from material.surface import SurfaceMaterial
from core_ext.texture import Texture
from extras.text_texture import TextTexture
from material.texture import TextureMaterial

class Example(Base):
    """
    Render the axes and the rotated xy-grid.
    Add box movement: WASDRF(move), QE(turn), TG(look).
    Para mexer a camera usar up left right down  e as tecals p l n m
    """
    def initialize(self):
        print("Initializing program...")
        print("Para mexer o modelo usar as teclas w,a,s,d")
        print("Para mexer a camera usar as teclas q(esquerda),e (direita),t (cima), g(baixo) ou o cursor")
        print("Para mudar a camera telca 'c', espaço para saltar e shift para sprintar")
        print("Para mudar ativar o modo criativo pressionar a tecla '' e usar 'z' para subir e 'x' para descer")

        # Shaders para distorção
        vertex_shader_code = """
            uniform mat4 projectionMatrix;
            uniform mat4 viewMatrix;
            uniform mat4 modelMatrix;
            in vec3 vertexPosition;
            in vec2 vertexUV;
            out vec2 UV;

            void main()
            {
                gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
                UV = vertexUV;
            }
        """
        fragment_shader_code = """
            uniform sampler2D rgbNoise;
            uniform sampler2D image;
            in vec2 UV;
            uniform float time;
            uniform vec2 repeatUV;
            out vec4 fragColor;

            void main()
            {
                vec2 uvShift = UV + vec2(-0.033, 0.07) * time;
                vec4 noiseValues = texture2D(rgbNoise, uvShift);
                vec2 uvNoise = UV * repeatUV + 0.01 * noiseValues.rg;
                fragColor = texture2D(image, uvNoise);
            }
        """
        #

        # Define grid properties
        self.grid_size = 2  # Size of each grid cell
        self.grid = {}  # Dictionary to store objects in each grid cell

        # Criação da cena
        self.renderer = Renderer()
        self.scene = Scene()
        self.rig = MovementRig()
        self.rig2 = MovementRig2()
        self.rig3 = MovementRig3()
        #

        # Adiciona luzes
        # Luz ambiente
        self.ambient_light = AmbientLight(color=[0.1, 0.1, 0.1])
        self.scene.add(self.ambient_light)

        # Luz direcional
        self.directional_light = DirectionalLight(color=[0.8, 0.8, 0.8], direction=[-1, -1, 0])
        self.scene.add(self.directional_light)
        #

        # Texturas
        rgb_noise_texture = Texture("images/rgb-noise.jpg")
        water_texture = Texture("images/water.jpg")
        self.distort_material = Material(vertex_shader_code, fragment_shader_code)
        self.distort_material.add_uniform("sampler2D", "rgbNoise", [rgb_noise_texture.texture_ref, 1])
        self.distort_material.add_uniform("sampler2D", "image", [water_texture.texture_ref, 2])
        self.distort_material.add_uniform("float", "time", 0.0)
        self.distort_material.add_uniform("vec2", "repeatUV", [10, 10])
        self.distort_material.locate_uniforms()

        # Textura do oceano
        ocean_geometry = RectangleGeometry(width=200, height=100)
        #ocean_geometry = OceanoGeometry(width=50, height=50)
        self.ocean = Mesh(ocean_geometry, self.distort_material)
        self.ocean.rotate_x(-math.pi/2)
        self.ocean.set_position([0, 0, -55])
        self.scene.add(self.ocean)
    
        # Textura do céu
        sky_geometry = SphereGeometry(radius=100)
        sky_material = TextureMaterial(texture=Texture(file_name="images/sky.jpg"))
        self.sky = Mesh(sky_geometry, sky_material)
        self.scene.add(self.sky)

        # Textura da areia
        sand_geometry = RectangleGeometry(width=200, height=100)
        sand_material = TextureMaterial(
            texture=Texture(file_name="images/sand.jpg"),
            property_dict={"repeatUV": [20, 20]}
        )
        self.sand = Mesh(sand_geometry, sand_material)
        self.sand.rotate_x(-math.pi/2)
        self.sand.set_position([0, 0, 45])
        self.scene.add(self.sand)
        #

        #modelo do boneco
        modelo_material = TextureMaterial(texture=Texture("images/Cor_Modelo.jpg"))
        modelo_geometry = ModeloGeometry()
        self.modelo = Mesh(modelo_geometry, modelo_material)
        self.modelo.set_position([0, 0, 0])
        #self.modelo.set_position([-1.75,29.5,79.5])
        self.modelo.rotate_y(110)
        self.rig.add(self.modelo)


        # Cubos

        cubo_material = TextureMaterial(texture=Texture("images/mine.png"))
        cubo_geometry = CuboGeometry()
        self.cubo = Mesh(cubo_geometry, cubo_material)
        self.cubo.set_position([0,3, 10])
        self.scene.add(self.cubo)
        self.cubo = Mesh(cubo_geometry, cubo_material)
        self.cubo.set_position([0,6, 13])
        self.scene.add(self.cubo)

        #pedra
        rocks_material = TextureMaterial(texture=Texture("images/rock.jpg"))
        rocks_geometry = rocksGeometry()
        self.rocks = Mesh(rocks_geometry, rocks_material)
        self.rocks.set_position([20, 0, 20])
        self.scene.add(self.rocks)
                
        # Criação da camera
        self.camera = Camera(aspect_ratio=800/600)
        self.camera.set_position([0, 2.93, -1])
        #self.camera.set_position([-1.75,29.5+2.93,79.5-1])
        self.rig.add(self.camera)
        self.scene.add(self.rig)
        self.scene.add(self.rig2)
        self.scene.add(self.rig3)

        # Criaçao da camara alternativa
        self.static_camera = Camera(aspect_ratio=800/600)
        self.static_camera.set_position([0, 2.5, 4])
        self.rig3.add(self.static_camera)
        self.active_camera = self.camera

        self.toggle_camera = False

    def add_to_grid(self, obj):
        """
        Add an object to the grid based on its position.
        """
        position = obj.global_position
        grid_x = int(position[0] / self.grid_size)
        grid_y = int(position[1] / self.grid_size)
        grid_z = int(position[2] / self.grid_size)
        key = (grid_x, grid_y, grid_z)
        if key not in self.grid:
            self.grid[key] = []
        self.grid[key].append(obj)

    def update_grid(self):
        """
        Update the grid by reassigning objects to appropriate grid cells.
        """
        self.grid = {}
        for obj in self.scene.children_list:
            if obj == self.rig or obj == self.ambient_light or obj == self.ocean or obj == self.sand or obj == self.directional_light or obj == self.sky:
                continue
            self.add_to_grid(obj)

    def get_nearby_objects(self, obj):
        """
        Get objects in the same or adjacent grid cells as the given object.
        """
        position = obj.global_position
        grid_x = int(position[0] / self.grid_size)
        grid_y = int(position[1] / self.grid_size)
        grid_z = int(position[2] / self.grid_size)
        nearby_objects = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    key = (grid_x + dx, grid_y + dy, grid_z + dz)
                    if key in self.grid:
                        nearby_objects.extend(self.grid[key])
        return nearby_objects

    def check_collisions(self):
        """
        Check for collisions between objects in the scene.
        """
        self.update_grid()
        nearby_objects = self.get_nearby_objects(self.camera)
        for other_obj in nearby_objects:
            if other_obj != self.camera and self.camera.intersects(other_obj):
                return self.determine_collision_direction(other_obj)
                #return True
        return False

    def determine_collision_direction(self, other_obj):
        """
        Determine the direction of collision between the camera and another object.
        """
        # Get positions of camera and other object
        cam_pos = np.array(self.camera.global_position)
        obj_pos = np.array(other_obj.global_position)
        
        # Calculate the vector from the camera to the object
        collision_vector = obj_pos - cam_pos

        # Normalize the vector to get the direction
        collision_direction = collision_vector / np.linalg.norm(collision_vector)
        
        # Determine the direction
        direction = ''
        
        if abs(collision_direction[0]) > abs(collision_direction[1]) and abs(collision_direction[0]) > abs(collision_direction[2]):
            if collision_direction[0] > 0:
                direction = 'right'
                self.rig.translate(-0.1, 0, 0, False)
            else:
                direction = 'left'
                self.rig.translate(0.1, 0, 0, False)
        elif abs(collision_direction[1]) > abs(collision_direction[0]) and abs(collision_direction[1]) > abs(collision_direction[2]):
            if collision_direction[1] > 0:
                direction = 'below'
                self.rig.translate(0, -0.1, 0, False)
            else:
                direction = 'above'
                return True
        else:
            if collision_direction[2] > 0:
                direction = 'front'
                self.rig.translate(0, 0, -0.1, False)
            else:
                direction = 'back'
                self.rig.translate(0, 0, 0.1, False)
        
        print("Collision direction:", direction)
        return False


    def update(self):
        self.distort_material.uniform_dict["time"].data += self.delta_time/5

        
        if self.input.is_key_pressed('c'):
            if not self.toggle_camera:
                self.toggle_camera = True
                if self.active_camera == self.camera:
                    self.active_camera = self.static_camera
                else:
                    self.active_camera = self.camera
        else: 
            self.toggle_camera = False
        collision = self.check_collisions()  # Get collision direction
        self.rig.update(self.input, self.delta_time, collision)
        self.rig2.update(self.input, self.delta_time, collision)
        self.rig3.update(self.input, self.delta_time, collision)
        self.renderer.render(self.scene, self.active_camera)
        # Check for collisions
# Instantiate this class and run the program
Example(screen_size=[800, 600]).run()