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
from geometry.modelo import ModeloGeometry
from geometry.sphere import SphereGeometry
from core_ext.texture import Texture
from material.texture import TextureMaterial
from geometry.bikini import BikiniGeometry
from geometry.cubo import CuboGeometry
from geometry.box import BoxGeometry
from geometry.arvore import ArvoreGeometry


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

        # Testes
        sphere_material = TextureMaterial(texture=Texture("images/brick-wall.jpg"))
        sphere_geometry = SphereGeometry()
        sphere_right = Mesh(sphere_geometry, sphere_material)
        sphere_right.set_position([2.5, 0, 0])
        self.scene.add(sphere_right)


        modelo_material = TextureMaterial(texture=Texture("images/Cor_Modelo.jpg"))
        modelo_geometry = ModeloGeometry()
        modelo = Mesh(modelo_geometry, modelo_material)
        modelo.set_position([0, 0, 0])
        self.scene.add(modelo)

        bikini_material = TextureMaterial(texture=Texture("images/rgb-noise.jpg"))
        bikini_geometry = BikiniGeometry()
        bikini = Mesh(bikini_geometry, bikini_material)
        bikini.set_position([-1, 0, 0])
        self.scene.add(bikini)

        cubo_material = TextureMaterial(texture=Texture("images/cubo.jpg"))
        cubo_geometry = CuboGeometry()
        cubo = Mesh(cubo_geometry, cubo_material)
        cubo.set_position([-2.5, 0, 0])
        self.scene.add(cubo)

        box_material = TextureMaterial(texture=Texture("images/cubo.jpg"))
        box_geometry = BoxGeometry()
        box = Mesh(box_geometry, box_material)
        box.set_position([0, 0, -2.5])
        self.scene.add(box)

        arvore_material = TextureMaterial(texture=Texture("images/arvore2.jpg"))
        arvore_geometry = ArvoreGeometry()
        arvore = Mesh(arvore_geometry, arvore_material)
        arvore.set_position([0, 0, 2.5])
        self.scene.add(arvore)
        #

        # Criação da camera
        self.camera = Camera(aspect_ratio=800/600)
        self.camera.set_position([0.65, 0.5, 2])
        self.rig.add(self.camera)
        self.scene.add(self.rig)
        #
        
    def update(self):
        self.rig.update(self.input, self.delta_time)
        self.renderer.render(self.scene, self.camera)


# Instantiate this class and run the program
Example(screen_size=[800, 600]).run()
