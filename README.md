# Proyecto de OpenGL en 3D

Segundo proyecto para el curso Modelación y Computación Gráfica para Ingenieros de la Universidad de Chile, semestre otoño, 2021.

Consiste en un juego en 3D creado con Python y OpenGL, acerca de un cubo de hielo que se desliza por un tobogán. Busca mostrar el uso de transformaciones, texturas, mallas de polígonos, shaders y curvas, entre otras funcionalidades 3D de OpenGL. Todos los elementos en la carpeta 'gráfica' fueron provistos por el profesor del curso Daniel Calderón.

### Métodos de ejecución:
- python displacement_view.py

Muestra un efecto de displacement map sobre una textura de agua, simulando su movimiento.
- python water_slide.py N V

Ejecuta el juego, N es la cantidad de obstáculos en total que posicionar a lo largo del tobogán, y V es la velocidad a la que avanza el cubo de hielo. Se recomienda un valor cercano a 10 para N y 15 para V.

### Controles
- Flechas arriba: Causa que el cubo de hielo comience a deslizarse
- Flechas derecha e izquierda: Mueve el cubo de lado a lado en el tobogán
- 1, 2: Hay dos toboganes ejecutándose a la vez, los números indican a cual tobogán seguir, cambiando la cámara de posición.
- Q: Se hace visible la curva que muestra la trayectoria de cada tobogán
- Barra espaciadora: Alterna entre dibujar polígonos rellenos y solo dibujar su contorno
- Escape: Cierra el juego
---
# OpenGL 3D project
Second project for the Modeling and Computer Graphics for Engineers course at the University de Chile, autumn semester, 2021.

Consists of of a 3D game made with Python and OpenGL, where an ice cube moves down along a water slide. It showcases use of transformations, textures, polygon meshes and curves, among other 3D functionalities available with OpenGL. All elements inside the 'gráfica' folder were provided by the course teacher Daniel Calderón.
### Execution methods:
- python displacement_view.py

Showcases a displacement map effect over a water texture, simulating movement.

- python water_slide.py N V

Executes que game, where N is the total quantity of obstacles to be positioned along the slide, and V is the ice cube's velocity. A value near 10 is recommended for N, and a value near 15 for V.

### Controls

- Up arrow key: Causes the ice cube to start moving along the slide
- Right and left arrow keys: Moves the cube from side to side on the slide
- 1, 2: There are two slides being executed at a time, the numbers let you select which one to follow, changing the camera's position accordingly
- Q: Toggles the visibility of the curve that shows off the trajectory of the slide
- Space bar: Toggles the drawing mode between fully colored polygons and only their outline
- Escape: Closes the game