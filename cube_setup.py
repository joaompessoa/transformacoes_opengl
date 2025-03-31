from OpenGL.GL import *
from OpenGL.GLU import *

vertices = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),  # Face traseira (z=-1)
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1),  # Face frontal (z=1)
)

# Normais das faces (vetores perpendiculares a cada face, apontando para fora)
# Essenciais para o cálculo da iluminação
normals = (
    (0, 0, -1),  # Traseira
    (0, 0, 1),  # Frontal
    (1, 0, 0),  # Direita
    (-1, 0, 0),  # Esquerda
    (0, 1, 0),  # Topo
    (0, -1, 0),  # Base
)

# Coordenadas de textura (mapeiam os cantos da imagem de textura para os cantos das faces)
# (0,0) é geralmente o canto inferior esquerdo da textura
# (1,1) é geralmente o canto superior direito da textura
tex_coords = (
    (0, 0),
    (1, 0),
    (1, 1),
    (0, 1),  # Ordem: inf-esq, inf-dir, sup-dir, sup-esq
)

# Definição das faces do cubo
# Cada face é uma lista de índices de vértices (da lista 'vertices')
# A ordem dos vértices importa para a direção da normal (regra da mão direita)
# A ordem aqui é consistente com as normais definidas acima
faces = (
    (3, 2, 1, 0),  # Traseira (normal 0) - Vértices 3, 2, 1, 0
    (4, 5, 7, 6),  # Frontal  (normal 1) - Vértices 4, 5, 7, 6
    (0, 1, 5, 4),  # Direita  (normal 2) - Vértices 0, 1, 5, 4
    (6, 7, 2, 3),  # Esquerda (normal 3) - Vértices 6, 7, 2, 3
    (1, 2, 7, 5),  # Topo     (normal 4) - Vértices 1, 2, 7, 5
    (6, 3, 0, 4),  # Base     (normal 5) - Vértices 6, 3, 0, 4
)


def texturedLitCube():
    """Desenha um cubo sólido com textura e iluminação."""
    glBegin(GL_QUADS)  # Começa a desenhar quadriláteros (faces do cubo)
    for i, face in enumerate(faces):
        glNormal3fv(normals[i])  # Define a normal para a face atual (para iluminação)
        # Mapeia os 4 cantos da textura para os 4 vértices da face
        glTexCoord2fv(tex_coords[0])  # Canto inferior esquerdo da textura
        glVertex3fv(vertices[face[0]])  # Primeiro vértice da face
        glTexCoord2fv(tex_coords[1])  # Canto inferior direito da textura
        glVertex3fv(vertices[face[1]])  # Segundo vértice da face
        glTexCoord2fv(tex_coords[2])  # Canto superior direito da textura
        glVertex3fv(vertices[face[2]])  # Terceiro vértice da face
        glTexCoord2fv(tex_coords[3])  # Canto superior esquerdo da textura
        glVertex3fv(vertices[face[3]])  # Quarto vértice da face
    glEnd()  # Termina de desenhar os quadriláteros
