import math
import openmesh as om
import random
import numpy as np

class Shape:
    def __init__(self, vertices, indices, textureFileName=None):
        self.vertices = vertices
        self.indices = indices
        self.textureFileName = textureFileName

def curve_line(curve):
    vertices = []
    indices = []
    for i in range(0, len(curve)):
        vertices += [curve[i][0], curve[i][1], curve[i][2], 1, 0, 0, 0, 0, 1]
    
    for i in range(0, len(curve)-1):
        indices += [i]

    return Shape(vertices, indices)

def curveLineV(curve):
    vertices = []
    indices = []
    for i in range(0, len(curve)):
        vertices += [curve[i][0], curve[i][1], curve[i][2], 0, 0, 1]
    
    for i in range(0, len(curve)-1):
        indices += [i]

    return Shape(vertices, indices)

def createHalfTubeMesh(N, r, curve):
    mesh = om.TriMesh()
    dtheta = math.pi/N

    for point in curve:
        for i in range(0, N + 1):
            theta = math.pi + dtheta * i
            mesh.add_vertex([point[0] + r * math.cos(theta), point[1], point[2] + r * math.sin(theta)])

    vertices = list(mesh.vertices())
    for i in range(0, len(curve) - 1):
        step = (N+1) * i
        for k in range(0, N):
            mesh.add_face(vertices[step + k + N + 1], vertices[step + k], vertices[step + k + 1])
            mesh.add_face(vertices[step + k + 1], vertices[step + k + N + 2], vertices[step + k + N + 1])

    return mesh

def createHalfTubeMeshRot(N, r, curve):
    mesh = om.TriMesh()
    dtheta = math.pi/N
    m = len(curve)

    for k in range(0, N+1):
        theta = math.pi + dtheta * k
        coords = [r * math.cos(theta), 0, r * math.sin(theta), 1]
        coords = matmul([translate(curve[0][0], curve[0][1], curve[0][2]), coords])
        mesh.add_vertex(coords)

    last_slope = 0
    offset = 0
    for i in range(1, m - 1):
        hor_slope = (curve[i+1][0] - curve[i-1][0])/(curve[i+1][1] - curve[i-1][1])
        if abs(hor_slope - last_slope) > 45:
            offset += math.pi
        z_angle = math.atan(hor_slope)
        last_slope = hor_slope
        for k in range(0, N + 1):
            theta = math.pi + dtheta * k
            coords = [r * math.cos(theta), 0, r * math.sin(theta), 1]
            coords = matmul([translate(curve[i][0], curve[i][1], curve[i][2]), rotationZ(-(z_angle + offset)), coords])
            mesh.add_vertex(coords)

    for k in range(0, N+1):
        theta = math.pi + dtheta * k
        coords = [r * math.cos(theta), 0, r * math.sin(theta), 1]
        coords = matmul([translate(curve[m-1][0], curve[m-1][1], curve[m-1][2]), coords])
        mesh.add_vertex(coords)

    vertices = list(mesh.vertices())
    for i in range(0, len(curve) - 1):
        step = (N+1) * i
        for k in range(0, N):
            mesh.add_face(vertices[step + k + N + 1], vertices[step + k], vertices[step + k + 1])
            mesh.add_face(vertices[step + k + 1], vertices[step + k + N + 2], vertices[step + k + N + 1])

    return mesh

def createRiverMesh(points):
    mesh = om.TriMesh()
    curve_n = len(points)
    for i in range(0, curve_n):
        curr_point = points[i]
        mesh.add_vertex(curr_point[0])
        mesh.add_vertex(curr_point[1])
        
    vertices = list(mesh.vertices())
    for i in range(0, curve_n - 1):
        mesh.add_face(vertices[2*i], vertices[2*i+1], vertices[2*i+3])
        mesh.add_face(vertices[2*i+3], vertices[2*i+2], vertices[2*i])
    
    return mesh

def createSpike(N, r, height):
    mesh = om.TriMesh()
    theta = 2*math.pi/N
    rad = r/N
    h = height/N
    mesh.add_vertex([0, 0, height])
    for i in range(1, N + 1):
        dr = i * rad
        dh = height - i * h
        for k in range(0, N):
            dtheta = k * theta
            x = dr * math.cos(dtheta)
            y = dr * math.sin(dtheta)
            z = dh
            mesh.add_vertex([x, y, z])
    vert = list(mesh.vertices())

    mesh.add_face(vert[0], vert[N], vert[1])
    for i in range(1, N):
        mesh.add_face(vert[0], vert[i], vert[i+1])

    for i in range(0, N-1):
        step = i*N
        sN = step + N
        mesh.add_face(vert[sN], vert[sN + N], vert[sN + 1])
        mesh.add_face(vert[sN + 1], vert[step + 1], vert[sN])
        for k in range(1, N):
            mesh.add_face(vert[step + k], vert[step + k + N], vert[step + k + 1 + N])
            mesh.add_face(vert[step + k + 1 + N], vert[step + k + 1], vert[step + k])
    return mesh

def toVerticesAndIndexes(mesh, r, g, b):
    faces = mesh.faces()

    vertices = []
    v = 0

    mesh.request_face_normals()
    mesh.request_vertex_normals()
    mesh.release_face_normals()
    mesh.update_vertex_normals()

    nor_list = mesh.vertex_normals()

    for vertex in mesh.points():
        vertices += vertex.tolist() # Pos
        vertices += [r, g, b] # Color
        vertices += [nor_list[v][0],nor_list[v][1],nor_list[v][2]] # Normales
            
        v += 1

    indexes = []

    for face in faces:
        face_indexes = mesh.fv(face)
        for vertex in face_indexes:
            indexes += [vertex.idx()]

    return vertices, indexes

def toTexVerticesAndIndexes(mesh):
    faces = mesh.faces()

    vertices = []
    v = 0

    mesh.request_face_normals()
    mesh.request_vertex_normals()
    mesh.release_face_normals()
    mesh.update_vertex_normals()

    nor_list = mesh.vertex_normals()

    for vertex in mesh.points():
        vert = vertex.tolist()
        vertices += vert # Pos
        vertices += [vert[0], vert[1]] # Tex        
        vertices += [nor_list[v][0],nor_list[v][1],nor_list[v][2]] # Normales
            
        v += 1

    indexes = []

    for face in faces:
        face_indexes = mesh.fv(face)
        for vertex in face_indexes:
            indexes += [vertex.idx()]

    return vertices, indexes

def createTextureNormalsCube(image_filename):

    # Defining locations,texture coordinates and normals for each vertex of the shape
    UT = 1/3
    DT = 2/3
    H = 1/2
    vertices = [
    #   positions            tex coords   normals
    # Z+
        -0.5, -0.5,  0.5,    DT, H,        0,0,1,
         0.5, -0.5,  0.5,    1, H,        0,0,1,
         0.5,  0.5,  0.5,    1, 0,        0,0,1,
        -0.5,  0.5,  0.5,    DT, 0,        0,0,1,   
    # Z-          
        -0.5, -0.5, -0.5,    0, 1,        0,0,-1,
         0.5, -0.5, -0.5,    1, 1,        0,0,-1,
         0.5,  0.5, -0.5,    1, 0,        0,0,-1,
        -0.5,  0.5, -0.5,    0, 0,        0,0,-1,
       
    # X+          
         0.5, -0.5, -0.5,    UT, H,        1,0,0,
         0.5,  0.5, -0.5,    DT, H,        1,0,0,
         0.5,  0.5,  0.5,    DT, 0,        1,0,0,
         0.5, -0.5,  0.5,    UT, 0,        1,0,0,   
    # X-          
        -0.5, -0.5, -0.5,    UT, H,        -1,0,0,
        -0.5,  0.5, -0.5,    DT, H,        -1,0,0,
        -0.5,  0.5,  0.5,    DT, 0,        -1,0,0,
        -0.5, -0.5,  0.5,    UT, 0,        -1,0,0,   
    # Y+          
        -0.5,  0.5, -0.5,    0, 1,        0,1,0,
         0.5,  0.5, -0.5,    UT, 1,        0,1,0,
         0.5,  0.5,  0.5,    UT, H,        0,1,0,
        -0.5,  0.5,  0.5,    0, H,        0,1,0,   
    # Y-          
        -0.5, -0.5, -0.5,    UT, 1,        0,-1,0,
         0.5, -0.5, -0.5,    DT, 1,        0,-1,0,
         0.5, -0.5,  0.5,    DT, H,        0,-1,0,
        -0.5, -0.5,  0.5,    UT, H,        0,-1,0
        ]   

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
          7, 6, 5, 5, 4, 7, # Z-
          8, 9,10,10,11, 8, # X+
         15,14,13,13,12,15, # X-
         19,18,17,17,16,19, # Y+
         20,21,22,22,23,20] # Y-

    return Shape(vertices, indices, image_filename)


# Transformaciones copiadas del modulo transformations
####################################################################
def translate(tx, ty, tz):
    return np.array([
        [1,0,0,tx],
        [0,1,0,ty],
        [0,0,1,tz],
        [0,0,0,1]], dtype = np.float32)

def rotationX(theta):
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    return np.array([
        [1,0,0,0],
        [0,cos_theta,-sin_theta,0],
        [0,sin_theta,cos_theta,0],
        [0,0,0,1]], dtype = np.float32)


def rotationY(theta):
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    return np.array([
        [cos_theta,0,sin_theta,0],
        [0,1,0,0],
        [-sin_theta,0,cos_theta,0],
        [0,0,0,1]], dtype = np.float32)


def rotationZ(theta):
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    return np.array([
        [cos_theta,-sin_theta,0,0],
        [sin_theta,cos_theta,0,0],
        [0,0,1,0],
        [0,0,0,1]], dtype = np.float32)

def matmul(mats):
    out = mats[0]
    for i in range(1, len(mats)):
        out = np.matmul(out, mats[i])

    return out
####################################################################