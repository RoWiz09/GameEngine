from RoDevGameEngine.light import Light

from OpenGL.GL import *
import glm, numpy as np

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

    def set_lights(self, light_data):
        pass

class BaseShaderProgram():
    def __init__(self):
        vertexShaderSource = """
        #version 330 core
        layout (location = 0) in vec3 aPos;
        layout (location = 1) in vec2 aTexCoord;
        layout (location = 2) in vec3 aNormal; // Normal attribute

        out vec2 TexCoord;
        out vec3 FragPos;
        out vec3 Normal;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        void main()
        {
            FragPos = vec3(model * vec4(aPos, 1.0)); // Transform position to world space
            Normal = mat3(transpose(inverse(model))) * aNormal; // Transform normal to world space
            TexCoord = aTexCoord;

            gl_Position = projection * view * model * vec4(aPos, 1.0);
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

        in vec2 TexCoord;
        in vec3 FragPos;
        in vec3 Normal;

        uniform sampler2D texture1; // Color texture
        uniform vec3 viewPos;       // Camera position
        uniform vec2 tilingData;

        // Maximum number of lights
        const int MAX_LIGHTS = 8;

        struct PointLight {
            vec3 position;
            vec3 color;
            float intensity;
            
            float constant;
            float linear;
            float quadratic;
        };

        uniform int numLights;
        uniform PointLight pointLights[MAX_LIGHTS];

        void main()
        {
            vec3 norm = normalize(Normal);
            vec3 result = vec3(0.0);

            for (int i = 0; i < numLights; i++)
            {
                // Compute the distance and attenuation
                vec3 lightDir = normalize(pointLights[i].position - FragPos);
                float diff = max(dot(norm, lightDir), 0.0);

                // Specular lighting (Phong)
                vec3 viewDir = normalize(viewPos - FragPos);
                vec3 reflectDir = reflect(-lightDir, norm);
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);

                // Attenuation based on distance
                float distance = length(pointLights[i].position - FragPos);
                float attenuation = 1.0 / (pointLights[i].constant + 
                                        pointLights[i].linear * distance + 
                                        pointLights[i].quadratic * (distance * distance));

                // Compute final light contribution
                vec3 diffuse = diff * pointLights[i].color * pointLights[i].intensity;
                vec3 specular = spec * pointLights[i].color * 0.5; // Specular strength
                
                result += (diffuse + specular) * attenuation;
            }

            // Apply texture color and combine with lighting
            vec4 textureColor = texture(texture1, TexCoord*tilingData);
            vec3 finalColor = textureColor.rgb * result;

            FragColor = vec4(finalColor, textureColor.a);
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
    
    def SetVec2(self, name, value):
        glUniform2f(glGetUniformLocation(self.program, name), *value)

    def SetVec4(self, name, value : glm.vec4):
        glUniform4f(glGetUniformLocation(self.program, name), *value)

    def SetInt(self, name, value):
        glUniform1i(glGetUniformLocation(self.program, name), value)

    def SetFloat(self, name, value):
        glUniform1f(glGetUniformLocation(self.program, name), value)

    def set_lights(self, light_data_tmp:list[Light]):
        light_data = []

        for light in light_data_tmp:
            if light.get_active() and light.parent.get_active():
                light_data.append(light)

        # Number of active lights
        num_lights = len(light_data)
        glUniform1i(glGetUniformLocation(self.program, "numLights"), num_lights)

        # Set light data in the shader
        for i, light in enumerate(light_data):
            glUniform3f(glGetUniformLocation(self.program, f"pointLights[{i}].position"), *light._pos)
            glUniform3f(glGetUniformLocation(self.program, f"pointLights[{i}].color"), *light.color)
            glUniform1f(glGetUniformLocation(self.program, f"pointLights[{i}].intensity"), light._intensity)
            glUniform1f(glGetUniformLocation(self.program, f"pointLights[{i}].constant"), light._constant)
            glUniform1f(glGetUniformLocation(self.program, f"pointLights[{i}].linear"), light._linear)
            glUniform1f(glGetUniformLocation(self.program, f"pointLights[{i}].quadratic"), light._quadratic)

    def Use(self):
        glUseProgram(self.program)

class RayShaderProgram():
    def __init__(self):
        vertexShaderSource = """
            #version 330 core
            layout (location = 0) in vec3 aPos;

            uniform mat4 uProjection;
            uniform mat4 uView;

            void main()
            {
                gl_Position = uProjection * uView * vec4(aPos, 1.0);
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

        uniform vec4 uColor;

        void main()
        {
            FragColor = uColor;
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
    
    def SetVec2(self, name, value):
        glUniform2f(glGetUniformLocation(self.program, name), *value)

    def SetVec4(self, name, value : glm.vec4):
        glUniform4f(glGetUniformLocation(self.program, name), *value)

    def SetInt(self, name, value):
        glUniform1i(glGetUniformLocation(self.program, name), value)

    def SetFloat(self, name, value):
        glUniform1f(glGetUniformLocation(self.program, name), value)

    def set_lights(self, light_data:list[Light]):
        # Number of active lights
        num_lights = len(light_data)
        glUniform1i(glGetUniformLocation(self.program, "numLights"), num_lights)

        # Set light data in the shader
        for i, light in enumerate(light_data):
            glUniform3f(glGetUniformLocation(self.program, f"pointLights[{i}].position"), *light._pos)
            glUniform3f(glGetUniformLocation(self.program, f"pointLights[{i}].color"), *light.color)
            glUniform1f(glGetUniformLocation(self.program, f"pointLights[{i}].intensity"), light._intensity)
            glUniform1f(glGetUniformLocation(self.program, f"pointLights[{i}].constant"), light._constant)
            glUniform1f(glGetUniformLocation(self.program, f"pointLights[{i}].linear"), light._linear)
            glUniform1f(glGetUniformLocation(self.program, f"pointLights[{i}].quadratic"), light._quadratic)

    def Use(self):
        glUseProgram(self.program)