from RoDevGameEngine.script import script

class Light(script):
    def __init__(self, parent, range:float = 1, color:list[float] = [1, 1, 1], intensity:float = 12.0, constant:float = 10.0):
        self.super = super().__init__(parent)

        self.color = color
        self.parent = parent

        self.pos = self.parent.get_transform().pos

        self.intensity = intensity*range
        self.constant = constant*range

        self.linear = 0.09
        self.quadratic = 0.032

    def update(self, deltatime):
        self.pos = self.parent.get_transform().pos

        return super().update(deltatime)
    