import glfw
import numpy as np
import grafica.transformations as tr
import math

class Player():
    # Clase que contiene al modelo del player / auro
    def __init__(self, size, pos, vel, curve, list):
        self.pos = pos # Posicion en el escenario
        self.orig = pos
        self.vel = vel # Velocidad de desplazamiento
        self.model = None # Referencia al grafo de escena asociado
        self.controller = None # Referencia del controlador, para acceder a sus variables
        self.size = size # Escala a aplicar al nodo 
        self.radio = 0.1 # distancia para realiozar los calculos de colision
        self.curve = curve
        self.list = list
        self.last_slope = 0
        self.rot_offset = 0
        self.x = 0
        self.y = 0
        self.z = 0

    def set_model(self, new_model):
        # Se obtiene una referencia a uno nodo
        self.model = new_model

    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller

    def update(self, delta):
        # Se actualiza la posicion del auto

        if self.controller.left_held and self.controller.offset < 1:
            self.controller.offset += 0.3 * delta
        if self.controller.right_held and self.controller.offset > 0:
            self.controller.offset -= 0.3 * delta
        # # Si detecta la tecla [W] presionada y no se ha salido de la pista se mueve hacia arriba
        # if self.controller.is_w_pressed and self.pos[1] < -0.45:
        #     self.pos[1] += self.vel[1] * delta
        # # Si detecta la tecla [S] presionada y no se ha salido de la pista se mueve hacia abajo
        # if self.controller.is_s_pressed and self.pos[1] > -0.8:
        #     self.pos[1] -= self.vel[1] * delta
        # #print(self.pos[0], self.pos[1])
        if self.controller.run and self.pos < len(self.list) - 2:
            self.pos += 1

        # Se le aplica la transformacion de traslado segun la posicion actual
        max_left = self.list[self.pos][0]
        max_right = self.list[self.pos][1]
        self.x = max_left[0] * self.controller.offset + max_right[0] * (1 - self.controller.offset)
        self.y = max_left[1] * self.controller.offset + max_right[1] * (1 - self.controller.offset)
        self.z = max_left[2] * self.controller.offset + max_right[2] * (1 - self.controller.offset)

        hor_slope = (self.curve[self.pos+1][0] - self.curve[self.pos-1][0])/(self.curve[self.pos+1][1] - self.curve[self.pos-1][1])
        if abs(hor_slope - self.last_slope) > 45:
            self.rot_offset += math.pi
        z_angle = math.atan(hor_slope)
        self.last_slope = hor_slope
        rotation = tr.rotationZ(-(z_angle + self.rot_offset))

        self.model.transform = tr.matmul([tr.translate(self.x, self.y, self.z + 0.075), tr.scale(self.size, self.size, self.size), rotation])

        return self.x, self.y, self.z

    def collision(self, cargas):
        # Funcion para detectar las colisiones con las cargas

        # Se recorren las cargas 
        for carga in cargas:
            # si la distancia a la carga es menor que la suma de los radios ha ocurrido en la colision
            if (self.radio+carga.radio)**2 > ((self.x- carga.pos[0])**2 + (self.y-carga.pos[1])**2):
                self.pos = self.orig
                return

class Obstáculo():
    # Clase para contener las caracteristicas de un objeto que representa un obstáculo 
    def __init__(self, pos, radio):
        self.pos = pos
        self.radio = radio
        self.model = None
    
    def set_model(self, new_model):
        self.model = new_model

    def update(self):
        # Se posiciona el nodo referenciado
        self.model.transform = tr.translate(self.pos[0], self.pos[1], self.pos[2])