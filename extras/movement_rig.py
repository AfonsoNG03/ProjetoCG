import math

from core_ext.object3d import Object3D


class MovementRig(Object3D):
    """
    Add moving forwards and backwards, left and right, up and down (all local translations),
    as well as turning left and right, and looking up and down
    """
    def __init__(self, units_per_second=3, degrees_per_second=60):
        # Initialize base Object3D.
        # Controls movement and turn left/right.
        super().__init__()
        # Initialize attached Object3D; controls look up/down
        self._look_attachment = Object3D()
        self.children_list = [self._look_attachment]
        self._look_attachment.parent = self
        # Control rate of movement
        self._units_per_second = units_per_second
        self._degrees_per_second = degrees_per_second
        self.keys_pressed = []

        # Customizable key mappings.
        # Defaults: W, A, S, D, R, F (move), Q, E (turn), T, G (look)
        self.KEY_MOVE_FORWARDS = "w"
        self.KEY_MOVE_BACKWARDS = "s"
        self.KEY_MOVE_LEFT = "a"
        self.KEY_MOVE_RIGHT = "d"
        self.KEY_JUMP = "space"  # New key for jumping
        self.KEY_MOVE_UP = "z"
        #self.KEY_MOVE_DOWN = "x"
        self.KEY_TURN_LEFT = "q"
        self.KEY_TURN_RIGHT = "e"
        self.KEY_LOOK_UP = "t"
        self.KEY_LOOK_DOWN = "g"
        self.KEY_SPRINT = "left shift"  # New key for sprinting
        self.mouse_sensitivity = 1.5
        self.mouse_x = 0
        self.mouse_y = 0


        # Flag to track if the player is currently jumping
        self.is_jumping = False
        self.jump_speed = 10  # Adjust as needed

    # Adding and removing objects applies to look attachment.
    # Override functions from the Object3D class.
    def add(self, child):
        self._look_attachment.add(child)

    def remove(self, child):
        self._look_attachment.remove(child)

    def restrict_movement(self):
        """
        Restringe o movimento com base na lista de teclas pressionadas durante uma colisão.
        """
        keys_to_restrict = ["w", "s", "a", "d", "z", "x"]
        # Restringir as teclas de movimento
        for key in keys_to_restrict:
            if key in self.keys_pressed:
                if key == "w":
                    self.KEY_MOVE_FORWARDS = ""
                elif key == "s":
                    self.KEY_MOVE_BACKWARDS = ""
                elif key == "a":
                    self.KEY_MOVE_LEFT = ""
                elif key == "d":
                    self.KEY_MOVE_RIGHT = ""
                elif key == "z":
                    self.KEY_MOVE_UP = ""
                #elif key == "x":
                 #   self.KEY_MOVE_DOWN = ""

        # Restaurar as teclas permitidas
        #self.allow_movement()

    def allow_movement(self):
        """
        Allow movement in all directions.
        """
        # Reset movement keys to default values
        self.KEY_MOVE_FORWARDS = "w"
        self.KEY_MOVE_BACKWARDS = "s"
        self.KEY_MOVE_LEFT = "a"
        self.KEY_MOVE_RIGHT = "d"
        self.KEY_MOVE_UP = "z"
        #self.KEY_MOVE_DOWN = "x"

    def update(self, input_object, delta_time, collision=False):
        move_amount = self._units_per_second * delta_time
        rotate_amount = self._degrees_per_second * (math.pi / 180) * delta_time
        rotate_amount *= self.mouse_sensitivity  # Apply mouse sensitivity
        
        # Sprint mechanic
        if input_object.is_key_pressed(self.KEY_SPRINT):
            move_amount *= 2  # Double the movement speed while sprinting

        # Jump mechanic
        if input_object.is_key_pressed(self.KEY_JUMP) and not self.is_jumping:
            self.is_jumping = True

        if self.is_jumping:
            # Move the object vertically (upwards) according to jump speed
            self.translate(0, self.jump_speed * delta_time, 0)
            # Adjust jump speed to simulate gravity
            self.jump_speed -= 15 * delta_time  # Simulate gravity (adjust as needed)

            # Check if the object has reached the ground level
            if collision:
                self.is_jumping = False
                self.jump_speed = 10
            elif self.global_position[1] <= 0:
                self.global_position[1] = 0  # Ensure object rests on the ground
                self.is_jumping = False
                self.jump_speed = 10  # Reset jump speed

        self.keys_pressed = [key for key in input_object.key_pressed_list]

        if collision:
            self.restrict_movement()
        else:
            self.allow_movement()

        if input_object.is_key_pressed(self.KEY_MOVE_FORWARDS):
            self.translate(0, 0, -move_amount)
        if input_object.is_key_pressed(self.KEY_MOVE_BACKWARDS):
            self.translate(0, 0, move_amount)
        if input_object.is_key_pressed(self.KEY_MOVE_LEFT):
            self.translate(-move_amount, 0, 0)
        if input_object.is_key_pressed(self.KEY_MOVE_RIGHT):
            self.translate(move_amount, 0, 0)
        if input_object.is_key_pressed(self.KEY_MOVE_UP):
            self.translate(0, move_amount, 0)
        if input_object.is_key_pressed(self.KEY_MOVE_DOWN):
            self.translate(0, -move_amount, 0)
        if input_object.is_key_pressed(self.KEY_TURN_RIGHT) or input_object.mouse_x > 0:
            self.rotate_y(-rotate_amount)
        if input_object.is_key_pressed(self.KEY_TURN_LEFT) or input_object.mouse_x < 0:
            self.rotate_y(rotate_amount)
        if input_object.is_key_pressed(self.KEY_LOOK_UP) or input_object.mouse_y < 0:
            self._look_attachment.rotate_x(rotate_amount)
        if input_object.is_key_pressed(self.KEY_LOOK_DOWN) or input_object.mouse_y > 0:
            self._look_attachment.rotate_x(-rotate_amount)
