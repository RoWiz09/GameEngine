from RoDevGameEngine.physics.collider import OBB, colliderTypes
from RoDevGameEngine import script

from glm import vec3, dot

class RigidbodyConstraints(script.dataContainer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_constraint(self, varname:str, value):
        globals()[varname] = value

    def get_constraint(self, constraint:str):
        return globals()[constraint]

class Rigidbody(script.script):
    def __init__(self, parent, script_path, max_step_size=1, max_slope_angle=45, gravity:float=0.1):
        from RoDevGameEngine.gameObjects import gameObject3D
        from RoDevGameEngine.sceneManager import get_all_objects

        self.get_objects = get_all_objects

        super().__init__(parent, script_path)
        self.parent = None
        if isinstance(parent, gameObject3D):
            self.parent = parent
        self.__transform = self.parent.get_transform()

        self.__gameObjects = []

        self.__air_time = 0
        self.__grounded = False
        self.gravity = gravity
        self.__has_gravitied_this_frame = False

        self.__cur_force = vec3(0,0,0)
        self.__friction = 100

        self.__colliding = False
        self.__was_colliding = False

        self.__triggering = False 
        self.__was_triggering = False

        self.__OBB : list[OBB] = None

        self.__constraints = RigidbodyConstraints()
        self.__constraints.set_constraint("gravity", True)

        self.__trying_to_move = False

        self.max_slope_angle = max_slope_angle
        self.max_step_size = max_step_size

    def update(self, deltatime):
        from RoDevGameEngine.sceneManager import get_all_objects
        super().update(deltatime)
        self.__gameObjects = get_all_objects()
        self.__OBB : list[OBB] = self.parent.get_components(OBB)

        if not self.__grounded and self.__constraints.get_constraint("gravity") and not self.__has_gravitied_this_frame and self.__cur_force.y <= 0:
            self.__has_gravitied_this_frame = True
            self.move_gravity([0, -self.gravity*self.__air_time*deltatime, 0])
            self.__air_time += 1

        if self.__cur_force:
            if any((self.__cur_force.x > 0, self.__cur_force.y > 0, self.__cur_force.z > 0)):
                self.__transform.move(self.__cur_force*deltatime)
            else:
                self.__cur_force = vec3(0,0,0)

            if self.__cur_force.x > 0:
                self.__cur_force.x -= self.__friction/100

            if self.__cur_force.y > 0:
                self.__cur_force.y -= (self.gravity*self.__air_time+self.__friction)/1000

            if self.__cur_force.z > 0:
                self.__cur_force.z -= self.__friction/100

        for obb in self.__OBB:
            for gameObject in self.__gameObjects:
                for other_obb in gameObject.get_components(OBB):
                    if other_obb.parent != self.parent:
                        collision_data = obb.is_colliding_with(other_obb)
                        if collision_data[0]:
                            if obb.collider_type == colliderTypes.normal_collider:
                                self.colliding = True
                                collision_info = collision_data[1]

                                for script_comp in self.parent.components:
                                    if hasattr(script_comp, 'on_collision_enter'):
                                        script_comp.on_collision_enter(self, other_obb, collision_info)

                            elif obb.collider_type == colliderTypes.trigger_collider:
                                self.__triggering = True

                                if self.__triggering and not self.__was_triggering:
                                    for script_comp in self.parent.components:
                                        if hasattr(script_comp, 'on_trigger_enter'):
                                            script_comp.on_trigger_enter(self, other_obb)

                                elif self.__triggering and self.__was_triggering:
                                    for script_comp in self.parent.components:
                                        if hasattr(script_comp, 'while_trigger'):
                                            script_comp.while_trigger(self, other_obb)

                                elif not self.__triggering and self.__was_triggering:
                                    for script_comp in self.parent.components:
                                        if hasattr(script_comp, 'on_trigger_exit'):
                                            script_comp.on_trigger_exit(self, other_obb)

        if not self.__colliding and self.__grounded and self.__constraints.get_constraint("gravity"):
            self.has_gravitied_this_frame = True
            self.grounded = False
            self.__air_time += 1

        self.__colliding = False

        self.__was_triggering = self.__triggering
        self.__triggering = False

        self.__has_gravitied_this_frame = False

    def is_ground_normal(self, normal):
        from math import degrees, acos
        angle = degrees(acos(dot(normal, vec3(0, 1, 0))))
        return angle < self.max_slope_angle

    def move(self, vel:list):
        self.trying_to_move = True

        self.__transform.move(vec3(*vel))

        self.update(0)

        self.trying_to_move = False

    def move_gravity(self, vel:list):
        self.__transform.move(vec3(*vel))
        
    def apply_force(self, force:vec3):
        self.__cur_force = force

    def on_collision_enter(self, my_obb, other, collision_info=None):
        if collision_info:
            self.grounded = True
            self.__air_time = 0

            normal = -collision_info["normal"]
            depth = collision_info["penetration_depth"]
            
            if not self.is_ground_normal(normal) or depth>self.max_step_size:
                correction = normal * depth

                self.__transform.move(correction)
            
                self.__cur_force = vec3(0,0,0)

            else:
                correction = vec3(0, normal.y, 0) * depth * 0.4

                self.__transform.move(correction)

