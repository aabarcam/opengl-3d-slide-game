from custom_modules.custom_GPUshape import GPUShapeDM
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from PIL import Image

import grafica.basic_shapes as bs
from grafica.gpu_shape import GPUShape

SIZE_IN_BYTES = 4

def twoTextureSimpleSetup(imgName, imgNameDM, sWrapMode, tWrapMode, minFilterMode, maxFilterMode):
     # wrapMode: GL_REPEAT, GL_CLAMP_TO_EDGE
     # filterMode: GL_LINEAR, GL_NEAREST
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    
    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, sWrapMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, tWrapMode)

    # texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minFilterMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, maxFilterMode)
    
    image = Image.open(imgName)
    img_data = np.array(image, np.uint8)

    if image.mode == "RGB":
        internalFormat = GL_RGB
        format = GL_RGB
    elif image.mode == "RGBA":
        internalFormat = GL_RGBA
        format = GL_RGBA
    else:
        print("Image mode not supported.")
        raise Exception()

    glTexImage2D(GL_TEXTURE_2D, 0, internalFormat, image.size[0], image.size[1], 0, format, GL_UNSIGNED_BYTE, img_data)
    
    
    textureDM = glGenTextures(1)
    glActiveTexture(GL_TEXTURE0 + 1)
    glBindTexture(GL_TEXTURE_2D, textureDM)
    
    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, sWrapMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, tWrapMode)

    # texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minFilterMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, maxFilterMode)
    
    imageDM = Image.open(imgNameDM)
    img_dataDM = np.array(imageDM, np.uint8)

    if imageDM.mode == "RGB":
        internalFormatDM = GL_RGB
        formatDM = GL_RGB
    elif imageDM.mode == "RGBA":
        internalFormatDM = GL_RGBA
        formatDM = GL_RGBA
    else:
        print("Image mode not supported.")
        raise Exception()

    glTexImage2D(GL_TEXTURE_2D, 0, internalFormatDM, imageDM.size[0], imageDM.size[1], 0, formatDM, GL_UNSIGNED_BYTE, img_dataDM)
    return (texture, textureDM)

class SimpleDisplacementTextureShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            uniform mat4 transform;

            in vec3 position;
            in vec2 texCoords;

            out vec2 outTexCoords;

            void main()
            {
                gl_Position = transform * vec4(position, 1.0f);
                outTexCoords = texCoords;
            }
            """

        fragment_shader = """
            #version 130

            in vec2 outTexCoords;

            out vec4 outColor;

            uniform int shift;
            uniform float x;
            uniform float y;

            uniform sampler2D samplerTex;
            uniform sampler2D dispMap;

            void main()
            {
                vec4 newColor;
                vec4 dMapColor;
                vec2 newTexCoords;
                vec2 dispMapCoords;
                vec2 staticTexCoords = vec2(outTexCoords[0]-x, outTexCoords[1]-y);

                dispMapCoords = vec2(outTexCoords[0]+x, outTexCoords[1]-y);
                dMapColor = texture(dispMap, dispMapCoords);
                newTexCoords = vec2(staticTexCoords[0] - (dMapColor[0] * 2 - 1) * 0.02, staticTexCoords[1] + (dMapColor[0] * 2 - 1) * 0.02);

                if (shift != 1) {
                    newColor = texture(samplerTex, newTexCoords);
                } else
                    newColor = texture(samplerTex, staticTexCoords);

                outColor = newColor;
            }
            """

        # Compiling our shader program
        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + 2d texture coordinates => 3*4 + 2*4 = 20 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(3 * SIZE_IN_BYTES))
        glEnableVertexAttribArray(texCoords)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShapeDM)

        glBindVertexArray(gpuShape.vao)
        # Binding the first texture
        glActiveTexture(GL_TEXTURE0 + 0)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        # Binding the second texture
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, gpuShape.dispMap)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

class MultipleDispTexturePhongShaderProgram:
    # Pipeline para multiples fuentes de luz, con texturas

    def __init__(self):
        vertex_shader = """
            #version 330 core
            
            in vec3 position;
            in vec2 texCoords;
            in vec3 normal;

            out vec3 fragPosition;
            out vec2 fragTexCoords;
            out vec3 fragNormal;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main()
            {
                fragPosition = vec3(model * vec4(position, 1.0));
                fragTexCoords = texCoords;
                fragNormal = mat3(transpose(inverse(model))) * normal;  
                
                gl_Position = projection * view * vec4(fragPosition, 1.0);
            }
            """

        fragment_shader = """
            #version 330 core

            in vec3 fragNormal;
            in vec3 fragPosition;
            in vec2 fragTexCoords;

            out vec4 fragColor;
            // Posiciones de las fuentes de luz
            vec3 lightPos0 = vec3(-8.0, 0.0f, 8.0f); 
            vec3 lightPos1 = vec3(-8.0, 9.0f, 2.0f); 
            vec3 lightPos2 = vec3(8.0f, 0.0f, 8.0f);  
            vec3 lightPos3 = vec3(8.0f, 9.0f, 2.0f);   
            vec3 lightPos4 = vec3(0.0f, 0.0f, 8.0f);   

            uniform vec3 viewPosition; 
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;

            uniform float x;
            uniform float y;

            uniform sampler2D samplerTex;
            uniform sampler2D dispMap;

            void main()
            {
                // movement
                vec2 waterCoords = vec2(fragTexCoords[0], fragTexCoords[1]-y);
                vec2 dispMapCoords = vec2(fragTexCoords[0]+x, fragTexCoords[1]-y);

                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse
                // fragment normal has been interpolated, so it does not necessarily have norm equal to 1
                vec3 normalizedNormal = normalize(fragNormal);
                
                vec4 dMapColor = texture(dispMap, dispMapCoords);
                vec2 newTexCoords = vec2(waterCoords[0] - (dMapColor[0] * 2 - 1) * 0.05, waterCoords[1] + (dMapColor[0] * 2 - 1) * 0.05);

                vec4 fragOriginalColor = texture(samplerTex, newTexCoords);



                // Vector para sumar la contribucion de cada fuente de luz
                vec3 result = vec3(0.0f, 0.0f, 0.0f);
                
                // Vector que almacena las fuentes de luz
                vec3 lights[5] = vec3[](lightPos0, lightPos1, lightPos2, lightPos3, lightPos4);

                // Se itera por cada fuente de luz para calcular su contribucion
                for (int i = 0; i < 5; i++)
                {
                    // direccion a la fuente de luz de la iteacion actual
                    vec3 toLight = lights[i] - fragPosition;

                    // Lo demas es exactamente igual
                    vec3 lightDir = normalize(toLight);
                    float diff = max(dot(normalizedNormal, lightDir), 0.0);
                    vec3 diffuse = Kd * Ld * diff;
                    
                    // specular
                    vec3 viewDir = normalize(viewPosition - fragPosition);
                    vec3 reflectDir = reflect(-lightDir, normalizedNormal);  
                    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                    vec3 specular = Ks * Ls * spec;

                    // attenuation
                    float distToLight = length(toLight);
                    float attenuation = constantAttenuation
                        + linearAttenuation * distToLight
                        + quadraticAttenuation * distToLight * distToLight;
                    
                    // Se suma la contribucion calculada en la iteracion actual
                    result += ((diffuse + specular) / attenuation);
                }

                // El calculo final es con la suma final
                result = (ambient + result) * fragOriginalColor.rgb;
                fragColor = vec4(result, 1.0);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color + 3d normals => 3*4 + 2*4 + 3*4 = 32 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(color, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShapeDM)

        glBindVertexArray(gpuShape.vao)
        # Binding the first texture
        glActiveTexture(GL_TEXTURE0 + 0)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        # Binding the second texture
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, gpuShape.dispMap)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)