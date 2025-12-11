"""
Juego de Aviones (versión CLI simple)

Cómo jugar:
- Ejecuta: `python aviones.py`
- El tablero es de 8x8. Las columnas usan letras A-H, las filas números 1-8.
- Introduce coordenadas para disparar: por ejemplo `A5` o `5 1` (fila columna).
- El objetivo: hundir todos los aviones del CPU.

Controles mínimos y diseño:
- El CPU y el jugador tienen flotas con varios aviones (representados como barcos).
- Para simplificar, la colocación es aleatoria para ambos.

Autor: generado por asistente
"""

import random
import string
import sys


def create_board(size):
	return [["." for _ in range(size)] for _ in range(size)]


def print_boards(player_board, enemy_view):
	size = len(player_board)
	letters = string.ascii_uppercase[:size]
	# Enemy view (what player sees of enemy)
	print("\nTablero enemigo (tus disparos):")
	print("   " + " ".join(letters))
	for i in range(size):
		row = enemy_view[i]
		print(f"{i+1:2} " + " ".join(row))

	# Player board (your ships + enemy hits)
	print("\nTu tablero:")
	print("   " + " ".join(letters))
	for i in range(size):
		row = player_board[i]
		print(f"{i+1:2} " + " ".join(row))


def positions_for_ship(start_r, start_c, length, orientation):
	if orientation == 'H':
		return [(start_r, start_c + i) for i in range(length)]
	else:
		return [(start_r + i, start_c) for i in range(length)]


def can_place(board, start_r, start_c, length, orientation):
	size = len(board)
	for r, c in positions_for_ship(start_r, start_c, length, orientation):
		if r < 0 or c < 0 or r >= size or c >= size:
			return False
		if board[r][c] != '.':
			return False
	return True


def place_ship(board, length):
	size = len(board)
	attempts = 0
	while True:
		orientation = random.choice(['H', 'V'])
		if orientation == 'H':
			r = random.randrange(0, size)
			c = random.randrange(0, size - length + 1)
		else:
			r = random.randrange(0, size - length + 1)
			c = random.randrange(0, size)

		if can_place(board, r, c, length, orientation):
			for rr, cc in positions_for_ship(r, c, length, orientation):
				board[rr][cc] = 'A'
			return

		attempts += 1
		if attempts > 1000:
			raise RuntimeError("No se pudo colocar el barco después de muchos intentos")


def place_fleet_random(board, ships):
	for length in ships:
		place_ship(board, length)


def parse_coord(s, size):
	s = s.strip().upper()
	# Formato letra+numero, p.ej. A5
	if len(s) >= 2 and s[0].isalpha():
		col = s[0]
		row_part = s[1:].strip()
		if col in string.ascii_uppercase[:size] and row_part.isdigit():
			r = int(row_part) - 1
			c = string.ascii_uppercase.index(col)
			if 0 <= r < size:
				return r, c
	# Formato número espacio número "fila col"
	parts = s.replace(',', ' ').split()
	if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
		r = int(parts[0]) - 1
		c = int(parts[1]) - 1
		if 0 <= r < size and 0 <= c < size:
			return r, c
	return None


def all_ships_sunk(board):
	for row in board:
		if 'A' in row:
			return False
	return True


def take_shot(target_board, view_board, r, c):
	if view_board[r][c] != '.':
		return False, "repetido"

	if target_board[r][c] == 'A':
		target_board[r][c] = 'X'
		view_board[r][c] = 'X'
		return True, "impacto"
	else:
		view_board[r][c] = 'o'
		return True, "agua"


def cpu_choose_shot(seen):
	size = len(seen)
	candidates = [(r, c) for r in range(size) for c in range(size) if seen[r][c] == '.']
	return random.choice(candidates) if candidates else None


def main():
	size = 8
	ships = [4, 3, 3, 2]

	player_board = create_board(size)
	cpu_board = create_board(size)

	# Place fleets
	place_fleet_random(player_board, ships)
	place_fleet_random(cpu_board, ships)

	# Boards for tracking shots
	enemy_view = create_board(size)  # what player sees of enemy
	player_seen = create_board(size)  # what CPU sees of player

	print("Bienvenido a Aviones (modo terminal). ¡A jugar!")

	turn = 'player'
	while True:
		print_boards(player_board, enemy_view)

		if turn == 'player':
			inp = input("Ingresa coordenada (ej. A5 o 5 1) o 'q' para salir: ")
			if inp.lower() in ('q', 'salir', 'exit'):
				print("Gracias por jugar. Hasta luego.")
				sys.exit(0)
			coord = parse_coord(inp, size)
			if coord is None:
				print("Entrada no válida. Usa A5 o 'fila columna' (ej. 5 1).")
				continue
			r, c = coord
			ok, result = take_shot(cpu_board, enemy_view, r, c)
			if not ok and result == 'repetido':
				print("Ya disparaste ahí. Intenta otra coordenada.")
				continue
			print(f"Has {result} en {inp.upper()}.")
			if all_ships_sunk(cpu_board):
				print("¡Felicidades! Hundiste todos los aviones enemigos.")
				print_boards(player_board, enemy_view)
				break
			if result == 'impacto':
				# same player continues after hit
				print("Impacto! Puedes disparar otra vez.")
				continue
			else:
				turn = 'cpu'

		else:
			# CPU turn
			shot = cpu_choose_shot(player_seen)
			if shot is None:
				print("CPU no tiene más tiros, empate técnico.")
				break
			r, c = shot
			ok, result = take_shot(player_board, player_seen, r, c)
			coord_name = f"{string.ascii_uppercase[c]}{r+1}"
			print(f"CPU dispara en {coord_name}: {result}.")
			if all_ships_sunk(player_board):
				print("Has perdido. El CPU hundió todos tus aviones.")
				print_boards(player_board, enemy_view)
				break
			if result == 'impacto':
				# CPU gets another shot
				continue
			else:
				turn = 'player'


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("\nJuego interrumpido. Hasta luego.")

