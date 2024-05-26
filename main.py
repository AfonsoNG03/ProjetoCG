import numpy as np
import math
import pygame
import os
import pathlib
import sys

from core.menu import GameMenu
from core.base import Base
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from core_ext.renderer2 import Renderer
from core_ext.scene import Scene
from extras.movement_rig import MovementRig
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
from geometry.salva import salvaGeometry
from geometry.sombrinha import sombrinhaGeometry
from geometry.rectangle import RectangleGeometry
from geometry.sphere import SphereGeometry
from geometry.toalha import ToalhaGeometry
from light.ambient import AmbientLight
from light.directional import DirectionalLight
from material.material import Material
from core_ext.texture import Texture
from extras.text_texture import TextTexture
from material.texture import TextureMaterial
import time

class Example(Base):
    """
    Render the axes and the rotated xy-grid.
    Add box movement: WASDRF(move), QE(turn), TG(look).
    Para mexer a camera usar up left right down e as teclas p l n m
    """
    def initialize(self):
        print("Initializing program...")
        print("Ao entrar no menu tem as opções de jogar, ver o placar e sair, para sair do placar pressione esc")
        print("Para mexer o modelo usar as teclas w,a,s,d")
        print("Para mexer a camera usar as teclas q(esquerda),e (direita),t (cima), g(baixo) ou o cursor")
        print("Para mudar a camera telca 'c', espaço para saltar e shift para sprintar")

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

        # Initialize Pygame mixer
        pygame.mixer.init()
        # Print current working directory to debug
        print("Current working directory:", os.getcwd())
        # Define the path to the music file
        music_file = 'music/FF2.mp3'
        # Check if the music file exists
        if not os.path.isfile(music_file):
            print(f"Music file not found: {music_file}")
        else:
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)  # musica em loop infinito
                print(f"Playing music: {music_file}")
            except pygame.error as e:
                print(f"Failed to load music file: {music_file}, error: {e}")

        # Define grid properties
        self.grid_size = 5  # Size of each grid cell
        self.grid = {}  # Dictionary to store objects in each grid cell
        self.tempo = 0
        self.objects_to_ignore = []

        # File path to the time records
        time_file_path = pathlib.Path("time_records.txt")
        self.three_lowest_times = self.get_three_lowest_times(time_file_path)
        self.checkPoint = False

        # Tempos
        self.start_time = 0
        self.timer_running = False
        self.cube_start_position = [-1.75, 2.0, 19.5] 
        self.final_portal_position = [48, 26, 2]  
        self.time_file_path = pathlib.Path("time_records.txt")

        self.tempos_string = "|| "
        for i, time in enumerate(self.three_lowest_times):
            self.tempos_string += f"{i+1} -> {time:.0f} s  || "

        # Criação da cena
        self.renderer = Renderer()
        self.scene = Scene()
        self.rig = MovementRig()
        self.rig3 = MovementRig3()
        self.objects_to_ignore.append(self.rig)
        self.objects_to_ignore.append(self.rig3)

        # Adiciona luzes
        # Luz ambiente
        self.ambient_light = AmbientLight(color=[0.1, 0.1, 0.1])
        self.scene.add(self.ambient_light)
        self.objects_to_ignore.append(self.ambient_light)

        # Luz direcional
        self.directional_light = DirectionalLight(color=[0.8, 0.8, 0.8], direction=[-1, -1, 0])
        self.scene.add(self.directional_light)
        self.objects_to_ignore.append(self.directional_light)

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
        self.objects_to_ignore.append(self.ocean)
    
        # Textura do céu
        sky_geometry = SphereGeometry(radius=100)
        sky_material = TextureMaterial(texture=Texture(file_name="images/sky.jpg"))
        self.sky = Mesh(sky_geometry, sky_material)
        self.scene.add(self.sky)
        self.objects_to_ignore.append(self.sky)

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
        self.objects_to_ignore.append(self.sand)

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
            self.objects_to_ignore.append(passa)

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
            self.objects_to_ignore.append(passa)

        #criação das árvores
        #coordenadas, sentido positivo da direita para a esquerda
        arvore_material = TextureMaterial(texture=Texture("images/arvore2.jpg"))
        arvore_geometry = ArvoreGeometry()
        arvore_positions= [
                        [-70, -3, 60],[-60, -3, 60],[-50, -3, 60],[-40, -3, 60],[-30, -3, 60],
                        [-20, -3, 60],[-10, -3, 60],[10, -3, 60],
                        [20, -3, 60],[25, -3, 60],[35, -3, 60],[40, -3, 60],
                        [50, -3, 60],[60, -3, 60],[70, -3, 60],
                        
                        [-60, -3, 70],[-50, -3, 70],[-40, -3, 70],[-30, -3, 70],
                        [-20, -3, 70],[-10, -3, 70],[10, -3, 70],
                        [20, -3, 70],[25, -3, 70],[35, -3, 70],[40, -3, 70],
                        [50, -3, 70],[60, -3, 70],

                        [-50, -3, 80],[-40, -3, 80],[-30, -3, 80],
                        [-20, -3, 80],[-10, -3, 80],[10, -3, 80],
                        [20, -3, 80],[25, -3, 80],[35, -3, 80],[40, -3, 80],
                        [50, -3, 80],
                        ]
        for position in arvore_positions:
            arvore = Mesh(arvore_geometry, arvore_material)
            arvore.set_position(position)
            self.scene.add(arvore)
            self.objects_to_ignore.append(arvore)

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
            self.objects_to_ignore.append(rocks)

        #Criação das toalhas
        texturas = ["images/SLB.jpg", "images/goku.png", "images/master.jpg", "images/lakers.png", "images/mario.png", "images/psg.png", "images/loveless.png", "images/pompup.png", "images/fish.png", "images/muppets.png", "images/owl.png", "images/wazowski.png"]
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
            self.objects_to_ignore.append(toalha)

        #criação das sombrinhas
        sombrinha_material = TextureMaterial(texture=Texture("images/parasol.jpg"))
        sombrinha_geometry = sombrinhaGeometry()
        sombrinha_positions= [
                        [-60, 0, 7],[-40, 0, 2],[-30, 0, 4.5],[-20, 0, 2],[-10, 0, 8],
                        [10, 0, 3],[20, 0, 2],[30, 0, 4.5],[40, 0, 2],[60, 0, 7]
                        ]
        for position in sombrinha_positions:
            sombrinha = Mesh(sombrinha_geometry, sombrinha_material)
            sombrinha.set_position(position)
            self.scene.add(sombrinha)
            self.objects_to_ignore.append(sombrinha)

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
            self.objects_to_ignore.append(cadeira)

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
            self.objects_to_ignore.append(espreguica)

        #criação da casa
        casa_material = TextureMaterial(texture=Texture("images/casa.png"))
        casa_geometry = casaGeometry()
        casa = Mesh(casa_geometry, casa_material)
        casa.set_position([-30, 0, 30])
        self.scene.add(casa)
        self.objects_to_ignore.append(casa)

        # Criação dos oculos
        oculos_material = TextureMaterial(texture=Texture("images/oculos.jpg"))
        oculos_geometry = OculosGeometry()
        self.oculos = Mesh(oculos_geometry, oculos_material)
        self.oculos.set_position([0, 0, 0.09])
        self.oculos.rotate_y(179.1)
        self.objects_to_ignore.append(self.oculos)

        #Criação do portal
        portal_material = TextureMaterial(texture=Texture("images/portal.jpg"))
        portal_geometry = portalGeometry()
        portal = Mesh(portal_geometry, portal_material)
        portal.set_position([-18, 52.0, 48.0])
        self.scene.add(portal)
        self.objects_to_ignore.append(portal)
        portal = Mesh(portal_geometry, portal_material)
        portal.set_position([-24, 52.0, -50.0])
        portal.rotate_y(math.pi/2)
        self.scene.add(portal)
        self.objects_to_ignore.append(portal)
        portal = Mesh(portal_geometry, portal_material)
        portal.set_position([48,32,2])
        self.scene.add(portal)
        self.objects_to_ignore.append(portal)

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

        #modelo do boneco
        modelo_material = TextureMaterial(texture=Texture("images/Cor_Modelo.jpg"))
        modelo_geometry = ModeloGeometry()
        self.modelo = Mesh(modelo_geometry, modelo_material)
        self.modelo.set_position([0, 0, 0])
        self.modelo.rotate_y(110)
        self.rig.add(self.modelo)
        self.objects_to_ignore.append(self.modelo)

        # LeaderBoard
        geometry = RectangleGeometry(width=2)
        message = TextTexture(text=self.tempos_string,
                               system_font_name="Impact",
                               font_size=32, font_color=[200, 0, 0],
                               image_width=600, image_height=300, transparent=True)
        material = TextureMaterial(message)
        self.mensagem = Mesh(geometry, material)
        self.mensagem.set_position([-1.5, 4.1, 0])
        self.rig.add(self.mensagem)
        self.rig3.add(self.mensagem)
        self.objects_to_ignore.append(self.mensagem)

        RectGeometry = RectangleGeometry(width=2)
        cTime = TextTexture(text= f"{self.start_time:.0f} s",
                               system_font_name="Impact",
                               font_size=32, font_color=[200, 0, 0],
                               image_width=600, image_height=300, transparent=True)
        materialT = TextureMaterial(cTime)
        self.cTime1 = Mesh(RectGeometry, materialT)
        self.cTime1.set_position([2.8, 4.1, 0])
        self.rig.add(self.cTime1)
        self.rig3.add(self.cTime1)
        self.objects_to_ignore.append(self.cTime1)

        #modelo do nadador salvador
        salva_material = TextureMaterial(texture=Texture("images/mass_monster.png"))
        salva_geometry = salvaGeometry()
        salva = Mesh(salva_geometry, salva_material)
        salva.set_position([-25, 4.8, 20])
        self.scene.add(salva)
        self.objects_to_ignore.append(salva)

        cubo_material = TextureMaterial(texture=Texture("images/mine.png"))
        cubo_geometry = CuboGeometry()
        cubo = Mesh(cubo_geometry, cubo_material)
        self.cube_positions = {
            "grupo1": [[-1.75, 2.0, 19.5], [-1.75, 4.0, 27.5], [-1.75, 6.0, 35.5]],
            "grupo2_x": [[-1.75, 8.0, 43.5], [-1.75, 10.0, 51.5], [-1.75, 12.0, 59.5]],
            "grupo3_x": [[-1.75, 14.0, 67.5]],
            "grupo3_y": [[-1.75, 16.0, 75.5], [-1.75, 18.0, 83.5], [-1.75, 20.0, 90]],
            "grupo4_x": [[-9, 22.0, 82.0], [-9, 24.0, 74.0], [-9, 26.0, 66.0], [-9, 28.0, 58.0]],
            "grupo5_x": [[-9, 30.0, 50.0]],
            "grupo5_y": [[-9, 32.0, 42.0], [-9, 34.0, 34.0], [-9, 36.0, 26.0]],
            "grupo6_x": [[-18, 38.0, 18.0] , [-18, 40.0, 26.0], [-18, 42.0, 34.0], [-18, 44.0, 42.0]],
            "Plataform": [[-18, 46.0, 50.0], [-16, 46, 50], [-16, 46, 48], [-18, 46, 48], [-20, 46, 48], [-20, 46, 50], [-20, 46, 52] , [-18, 46, 52], [-16, 46, 52]
                        ,[-14, 46, 52], [-14, 46, 50], [-14, 46, 48], [-22, 46, 48], [-22, 46, 50], [-22, 46, 52]],
            "Plataform2": [[-18, 46.0, -50.0], [-16, 46, -50], [-16, 46, -48], [-18, 46, -48], [-20, 46, -48], [-20, 46, -50], [-20, 46, -52] , [-18, 46, -52], [-16, 46, -52]
                        ,[-14, 46, -52], [-14, 46, -50], [-14, 46, -48], [-22, 46, -48], [-22, 46, -50], [-22, 46, -52]],
            "grupo7_x": [[-3, 40, -50], [6, 35, -50]],
            "grupo8_x": [[20, 30, -50], [25, 25, -50] , [35, 20, -50]],
            "grupo9_x": [[40, 22, -42], [48, 24, -36] , [40, 26, -28]],
            "Fim": [[48, 26, -20], [48, 26, -10] , [48, 26, 0],
                    [48,26,2] , [48,26,4] , [48,26,6] , [46,26,2], [46,26,4], [46,26,6], [50,26,2], [50,26,4], [50,26,6]
                    , [52,26,2], [52,26,4], [52,26,6], [44,26,2], [44,26,4], [44,26,6]],
        }

        # Create and store the cube meshes in the same dictionary
        self.cube_meshes = {
            "grupo1": [],
            "grupo2_x": [],
            "grupo3_x": [],
            "grupo3_y": [],
            "grupo4_x": [],
            "grupo5_x": [],
            "grupo5_y": [],
            "grupo6_x": [],
            "Plataform": [],
            "Plataform2": [],
            "grupo7_x": [],
            "grupo8_x": [],
            "grupo9_x": [],
            "Fim": []
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
        self.camera.set_position([0, 2.93, -1])
        #self.camera.set_position([-1.75,29.5+2.93,79.5-1])
        self.rig.add(self.camera)
        self.scene.add(self.rig)

        # Criaçao da camara alternativa
        self.static_camera = Camera(aspect_ratio=800/600)
        self.static_camera.set_position([0, 4, 4])
        model_position = self.modelo.global_position
        self.static_camera.look_at([model_position[0], model_position[1]+2.5, model_position[2]])
        self.rig3.add(self.static_camera)

        # Criacao da camara cinemática
        self.cinematic_camera = Camera(aspect_ratio=800/600)
        self.cinematic_camera.set_position([10, 10, 10])
        model_position = self.modelo.global_position
        self.cinematic_camera.look_at([model_position[0], model_position[1]+2.5, model_position[2]])
        self.active_camera = self.camera
        self.toggle_camera = False
        self.update_grid()

    # Function to read times from the file and return the three lowest times
    def get_three_lowest_times(self, file_path):
        times = []
        with open(file_path, "r") as file:
            for line in file:
                if "Time:" in line:
                    time_str = line.split("Time:")[1].strip().split()[0]
                    times.append(float(time_str))
        return sorted(times)[:3]

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
            #if obj == self.rig or obj == self.ambient_light or obj == self.ocean or obj == self.sand or obj == self.directional_light or obj == self.sky:
            if obj in self.objects_to_ignore:
                continue
            self.add_to_grid(obj)
        print(len(self.grid))

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
        if self.camera == self.static_camera:
            cam_pos = cam_pos 
        obj_pos = np.array(other_obj.global_position)

        # Calculate the vector from the camera to the object
        collision_vector = obj_pos - cam_pos
        collision_vector[1] -= 0.15

        # Normalize the vector to get the direction
        collision_direction = collision_vector / np.linalg.norm(collision_vector)
        
        # Determine the direction
        #direction = ''
        if  other_obj.global_position[1] + other_obj._height/2 +2.45 <= self.camera.global_position[1]:
            if abs(collision_direction[0]) > abs(collision_direction[1]) and abs(collision_direction[0]) > abs(collision_direction[2]):
                if collision_direction[0] > 0:
                    #direction = 'right'
                    self.rig.translate(-0.1, 0, 0, False)
                    self.rig3.translate(-0.1, 0, 0, False)
                else:
                    #direction = 'left'
                    self.rig.translate(0.1, 0, 0, False)
                    self.rig3.translate(0.1, 0, 0, False)
            elif abs(collision_direction[1]) > abs(collision_direction[0]) and abs(collision_direction[1])  > abs(collision_direction[2]):
                if collision_direction[1] > -0.1:
                    #direction = 'below'
                    self.rig.translate(0, -0.1, 0, False)
                    self.rig3.translate(0, -0.1, 0, False)
                else:
                    #direction = 'above'
                    if self.camera.global_position[1] - other_obj.global_position[1] <= 3.9:
                        self.rig.translate(0, self._delta_time*2.7, 0, False)
                        self.rig3.translate(0, self._delta_time*2.7, 0, False)
                    return True
            else:
                if collision_direction[2] > 0:
                    #direction = 'front'
                    self.rig.translate(0, 0, -0.1, False)
                    self.rig3.translate(0, 0, -0.1, False)
                else:
                    #direction = 'back'
                    self.rig.translate(0, 0, 0.1, False)
                    self.rig3.translate(0, 0, 0.1, False)
        else:
            if abs(collision_direction[0]) > abs(collision_direction[2]):
                if collision_direction[0] > 0:
                    #direction = 'right'
                    self.rig.translate(-0.1, 0, 0, False)
                    self.rig3.translate(-0.1, 0, 0, False)
                else:
                    #direction = 'left'
                    self.rig.translate(0.1, 0, 0, False)
                    self.rig3.translate(0.1, 0, 0, False)
            else:
                if collision_direction[2] > 0:
                    #direction = 'front'
                    self.rig.translate(0, 0, -0.1, False)
                    self.rig3.translate(0, 0, -0.1, False)
                else:
                    #direction = 'back'
                    self.rig.translate(0, 0, 0.1, False)
                    self.rig3.translate(0, 0, 0.1, False)
        return False
    
    #Diferentes posicoes para a camera cinematogra
    posicoes = [[ 10, 10, 10], [30, 30, 30], [1,10,0] , [ 5, 5, 20]]

    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        print("Timer started")

    def stop_timer(self):
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            self.timer_running = False
            print(f"Timer stopped: {elapsed_time:.2f} seconds")
            self.save_time_to_file(elapsed_time)

    def reset_timer(self):
        self.start_time = 0
        self.timer_running = False
        print("Timer reset")

    def save_time_to_file(self, elapsed_time):
        with open(self.time_file_path, "a") as file:
            file.write(f"Time: {elapsed_time:.2f} seconds\n")
        print(f"Time saved to {self.time_file_path}")

    def check_if_player_fell(self):
        # Example condition to check if the player fell
        if self.rig.global_position[1] <= 0 and self.timer_running:  # Adjust based on your game's logic
            if self.checkPoint:
                self.rig.set_position([-18, 47, -52])
                self.rig3.set_position([-18, 47, -52])
            else: 
                self.reset_timer()
                self.rig.set_position([0, 0, 0])  # Reset player position
                self.rig3.set_position([0, 0, 0])  # Reset player position

    def check_if_player_reached_start(self):
        # Example condition to check if the player reached the start
        if np.linalg.norm(np.array(self.rig.global_position) - np.array(self.cube_start_position)) < 2:
            if not self.timer_running:
                self.start_timer()

    def check_if_player_reached_end(self):
        # Example condition to check if the player reached the end
        if np.linalg.norm(np.array(self.rig.global_position) - np.array(self.final_portal_position)) < 2:
            self.stop_timer()
            self.rig.set_position([0, 0, 0])  # Reset player position
            self.rig3.set_position([0, 0, 0])  # Reset player position
            time_file_path = pathlib.Path("time_records.txt")
            self.three_lowest_times = self.get_three_lowest_times(time_file_path)
            message = TextTexture(text=self.tempos_string,
                               system_font_name="Impact",
                               font_size=32, font_color=[200, 0, 0],
                               image_width=600, image_height=300, transparent=True)
            material = TextureMaterial(message)
            self.mensagem._material = material
            self.checkPoint = False

    def update(self):
        self.distort_material.uniform_dict["time"].data += self.delta_time/5
        time2 = self.time * 0.5  # Adjust the speed of the movement
        
        # Check if the player fell
        self.check_if_player_fell()
        # Check if the player reached the start
        self.check_if_player_reached_start()
        # Check if the player reached the end
        self.check_if_player_reached_end()

        if self.active_camera == self.cinematic_camera:
            self.tempo += self.delta_time
            if self.tempo > 4:
                self.cinematic_camera.set_position(self.posicoes[np.random.randint(0,len(self.posicoes))])
                self.tempo = 0
            modelo_position = self.modelo.global_position
            self.cinematic_camera.look_at([modelo_position[0], modelo_position[1]+2.5, modelo_position[2]])
        
        # Define different amplitudes for each group
        amplitudes = {
            "grupo1": 1.2,
            "grupo2_x": 2.4,
            "grupo3_x": 5.0,
            "grupo3_y": 3,
            "grupo4_x": 5,
            "grupo5_x": 5,
            "grupo5_y": 3.6,
            "grupo6_x": 5,
            "Plataform": 0,
            "Plataform2": 0,
            "grupo7_x": 3,
            "grupo8_x": 4,
            "grupo9_x": 2,
            "Fim": 0
        }
        
        for grupo, meshes in self.cube_meshes.items():#movimentação dos cubos
            amplitude = amplitudes[grupo]  # Get the amplitude for the current group
            for i, mesh in enumerate(meshes):
                original_position = self.cube_positions[grupo][i]
                if '_y' in grupo:
                    # Vertical 
                    new_y = original_position[1] + amplitude * math.sin(time2 + i)
                    mesh.set_position([original_position[0], new_y, original_position[2]])
                elif '_x' in grupo:
                    # Horizontal 
                    new_x = original_position[0] + amplitude * math.sin(time2 + i)
                    mesh.set_position([new_x, original_position[1], original_position[2]])
                else:
                    # grupo sem '_x' or '_y' adota o tradicional movimento em Y
                    new_y = original_position[1] + amplitude * math.sin(time2 + i)
                    mesh.set_position([original_position[0], new_y, original_position[2]])
        
        if self.rig.global_position[0] < -17 and self.rig.global_position[0] > -19 and self.rig.global_position[1] < 49 and self.rig.global_position[1] > 47 and self.rig.global_position[2] < 49 and self.rig.global_position[2] > 47:
            self.checkPoint = True
            self.rig.translate(0, 0, -100, False)
            self.rig3.translate(0, 0, -100, False)

        if self.input.is_key_pressed('c'):
            if not self.toggle_camera:
                self.toggle_camera = True
                if self.active_camera == self.camera:
                    self.active_camera = self.static_camera
                else:
                    self.active_camera = self.camera
        elif self.input.is_key_pressed('v'):
            if not self.toggle_camera:
                self.toggle_camera = True
                if self.active_camera == self.camera:
                    self.active_camera = self.cinematic_camera
                else:
                    self.active_camera = self.camera
        else: 
            self.toggle_camera = False
        collision = self.check_collisions()  # Get collision direction
        self.rig.update(self.input, self.delta_time, collision)
        self.rig3.update(self.input, self.delta_time, collision)
        self.renderer.render(self.scene, self.active_camera)
        self.static_camera 
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
        else:
            elapsed_time = 0
        cTime = TextTexture(text= f" Current Time: {elapsed_time:.0f} s",
                               system_font_name="Impact",
                               font_size=32, font_color=[200, 0, 0],
                               image_width=600, image_height=300, transparent=True)
        materialT = TextureMaterial(cTime)

        self.cTime1._material = materialT
        # Check for collisions

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Beach Rush")

    menu = GameMenu(screen)
    while True:
        choice = menu.run()
        if choice == "start_game":
            break
        elif choice == "options":
            # Handle options logic if needed
            pass
    pygame.quit()

if __name__ == "__main__":
    main()

# Instantiate this class and run the program
Example(screen_size=[800, 600]).run()