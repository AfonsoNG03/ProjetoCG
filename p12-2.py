import numpy as np
import math
import pathlib
import sys

from core.base import Base
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from core_ext.renderer2 import Renderer
from core_ext.scene import Scene
from geometry.cadeira import CadeiraGeometry
from geometry.oculos import OculosGeometry
from geometry.bikini import BikiniGeometry
from geometry.toalha import ToalhaGeometry
from extras.movement_rig import MovementRig
from extras.movement_rig2 import MovementRig2
from geometry.rectangle import RectangleGeometry
from geometry.sphere import SphereGeometry
from light.ambient import AmbientLight
from light.directional import DirectionalLight
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
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=800/600)
        #self.camera.set_position([0.2, 0.5, -3])
        #change camera global position to 0.65, 0.5, -2.7
        self.camera.set_position([0.65, 0.5, 2])
        ambient_light = AmbientLight(color=[0.1, 0.1, 0.1])
        self.scene.add(ambient_light)
        self.directional_light = DirectionalLight(color=[0.8, 0.8, 0.8], direction=[-1, -1, 0])
        self.scene.add(self.directional_light)
        phong_material = PhongMaterial(
            number_of_light_sources=2,
            texture = Texture(file_name="images/grass.jpg")
        )
        geometry = OculosGeometry()
        geometryCadeira = CadeiraGeometry()
        phong_material2 = PhongMaterial(
            number_of_light_sources=2,
            texture = Texture(file_name="images/whool.jpg")
        )
        grid_textureCadeira = Texture(file_name="images/whool.jpg")
        materialCadeira = TextureMaterial(texture=grid_textureCadeira)
        self.meshCadeira = Mesh(geometry=geometryCadeira, material=phong_material2)
        self.meshCadeira.set_position([0,0.1,0.5])
        #material = SurfaceMaterial(property_dict={"useVertexColors": True})
        grid_texture = Texture(file_name="images/crate.jpg")
        material = TextureMaterial(texture=grid_texture)
        self.mesh = Mesh(geometry=geometry,
            material=phong_material)

        geometryBikini = BikiniGeometry()
        grid_textureBikini = Texture(file_name="images/whool.jpg")
        materialBikini = TextureMaterial(texture=grid_textureBikini)
        self.meshBikini = Mesh(geometry=geometryBikini, material=phong_material2)
        self.meshBikini.set_position([1.5,0.1,0.5])

        geometryToalha = ToalhaGeometry()
        grid_textureToalha = Texture(file_name="images/whool.jpg")
        materialToalha = TextureMaterial(texture=grid_textureToalha)
        self.meshToalha = Mesh(geometry=geometryToalha, material=phong_material2)
        self.meshToalha.set_position([1,0.1,0.5])
        
        
        self.rig2 = MovementRig2()
        self.rig2.add(self.camera)
        self.scene.add(self.rig2)
        self.rig = MovementRig()
        self.scene.add(self.meshCadeira)
        self.scene.add(self.meshBikini)
        self.scene.add(self.meshToalha)
        self.rig.add(self.mesh)
        self.rig.set_position([0, 0.5, -0.5])
        self.scene.add(self.rig)
        sky_geometry = SphereGeometry(radius=50)
        sky_material = TextureMaterial(texture=Texture(file_name="images/sky.jpg"))
        sky = Mesh(sky_geometry, sky_material)
        self.scene.add(sky)
        grass_geometry = RectangleGeometry(width=100, height=100)
        grass_material = TextureMaterial(
            texture=Texture(file_name="images/sand.jpg"),
            property_dict={"repeatUV": [50, 50]}
        )
        grass = Mesh(grass_geometry, grass_material)
        grass.rotate_x(-math.pi/2)
        grass.set_position([0, 0, 45])
        self.scene.add(grass)

        ocean_geomatry = RectangleGeometry(width=100, height=100)
        ocean_material = TextureMaterial(
            texture=Texture(file_name="images/water.jpg"),
            property_dict={"repeatUV": [50, 50]}
        )
        ocean = Mesh(ocean_geomatry, ocean_material)
        ocean.rotate_x(-math.pi/2)
        ocean.set_position([0, 0, -55])
        self.scene.add(ocean)

    def update(self):
        self.rig.update(self.input, self.delta_time)
        self.rig2.update(self.input, self.delta_time)
        self.renderer.render(self.scene, self.camera)


# Instantiate this class and run the program
Example(screen_size=[800, 600]).run()
