import numpy as np
import math
import random as rd
from OpenGL.GL import *
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.scene_graph as sg
import sys, os.path

import custom_modules.custom_shapes as csh
import custom_modules.custom_curves as cc

from grafica.assets_path import getAssetPath
from custom_modules.custom_GPUshape import *

def createGPUShape(shape, pipeline):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

def createTextureGPUShape(shape, pipeline, path):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape con texturas
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = es.textureSimpleSetup(
        path, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    return gpuShape

def createPlayerModel(tex_pipeline):
    # Se crea el nodo del modelo del jugador
    cubeShape = csh.createTextureNormalsCube(getAssetPath("ice_tex.png"))

    gpuCube = createTextureGPUShape(cubeShape, tex_pipeline, cubeShape.textureFileName)

    playerNode = sg.SceneGraphNode("player")
    playerNode.childs = [gpuCube]

    return playerNode

def createTube(pipeline, rot, color, circle_N, curve):
    if rot:
        tubeMesh = csh.createHalfTubeMeshRot(circle_N, 1, curve)
    else:
        curve = cc.deleteRepeated(curve)
        tubeMesh = csh.createHalfTubeMesh(circle_N, 1, curve)
    tubeVertices, tubeIndices = csh.toVerticesAndIndexes(tubeMesh, color[0], color[1],color[2])
    tubeGpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(tubeGpu)
    tubeGpu.fillBuffers(tubeVertices, tubeIndices, GL_STATIC_DRAW)
    return tubeGpu, tubeMesh, curve

def createRiver(pipeline, river_list):
    riverMesh = csh.createRiverMesh(river_list)
    riverV, riverI = csh.toTexVerticesAndIndexes(riverMesh)
    riverGpu = GPUShapeDM().initBuffers()
    pipeline.setupVAO(riverGpu)
    riverGpu.fillBuffers(riverV, riverI, GL_STATIC_DRAW)
    riverGpu.texture = es.textureSimpleSetup(getAssetPath("water_1.jpg"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    riverGpu.dispMap = es.textureSimpleSetup(getAssetPath("water_disp4.jpg"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    return riverGpu, riverMesh

def createObstaclesModels(pipeline, N, M):
    modelsNode = sg.SceneGraphNode("modelos")
    modelsNode.childs = []
    
    for i in range(N):
        obsMesh = csh.createSpike(M, 0.05, 0.8)
        obsV, obsI = csh.toVerticesAndIndexes(obsMesh, 1, 0, 0)
        obsGpu = es.GPUShape().initBuffers()
        pipeline.setupVAO(obsGpu)
        obsGpu.fillBuffers(obsV, obsI, GL_STATIC_DRAW)
        obstacleNode = sg.SceneGraphNode("obs" + str(i))
        obstacleNode.childs = [obsGpu]

        modelsNode.childs.append(obstacleNode)

    return modelsNode