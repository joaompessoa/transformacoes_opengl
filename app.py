import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from cube_setup import texturedLitCube
import os  

# --- Inicialização do Pygame ---
pygame.init()

# --- Configurações do Projeto ---
screen_width = 800
screen_height = 800
background_color = (0.1, 0.1, 0.2, 1.0)  # Um azul escuro suave
texture_file = "texture.png"  # Nome do arquivo de textura esperado

# Configuração da fonte para renderizar texto na tela
try:
    font = pygame.font.SysFont("JetBrains Mono", 16)
except pygame.error:
    print("Aviso: Fonte 'JetBrains Mono' não encontrada, usando fonte padrão.")
    font = pygame.font.Font(None, 24)  # Usa a fonte padrão do Pygame

# Configurar o display principal
screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
pygame.display.set_caption("OpenGL - Transformações Geométricas (Textura e Luz)")

# --- Variáveis Globais ---

# ID da textura carregada pelo OpenGL
texture_id = None

# Parâmetros de transformação
translation_x = 0.0
translation_y = 0.0
translation_z = 0.0
scale_factor = 1.0
mirror_x = 1.0
mirror_y = 1.0
mirror_z = 1.0

# Estado da aplicação (qual transformação está ativa)
translate_active = False
scale_active = False
mirror_active = False

# Parâmetros da animação de rotação automática
rotate_x = 0
rotate_y = 0
rotate_z = 0

# --- Funções ---

def load_texture(filename):
    """Carrega uma imagem usando Pygame e cria uma textura OpenGL."""
    global texture_id
    if not os.path.exists(filename):
        print(f"Erro: Arquivo de textura '{filename}' não encontrado!")
        # Cria uma textura branca simples como fallback
        textureData = bytes([255, 255, 255, 255] * 64 * 64)  # 64x64 branco
        width, height = 64, 64
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            width,
            height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            textureData,
        )
        print("Usando textura branca padrão.")
        return

    try:
        textureSurface = pygame.image.load(filename)
        # Converte a superfície Pygame para uma string de bytes RGBA que o OpenGL entende
        # O '1' no final inverte a imagem verticalmente, pois Pygame e OpenGL têm origens Y diferentes
        textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
        width = textureSurface.get_width()
        height = textureSurface.get_height()

        texture_id = glGenTextures(1)  # Gera um ID para a textura
        glBindTexture(GL_TEXTURE_2D, texture_id)  # Ativa a textura recém-criada

        # Define como a textura deve ser filtrada (LINEAR para suavização)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # Usa mipmaps para melhor qualidade quando a textura é vista de longe
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        # Define como a textura se repete fora das coordenadas [0, 1]
        glTexParameteri(
            GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT
        )  # Repete horizontalmente
        glTexParameteri(
            GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT
        )  # Repete verticalmente

        # Envia os dados da textura para a GPU e gera mipmaps automaticamente
        gluBuild2DMipmaps(
            GL_TEXTURE_2D,
            GL_RGBA,
            width,
            height,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            textureData,
        )

        print(f"Textura '{filename}' carregada com sucesso (ID: {texture_id}).")

    except Exception as e:
        print(f"Erro ao carregar textura '{filename}': {e}")
        texture_id = None  # Garante que texture_id seja None se o carregamento falhar


def initialise():
    """Configura o estado inicial do OpenGL."""
    global texture_id
    glClearColor(
        background_color[0],
        background_color[1],
        background_color[2],
        background_color[3],
    )

    # --- Configuração da Projeção ---
    glMatrixMode(GL_PROJECTION)  # Seleciona a matriz de projeção
    glLoadIdentity()  # Reseta a matriz
    # Define a perspectiva 
    gluPerspective(60, (screen_width / screen_height), 0.1, 100.0)

    # --- Configuração da Visão/Modelo (Modelview) ---
    glMatrixMode(GL_MODELVIEW)  # Seleciona a matriz de modelo/visão
    glLoadIdentity()  # Reseta a matriz
    # Define a área da janela onde o OpenGL vai desenhar (janela inteira aqui)
    glViewport(0, 0, screen.get_width(), screen.get_height())
    # Habilita o teste de profundidade para que objetos na frente ocultem os de trás
    glEnable(GL_DEPTH_TEST)
    # Habilita oclusão de face traseira (melhora performance, opcional)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    # --- Configuração da Iluminação ---
    glEnable(GL_LIGHTING)  # Habilita o cálculo de iluminação
    glEnable(GL_LIGHT0)  # Habilita a fonte de luz 0
    # Permite que chamadas glColor() afetem as propriedades do material (conveniente)
    glEnable(GL_COLOR_MATERIAL)
    # Define que glColor afeta as cores ambiente e difusa do material
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # Propriedades da Fonte de luz
    light_position = (5.0, 5.0, 5.0, 1.0)  # origem 
    light_ambient = (0.2, 0.2, 0.2, 1.0)  # ambiente 
    light_diffuse = (0.8, 0.8, 0.8, 1.0)  # principal
    light_specular = (0.6, 0.6, 0.6, 1.0)  # brilho

    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    # Propriedades do Material do Cubo 
    mat_specular = (1.0, 1.0, 1.0, 1.0)  #  brilho
    mat_shininess = 50.0  # nivel brilho

    # Define a cor do brilho e a intensidade para as faces frontais
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, mat_shininess)

    # Define um modelo de luz ambiente global 
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.2, 0.2, 0.2, 1.0))

    # --- Carregar Textura ---
    load_texture(texture_file)

    # --- Posição Inicial da Câmera ---
    # Afasta a câmera 5 unidades no eixo Z para ver o cubo na origem
    glTranslate(0.0, 0.0, -5.0)


def display():
    """Função principal de desenho."""
    global rotate_x, rotate_y, rotate_z

    # Limpa os buffers de cor e profundidade
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Reseta a matriz de modelo/visão para a posição da câmera
    glLoadIdentity()
    glTranslate(0.0, 0.0, -5.0)  # Reposiciona a câmera

    # --- Posição da Luz ---
    # Luz que acompanha a câmera:
    glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 2.0, 2.0, 1.0)) # Posição relativa à câmera

    # --- Rotação Automática ---
    rotate_x = (rotate_x + 0.5) % 360  # Incrementa e limita a 360 graus
    rotate_y = (rotate_y + 0.4) % 360
    rotate_z = (rotate_z + 0.3) % 360

    # --- Aplica as Transformações Interativas ---
    glPushMatrix()  # Salva o estado atual da matriz (posição da câmera)

    # 1. Translação
    glTranslatef(translation_x, translation_y, translation_z)
    # 2. Rotação (padronizada)
    glRotatef(rotate_x, 1, 0, 0)
    glRotatef(rotate_y, 0, 1, 0)
    glRotatef(rotate_z, 0, 0, 1)
    # 3. Espelhamento 
    glScalef(mirror_x, mirror_y, mirror_z)
    # 4. Escala
    glScalef(scale_factor, scale_factor, scale_factor)

    # --- Desenha o Cubo ---
    if texture_id is not None:
        glEnable(GL_TEXTURE_2D)  # Habilita texturização
        glBindTexture(GL_TEXTURE_2D, texture_id)  # Seleciona a textura carregada
    else:
        glDisable(GL_TEXTURE_2D)  # Garante que texturização está desligada se falhou

    # Define a cor base do material, neutra no caso
    glColor4f(1.0, 1.0, 1.0, 1.0)

    # Chama a função que desenha o cubo 
    texturedLitCube()

    # Desabilita texturização após desenhar o objeto
    glDisable(GL_TEXTURE_2D)

    glPopMatrix()  # Restaura a matriz para o estado antes das transformações do cubo


def toggle_transform(transform_type):
    """Ativa/Desativa um modo de transformação."""
    global translate_active, scale_active, mirror_active
    # Desativa todos primeiro para garantir apenas um ativo

    if transform_type == "translate":
        translate_active = not translate_active
        scale_active = False
        mirror_active = False
    elif transform_type == "scale":
        scale_active = not scale_active
        translate_active = False
        mirror_active = False
    elif transform_type == "mirror":
        mirror_active = not mirror_active
        translate_active = False
        scale_active = False
    print(
        f"Translate: {translate_active}, Scale: {scale_active}, Mirror: {mirror_active}"
    )


def reset_cube():
    """Reseta todos os parâmetros de transformação"""
    global translation_x, translation_y, translation_z, scale_factor
    global mirror_x, mirror_y, mirror_z, rotate_x, rotate_y, rotate_z

    translation_x = 0.0
    translation_y = 0.0
    translation_z = 0.0
    scale_factor = 1.0
    mirror_x = 1.0
    mirror_y = 1.0
    mirror_z = 1.0
    rotate_x = 0
    rotate_y = 0
    rotate_z = 0
    print("Cubo resetado.")


def draw_text_overlay():
    """Desenha informações 2D sobre a cena 3D."""
    # Cria uma superfície Pygame transparente para desenhar o texto
    text_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    text_surface.fill((0, 0, 0, 0))  # Preenche com transparente

    # --- Renderiza as linhas de texto ---
    y_pos = 20
    line_height = 25
    text_color = (230, 230, 230)  # Cor principal do texto
    highlight_color = (255, 255, 0)  # Cor para modos ativos
    value_color = (180, 255, 180)  # Cor para valores numéricos

    # Título
    title_text = font.render("Transformações Geométricas 3D", True, text_color)
    text_surface.blit(title_text, (20, y_pos))
    y_pos += line_height * 2

    # Modos ativos
    modes = []
    if translate_active:
        modes.append("Translação")
    if scale_active:
        modes.append("Escala")
    if mirror_active:
        modes.append("Espelhamento")
    modes_text = "Modo Ativo: " + (", ".join(modes) if modes else "Nenhum")
    mode_render = font.render(modes_text, True, highlight_color)
    text_surface.blit(mode_render, (20, y_pos))
    y_pos += line_height * 1.5

    # Estado atual das transformações
    trans_text = f"Translação: X={translation_x:.1f}, Y={translation_y:.1f}, Z={translation_z:.1f}"
    scale_text = f"Escala: {scale_factor:.2f}"
    mirror_text = (
        f"Espelhamento: X={'Inv' if mirror_x < 0 else 'Norm'}, "
        + f"Y={'Inv' if mirror_y < 0 else 'Norm'}, "
        + f"Z={'Inv' if mirror_z < 0 else 'Norm'}"
    )

    text_surface.blit(font.render(trans_text, True, value_color), (20, y_pos))
    y_pos += line_height
    text_surface.blit(font.render(scale_text, True, value_color), (20, y_pos))
    y_pos += line_height
    text_surface.blit(font.render(mirror_text, True, value_color), (20, y_pos))
    y_pos += line_height * 2

    # Instruções
    instructions = [
        "COMANDOS:",
        "1: Modo Translação (Setas + Z/X)",
        "2: Modo Escala (Setas/Z/X)",
        "3: Modo Espelhamento (Setas/Z/X - Inverte)",
        "R: Resetar Cubo",
        "ESC: Sair",
    ]
    for instruction in instructions:
        instr_render = font.render(instruction, True, text_color)
        text_surface.blit(instr_render, (20, y_pos))
        y_pos += line_height

    # --- Desenha a superfície de texto como uma textura sobre a cena ---
    # Salva o estado atual do OpenGL (iluminação, profundidade, matrizes, etc.)
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glDisable(GL_LIGHTING)  # Desabilita iluminação para o 2D
    glDisable(GL_DEPTH_TEST)  # Desabilita teste de profundidade
    glDisable(GL_CULL_FACE)  # Desabilita culling para o quad 2D

    # Configura matrizes para desenho 2D 
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()  # Salva matriz de projeção 3D
    glLoadIdentity()
    glOrtho(0, screen_width, screen_height, 0, -1, 1) 
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()  # Salva matriz 
    glLoadIdentity()  # Reseta para desenho 2D

    # Converte a superfície Pygame para textura OpenGL
    texture_data = pygame.image.tostring(text_surface, "RGBA", 0)  # 0 = sem inversão Y
    overlay_texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, overlay_texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        screen_width,
        screen_height,
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        texture_data,
    )

    # Habilita texturização e blending para transparência
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # Blending padrão para alpha

    # Desenha um quadrilátero cobrindo toda a tela com a textura do texto
    glColor4f(1.0, 1.0, 1.0, 1.0)  # Cor branca para não tingir a textura
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(0, 0)  # Topo-Esquerda
    glTexCoord2f(1, 0)
    glVertex2f(screen_width, 0)  # Topo-Direita
    glTexCoord2f(1, 1)
    glVertex2f(screen_width, screen_height)  # Base-Direita
    glTexCoord2f(0, 1)
    glVertex2f(0, screen_height)  # Base-Esquerda
    glEnd()

    # Limpa e restaura o estado do OpenGL
    glDisable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)
    glDeleteTextures(1, [overlay_texture_id])  # Libera a textura do overlay

    # Restaura as matrizes
    glPopMatrix()  # Restaura modelview
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()  # Restaura projection
    glMatrixMode(GL_MODELVIEW)

    # Restaura outros atributos (iluminação, profundidade, etc.)
    glPopAttrib()


# --- Loop Principal ---
done = False
initialise()  # Chama a função de inicialização
clock = pygame.time.Clock()  # Objeto para controlar os frames por segundo

print("Aplicação iniciada. Pressione ESC para sair.")

while not done:
    # --- Processamento de Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:  # Tecla ESC para sair
                done = True
            # --- Controle de Modos ---
            elif event.key == K_1:
                toggle_transform("translate")
            elif event.key == K_2:
                toggle_transform("scale")
            elif event.key == K_3:
                toggle_transform("mirror")
            elif event.key == K_r:
                reset_cube()

            # --- Controle de Espelhamento (ação única no keydown) ---
            if mirror_active:
                if event.key == K_RIGHT or event.key == K_LEFT:
                    mirror_x *= -1
                    print(f"Mirror X: {mirror_x}")
                elif event.key == K_UP or event.key == K_DOWN:
                    mirror_y *= -1
                    print(f"Mirror Y: {mirror_y}")
                elif event.key == K_z or event.key == K_x:
                    mirror_z *= -1
                    print(f"Mirror Z: {mirror_z}")

    # --- Verificação Contínua de Teclas Pressionadas ---
    keys = pygame.key.get_pressed()
    move_speed = 0.05  # Velocidade de translação
    scale_speed = 0.01  # Velocidade de escala

    # --- Controle de Translação ---
    if translate_active:
        if keys[K_RIGHT]:
            translation_x += move_speed
        if keys[K_LEFT]:
            translation_x -= move_speed
        if keys[K_UP]:
            translation_y += move_speed
        if keys[K_DOWN]:
            translation_y -= move_speed
        if keys[K_z]:
            translation_z += move_speed  # Z aumenta para "dentro" da tela
        if keys[K_x]:
            translation_z -= move_speed  # X diminui para "fora" da tela

    # --- Controle de Escala ---
    if scale_active:
        if keys[K_UP] or keys[K_RIGHT] or keys[K_z]:
            scale_factor += scale_speed
        if keys[K_DOWN] or keys[K_LEFT] or keys[K_x]:
            # Garante que a escala não fique menor que 0.1
            scale_factor = max(0.1, scale_factor - scale_speed)

    # --- Desenho ---
    display()  # Desenha a cena 3D
    draw_text_overlay()  # Desenha a interface 2D por cima

    # --- Atualização da Tela ---
    pygame.display.flip()  # padrão do pygame para atualizar a tela
    clock.tick(60)  # Limita o loop a 60 frames por segundo

# --- Finalização ---
pygame.quit()
print("Aplicação finalizada.")
