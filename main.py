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
from geometry.esperguica import espreguicaGeometry 
from geometry.animal import animalGeometry
from geometry.arvore import ArvoreGeometry
from geometry.bola import bolaGeometry
from geometry.bikini import BikiniGeometry
from geometry.cadeira import cadeiraGeometry
from geometry.casa import casaGeometry
from geometry.golfinho import golfinhoGeometry
from geometry.jetski import JetskiGeometry
from geometry.modelo import ModeloGeometry
from geometry.oculos import OculosGeometry
from geometry.cubo import CuboGeometry
from geometry.passa import passaGeometry
from geometry.passa2 import passa2Geometry
from geometry.placa import placaGeometry
from geometry.portal import portalGeometry
from geometry.stand import standGeometry
from geometry.pokeball import pokeballGeometry
from geometry.rocks import rocksGeometry
from geometry.sombrinha import sombrinhaGeometry
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
    Para mexer a camera usar up left right down e as teclas p l n m
    """
    def initialize(self):
        print("Initializing program...")
        print("Para mexer o modelo usar as teclas w,a,s,d")
        print("Para mexer a camera usar as teclas q(esquerda),e (direita),t (cima), g(baixo) ou o cursor")
        print("Para mudar a camera telca 'c', espaço para saltar e shift para sprintar")
        print("Para ativar o modo criativo pressionar a tecla 'u' e usar 'z' para subir e 'x' para descer")

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

        # Define grid properties
        self.grid_size = 2  # Size of each grid cell
        self.grid = {}  # Dictionary to store objects in each grid cell

        # Criação da cena
        self.renderer = Renderer()
        self.scene = Scene()
        self.rig = MovementRig()
        self.rig2 = MovementRig2()
        self.rig3 = MovementRig3()

        # Adiciona luzes
        # Luz ambiente
        self.ambient_light = AmbientLight(color=[0.1, 0.1, 0.1])
        self.scene.add(self.ambient_light)

        # Luz direcional
        self.directional_light = DirectionalLight(color=[0.8, 0.8, 0.8], direction=[-1, -1, 0])
        self.scene.add(self.directional_light)

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

        """# Testes
        phong_material = PhongMaterial(
            property_dict={"baseColor": [1, 0, 1]},
            number_of_light_sources=2
        )
        sphere_geometry = SphereGeometry()
        sphere_right = Mesh(sphere_geometry, phong_material)
        sphere_right.set_position([2.5, 0, 0])
        self.scene.add(sphere_right)"""
        
        #Passadiço vertical
        passa_material = TextureMaterial(texture=Texture("images/passa.png"))
        passa_geometry = passaGeometry()
        passa_positions = [
                           [30,-2,55.5],[30,-2,64],[30,-2,72.5],[30,-2,81],[30,-2,89.5]
                           ]
        for position in passa_positions:
            passa = Mesh(passa_geometry, passa_material)
            passa.set_position(position)
            self.scene.add(passa) 

        #Passadiço horizontal
        passa_material = TextureMaterial(texture=Texture("images/passa.png"))
        passa_geometry = passa2Geometry()
        passa_positions = [
                           [-80.5,-2,53.5],[-72,-2,53.5],[-63.5,-2,53.5], [-55,-2,53.5],[-46.5,-2,53.5],
                           [-38,-2,53.5], [-29.5,-2,53.5],[-21,-2,53.5],[-12.5,-2,53.5],[-4,-2,53.5],
                           [4.5,-2,53.5],[13,-2,53.5],[21.5,-2,53.5],[30,-2,53.5],[38.5,-2,53.5],
                           [30,-2,53.5],[38.5,-2,53.5],[47,-2,53.5],[55.5,-2,53.5],[64,-2,53.5],[72.5,-2,53.5],[81,-2,53.5]
                           ]
        for position in passa_positions:
            passa = Mesh(passa_geometry, passa_material)
            passa.set_position(position)
            self.scene.add(passa) 

        #criação das árvores
        #coordenadas, sentido positivo da direita para a esquerda
        arvore_material = TextureMaterial(texture=Texture("images/arvore2.jpg"))
        arvore_geometry = ArvoreGeometry()
        arvore_positions= [
                        [-70, -3, 60],[-60, -3, 60],[-50, -3, 60],[-40, -3, 60],[-30, -3, 60],
                        [-20, -3, 60],[-10, -3, 60],[10, -3, 60],
                        [20, -3, 60],[25, -3, 60],[35, -3, 60],[40, -3, 60],
                        [50, -3, 60],[60, -3, 60],[70, -3, 60],
                        
                        [-70, -3, 70],[-60, -3, 70],[-50, -3, 70],[-40, -3, 70],[-30, -3, 70],
                        [-20, -3, 70],[-10, -3, 70],[10, -3, 70],
                        [20, -3, 70],[25, -3, 70],[35, -3, 70],[40, -3, 70],
                        [50, -3, 70],[60, -3, 70],[70, -3, 70],

                        [-70, -3, 80],[-60, -3, 80],[-50, -3, 80],[-40, -3, 80],[-30, -3, 80],
                        [-20, -3, 80],[-10, -3, 80],[10, -3, 80],
                        [20, -3, 80],[25, -3, 80],[35, -3, 80],[40, -3, 80],
                        [50, -3, 80],[60, -3, 80],[70, -3, 80],
                        ]
        for position in arvore_positions:
            arvore = Mesh(arvore_geometry, arvore_material)
            arvore.set_position(position)
            self.scene.add(arvore)
  
        # Criação rochas
        rocks_material = TextureMaterial(texture=Texture("images/rock.jpg"))
        rocks_geometry = rocksGeometry()
        rock_positions = [
                          [-80, -1, -50],[-80, -1, -45],[-80, -1, -40],[-80, -1, -35],[-80, -1, -30],[-80, -1, -25],
                          [-80, -1, -20],[-80, -1, -15],[-80, -1, -10],[-80, -1, -5],[-80, -1, 0],
                          [-80, -1, 5],[-80, -1, 10],[-80, -1, 15],[-80, -1, 20],[-80, -1, 25],
                          [-80, -1, 30],[-80, -1, 35],[-80, -1, 40],[-78, -1, 45],
                          [85, -1, -50],[85, -1, -45],[85, -1, -40],[85, -1, -35],[85, -1, -30],
                          [85, -1, -25],[85, -1, -20],[85, -1, -15],[85, -1, -10],[85, -1, -5],
                          [85, -1, 0],[85, -1, 5],[85, -1, 10],[85, -1, 15],[85, -1, 20],[85, -1, 25],
                          [85, -1, 30],[85, -1, 35],[85, -1, 40],[83, -1, 45],
                          ]
        for position in rock_positions:
            rocks = Mesh(rocks_geometry, rocks_material)
            rocks.set_position(position)
            self.scene.add(rocks)

        # Criação das toalhas
        texturas = ["images/SLB.jpg", "images/goku.png", "images/master.jpg"]
        toalha_geometry = ToalhaGeometry()
        toalha_positions = [[-50, 0, 15],[-50, 0, 10],[-35, 0, 5],[-35, 0, 2],[-20, 0, 10],
                            [-15, 0, 10],[-15, 0, 5],[-10, 0, 5],[-10, 0, 10],[-7, 0, 15],[-6, 0, 10],[-2, 0, 5],
                            [0, 0, 10],[6, 0, 10],[10, 0, 5],[14, 0, 10],[16, 0, 15],[19, 0, 5],[22, 0, 10],
                            [25, 0, 5],[35, 0, 5],[40, 0, 15],[40, 0, 7],[55, 0, 10],[55, 0, 5],[70, 0, 10],[70, 0, 15]]
        for position in toalha_positions:
            toalha_material = TextureMaterial(texture=Texture(np.random.choice(texturas)))
            toalha = Mesh(toalha_geometry, toalha_material)
            toalha.set_position(position)
            toalha.scale(2.5)
            self.scene.add(toalha)

        #criação das sombrinhas
        sombrinha_material = TextureMaterial(texture=Texture("images/rgb-noise.jpg"))
        sombrinha_geometry = sombrinhaGeometry()
        sombrinha_positions= [
                        [-60, 0, 7],[-40, 0, 2],[-30, 0, 4.5],[-20, 0, 2],[-10, 0, 8],
                        [10, 0, 3],[20, 0, 2],[30, 0, 4.5],[40, 0, 2],[60, 0, 7]
                        ]
        for position in sombrinha_positions:
            sombrinha = Mesh(sombrinha_geometry, sombrinha_material)
            sombrinha.set_position(position)
            self.scene.add(sombrinha)

        #criação da cadeira
        cadeira_material = TextureMaterial(texture=Texture("images/whool.jpg"))
        cadeira_geometry = cadeiraGeometry()
        cadeira_positions= [
                        [-59, 0, 9],[-39, 0, 4],[-29, 0, 6.5],[-19, 0, 4],[-9, 0, 10],
                        [9, 0, 5],[19, 0, 4],[29, 0, 6.5],[39, 0, 4],[59, 0, 9],
                        ]
        for position in cadeira_positions:
            cadeira = Mesh(cadeira_geometry, cadeira_material)
            cadeira.set_position(position)
            self.scene.add(cadeira)

        #criação da espreguiçadeira
        espreguica_material = TextureMaterial(texture=Texture("images/golfinho.jpg"))
        espreguica_geometry = espreguicaGeometry()
        espreguica_positions= [
                        [-59, 0, 40],[-39, 0, 40],[-29, 0, 40],[-19, 0, 40],[-9, 0, 40],
                        [9, 0, 40],[19, 0, 40],[29, 0, 40],[39, 0, 40],[59, 0, 40],
                        ]
        for position in espreguica_positions:
            espreguica = Mesh(espreguica_geometry, espreguica_material)
            espreguica.set_position(position)
            self.scene.add(espreguica)

        #criação da casa
        casa_material = TextureMaterial(texture=Texture("images/casa.png"))
        casa_geometry = casaGeometry()
        casa = Mesh(casa_geometry, casa_material)
        casa.set_position([-30, 0, 30])
        self.scene.add(casa)

        # Criação do bikini
        bikini_material = TextureMaterial(texture=Texture("images/rgb-noise.jpg"))
        bikini_geometry = BikiniGeometry()
        bikini = Mesh(bikini_geometry, bikini_material)
        bikini.set_position([-1, 0, 0])
        self.scene.add(bikini)

        # Criação dos oculos
        oculos_material = TextureMaterial(texture=Texture("images/oculos.jpg"))
        oculos_geometry = OculosGeometry()
        self.oculos = Mesh(oculos_geometry, oculos_material)
        self.oculos.set_position([0, 0, 0.09])
        self.oculos.rotate_y(179.1)

        # Criação do portal
        portal_material = TextureMaterial(texture=Texture("images/portal.jpg"))
        portal_geometry = portalGeometry()
        portal = Mesh(portal_geometry, portal_material)
        #portal.set_position([-1.75, 35, 90.5])
        portal.set_position([-1.75, 36, 86])
        self.scene.add(portal)
        
        #placa das direções
        placa_material = TextureMaterial(texture=Texture("images/p2.png"))
        placa_geometry = placaGeometry()
        placa = Mesh(placa_geometry, placa_material)
        placa.set_position([-2, 0, 16])
        self.scene.add(placa)

        #placa das instruções
        stand_material = TextureMaterial(texture=Texture("images/metal.jpg"))
        stand_geometry = standGeometry()
        self.stand = Mesh(stand_geometry, stand_material)
        self.stand.set_position([8, 0, 14])
        self.scene.add(self.stand)

        # Criação do jet ski
        jetski_material = TextureMaterial(texture=Texture("images/blue.jpg"))
        jetski_geometry = JetskiGeometry()
        jetski = Mesh(jetski_geometry, jetski_material)
        jetski.set_position([0, 0, -10])
        self.scene.add(jetski)

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

        """#Navios
        warship_material = TextureMaterial(texture=Texture("images/warship.png"))
        warship_geometry = warshipGeometry()
        warship = Mesh(warship_geometry, warship_material)
        warship.set_position([-10, 0, -75])
        self.scene.add(warship)

        warship2_material = TextureMaterial(texture=Texture("images/T (61).png"))
        warship2_geometry = warship2Geometry()
        warship2 = Mesh(warship2_geometry, warship2_material)
        warship2.set_position([40, 0, -55])
        self.scene.add(warship2)
        
        # Criação yate
        yatch_material = TextureMaterial(texture=Texture("images/red2.jpg"))
        yatch_geometry = YatchGeometry()
        yatch = Mesh(yatch_geometry, yatch_material)
        yatch.set_position([10, 0, -13])
        self.scene.add(yatch)"""

        #modelo do boneco
        modelo_material = TextureMaterial(texture=Texture("images/Cor_Modelo.jpg"))
        modelo_geometry = ModeloGeometry()
        self.modelo = Mesh(modelo_geometry, modelo_material)
        self.modelo.set_position([0, 0, 0])
        #self.modelo.set_position([-1.75,29.5,79.5])
        self.modelo.rotate_y(110)

        #criação do cubo
        cubo_material = TextureMaterial(texture=Texture("images/mine.png"))
        cubo_geometry = CuboGeometry()
        cubo = Mesh(cubo_geometry, cubo_material)
        self.cube_positions = {
            "grupo1": [[-1.75, 4.5, 19.5], [-1.75, 6.5, 21.5], [-1.75, 8.5, 23.5]],
            "grupo2_x": [[-1.75, 9.5, 31.5],[-1.75, 9.5, 33.5],[-1.75, 9.5, 35.5]],
            "grupo3_x": [[-1.75, 14.5, 45.5]],
            "grupo3_y": [[-1.75, 14.5, 43.5], [-1.75, 14.5, 47.5]],
            "grupo4_x": [[-1.75, 19.5, 55.5]],
            "grupo4_y": [[-1.75, 19.5, 57.5], [-1.75, 19.5, 59.5]],
            "grupo5_x": [[-1.75, 24.5, 65.5]],
            "grupo5_y": [[-1.75, 24.5, 67.5], [-1.75, 24.5, 69.5]],
            "grupo6_x": [[-1.75, 29.5, 77.5]],
            "grupo6_y": [[-1.75, 29.5, 79.5], [-1.75, 29.5, 81.5]],
        }
        # Create and store the cube meshes in the same dictionary
        self.cube_meshes = {
            "grupo1": [],
            "grupo2_x": [],
            "grupo3_x": [],
            "grupo3_y": [],
            "grupo4_x": [],
            "grupo4_y": [],
            "grupo5_x": [],
            "grupo5_y": [],
            "grupo6_x": [],
            "grupo6_y": [],
        }
        # Create the cubes and store the references in the dictionary
        for grupo, positions in self.cube_positions.items():
            for position in positions:
                cubo = Mesh(cubo_geometry, cubo_material)
                cubo.set_position(position)
                self.scene.add(cubo)
                self.cube_meshes[grupo].append(cubo)
                
        # Criação da camera
        self.camera = Camera(aspect_ratio=800/600)
        self.camera.set_position([0, 2.93, 0])
        #self.camera.set_position([-1.75,29.5+2.93,79.5-1])
        self.rig.add(self.camera)
        self.scene.add(self.rig)
        self.scene.add(self.rig2)
        self.scene.add(self.rig3)

        # Criaçao da camara alternativa
        self.third_person_cam = Camera(aspect_ratio=800/600)
        self.third_person_cam.set_position([0, 2.5, 4])
        self.rig3.add(self.third_person_cam)
        self.active_camera = self.camera

        self.toggle_camera = False

    def update(self):
        self.distort_material.uniform_dict["time"].data += self.delta_time/5
        # Time-based movement using sine function
        time = self.time * 0.5  # Adjust the speed of the movement
        
        # Atualizar a lógica de rotação para apenas no eixo X
        if self.active_camera == self.camera:
            camera_position = self.camera.global_position
            look_at_position = [camera_position[0], 0, camera_position[2]]
        else:
            modelo_position = self.modelo.global_position
            look_at_position = [modelo_position[0], 0, modelo_position[2]]
        
        self.stand.look_at(look_at_position)
        
        # Define different amplitudes for each group
        amplitudes = {
            "grupo1": 1.2,
            "grupo2_x": 2.4,
            "grupo3_x": 5.0,
            "grupo3_y": 5.0,
            "grupo4_x": 10.0,
            "grupo4_y": 10.0,
            "grupo5_x": 10.0,
            "grupo5_y": 10.0,
            "grupo6_x": 10.0,
            "grupo6_y": 10.0,
        }
        
        for grupo, meshes in self.cube_meshes.items():#movimentação dos cubos
            amplitude = amplitudes[grupo]  # Get the amplitude for the current group
            for i, mesh in enumerate(meshes):
                original_position = self.cube_positions[grupo][i]
                if '_y' in grupo:
                    # Vertical 
                    new_y = original_position[1] + amplitude * math.sin(time + i)
                    mesh.set_position([original_position[0], new_y, original_position[2]])
                elif '_x' in grupo:
                    # Horizontal 
                    new_x = original_position[0] + amplitude * math.sin(time + i)
                    mesh.set_position([new_x, original_position[1], original_position[2]])
                else:
                    # grupo sem '_x' or '_y' adota o tradicional movimento em Y
                    new_y = original_position[1] + amplitude * math.sin(time + i)
                    mesh.set_position([original_position[0], new_y, original_position[2]])
        
        if self.input.is_key_pressed('c'):
            if not self.toggle_camera:
                self.toggle_camera = True
                if self.active_camera == self.camera:
                    self.active_camera = self.third_person_cam
                    self.rig3.set_rotation_x(0)
                    # Adicionar o modelo e os óculos à cena
                    self.rig2.add(self.modelo)
                    self.rig2.add(self.oculos)
                else:
                    self.active_camera = self.camera
                    self.rig.set_rotation_x(0)
                    # Remover o modelo e os óculos da cena
                    self.rig2.remove(self.modelo)
                    self.rig2.remove(self.oculos)
        else: 
            self.toggle_camera = False
        collision = self.check_collisions()  # Get collision direction
        self.rig.update(self.input, self.delta_time, collision)
        self.rig2.update(self.input, self.delta_time, collision)
        self.rig3.update(self.input, self.delta_time, collision)
        self.renderer.render(self.scene, self.active_camera)
        # Check for collisions

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
            # Ignore collisions with oculos and modelo
            if other_obj == self.oculos or other_obj == self.modelo:
                continue
            if other_obj != self.camera and self.camera.intersects(other_obj):
                self.determine_collision_direction(other_obj)
                return True
            elif other_obj != self.third_person_cam and self.third_person_cam.intersects(other_obj):
                self.determine_collision_direction(other_obj)
                return True
        return False

    def determine_collision_direction(self, other_obj):
        """
        Determine the direction of collision between the camera and another object.
        """
        # Get positions of camera and other object
        cam_pos = np.array(self.camera.global_position)
        obj_pos = np.array(other_obj.global_position)
        obj_height = other_obj._heightMesh

        if cam_pos[1] > obj_pos[1] + obj_height/2:
            self.rig.translate(0, 0.2, 0)
            return "up"
        # Calculate direction vector from other object to camera
        direction = cam_pos - obj_pos

        direction = [direction[0], direction[2]]
        min_index = np.argmin(np.abs(direction))
        
        if min_index == 0:
            if direction[0] > 0:
                self.rig.translate(0.1, 0, 0)
            else:
                self.rig.translate(-0.1, 0, 0)
        else:
            if direction[1] > 0:
                self.rig.translate(0,0 , 0.1)
            else:
                self.rig.translate(0, 0, -0.1)

# Instantiate this class and run the program
Example(screen_size=[800, 600]).run()