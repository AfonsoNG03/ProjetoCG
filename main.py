import numpy as np
import pygame

from core.menu import GameMenu
from core.base import Base
from core_ext.camera import Camera
from core_ext.renderer2 import Renderer
from core_ext.scene import Scene
from extras.movement_rig import MovementRig
from extras.movement_rig3 import MovementRig3
from music.music import Music
from colisoes.colisoes import Colisoes
from tempos.tempo import Tempo
from nivel.nivel1 import Nivel1

class Main(Base):
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
      
        # Criação da cena e rigs
        self.renderer = Renderer()
        self.scene = Scene()
        self.rig = MovementRig()
        self.rig3 = MovementRig3()

        # Criação do nivel
        self.Nivel1 = Nivel1(self.scene, self.rig, self.rig3, self.time)
        self.objects_to_ignore = self.Nivel1.objects_to_ignore

        # Adiciona os objetos a serem ignorados
        self.objects_to_ignore.append(self.rig)
        self.objects_to_ignore.append(self.rig3)

        # Criação da camera principal
        self.camera = Camera(aspect_ratio=800/600)
        self.camera.set_position([0, 2.93, -1])
        self.rig.add(self.camera)
        self.scene.add(self.rig)

        # Criaçao da camara alternativa
        self.static_camera = Camera(aspect_ratio=800/600)
        self.static_camera.set_position([0, 4, 4])
        model_position = self.Nivel1.modelo.global_position
        self.static_camera.look_at([model_position[0], model_position[1]+2.5, model_position[2]])
        self.rig3.add(self.static_camera)

        # Criacao da camara cinemática
        self.cinematic_camera = Camera(aspect_ratio=800/600)
        self.cinematic_camera.set_position([10, 10, 10])
        model_position = self.Nivel1.modelo.global_position
        self.cinematic_camera.look_at([model_position[0], model_position[1]+2.5, model_position[2]])

        # Adiciona a camera a cena
        self.active_camera = self.camera
        self.toggle_camera = False

        # Tratamento de colisões
        self.Coli = Colisoes(self.objects_to_ignore)
        self.Coli.update_grid(self.scene)

        # Criação do tempo
        self.TempoCounter = Tempo(self.rig, self.rig3)
        self.objects_to_ignore.append(self.TempoCounter.mensagem)

        #Diferentes posicoes para a camera cinematogra
        self.posicoes = [[ 10, 10, 10], [30, 30, 30], [1,10,0] , [ 5, 5, 20]]

        Music()

    def camera_cinematografica(self):
        '''
        Função que controla a camera cinematográfica
        '''
        if self.active_camera == self.cinematic_camera:
            self.TempoCounter.tempo += self.delta_time
            if self.TempoCounter.tempo > 4:
                self.cinematic_camera.set_position(self.posicoes[np.random.randint(0,len(self.posicoes))])
                self.TempoCounter.tempo = 0
            modelo_position = self.Nivel1.modelo.global_position
            self.cinematic_camera.look_at([modelo_position[0], modelo_position[1]+2.5, modelo_position[2]])

    def checkpoint(self):
        '''
        Função que controla o checkpoint
        '''
        if self.rig.global_position[0] < -17 and self.rig.global_position[0] > -19 and self.rig.global_position[1] < 49 and self.rig.global_position[1] > 47 and self.rig.global_position[2] < 49 and self.rig.global_position[2] > 47:
            self.TempoCounter.checkPoint = True
            self.rig.translate(0, 0, -100, False)
            self.rig3.translate(0, 0, -100, False)

    def camera_change(self):
        '''
        Função que controla a mudança de camera
        '''
        if self.input.is_key_pressed('c'):
            if not self.toggle_camera:
                self.toggle_camera = True
                if self.active_camera == self.camera:
                    self.active_camera = self.static_camera
                    #self.Nivel1.cTime1.set_position([2.8, 4.1, 0])
                    #self.TempoCounter.mensagem.set_position([-1.5, 4.1, 0])
                else:
                    self.active_camera = self.camera
                    self.Nivel1.cTime1.set_position([2.5, 4.1, -4])
                    self.TempoCounter.mensagem.set_position([-1.3, 4.1, -4])

        elif self.input.is_key_pressed('v'):
            if not self.toggle_camera:
                self.toggle_camera = True
                if self.active_camera == self.camera:
                    self.active_camera = self.cinematic_camera
                else:
                    self.active_camera = self.camera
        else: 
            self.toggle_camera = False

    def update(self):
        '''
        Função que atualiza o jogo
        '''
        self.Nivel1.distort_material.uniform_dict["time"].data += self.delta_time/5
        self.Nivel1.time = self.time
       
        self.TempoCounter.check_if_player_fell()
        self.TempoCounter.check_if_player_reached_start()
        self.TempoCounter.check_if_player_reached_end()

        self.camera_cinematografica()
        self.Nivel1.update_Cubos()
        self.Nivel1.update_jump(self.delta_time)
        self.checkpoint()
        self.camera_change()
        
        collision = self.Coli.check_collisions(self.camera, self.static_camera, self.rig, self.rig3, self._delta_time)

        self.rig.update(self.input, self.delta_time, collision)
        self.rig3.update(self.input, self.delta_time, collision)
        
        self.renderer.render(self.scene, self.active_camera)
        self.TempoCounter.updateCurrentTime(self.Nivel1.cTime1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    menu = GameMenu(screen)
    while True:
        choice = menu.run()
        if choice == "start_game":
            break
        elif choice == "options":
            pass
    pygame.quit()

if __name__ == "__main__":
    main()

# Instantiate this class and run the program
Main(screen_size=[800, 600]).run()