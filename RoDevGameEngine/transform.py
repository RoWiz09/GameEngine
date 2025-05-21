import glm

class transform:
    def __init__(self, pos : glm.vec3, rot : glm.vec3, scale : glm.vec3):
        self.pos = pos
        self.lpos = glm.vec3(pos.to_tuple())

        self.rot = rot
        self.lrot = glm.vec3(rot.to_tuple())

        self.scale = scale
        self.lscale = glm.vec3(scale.to_tuple())

    def move(self, vel:glm.vec3):
        self.lpos = glm.vec3(self.pos)
        self.lrot = glm.vec3(self.rot)
        self.lscale = glm.vec3(self.scale)

        self.pos = glm.add(self.pos, vel)

    def get_model_matrix(self):
        T = glm.mat4(1.0)

        Q = glm.quat(glm.radians(self.rot.yxz))
        R = glm.mat4_cast(Q)

        T = glm.translate(T, self.pos)

        T *= R
        
        S = glm.scale(glm.mat4(1.0), self.scale)

        return T * S
    
    @property
    def rotation_matrix(self):
        q = glm.quat(glm.radians(self.rot.yxz))
        return glm.mat4_cast(q)
        
    def return_to_last_pos(self):
        self.pos = self.lpos
        self.rot = self.lrot
        self.scale = self.lscale