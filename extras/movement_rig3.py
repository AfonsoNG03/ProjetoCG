import math
from core_ext.object3d import Object3D

class MovementRig3(Object3D):
    def __init__(self, units_per_second=3, degrees_per_second=60):
        super().__init__()
        self._look_attachment = Object3D()
        self.children_list = [self._look_attachment]
        self._look_attachment.parent = self

        self._units_per_second = units_per_second
        self._degrees_per_second = degrees_per_second
        self.keys_pressed = []
        self.mouse_sensitivity = 1.5
        self.mouse_x = 0
        self.mouse_y = 0
        self.is_jumping = False
        self.jump_speed = 10
        self.fall_speed = 0.0
        self.gravity = 15.0
        self.modo_criativo_enabled = False
<<<<<<< HEAD
        self._heightMesh = 0.0

        self.current_rotation_x = 0
        self.current_rotation_y = 0
=======
>>>>>>> Afonso

        self.keys = {
            "MOVE_FORWARDS": "w",
            "MOVE_BACKWARDS": "s",
            "MOVE_LEFT": "a",
            "MOVE_RIGHT": "d",
            "JUMP": "space",
            "MOVE_UP": "z",
            "MOVE_DOWN": "x",
            "TURN_LEFT": "q",
            "TURN_RIGHT": "e",
            "LOOK_UP": "t",
            "LOOK_DOWN": "g",
            "SPRINT": "left shift",
            "MODO_CRIATIVO": "u"
        }

    def add(self, child):
        self._look_attachment.add(child)

    def remove(self, child):
        self._look_attachment.remove(child)

    def restrict_movement(self):
        restricted_keys = ["MOVE_FORWARDS", "MOVE_BACKWARDS", "MOVE_LEFT", "MOVE_RIGHT", "MOVE_UP", "MOVE_DOWN"]
        for key in restricted_keys:
            if self.keys[key] in self.keys_pressed:
                self.keys[key] = ""

    def allow_movement(self):
        self.keys.update({
            "MOVE_FORWARDS": "w",
            "MOVE_BACKWARDS": "s",
            "MOVE_LEFT": "a",
            "MOVE_RIGHT": "d",
            "MOVE_UP": "z",
            "MOVE_DOWN": "x"
        })

    def set_rotation_x(self, angle):
        self._look_attachment.rotate_x(angle - self.current_rotation_x)
        self.current_rotation_x = angle

    def set_rotation_y(self, angle):
        self.rotate_y(angle - self.current_rotation_y)
        self.current_rotation_y = angle

    def update(self, input_object, delta_time, collision=False):
        move_amount = self._units_per_second * delta_time
        rotate_amount = self._degrees_per_second * (math.pi / 180) * delta_time * self.mouse_sensitivity
        
        if input_object.is_key_pressed(self.keys["SPRINT"]):
            move_amount *= 2

        if input_object.is_key_pressed(self.keys["JUMP"]) and not self.is_jumping:
            self.is_jumping = True

        if input_object.is_key_pressed(self.keys["MODO_CRIATIVO"]):
            self.modo_criativo_enabled = not self.modo_criativo_enabled

        if self.global_position[1] < 0:
            self.translate(0, -self.global_position[1], 0)
            self.fall_speed = 0.0
        
        if collision:
            self.fall_speed = 0.0

        if self.global_position[1] > 0 and not self.is_jumping and not collision:
            self.fall_speed += self.gravity * delta_time
            self.translate(0, -self.fall_speed * delta_time, 0)
            if self.global_position[1] <= 0:
                self.global_position[1] = 0
                self.fall_speed = 0.0

        if self.is_jumping:
            self.translate(0, self.jump_speed * delta_time, 0)
            self.jump_speed -= 15 * delta_time
            if collision:
                self.is_jumping = False
                self.jump_speed = 10
                self.translate(0, 16 * delta_time, 0)
                #self.translate(0, 0.5, 0)
            if self.global_position[1] <= 0:
                self.is_jumping = False
                self.jump_speed = 10
                self.global_position[1] = 0

        self.keys_pressed = input_object.key_pressed_list

        movement_actions = {
            "MOVE_FORWARDS": (0, 0, -move_amount),
            "MOVE_BACKWARDS": (0, 0, move_amount),
            "MOVE_LEFT": (-move_amount, 0, 0),
            "MOVE_RIGHT": (move_amount, 0, 0),
            "MOVE_UP": (0, move_amount, 0) if self.modo_criativo_enabled else (0, 0, 0),
            "MOVE_DOWN": (0, -move_amount, 0) if self.modo_criativo_enabled else (0, 0, 0)
        }

        for action, translation in movement_actions.items():
            if input_object.is_key_pressed(self.keys[action]):
                self.translate(*translation)

        rotation_actions = {
            "TURN_RIGHT": -rotate_amount,
            "TURN_LEFT": rotate_amount
        }

        for action, rotation in rotation_actions.items():
            if input_object.is_key_pressed(self.keys[action]) or (action == "TURN_RIGHT" and input_object.mouse_x > 0) or (action == "TURN_LEFT" and input_object.mouse_x < 0):
                self.rotate_y(rotation)
                self.current_rotation_y += rotation

        look_actions = {
            "LOOK_UP": rotate_amount,
            "LOOK_DOWN": -rotate_amount
        }

        for action, rotation in look_actions.items():
            if input_object.is_key_pressed(self.keys[action]) or (action == "LOOK_UP" and input_object.mouse_y < 0) or (action == "LOOK_DOWN" and input_object.mouse_y > 0):
                self._look_attachment.rotate_x(rotation)
                self.current_rotation_x += rotation