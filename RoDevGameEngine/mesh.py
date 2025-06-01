import numpy as np, ctypes
import OpenGL.GL as GL
import RoDevGameEngine.material as mat

class Mesh:
    def __init__(self, verticies : np.ndarray, material : mat.Material):
        self.mat = material
        self.transform = None

        self.verticies = (len(verticies)//8)*3
        # Generate Vertex Buffer Object (VBO) and Vertex Array Object (VAO)
        self.vbo = GL.glGenBuffers(1)
        self.vao = GL.glGenVertexArrays(1)

        # Bind VAO and VBO
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, verticies.nbytes, verticies, GL.GL_STATIC_DRAW)

        # Position Attribute
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 8 * verticies.itemsize, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)

        # UV Attribute
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 8 * verticies.itemsize, ctypes.c_void_p(3 * verticies.itemsize))
        GL.glEnableVertexAttribArray(1)

        # Normal Attribute
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, GL.GL_FALSE, 8 * verticies.itemsize, ctypes.c_void_p(5 * verticies.itemsize))
        GL.glEnableVertexAttribArray(2)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        GL.glBindVertexArray(0)

    def update(self, view_mat, proj_mat):
        self.mat.apply(self.transform.get_model_matrix())
        self.mat.shader_prog.SetMat4x4("view", view_mat)
        self.mat.shader_prog.SetMat4x4("projection", proj_mat)

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.verticies)
    
    def cube_verts():
        return np.array([
            # Face y+ (Top)
            1.0, 1.0, 0.0,   1.0, 0.0,  0.0, 1.0, 0.0,  # Bottom-right
            0.0, 1.0, 0.0,   0.0, 0.0,  0.0, 1.0, 0.0,  # Bottom-left
            0.0, 1.0, 1.0,   0.0, 1.0,  0.0, 1.0, 0.0,  # Top-left

            1.0, 1.0, 0.0,   1.0, 0.0,  0.0, 1.0, 0.0,  # Bottom-right
            0.0, 1.0, 1.0,   0.0, 1.0,  0.0, 1.0, 0.0,  # Top-left
            1.0, 1.0, 1.0,   1.0, 1.0,  0.0, 1.0, 0.0,  # Top-right

            # Face y- (Bottom)
            0.0, 0.0, 1.0,   0.0, 1.0,  0.0, -1.0, 0.0,  # Top-left
            0.0, 0.0, 0.0,   0.0, 0.0,  0.0, -1.0, 0.0,  # Bottom-left
            1.0, 0.0, 0.0,   1.0, 0.0,  0.0, -1.0, 0.0,  # Bottom-right

            1.0, 0.0, 1.0,   1.0, 1.0,  0.0, -1.0, 0.0,  # Top-right
            0.0, 0.0, 1.0,   0.0, 1.0,  0.0, -1.0, 0.0,  # Top-Left
            1.0, 0.0, 0.0,   1.0, 0.0,  0.0, -1.0, 0.0,  # Bottom-right

            # Face x+ (Right)
            1.0, 0.0, 1.0,   0.0, 1.0,  1.0, 0.0, 0.0,  # Top-left
            1.0, 0.0, 0.0,   0.0, 0.0,  1.0, 0.0, 0.0,  # Bottom-left
            1.0, 1.0, 0.0,   1.0, 0.0,  1.0, 0.0, 0.0,  # Bottom-right

            1.0, 1.0, 1.0,   1.0, 1.0,  1.0, 0.0, 0.0,  # Top-right
            1.0, 0.0, 1.0,   0.0, 1.0,  1.0, 0.0, 0.0,  # Top-Left
            1.0, 1.0, 0.0,   1.0, 0.0,  1.0, 0.0, 0.0,  # Bottom-right

            # Face x- (Left)
            0.0, 1.0, 0.0,   1.0, 0.0,  -1.0, 0.0, 0.0,  # Bottom-right
            0.0, 0.0, 0.0,   0.0, 0.0,  -1.0, 0.0, 0.0,  # Bottom-left
            0.0, 0.0, 1.0,   0.0, 1.0,  -1.0, 0.0, 0.0,  # Top-left

            0.0, 1.0, 0.0,   1.0, 0.0,  -1.0, 0.0, 0.0,  # Bottom-right
            0.0, 0.0, 1.0,   0.0, 1.0,  -1.0, 0.0, 0.0,  # Top-Left
            0.0, 1.0, 1.0,   1.0, 1.0,  -1.0, 0.0, 0.0,  # Top-right

            # Face z+ (Front)
            0.0, 1.0, 1.0,   1.0, 0.0,  0.0, 0.0, 1.0,  # Bottom-right
            0.0, 0.0, 1.0,   0.0, 0.0,  0.0, 0.0, 1.0,  # Bottom-left
            1.0, 0.0, 1.0,   0.0, 1.0,  0.0, 0.0, 1.0,  # Top-left

            0.0, 1.0, 1.0,   1.0, 0.0,  0.0, 0.0, 1.0,  # Bottom-right
            1.0, 0.0, 1.0,   0.0, 1.0,  0.0, 0.0, 1.0,  # Top-Left
            1.0, 1.0, 1.0,   1.0, 1.0,  0.0, 0.0, 1.0,  # Top-right

            # Face z- (Back)
            1.0, 0.0, 0.0,   0.0, 1.0,  0.0, 0.0, -1.0,  # Top-left
            0.0, 0.0, 0.0,   0.0, 0.0,  0.0, 0.0, -1.0,  # Bottom-left
            0.0, 1.0, 0.0,   1.0, 0.0,  0.0, 0.0, -1.0,  # Bottom-right

            1.0, 1.0, 0.0,   1.0, 1.0,  0.0, 0.0, -1.0,  # Top-right
            1.0, 0.0, 0.0,   0.0, 1.0,  0.0, 0.0, -1.0,  # Top-Left
            0.0, 1.0, 0.0,   1.0, 0.0,  0.0, 0.0, -1.0,  # Bottom-right

        ], dtype=np.float32)
    
    def cylinder_verts(faces):
        deg_added = 360 / faces
        deg = 0

        verticies = []
        for side in range(faces):
            radians = deg * (np.pi/180)
            radians_added = (deg+deg_added) * (np.pi/180)

            verticies.extend([
                np.cos(radians)*1+0.5, 0, np.sin(radians)*1+0.5, 1.0, deg/360*2, # Bottom Left
                np.cos(radians)*1+0.5, 1, np.sin(radians)*1+0.5, 0.0, deg/360*2, # Top Left
                np.cos(radians_added)*1+0.5, 1, np.sin(radians_added)*1+0.5, 0.0, (deg+deg_added)/360*2, # Top Right

                np.cos(radians_added)*1+0.5, 1, np.sin(radians_added)*1+0.5, 0.0, (deg+deg_added)/360*2,  # Top Right
                np.cos(radians_added)*1+0.5, 0, np.sin(radians_added)*1+0.5, 1.0, (deg+deg_added)/360*2, # Bottom Right
                np.cos(radians)*1+0.5, 0, np.sin(radians)*1+0.5, 1.0, deg/360*2, # Bottom Left

                # Top Face
                np.cos(radians)*1+0.5, 1, np.sin(radians)*1+0.5, 0, 0, 
                0.5, 1, 0.5, 0.5, 0.5, 
                np.cos(radians_added)*1+0.5, 1, np.sin(radians_added)*1+0.5, 0, 1, 

                # Bottom Face
                np.cos(radians_added)*1+0.5, 0, np.sin(radians_added)*1+0.5, 0, 1, 
                0.5, 0, 0.5, 0.5, 0.5, 
                np.cos(radians)*1+0.5, 0, np.sin(radians)*1+0.5, 0, 0, 
            ])

            deg += deg_added

        return np.array(verticies, dtype=np.float32)