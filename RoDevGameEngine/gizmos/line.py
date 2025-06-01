from RoDevGameEngine.shaders import RayShaderProgram

import OpenGL.GL as gl
import glm
import numpy as np

import time

class Line:
    def __init__(self, start: glm.vec3, end: glm.vec3, color: glm.vec4, decay_time: float = 3):
        self.start = start
        self.end = end
        self.color = color

        self.decay_time = decay_time
        self.init_time = 0

class LineRenderer:
    def __init__(self):
        self.__shader = RayShaderProgram()
        self.__vao = gl.glGenVertexArrays(1)
        self.__vbo = gl.glGenBuffers(1)
        self.__rays: list[Line] = []

        gl.glBindVertexArray(self.__vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.__vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, 6 * 4, None, gl.GL_DYNAMIC_DRAW)

        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glBindVertexArray(0)

        self.time = time.time()

    def update(self, projection, view):
        self.__shader.Use()
        self.__shader.SetMat4x4("uProjection", projection)
        self.__shader.SetMat4x4("uView", view)

        gl.glBindVertexArray(self.__vao)

        for line in self.__rays:
            # Prepare vertex data
            vertices = np.array([
                line.start.x, line.start.y, line.start.z,
                line.end.x, line.end.y, line.end.z
            ], dtype=np.float32)

            # Upload to GPU
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.__vbo)
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
            # Set color and draw
            self.__shader.SetVec4("uColor", line.color)
            gl.glDrawArrays(gl.GL_LINES, 0, 2)
            
            if self.time - line.init_time > line.decay_time:
                self.__rays.remove(line)

        self.time = time.time()

        gl.glBindVertexArray(0)

    def add_line(self, line: Line):
        line.init_time = self.time
        self.__rays.append(line)

    def clear(self):
        self.__rays.clear()
