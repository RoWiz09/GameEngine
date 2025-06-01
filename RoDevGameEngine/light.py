from RoDevGameEngine.script import script

class Light(script):
    def __init__(self, parent, script_path):
        super().__init__(parent, script_path)

        self._always_run = True

        self.color = [1, 1, 1]
        self.parent = parent

        self._pos = self.parent.get_transform().pos

        self.original_intensity = 12
        self.original_constant = 10

        self.range = 1

        self._intensity = self.original_intensity*self.range
        self._constant = self.original_constant*self.range

        self._linear = 0.09
        self._quadratic = 0.032

    def update(self, deltatime):
        self._intensity = self.original_intensity*self.range
        self._constant = self.original_constant*self.range

        self._pos = self.parent.get_transform().pos

        return super().update(deltatime)
    