import numpy as np, ctypes
import OpenGL.GL as GL
import RoDevGameEngine.material as mat

class Mesh:
    def __init__(self, verticies : np.ndarray, material : mat.Material):
        self.mat = material
        self.transform = None

        self.verticies = (len(verticies)//5)*3
        # Generate Vertex Buffer Object (VBO) and Vertex Array Object (VAO)
        self.vbo = GL.glGenBuffers(1)
        self.vao = GL.glGenVertexArrays(1)

        # Bind VAO and VBO
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, verticies.nbytes, verticies, GL.GL_STATIC_DRAW)

        # Position Attribute
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 5 * verticies.itemsize, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)

        # UV Attribute
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 5 * verticies.itemsize, ctypes.c_void_p(3 * verticies.itemsize))
        GL.glEnableVertexAttribArray(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        GL.glBindVertexArray(0)

    def update(self, view_mat, proj_mat):
        self.mat.apply(self.transform.getModelMatrix())
        self.mat.shader_prog.SetMat4x4("view", view_mat)
        self.mat.shader_prog.SetMat4x4("projection", proj_mat)

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.verticies)

    cube_verts = np.array([
        # Face y+
        1.0, 1.0, 0.0,    1.0, 0.0,  # Bottom-right
        0.0, 1.0, 0.0,   0.0, 0.0,  # Bottom-left
        0.0, 1.0,  1.0,   0.0, 1.0,  # Top-left

        1.0, 1.0, 0.0,    1.0, 0.0,  # Bottom-right
        0.0, 1.0, 1.0,    0.0, 1.0,  # Top-Left
        1.0, 1.0, 1.0,     1.0, 1.0,  # Top-right

        # Face y-
        0.0, 0.0,  1.0,   0.0, 1.0,  # Top-left
        0.0, 0.0, 0.0,   0.0, 0.0,  # Bottom-left
        1.0, 0.0, 0.0,    1.0, 0.0,  # Bottom-right

        1.0, 0.0, 1.0,     1.0, 1.0,  # Top-right
        0.0, 0.0, 1.0,    0.0, 1.0,  # Top-Left
        1.0, 0.0, 0.0,    1.0, 0.0,  # Bottom-right

        # Face x+
        1.0, 0.0,  1.0,   0.0, 1.0,  # Top-left
        1.0, 0.0, 0.0,   0.0, 0.0,  # Bottom-left
        1.0, 1.0, 0.0,    1.0, 0.0,  # Bottom-right

        1.0, 1.0, 1.0,     1.0, 1.0,  # Top-right
        1.0, 0.0, 1.0,    0.0, 1.0,  # Top-Left
        1.0, 1.0, 0.0,    1.0, 0.0,  # Bottom-right

        # Face x-
        0.0, 1.0, 0.0,    1.0, 0.0,  # Bottom-right
        0.0, 0.0, 0.0,   0.0, 0.0,  # Bottom-left
        0.0, 0.0,  1.0,   0.0, 1.0,  # Top-left

        0.0, 1.0, 0.0,    1.0, 0.0,  # Bottom-right
        0.0, 0.0, 1.0,    0.0, 1.0,  # Top-Left
        0.0, 1.0, 1.0,     1.0, 1.0,  # Top-right

        # Face z+
        0.0, 1.0, 1.0,    1.0, 0.0,  # Bottom-right
        0.0, 0.0, 1.0,   0.0, 0.0,  # Bottom-left
        1.0, 0.0,  1.0,   0.0, 1.0,  # Top-left

        0.0, 1.0, 1.0,    1.0, 0.0,  # Bottom-right
        1.0, 0.0, 1.0,    0.0, 1.0,  # Top-Left
        1.0, 1.0, 1.0,     1.0, 1.0,  # Top-right

        # Face z-
        1.0, 0.0,  0.0,   0.0, 1.0,  # Top-left
        0.0, 0.0, 0.0,   0.0, 0.0,  # Bottom-left
        0.0, 1.0, 0.0,    1.0, 0.0,  # Bottom-right

        1.0, 1.0, 0.0,     1.0, 1.0,  # Top-right
        1.0, 0.0, 0.0,    0.0, 1.0,  # Top-Left
        0.0, 1.0, 0.0,    1.0, 0.0,  # Bottom-right

    ], dtype=np.float32)
