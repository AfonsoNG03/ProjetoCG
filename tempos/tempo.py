

import pathlib
import time

import numpy as np

from core_ext.mesh import Mesh
from extras.text_texture import TextTexture
from geometry.rectangle import RectangleGeometry
from material.texture import TextureMaterial


class Tempo:
    def __init__(self, rig, rig3):
        '''
        Initialize the timer and the player positions.
        '''
        self.three_lowest_times = []
        self.checkPoint = False
        self.start_time = 0
        self.timer_running = False
        self.tempo = 0

        self.cube_start_position = [-1.75, 2.0, 19.5]
        self.final_portal_position = [48, 26, 2]

        self.time_file_path = pathlib.Path("time_records.txt")
        self.tempos_string = "|| "
        for i, time in enumerate(self.get_three_lowest_times(self.time_file_path)):
            self.tempos_string += f"{i+1} -> {time:.0f} s  || "

        self.rig = rig
        self.rig3 = rig3

        # LeaderBoard
        geometry = RectangleGeometry(width=2)
        message = TextTexture(text=self.tempos_string,
                            system_font_name="Impact",
                            font_size=32, font_color=[200, 0, 0],
                            image_width=600, image_height=300, transparent=True)
        material = TextureMaterial(message)
        self.mensagem = Mesh(geometry, material)
        self.mensagem.set_position([-1.3, 4.1, -4])
        self.rig.add(self.mensagem)
        self.rig3.add(self.mensagem)
        


    def get_three_lowest_times(self, file_path):
        '''
        Read the time records from the file and return the three lowest times.
        '''
        times = []
        with open(file_path, "r") as file:
            for line in file:
                if "Time:" in line:
                    time_str = line.split("Time:")[1].strip().split()[0]
                    times.append(float(time_str))
        return sorted(times)[:3]
    
    def start_timer(self):
        '''
        Start the timer.
        '''
        self.start_time = time.time()
        self.timer_running = True
        print("Timer started")

    def stop_timer(self):
        '''
        Stop the timer and save the elapsed time to a file.
        '''
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            self.timer_running = False
            print(f"Timer stopped: {elapsed_time:.2f} seconds")
            self.save_time_to_file(elapsed_time)

    def reset_timer(self):
        '''
        Reset the timer.
        '''
        self.start_time = 0
        self.timer_running = False
        print("Timer reset")

    def save_time_to_file(self, elapsed_time):
        '''
        Save the elapsed time to a file.
        '''
        with open(self.time_file_path, "a") as file:
            file.write(f"Time: {elapsed_time:.2f} seconds\n")
        print(f"Time saved to {self.time_file_path}")

    def check_if_player_fell(self):
        '''
        Check if the player fell and reset the player position.
        '''
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
        '''
        Check if the player reached the start and start the timer.
        '''
        if np.linalg.norm(np.array(self.rig.global_position) - np.array(self.cube_start_position)) < 2:
            if not self.timer_running:
                self.start_timer()

    def check_if_player_reached_end(self):
        '''
        Check if the player reached the end and stop the timer.
        '''
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

    def updateCurrentTime(self, cTime1):
        '''
        Update the current time text.
        '''
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
        else:
            elapsed_time = 0
        cTime = TextTexture(text= f" Current Time: {elapsed_time:.0f} s",
                               system_font_name="Impact",
                               font_size=32, font_color=[200, 0, 0],
                               image_width=600, image_height=300, transparent=True)
        materialT = TextureMaterial(cTime)
        cTime1._material = materialT

    '''
    if self.TempoCounter.timer_running:
            elapsed_time = time.time() - self.start_time
        else:
            elapsed_time = 0
        cTime = TextTexture(text= f" Current Time: {elapsed_time:.0f} s",
                               system_font_name="Impact",
                               font_size=32, font_color=[200, 0, 0],
                               image_width=600, image_height=300, transparent=True)
        materialT = TextureMaterial(cTime)

        self.cTime1._material = materialT
    '''
