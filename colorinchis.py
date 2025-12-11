import pygame
import sys

# Inicializar Pygame
pygame.init()

# Configuración
ANCHO = 600
ALTO = 700
TAMAÑO_CELDA = 200
LINEA_ANCHO = 15
CIRCULO_RADIO = TAMAÑO_CELDA // 2 - LINEA_ANCHO
CRUZ_ESPACIO = TAMAÑO_CELDA // 4
CRUZ_ANCHO = 25
ESPACIO = 50

# Colores
BLANCO = (255, 255, 255)
GRIS = (28, 170, 156)
GRIS_CLARO = (200, 200, 200)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
NEGRO = (0, 0, 0)

# Pantalla
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Tateti - Tres en Raya")
pantalla.fill(GRIS)

# Reloj
reloj = pygame.time.Clock()

# Tablero (0 = vacío, 1 = jugador X, 2 = IA O)
tablero = [[0, 0, 0],
           [0, 0, 0],
           [0, 0, 0]]

# Variables del juego
turno = 1  # 1 = Jugador, 2 = IA
juego_terminado = False
ganador = None

def dibujar_lineas():
    """Dibuja las líneas del tablero"""
    # Líneas horizontales
    pygame.draw.line(pantalla, BLANCO, (0, TAMAÑO_CELDA), (ANCHO, TAMAÑO_CELDA), LINEA_ANCHO)
    pygame.draw.line(pantalla, BLANCO, (0, 2 * TAMAÑO_CELDA), (ANCHO, 2 * TAMAÑO_CELDA), LINEA_ANCHO)
    
    # Líneas verticales
    pygame.draw.line(pantalla, BLANCO, (TAMAÑO_CELDA, 0), (TAMAÑO_CELDA, 3 * TAMAÑO_CELDA), LINEA_ANCHO)
    pygame.draw.line(pantalla, BLANCO, (2 * TAMAÑO_CELDA, 0), (2 * TAMAÑO_CELDA, 3 * TAMAÑO_CELDA), LINEA_ANCHO)

def dibujar_figuras():
    """Dibuja las X y O en el tablero"""
    fuente = pygame.font.Font(None, 120)
    
    for fila in range(3):
        for col in range(3):
            if tablero[fila][col] == 1:  # Jugador (X)
                texto = fuente.render("X", True, AZUL)
                x = col * TAMAÑO_CELDA + TAMAÑO_CELDA // 2 - 30
                y = fila * TAMAÑO_CELDA + TAMAÑO_CELDA // 2 - 60
                pantalla.blit(texto, (x, y))
            elif tablero[fila][col] == 2:  # IA (O)
                texto = fuente.render("O", True, ROJO)
                x = col * TAMAÑO_CELDA + TAMAÑO_CELDA // 2 - 30
                y = fila * TAMAÑO_CELDA + TAMAÑO_CELDA // 2 - 60
                pantalla.blit(texto, (x, y))

def dibujar_estado():
    """Dibuja el estado del juego"""
    fuente = pygame.font.Font(None, 40)
    
    if juego_terminado:
        if ganador == 1:
            texto = fuente.render("¡Ganaste!", True, AZUL)
        elif ganador == 2:
            texto = fuente.render("¡Perdiste!", True, ROJO)
        else:
            texto = fuente.render("¡Empate!", True, NEGRO)
        pantalla.blit(texto, (150, 3 * TAMAÑO_CELDA + 20))
        
        # Botón para reiniciar
        fuente_chica = pygame.font.Font(None, 30)
        reinicio_texto = fuente_chica.render("Presiona R para reiniciar", True, NEGRO)
        pantalla.blit(reinicio_texto, (120, 3 * TAMAÑO_CELDA + 80))
    else:
        if turno == 1:
            texto = fuente.render("Tu turno (X)", True, AZUL)
        else:
            texto = fuente.render("IA jugando (O)...", True, ROJO)
        pantalla.blit(texto, (150, 3 * TAMAÑO_CELDA + 20))

def marcar_celda(fila, col, jugador):
    """Marca una celda en el tablero"""
    if tablero[fila][col] == 0:
        tablero[fila][col] = jugador
        return True
    return False

def verificar_ganador():
    """Verifica si hay un ganador"""
    # Verificar filas
    for fila in range(3):
        if tablero[fila][0] == tablero[fila][1] == tablero[fila][2] != 0:
            return tablero[fila][0]
    
    # Verificar columnas
    for col in range(3):
        if tablero[0][col] == tablero[1][col] == tablero[2][col] != 0:
            return tablero[0][col]
    
    # Verificar diagonales
    if tablero[0][0] == tablero[1][1] == tablero[2][2] != 0:
        return tablero[0][0]
    
    if tablero[0][2] == tablero[1][1] == tablero[2][0] != 0:
        return tablero[0][2]
    
    return None

def tablero_lleno():
    """Verifica si el tablero está lleno"""
    for fila in tablero:
        if 0 in fila:
            return False
    return True

def movimiento_ia():
    """IA juega - intenta ganar, bloquea al jugador o elige celda al azar"""
    
    # Intentar ganar
    for fila in range(3):
        for col in range(3):
            if tablero[fila][col] == 0:
                tablero[fila][col] = 2
                if verificar_ganador() == 2:
                    return
                tablero[fila][col] = 0
    
    # Bloquear al jugador
    for fila in range(3):
        for col in range(3):
            if tablero[fila][col] == 0:
                tablero[fila][col] = 1
                if verificar_ganador() == 1:
                    tablero[fila][col] = 2
                    return
                tablero[fila][col] = 0
    
    # Elegir celda al azar
    celdas_libres = []
    for fila in range(3):
        for col in range(3):
            if tablero[fila][col] == 0:
                celdas_libres.append((fila, col))
    
    if celdas_libres:
        import random
        fila, col = random.choice(celdas_libres)
        tablero[fila][col] = 2

def reiniciar_juego():
    """Reinicia el juego"""
    global tablero, turno, juego_terminado, ganador
    tablero = [[0, 0, 0],
               [0, 0, 0],
               [0, 0, 0]]
    turno = 1
    juego_terminado = False
    ganador = None

# Bucle principal
corriendo = True
while corriendo:
    reloj.tick(60)
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False
        
        if evento.type == pygame.MOUSEBUTTONDOWN and turno == 1 and not juego_terminado:
            x = evento.pos[0] // TAMAÑO_CELDA
            y = evento.pos[1] // TAMAÑO_CELDA
            
            if x < 3 and y < 3:
                if marcar_celda(y, x, 1):
                    ganador = verificar_ganador()
                    
                    if ganador or tablero_lleno():
                        juego_terminado = True
                    else:
                        turno = 2
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                reiniciar_juego()
    
    # Turno de la IA
    if turno == 2 and not juego_terminado:
        movimiento_ia()
        ganador = verificar_ganador()
        
        if ganador or tablero_lleno():
            juego_terminado = True
        else:
            turno = 1
    
    # Dibujar
    pantalla.fill(GRIS)
    dibujar_lineas()
    dibujar_figuras()
    dibujar_estado()
    
    pygame.display.update()

pygame.quit()
sys.exit()
