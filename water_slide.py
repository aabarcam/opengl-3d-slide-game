import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import random as rd
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.scene_graph as sg
from grafica.assets_path import getAssetPath

import custom_modules.custom_shapes as csh
import custom_modules.custom_shaders as csd
import custom_modules.custom_curves as cc
import custom_modules.newLightShaders as ns
from custom_modules.custom_GPUshape import *

import shapes as sh
import models as md

class Controller:
    def __init__(self):
        self.fillPolygon = True
###########################################################
        self.theta = np.pi
        self.eye = [0, 0.8, 0.1]
        self.at = [0, 0, 0.1]
        self.up = [0, 0, 1]
        self.markerPos = 0
        self.cam = 1
        self.offset = 0.5

        self.start = False
        self.run = False
        self.right_held = False
        self.left_held = False
        self.show_line = False

controller = Controller()

def on_key(window, key, scancode, action, mods):

    global controller

    if key == glfw.KEY_RIGHT:
        if action == glfw.PRESS:
            controller.right_held = True
        elif action == glfw.RELEASE:
            controller.right_held = False

    elif key == glfw.KEY_LEFT:
        if action == glfw.PRESS:
            controller.left_held = True
        elif action == glfw.RELEASE:
            controller.left_held = False

    if action != glfw.PRESS and action != glfw.REPEAT:
        return
    
    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    elif key == glfw.KEY_UP:
        controller.start = True

    elif key == glfw.KEY_1:
        controller.cam = 1

    elif key == glfw.KEY_2:
        controller.cam = 2

    elif key == glfw.KEY_Q:
        controller.show_line = not controller.show_line

def create_skybox(pipeline):
    shapeSky = bs.createTextureNormalsCube('paisaje.jfif')
    gpuSky = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuSky)
    gpuSky.fillBuffers(shapeSky.vertices, shapeSky.indices, GL_STATIC_DRAW)
    gpuSky.texture = es.textureSimpleSetup(
        getAssetPath("paisaje2.jfif"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    
    skybox = sg.SceneGraphNode("skybox")
    skybox.transform = tr.uniformScale(20)
    skybox.childs += [gpuSky]

    return skybox

if __name__ == "__main__":
    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Water slide", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating shader programs for textures and for colors
    textureShaderProgram = ns.MultipleTexturePhongShaderProgram()
    colorShaderProgram = ns.MultiplePhongShaderProgram()
    dispTexShaderProgram = csd.MultipleDispTexturePhongShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

###########################################################################################
    obs_N = int(sys.argv[1])
    vel = int(sys.argv[2])
    smooth = 5

    # Creating shapes on GPU memory
    circle_N = 40
    curve_N = 20
    curve_offset = 8


    P00 = np.array([[0.0-curve_offset, -10.0, 9.0]]).T
    P01 = np.array([[0.0-curve_offset, -9.5, 9.0]]).T
    P02 = np.array([[0.0-curve_offset, -8.0, 9.0]]).T
    P03 = np.array([[0.7-curve_offset, -7.0, 9.0]]).T
    P04 = np.array([[1.8-curve_offset, -6.0, 8.0]]).T
    P05 = np.array([[2.0-curve_offset, -4.0, 6.0]]).T
    P06 = np.array([[1.8-curve_offset, -2.0, 4.0]]).T
    P07 = np.array([[0.7-curve_offset, -1.0, 3.0]]).T
    P08 = np.array([[0.0-curve_offset, 0.0, 2.0]]).T
    P085 = np.array([[0.0-curve_offset, 1.5, 0.5]]).T
    P088 = np.array([[0.5-curve_offset, 3.0, -1.0]]).T
    P09 = np.array([[0.5-curve_offset, 4.0, -2.0]]).T
    P10 = np.array([[0.0-curve_offset, 5.0, -3.0]]).T
    P15 = np.array([[-0.5-curve_offset, 6.0, -4.0]]).T
    P155 = np.array([[-0.5-curve_offset, 7.0, -5.0]]).T
    P16 = np.array([[0.0-curve_offset, 9.0, -6.5]]).T
    P17 = np.array([[0.0-curve_offset, 10.0, -7.5]]).T
    tube_curve_p = [P00, P01, P02, P03, P04, P05, P06, P07, P08, P085, P088, P09, P10, P15, P155, P16, P17]
    tube_curve = cc.catMullCurve(curve_N * smooth, tube_curve_p)

    curve_offset = 2
    V00 = np.array([[0.0+curve_offset, -10.0, 9.0]]).T
    V01 = np.array([[0.0+curve_offset, -9.5, 9.0]]).T
    V02 = np.array([[0.0+curve_offset, -8.0, 9.0]]).T
    V03 = np.array([[0.7+curve_offset, -7.0, 9.0]]).T
    V04 = np.array([[1.8+curve_offset, -6.0, 8.0]]).T
    V05 = np.array([[2.0+curve_offset, -4.0, 6.0]]).T
    V06 = np.array([[1.8+curve_offset, -2.0, 4.0]]).T
    V07 = np.array([[0.7+curve_offset, -1.0, 3.0]]).T
    V08 = np.array([[0.0+curve_offset, 0.0, 2.0]]).T
    V085 = np.array([[0.0+curve_offset, 1.5, 0.5]]).T
    V088 = np.array([[0.0+curve_offset, 3.0, -1.0]]).T
    V09 = np.array([[0.0+curve_offset, 4.0, -2.0]]).T
    V10 = np.array([[0.5+curve_offset, 5.0, -3.0]]).T
    V11 = np.array([[3.0+curve_offset, 7.0, -4.0]]).T
    V12 = np.array([[5.5+curve_offset, 5.0, -5.0]]).T
    V13 = np.array([[3.0+curve_offset, 3.0, -6.0]]).T
    V14 = np.array([[0.5+curve_offset, 5.0, -7.0]]).T
    V15 = np.array([[0.0+curve_offset, 6.0, -8.0]]).T
    V155 = np.array([[0.0+curve_offset, 7.0, -8.5]]).T
    V16 = np.array([[0.0+curve_offset, 9.0, -8.5]]).T
    V17 = np.array([[0.0+curve_offset, 10.0, -9.5]]).T
    tube_curve_p_rot = [V00, V01, V02, V03, V04, V05, V06, V07, V08, V085, V088, V09, V10, V11, V12, V13, V14, V15, V155, V16, V17]
    tube_curve_rot = cc.catMullCurve(curve_N * smooth, tube_curve_p_rot)

    ###
    tubeCurveShape = csh.curve_line(tube_curve)
    tubeGpuCurve = es.GPUShape().initBuffers()
    colorShaderProgram.setupVAO(tubeGpuCurve)
    tubeGpuCurve.fillBuffers(tubeCurveShape.vertices, tubeCurveShape.indices, GL_STATIC_DRAW)
    ###

    tubeGpu, tubeMesh, tube_curve = sh.createTube(colorShaderProgram, False, [0.4,0.4,0.4], circle_N, tube_curve)

    river_list = cc.getVerticesOnHeight(tube_curve, tubeMesh, circle_N/4, circle_N)
    riverGpu, riverMesh = sh.createRiver(dispTexShaderProgram, river_list)

    tubeRotGpu, tubeRotMesh, tube_curve_rot = sh.createTube(colorShaderProgram, True, [0.4,0.4,0.4], circle_N, tube_curve_rot)

    river_list_rot = cc.getVerticesOnHeight(tube_curve_rot, tubeRotMesh, circle_N/4, circle_N)
    riverGpuRot, riverMeshRot = sh.createRiver(dispTexShaderProgram, river_list_rot)

    tubeNode = sg.SceneGraphNode("tubo")
    tubeNode.childs = [tubeGpu]

    tubeRotNode = sg.SceneGraphNode("tubo_rot")
    tubeRotNode.childs = [tubeRotGpu]

    tubesNode = sg.SceneGraphNode("tubos")
    tubesNode.childs = [tubeNode, tubeRotNode]

    obstacleNode1 = sh.createObstaclesModels(colorShaderProgram, obs_N, 20)
    obsList = []
    curve_N_obs = len(tube_curve)
    curve_offset = curve_N_obs // 10
    av = river_list[2 * curve_offset:curve_N_obs-curve_offset]
    loc = (curve_offset * 7) // obs_N
    for i in range(0, obs_N):
        pos = av[i * loc]
        max_left, max_right = pos[0], pos[1]
        rand_offset = rd.randint(0, 100) / 100
        x = max_left[0] * rand_offset + max_right[0] * (1 - rand_offset)
        y = max_left[1] * rand_offset + max_right[1] * (1 - rand_offset)
        z = (max_left[2] * rand_offset + max_right[2] * (1 - rand_offset)) - 0.05
        obs = md.Obstáculo([x,y,z], 0.05)
        obs.set_model(obstacleNode1.childs[i])
        obsList.append(obs)

    obstacleNode2 = sh.createObstaclesModels(colorShaderProgram, obs_N, 20)
    obsList2 = []
    curve_N_obs2 = len(tube_curve_rot)
    curve_offset2 = curve_N_obs // 10
    av2 = river_list_rot[2 * curve_offset2:curve_N_obs]
    loc2 = (curve_offset2 * 8) // obs_N
    for i in range(0, obs_N):
        pos2 = av2[i * loc2]
        max_left, max_right = pos2[0], pos2[1]
        rand_offset = rd.randint(0, 100) / 100
        x2 = max_left[0] * rand_offset + max_right[0] * (1 - rand_offset)
        y2 = max_left[1] * rand_offset + max_right[1] * (1 - rand_offset)
        z2 = (max_left[2] * rand_offset + max_right[2] * (1 - rand_offset)) - 0.05
        obs2 = md.Obstáculo([x2,y2,z2], 0.05)
        obs2.set_model(obstacleNode2.childs[i])
        obsList2.append(obs2)

    skybox = create_skybox(textureShaderProgram)

    # Creating models
    start_offset = 30
    cam_height = 0.05
    player = md.Player(0.1, smooth * start_offset, 1, tube_curve, river_list)
    playerModel = sh.createPlayerModel(textureShaderProgram)
    player.set_controller(controller)
    player.set_model(playerModel)

    player2 = md.Player(0.1, smooth * start_offset, 1, tube_curve_rot, river_list_rot)
    playerModel2 = sh.createPlayerModel(textureShaderProgram)
    player2.set_controller(controller)
    player2.set_model(playerModel2)

    playersNode = sg.SceneGraphNode("players")
    playersNode.childs = [player.model, player2.model]

###########################################################################################

    # View and projection
    projection = tr.perspective(60, float(width)/float(height), 0.1, 100)

    t0 = glfw.get_time()
    flag = True
    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()
        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        t1 = glfw.get_time()
        delta = t1 -t0
        t0 = t1

###########################################################################
        if controller.cam == 0:
            at_x = controller.eye[0] + np.cos(controller.theta)
            at_y = controller.eye[1] + np.sin(controller.theta)
            controller.at = np.array([at_x, at_y, controller.at[2]])
        elif controller.cam == 1:
            cam_point = tube_curve[player.pos - smooth * start_offset//2]
            controller.eye = [cam_point[0], cam_point[1], cam_point[2] + cam_height]
            temp = tube_curve[player.pos]
            controller.at = np.array([temp[0], temp[1], temp[2] - cam_height])
        elif controller.cam == 2:
            cam_point2 = tube_curve_rot[player2.pos - smooth * start_offset//2]
            controller.eye = [cam_point2[0], cam_point2[1], cam_point2[2] + cam_height]
            temp = tube_curve_rot[player2.pos]
            controller.at = np.array([temp[0], temp[1], temp[2] - cam_height])
    

        view = tr.lookAt(controller.eye, controller.at, controller.up)

###########################################################################

        # Drawing (no texture)
        glUseProgram(colorShaderProgram.shaderProgram)


        lightposition = [0, 0, 2.3]

        interval = (t1*vel * smooth)%1
        if interval < 0.5 and flag:
            cd = True
            flag = False
            if controller.start:
                controller.run = True
        if interval > 0.5 and not flag:
            flag = True

        # Setting all uniform shader variables
        
        glUseProgram(colorShaderProgram.shaderProgram)
        glUniform3f(glGetUniformLocation(colorShaderProgram.shaderProgram, "La"), 0.25, 0.25, 0.25)
        glUniform3f(glGetUniformLocation(colorShaderProgram.shaderProgram, "Ld"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(colorShaderProgram.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(colorShaderProgram.shaderProgram, "Ka"), 0.6, 0.6, 0.6)
        glUniform3f(glGetUniformLocation(colorShaderProgram.shaderProgram, "Kd"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(colorShaderProgram.shaderProgram, "Ks"), 0.2, 0.2, 0.2)

        # Ya no se necesita la posicion de la fuentes de luz, se declaran constantes en los shaders
        glUniform3f(glGetUniformLocation(colorShaderProgram.shaderProgram, "viewPosition"), controller.eye[0], controller.eye[1], controller.eye[2])
        glUniform1ui(glGetUniformLocation(colorShaderProgram.shaderProgram, "shininess"), 10)
        
        glUniform1f(glGetUniformLocation(colorShaderProgram.shaderProgram, "constantAttenuation"), 0.01)
        glUniform1f(glGetUniformLocation(colorShaderProgram.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(colorShaderProgram.shaderProgram, "quadraticAttenuation"), 0.05)

        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        if controller.show_line:
            colorShaderProgram.drawCall(tubeGpuCurve, GL_LINE_STRIP)

        sg.drawSceneGraphNode(tubesNode, colorShaderProgram, "model")
        
        glUniform3f(glGetUniformLocation(colorShaderProgram.shaderProgram, "Ka"), 0.8, 0.8, 0.8)
        glUniform3f(glGetUniformLocation(colorShaderProgram.shaderProgram, "Ks"), 0.7, 0.7, 0.7)
        glUniform1ui(glGetUniformLocation(colorShaderProgram.shaderProgram, "shininess"), 100)
        sg.drawSceneGraphNode(obstacleNode1, colorShaderProgram, "model")
        sg.drawSceneGraphNode(obstacleNode2, colorShaderProgram, "model")

        # Drawing skybox (with texture, another shader program)
        glUseProgram(textureShaderProgram.shaderProgram)

        glUniform3f(glGetUniformLocation(textureShaderProgram.shaderProgram, "La"), 0.25, 0.25, 0.25)
        glUniform3f(glGetUniformLocation(textureShaderProgram.shaderProgram, "Ld"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(textureShaderProgram.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(textureShaderProgram.shaderProgram, "Ka"), 0.6, 0.6, 0.6)
        glUniform3f(glGetUniformLocation(textureShaderProgram.shaderProgram, "Kd"), 0.9 , 0.9, 0.9)
        glUniform3f(glGetUniformLocation(textureShaderProgram.shaderProgram, "Ks"), 0.1, 0.1, 0.1)

        # Ya no se necesita la posicion de la fuentes de lus, se declaran constantes en los shaders
        glUniform3f(glGetUniformLocation(textureShaderProgram.shaderProgram, "viewPosition"), controller.eye[0], controller.eye[1], controller.eye[2])
        glUniform1ui(glGetUniformLocation(textureShaderProgram.shaderProgram, "shininess"), 5)
        
        glUniform1f(glGetUniformLocation(textureShaderProgram.shaderProgram, "constantAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(textureShaderProgram.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(textureShaderProgram.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        # colorShaderProgram.drawCall(testSpikeGpu)
        sg.drawSceneGraphNode(skybox, textureShaderProgram, "model")
        sg.drawSceneGraphNode(playersNode, textureShaderProgram, "model")

        # Drawing river with displacement map
        glUseProgram(dispTexShaderProgram.shaderProgram)

        glUniform3f(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "La"), 0.25, 0.25, 0.25)
        glUniform3f(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "Ld"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "Ka"), 0.6, 0.6, 0.6)
        glUniform3f(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "Kd"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        # Ya no se necesita la posicion de la fuentes de lus, se declaran constantes en los shaders
        glUniform3f(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "viewPosition"), controller.eye[0], controller.eye[1], controller.eye[2])
        glUniform1ui(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "shininess"), 100)
        
        glUniform1f(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "constantAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        m = (t1%2) * 0.5
        glUniform1f(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "x"), m)
        glUniform1f(glGetUniformLocation(dispTexShaderProgram.shaderProgram, "y"), m)

        dispTexShaderProgram.drawCall(riverGpu)
        dispTexShaderProgram.drawCall(riverGpuRot)

        player.collision(obsList)
        player.update(delta)
        player2.collision(obsList2)
        player2.update(delta)
        for spike in obsList:
            spike.update()
        for spike in obsList2:
            spike.update()

        controller.run = False
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
