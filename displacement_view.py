import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica.gpu_shape import GPUShape, SIZE_IN_BYTES
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
from grafica.assets_path import getAssetPath

# Custom imports
import custom_modules.custom_shaders as cs
from custom_modules.custom_GPUshape import GPUShapeDM

SIZE_IN_BYTES = 4

class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.shift = True

controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    if key == glfw.KEY_Q:
        controller.shift = not controller.shift

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key')

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Displacement View", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # A simple shader program with position and texture coordinates as inputs.
    pipeline = cs.SimpleDisplacementTextureShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Creating shapes on GPU memory
    shapeWater = bs.createTextureQuad(1,1)
    gpuWater = GPUShapeDM().initBuffers()
    pipeline.setupVAO(gpuWater)
    gpuWater.fillBuffers(shapeWater.vertices, shapeWater.indices, GL_STATIC_DRAW)
    gpuWater.texture = es.textureSimpleSetup(getAssetPath("water_1.jpg"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    gpuWater.dispMap = es.textureSimpleSetup(getAssetPath("water_disp4.jpg"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)


        

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        theta = glfw.get_time()
        # Drawing the shapes
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.uniformScale(2))

        m = (theta%10) * 0.1
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "x"), m)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "y"), m)

        if not controller.shift:
            glUniform1i(glGetUniformLocation(pipeline.shaderProgram, "shift"), 1)
        else:
            glUniform1i(glGetUniformLocation(pipeline.shaderProgram, "shift"), 0)

        glUniform1i(glGetUniformLocation(pipeline.shaderProgram, "dispMap"), 1) # Entrega el displacement map al shader
        
        pipeline.drawCall(gpuWater)
        
        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuWater.clear()

    glfw.terminate()
