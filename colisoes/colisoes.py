

import numpy as np


class Colisoes:
    def __init__(self, objects_to_ignore=[]):
        self.grid_size = 5
        self.grid = {}
        self.objects_to_ignore = objects_to_ignore

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

    def update_grid(self, scene):
        """
        Update the grid by reassigning objects to appropriate grid cells.
        """
        self.grid = {}
        for obj in scene.children_list:
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

    def check_collisions(self, camera, static_camera, rig, rig3, delta_time):
        """
        Check for collisions between objects in the scene.
        """
        nearby_objects = self.get_nearby_objects(camera)
        for other_obj in nearby_objects:
            if other_obj != camera and camera.intersects(other_obj):
                return self.determine_collision_direction(other_obj, camera, static_camera, rig, rig3, delta_time)
        return False

    def determine_collision_direction(self, other_obj, camera, static_camera, rig, rig3, delta_time):
        """
        Determine the direction of collision between the camera and another object.
        """
        # Get positions of camera and other object
        cam_pos = np.array(camera.global_position)
        if camera == static_camera:
            cam_pos = cam_pos 
        obj_pos = np.array(other_obj.global_position)

        # Calculate the vector from the camera to the object
        collision_vector = obj_pos - cam_pos

        collision_vector[1] -= 0.15

        # Normalize the vector to get the direction
        collision_direction = collision_vector / np.linalg.norm(collision_vector)
        
        # Determine the direction
        #direction = ''
        if  other_obj.global_position[1] + other_obj._height/2 +2.45 <= camera.global_position[1]:
            if abs(collision_direction[0]) > abs(collision_direction[1]) and abs(collision_direction[0]) > abs(collision_direction[2]):
                if collision_direction[0] > 0:
                    #direction = 'right'
                    rig.translate(-0.1, 0, 0, False)
                    rig3.translate(-0.1, 0, 0, False)
                else:
                    #direction = 'left'
                    rig.translate(0.1, 0, 0, False)
                    rig3.translate(0.1, 0, 0, False)
            elif abs(collision_direction[1]) > abs(collision_direction[0]) and abs(collision_direction[1])  > abs(collision_direction[2]):
                if collision_direction[1] > -0.1:
                    #direction = 'below'
                    rig.translate(0, -0.1, 0, False)
                    rig3.translate(0, -0.1, 0, False)
                else:
                    #direction = 'above'
                    if camera.global_position[1] - other_obj.global_position[1] <= 3.9:
                        rig.translate(0, delta_time*2.7, 0, False)
                        rig3.translate(0, delta_time*2.7, 0, False)
                    return True
            else:
                if collision_direction[2] > 0:
                    #direction = 'front'
                    rig.translate(0, 0, -0.1, False)
                    rig3.translate(0, 0, -0.1, False)
                else:
                    #direction = 'back'
                    rig.translate(0, 0, 0.1, False)
                    rig3.translate(0, 0, 0.1, False)
        else:
            if abs(collision_direction[0]) > abs(collision_direction[2]):
                if collision_direction[0] > 0:
                    #direction = 'right'
                    rig.translate(-0.1, 0, 0, False)
                    rig3.translate(-0.1, 0, 0, False)
                else:
                    #direction = 'left'
                    rig.translate(0.1, 0, 0, False)
                    rig3.translate(0.1, 0, 0, False)
            else:
                if collision_direction[2] > 0:
                    #direction = 'front'
                    rig.translate(0, 0, -0.1, False)
                    rig3.translate(0, 0, -0.1, False)
                else:
                    #direction = 'back'
                    rig.translate(0, 0, 0.1, False)
                    rig3.translate(0, 0, 0.1, False)
        
        return False

'''
# Define grid properties
        self.grid_size = 5  # Size of each grid cell
        self.grid = {}  # Dictionary to store objects in each grid cell
        self.tempo = 0
        self.objects_to_ignore = []
'''