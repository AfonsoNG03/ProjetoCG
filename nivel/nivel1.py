

import math
import numpy as np

from core_ext.mesh import Mesh
from core_ext.texture import Texture
from extras.text_texture import TextTexture
from geometry.animal import animalGeometry
from geometry.arvore import ArvoreGeometry
from geometry.bola import bolaGeometry
from geometry.cadeira import cadeiraGeometry
from geometry.casa import casaGeometry
from geometry.cubo import CuboGeometry
from geometry.esperguica import espreguicaGeometry
from geometry.golfinho import golfinhoGeometry
from geometry.modelo import ModeloGeometry
from geometry.oculos import OculosGeometry
from geometry.passa import passaGeometry
from geometry.passa2 import passa2Geometry
from geometry.placa import placaGeometry
from geometry.pokeball import pokeballGeometry
from geometry.portal import portalGeometry
from geometry.rectangle import RectangleGeometry
from geometry.rocks import rocksGeometry
from geometry.salva import salvaGeometry
from geometry.sombrinha import sombrinhaGeometry
from geometry.sphere import SphereGeometry
from geometry.stand import standGeometry
from geometry.toalha import ToalhaGeometry
from light.ambient import AmbientLight
from light.directional import DirectionalLight
from material.material import Material
from material.texture import TextureMaterial


class Nivel1:
    def __init__(self, scene, rig, rig3, time):
        '''
        Inicializa o nivel 1.
        '''

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

        self.scene = scene
        self.rig = rig
        self.rig3 = rig3
        self.time = time
        self.objects_to_ignore = []


        # Luz ambiente
        self.ambient_light = AmbientLight(color=[0.1, 0.1, 0.1])
        self.scene.add(self.ambient_light)
        self.objects_to_ignore.append(self.ambient_light)

        # Luz direcional
        self.directional_light = DirectionalLight(color=[0.8, 0.8, 0.8], direction=[-1, -1, 0])
        self.scene.add(self.directional_light)
        self.objects_to_ignore.append(self.directional_light)

        # Oceano
        rgb_noise_texture = Texture("images/rgb-noise.jpg")
        water_texture = Texture("images/water.jpg")
        self.distort_material = Material(vertex_shader_code, fragment_shader_code)
        self.distort_material.add_uniform("sampler2D", "rgbNoise", [rgb_noise_texture.texture_ref, 1])
        self.distort_material.add_uniform("sampler2D", "image", [water_texture.texture_ref, 2])
        self.distort_material.add_uniform("float", "time", 0.0)
        self.distort_material.add_uniform("vec2", "repeatUV", [10, 10])
        self.distort_material.locate_uniforms()

        ocean_geometry = RectangleGeometry(width=200, height=100)
        self.ocean = Mesh(ocean_geometry, self.distort_material)
        self.ocean.rotate_x(-math.pi/2)
        self.ocean.set_position([0, 0, -55])
        self.scene.add(self.ocean)
        self.objects_to_ignore.append(self.ocean)
    

        # Céu
        sky_geometry = SphereGeometry(radius=100)
        sky_material = TextureMaterial(texture=Texture(file_name="images/sky.jpg"))
        self.sky = Mesh(sky_geometry, sky_material)
        self.scene.add(self.sky)
        self.objects_to_ignore.append(self.sky)


        # Areia
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


        # Passadiço vertical
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


        # Passadiço horizontal
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

        # Árvores
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


        # Rochas
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


        # Toalhas
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
            self.objects_to_ignore.append(toalha)


        # Sombrinhas
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


        # Cadeiras
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


        # Espreguiçadeiras
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


        # Casa
        casa_material = TextureMaterial(texture=Texture("images/casa.png"))
        casa_geometry = casaGeometry()
        casa = Mesh(casa_geometry, casa_material)
        casa.set_position([-30, 0, 30])
        self.scene.add(casa)
        self.objects_to_ignore.append(casa)


        # Óculos
        oculos_material = TextureMaterial(texture=Texture("images/oculos.jpg"))
        oculos_geometry = OculosGeometry()
        self.oculos = Mesh(oculos_geometry, oculos_material)
        self.oculos.set_position([0, 0, 0.09])
        self.oculos.rotate_y(179.1)
        self.objects_to_ignore.append(self.oculos)


        # Portais
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

        # Placa das direções
        placa_material = TextureMaterial(texture=Texture("images/p2.png"))
        placa_geometry = placaGeometry()
        placa = Mesh(placa_geometry, placa_material)
        placa.set_position([-2, 0, 16])
        self.scene.add(placa)


        # Placa das instruções
        stand_material = TextureMaterial(texture=Texture("images/metal.jpg"))
        stand_geometry = standGeometry()
        self.stand = Mesh(stand_geometry, stand_material)
        self.stand.set_position([8, 0, 14])
        self.scene.add(self.stand)


        # Animais
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


        # Bola
        bola_material = TextureMaterial(texture=Texture("images/volleyball.png"))
        bola_geometry = bolaGeometry()
        bola = Mesh(bola_geometry, bola_material)
        bola.set_position([-5, 0.15, -3.5])
        self.scene.add(bola)
            

        # Easter Egg
        pokeball_material = TextureMaterial(texture=Texture("images/poke.png"))
        pokeball_geometry = pokeballGeometry()
        pokeball = Mesh(pokeball_geometry, pokeball_material)
        pokeball.set_position([0, -0.001, -12])
        self.scene.add(pokeball)


        # Boneco
        modelo_material = TextureMaterial(texture=Texture("images/Cor_Modelo.jpg"))
        modelo_geometry = ModeloGeometry()
        self.modelo = Mesh(modelo_geometry, modelo_material)
        self.modelo.set_position([0, 0, 0])
        self.modelo.rotate_y(110)
        self.rig.add(self.modelo)
        self.objects_to_ignore.append(self.modelo)


        
        # Current time
        RectGeometry = RectangleGeometry(width=2)
        cTime = TextTexture(text= f"0 s",
                               system_font_name="Impact",
                               font_size=32, font_color=[200, 0, 0],
                               image_width=600, image_height=300, transparent=True)
        materialT = TextureMaterial(cTime)
        self.cTime1 = Mesh(RectGeometry, materialT)
        self.cTime1.set_position([2.5, 4.1, -4])
        self.rig.add(self.cTime1)
        self.rig3.add(self.cTime1)
        self.objects_to_ignore.append(self.cTime1)


        # Nadador salvador
        salva_material = TextureMaterial(texture=Texture("images/mass_monster.png"))
        salva_geometry = salvaGeometry()
        salva = Mesh(salva_geometry, salva_material)
        salva.set_position([-10, 0, 20])
        self.scene.add(salva)
        self.objects_to_ignore.append(salva)


        # Cubos
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


        for grupo, positions in self.cube_positions.items():
            for position in positions:
                cubo = Mesh(cubo_geometry, cubo_material)
                cubo.set_position(position)
                self.scene.add(cubo)
                self.cube_meshes[grupo].append(cubo)



    def update_Cubos(self):
        '''
        Update the positions of the cubes using a sine function.
        '''
        time2 = self.time * 0.5
        
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
        
        for grupo, meshes in self.cube_meshes.items():
            amplitude = amplitudes[grupo]
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
                    # grupo sem '_x' or '_y' move-se em Y
                    new_y = original_position[1] + amplitude * math.sin(time2 + i)
                    mesh.set_position([original_position[0], new_y, original_position[2]])
                