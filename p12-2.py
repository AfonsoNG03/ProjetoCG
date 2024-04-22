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
from geometry.oceano import OceanoGeometry
from geometry.rectangle import RectangleGeometry
from geometry.sphere import SphereGeometry
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

        # Criação da cena
        self.renderer = Renderer()
        self.scene = Scene()
        self.rig = MovementRig()
        #

        # Adiciona luzes
        # Luz ambiente
        ambient_light = AmbientLight(color=[0.1, 0.1, 0.1])
        self.scene.add(ambient_light)

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
        ocean = Mesh(ocean_geometry, self.distort_material)
        ocean.rotate_x(-math.pi/2)
        ocean.set_position([0, 0, -55])
        self.scene.add(ocean)
    
        # Textura do céu
        sky_geometry = SphereGeometry(radius=50)
        sky_material = TextureMaterial(texture=Texture(file_name="images/sky.jpg"))
        sky = Mesh(sky_geometry, sky_material)
        self.scene.add(sky)

        # Textura da areia
        sand_geometry = RectangleGeometry(width=100, height=100)
        sand_material = TextureMaterial(
            texture=Texture(file_name="images/sand.jpg"),
            property_dict={"repeatUV": [20, 20]}
        )
        sand = Mesh(sand_geometry, sand_material)
        sand.rotate_x(-math.pi/2)
        sand.set_position([0, 0, 45])
        self.scene.add(sand)
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

        #

        # Criação da camera
        self.camera = Camera(aspect_ratio=800/600)
        self.camera.set_position([0.65, 0.5, 2])
        self.rig.add(self.camera)
        self.scene.add(self.rig)
        #
        
    def update(self):
        self.distort_material.uniform_dict["time"].data += self.delta_time/5
        self.rig.update(self.input, self.delta_time)
        self.renderer.render(self.scene, self.camera)


# Instantiate this class and run the program
Example(screen_size=[800, 600]).run()
