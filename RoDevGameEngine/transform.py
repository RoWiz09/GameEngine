import glm

class transform:
    def __init__(self, pos : glm.vec3, rot : glm.vec3, scale : glm.vec3):
        self.pos = pos
        self.rot = rot
        self.scale = scale

    def getModelMatrix(self) -> glm.mat4x4:
        model = glm.mat4(1.0)

        model = glm.translate(model, self.pos)
        
        model = glm.rotate(model, glm.radians(self.rot.x), glm.vec3(1, 0, 0))
        model = glm.rotate(model, glm.radians(self.rot.y), glm.vec3(0, 1, 0))
        model = glm.rotate(model, glm.radians(self.rot.z), glm.vec3(0, 0, 1))

        model = glm.scale(model, self.scale)

        return model