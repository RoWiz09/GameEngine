from OpenGL.GL import *
import glm

class ShaderProgram():
    def __init__(self, vertex_path, fragment_path):
        with open(vertex_path, "r") as file:
            vertexShaderSource = file.read()

        vertexShader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertexShader, vertexShaderSource)
        glCompileShader(vertexShader)

        if glGetShaderiv(vertexShader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(vertexShader))

        with open(fragment_path, "r") as file:
            fragmentShaderSource = file.read()

        fragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragmentShader, fragmentShaderSource)
        glCompileShader(fragmentShader)

        if glGetShaderiv(fragmentShader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(fragmentShader))

        shader_prog = glCreateProgram()
        glAttachShader(shader_prog, vertexShader)
        glAttachShader(shader_prog, fragmentShader)
        glLinkProgram(shader_prog)

        if glGetProgramiv(shader_prog, GL_LINK_STATUS) != GL_TRUE:
            raise RuntimeError(glGetProgramInfoLog(shader_prog))

        glUseProgram(shader_prog)

        glDeleteShader(vertexShader)
        glDeleteShader(fragmentShader)

        self.program = shader_prog

    def SetMat4x4(self, name, matrix):
        glUniformMatrix4fv(glGetUniformLocation(self.program, name), 1, GL_FALSE, glm.value_ptr(matrix))

    def SetVec3(self, name, value):
        glUniform3f(glGetUniformLocation(self.program, name), *value)

    def SetVec4(self, name, value : glm.vec4):
        glUniform4f(glGetUniformLocation(self.program, name), *value)

    def SetInt(self, name, value):
        glUniform1i(glGetUniformLocation(self.program, name), value)

    def SetFloat(self, name, value):
        glUniform1f(glGetUniformLocation(self.program, name), value)

    def Use(self):
        glUseProgram(self.program)

class BaseShaderProgram():
    def __init__(self):
        vertexShaderSource = """
        #version 330 core
        layout (location = 0) in vec3 aPos;
        layout (location = 1) in vec2 aTexCoord;


        out vec4 vertexColor; // specify a color output to the fragment shader
        out vec2 TexCoord;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        uniform vec4 color;

        void main()
        {
            gl_Position = projection * view * model * vec4(aPos, 1.0);
            vertexColor = color;
            TexCoord = aTexCoord;
        }
        """

        vertexShader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertexShader, vertexShaderSource)
        glCompileShader(vertexShader)

        if glGetShaderiv(vertexShader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(vertexShader))

        fragmentShaderSource = """
        #version 330 core
        out vec4 FragColor;

        in vec4 vertexColor;
        in vec2 TexCoord;

        uniform sampler2D texture1;   // Color texture
        void main()
        {
            vec4 textureColor = texture(texture1, TexCoord).rgba;
            FragColor = vertexColor*textureColor;
        } 
        """

        fragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragmentShader, fragmentShaderSource)
        glCompileShader(fragmentShader)

        if glGetShaderiv(fragmentShader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(fragmentShader))

        shader_prog = glCreateProgram()
        glAttachShader(shader_prog, vertexShader)
        glAttachShader(shader_prog, fragmentShader)
        glLinkProgram(shader_prog)

        if glGetProgramiv(shader_prog, GL_LINK_STATUS) != GL_TRUE:
            raise RuntimeError(glGetProgramInfoLog(shader_prog))

        glUseProgram(shader_prog)

        glDeleteShader(vertexShader)
        glDeleteShader(fragmentShader)

        self.program = shader_prog

    def SetMat4x4(self, name, matrix):
        glUniformMatrix4fv(glGetUniformLocation(self.program, name), 1, GL_FALSE, glm.value_ptr(matrix))

    def SetVec3(self, name, value):
        glUniform3f(glGetUniformLocation(self.program, name), *value)

    def SetVec4(self, name, value : glm.vec4):
        glUniform4f(glGetUniformLocation(self.program, name), *value)

    def SetInt(self, name, value):
        glUniform1i(glGetUniformLocation(self.program, name), value)

    def SetFloat(self, name, value):
        glUniform1f(glGetUniformLocation(self.program, name), value)

    def Use(self):
        glUseProgram(self.program)