from PIL.Image import new
import numpy as np
import math

def catMullCurve(N, p_list):
    puntos = len(p_list)
    ts = np.linspace(0.0, 1.0, N)
    M_CR = np.array([[0, -1/2, 2/2, -1/2],
                     [2/2, 0, -5/2, 3/2],
                     [0, 1/2, 4/2, -3/2],
                     [0, 0, -1/2, 1/2]])

    seg_list = []
    curves_list = []
    for i in range(1, puntos - 2):
        p = np.concatenate((p_list[i-1],p_list[i],p_list[i+1],p_list[i+2]), axis=1)
        segmento = np.matmul(p, M_CR)
        c_vacia = np.ndarray(shape=(N, 3), dtype=float)
        seg_list += [segmento]
        curves_list += [c_vacia]

    seg_list = np.array(seg_list)

    for i in range(0,puntos - 3):
        for k in range(len(ts)):
            T = np.array([[1, ts[k], ts[k]**2, ts[k]**3]]).T
            curves_list[i][k, 0:3] = (np.matmul(seg_list[i], T).T)

    final_curve = []
    for curr_curve in curves_list:
        for k in curr_curve:
            final_curve.append(k)

    final_curve = np.array(final_curve)

    return final_curve

def deleteRepeated(pointsList):
    newList = [pointsList[0]]
    epsilon = 0.05
    for i in range(1, len(pointsList)):
        if pointsList[i-1][0] != pointsList[i][0] or pointsList[i-1][1] != pointsList[i][1] or pointsList[i-1][2] != pointsList[i][2]:
            newList.append(pointsList[i])
    return newList

def distTwoPoints(a, b):
    return np.sqrt((b[0]-a[0])**2+(b[1]-a[1])**2+(b[2]-a[2])**2)

def getVerticesOnHeight(curve, mesh, height, N):
    final_list = []
    v_list = mesh.points()
    for i in range(0, len(curve)):
        step = i * (N+1)
        ind1 = int(step + math.ceil(N/2) - height)
        ind2 = int(step + math.ceil(N/2) + height)
        v1 = v_list[ind1]
        v2 = v_list[ind2]
        final_list.append([v1, v2])
    return final_list

# def catMullCurveModified(N, p_list):
#     puntos = len(p_list)
#     ts = np.linspace(0.0, 1.0, N)
#     M_CR = np.array([[0, -1/2, 2/2, -1/2],
#                      [2/2, 0, -5/2, 3/2],
#                      [0, 1/2, 4/2, -3/2],
#                      [0, 0, -1/2, 1/2]])

#     # Creación curva inicial
#     seg_list = []
#     curves_list = []
#     for i in range(1, puntos - 2):
#         p = np.concatenate((p_list[i-1],p_list[i],p_list[i+1],p_list[i+2]), axis=1)
#         segmento = np.matmul(p, M_CR)
#         c_vacia = np.ndarray(shape=(N, 3), dtype=float)
#         seg_list += [segmento]
#         curves_list += [c_vacia]

#     seg_list = np.array(seg_list)

#     for i in range(0,puntos - 3):
#         for k in range(len(ts)):
#             T = np.array([[1, ts[k], ts[k]**2, ts[k]**3]]).T
#             curves_list[i][k, 0:3] = (np.matmul(seg_list[i], T).T)

# ########################################################

#     total_length = 0
#     curves_len = []
#     for curve in curves_list:
#         curr_dist = 0
#         for k in range(1, len(curve)):
#             dist = distTwoPoints(curve[k-1], curve[k])
#             curr_dist += dist
#             total_length += dist
#         curves_len.append(curr_dist)

#     # Curva ajustada
#     seg_list = []
#     curves_list = []
#     for i in range(1, puntos - 2):
#         p = np.concatenate((p_list[i-1],p_list[i],p_list[i+1],p_list[i+2]), axis=1)
#         segmento = np.matmul(p, M_CR)
#         seg_list += [segmento]

#     seg_list = np.array(seg_list)

#     for i in range(0,puntos - 3):
#         # print(curves_len[i], N, total_length)
#         # print(100*curves_len[i]*N/total_length)
#         new_N = int(np.ceil(20*N*(curves_len[i]/total_length)))
#         print(new_N)
#         ts = np.linspace(0.0, 1.0, new_N)
#         # print(ts)
#         for k in range(len(ts)):
#             c_vacia = np.ndarray(shape=(N, 3), dtype=float)
#             curves_list += [c_vacia]
#             # print(k)
#             # print(ts[k])
#             T = np.array([[1, ts[k], ts[k]**2, ts[k]**3]]).T
#             curves_list[i][k, 0:3] = (np.matmul(seg_list[i], T).T)

#     final_curve = []
#     for curr_curve in curves_list:
#         for k in curr_curve:
#             final_curve.append(k)

#     final_curve = np.array(final_curve)
#     print(curves_len)
    
#     # for k in curves_len:
#     #     print(k/total_length)

#     return final_curve