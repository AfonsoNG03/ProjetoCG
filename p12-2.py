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
from geometry.animal import animalGeometry
from geometry.bola import bolaGeometry
from geometry.arvore import ArvoreGeometry
from geometry.bikini import BikiniGeometry
from geometry.cadeira import CadeiraGeometry
from geometry.golfinho import golfinhoGeometry
from geometry.jetski import JetskiGeometry
from geometry.modelo import ModeloGeometry
from geometry.oculos import OculosGeometry
from geometry.placa import placaGeometry
from geometry.pokeball import pokeballGeometry
from geometry.rocks import rocksGeometry
from geometry.yatch import YatchGeometry
from geometry.warship import warshipGeometry
from geometry.rectangle import RectangleGeometry
from geometry.sphere import SphereGeometry
from geometry.toalha import ToalhaGeometry
from light.ambient import AmbientLight
from light.directional import DirectionalLight
from material.material import Material
from material.phong import PhongMaterial
from material.surface import SurfaceMaterial
from core_ext.texture import Texture
from material.texture import TextureMaterial


class Example(Base):
    """
    Render the axes and the rotated xy-grid.
    Add box movement: WASDRF(move), QE(turn), TG(look).
    Para mexer a camera usar up left right down  e as tecals p l n m
    """
    def initialize(self):
        print("Initializing program...")
        print("Para mexer os oculos usar as teclas wasd e q r f t g")
        print("Para mexer a camera usar as setas (up left right down) e as teclas p l n m h b")

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
        ocean_geometry = RectangleGeometry(width=100, height=100)
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
        sand_geometry = RectangleGeometry(width=100, height=100)
        sand_material = TextureMaterial(
            texture=Texture(file_name="images/sand.jpg"),
            property_dict={"repeatUV": [20, 20]}
        )
        self.sand = Mesh(sand_geometry, sand_material)
        self.sand.rotate_x(-math.pi/2)
        self.sand.set_position([0, 0, 45])
        self.scene.add(self.sand)
        #

        # Testes
        phong_material = PhongMaterial(
            property_dict={"baseColor": [1, 0, 1]},
            number_of_light_sources=2
        )
        sphere_geometry = SphereGeometry()
        sphere_right = Mesh(sphere_geometry, phong_material)
        sphere_right.set_position([2.5, 0, 0])
        self.scene.add(sphere_right)

        #modelo do boneco
        modelo_material = TextureMaterial(texture=Texture("images/Cor_Modelo.jpg"))
        modelo_geometry = ModeloGeometry()
        modelo = Mesh(modelo_geometry, modelo_material)
        modelo.set_position([0, 0, 0])
        self.scene.add(modelo)
        
        #criação das árvores
        #coordenadas, sentido positivo da direita para a esquerda
        arvore_material = TextureMaterial(texture=Texture("images/arvore2.jpg"))
        arvore_geometry = ArvoreGeometry()
        arvore_positions= [[4, -3, 20],
                        [-40, -3, 35],[-30, -3, 35],[-20, -3, 35],[-14, -3, 35], [-7, -3, 40],[0, -3, 40], [4, -3, 32],[12, -3, 40],[20, -3, 32],[28, -3, 40],[37, -3, 41],]
        for position in arvore_positions:
            arvore = Mesh(arvore_geometry, arvore_material)
            arvore.set_position(position)
            self.scene.add(arvore)
  
        # Criação rochas
        rocks_material = TextureMaterial(texture=Texture("images/rock.jpg"))
        rocks_geometry = rocksGeometry()
        rock_positions = [[-20, -3, 35],[-5, -3, 35],[10, -3, 35], [25, -3, 35],[40, -3, 35],
                        [10, -3, 40],[25, -3, 40]]
        for position in rock_positions:
            rocks = Mesh(rocks_geometry, rocks_material)
            rocks.set_position(position)
            self.scene.add(rocks)

        # Criação do bikini
        bikini_material = TextureMaterial(texture=Texture("images/rgb-noise.jpg"))
        bikini_geometry = BikiniGeometry()
        bikini = Mesh(bikini_geometry, bikini_material)
        bikini.set_position([-1, 0, 0])
        self.scene.add(bikini)

        # Criação dos oculos
        oculos_material = TextureMaterial(texture=Texture("images/oculos.jpg"))
        oculos_geometry = OculosGeometry()
        oculos = Mesh(oculos_geometry, oculos_material)
        oculos.set_position([0, 0, -0.09])
        self.scene.add(oculos)

        # Criação da cadeira
        #cadeira_material = TextureMaterial(texture=Texture("images/crate.jpg"))
        #cadeira_geometry = CadeiraGeometry()
        #cadeira = Mesh(cadeira_geometry, cadeira_material)
        #cadeira.set_position([0, 0, 0])
        #self.scene.add(cadeira)

        # Criação das toalhas
        texturas = [ "images/whool.jpg", "images/stripes.jpg", "images/toalha.jpg", "images/master.jpg"]
        toalha_geometry = ToalhaGeometry()
        for i in range(30):
            toalha_material = TextureMaterial(texture=Texture(np.random.choice(texturas)))
            toalha = Mesh(toalha_geometry, toalha_material)
            toalha.scale(2.5)
            toalha.set_position([np.random.uniform(-50, 50), 0, np.random.uniform(0, 50)])
            self.scene.add(toalha)
        
        #placa das direções
        placa_material = TextureMaterial(texture=Texture("images/p2.png"))
        placa_geometry = placaGeometry()
        placa = Mesh(placa_geometry, placa_material)
        placa.set_position([-2, 0, 16])
        self.scene.add(placa)

        """texturas = [ "images/p1.png", "images/p2.png", "images/p3.png", "images/p4.png", "images/p5.png", "images/p6.png"]
        placa_geometry = placaGeometry()
        placa_material = TextureMaterial(texture=Texture(texturas))
        placa = Mesh(placa_geometry, placa_material)
        placa.set_position([0, 0, -10])
        self.scene.add(placa)
        """

        # Criação do jet ski
        jetski_material = TextureMaterial(texture=Texture("images/blue.jpg"))
        jetski_geometry = JetskiGeometry()
        jetski = Mesh(jetski_geometry, jetski_material)
        jetski.set_position([0, 0, -10])
        self.scene.add(jetski)

        # Criação yate
        yatch_material = TextureMaterial(texture=Texture("images/red2.jpg"))
        yatch_geometry = YatchGeometry()
        yatch = Mesh(yatch_geometry, yatch_material)
        yatch.set_position([10, 0, -13])
        self.scene.add(yatch)

        # Criação dos animais
        animal_material = TextureMaterial(texture=Texture("images/k2.png"))
        animal_geometry = animalGeometry()
        animal = Mesh(animal_geometry, animal_material)
        animal.set_position([-10, -1, -25])
        self.scene.add(animal)
        golfinho_material = TextureMaterial(texture=Texture("images/golfinho.jpg"))
        golfinho_geometry = golfinhoGeometry()
        golfinho = Mesh(golfinho_geometry, golfinho_material)
        golfinho.set_position([-5, -0.25, -20])
        self.scene.add(golfinho)

        # Criação bola
        bola_material = TextureMaterial(texture=Texture("images/volleyball.png"))
        bola_geometry = bolaGeometry()
        bola = Mesh(bola_geometry, bola_material)
        bola.set_position([-5, 0.15, -3.5])
        self.scene.add(bola)

        #Easter Egg
        pokeball_material = TextureMaterial(texture=Texture("images/poke.png"))
        pokeball_geometry = pokeballGeometry()
        pokeball = Mesh(pokeball_geometry, pokeball_material)
        pokeball.set_position([0, -0.001, -12])
        self.scene.add(pokeball)

        warship_material = TextureMaterial(texture=Texture("images/warship.png"))
        warship_geometry = warshipGeometry()
        warship = Mesh(warship_geometry, warship_material)
        warship.set_position([0, 0, -85])
        self.scene.add(warship)

        # Criação da camera
        self.camera = Camera(aspect_ratio=800/600)
        self.camera.set_position([0.65, 2.5, -2])
        self.rig.add(self.camera)
        self.scene.add(self.rig)
        #

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
            if self.camera != other_obj and self.camera.intersects(other_obj):
                # Collision detected, determine direction
                collision_direction = self.determine_collision_direction(other_obj)
                print("Collision detected!")
                return collision_direction
        return None

    def determine_collision_direction(self, other_obj):
        """
        Determine the direction of collision between the camera and another object.
        """
        # Get positions of camera and other object
        cam_pos = np.array(self.camera.global_position)
        obj_pos = np.array(other_obj.global_position)
        # Calculate direction vector from other object to camera
        direction = cam_pos - obj_pos
        # Determine dominant axis of direction vectorw
        max_index = np.argmax(np.abs(direction))
        if max_index == 0:
            # X-axis is dominant
            return "x"
        elif max_index == 1:
            # Y-axis is dominant
            return "y"
        else:
            # Z-axis is dominant
            return "z"

        
    def update(self):
        self.distort_material.uniform_dict["time"].data += self.delta_time/5
        self.rig.update(self.input, self.delta_time)
        self.renderer.render(self.scene, self.camera)
        # Check for collisions
        collision_direction = self.check_collisions()  # Get collision direction
        if collision_direction:
            # If collision occurred, restrict movement in that direction
            self.rig.restrict_movement(collision_direction)
        else:
            # No collision, allow movement in all directions
            self.rig.allow_movement()

# Instantiate this class and run the program
Example(screen_size=[800, 600]).run()
