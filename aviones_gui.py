"""
Aviones - Interfaz gráfica (Tkinter)

Ejecuta: `python aviones_gui.py`

Ventajas:
- Tablero enemigo clickable (haz clic para disparar).
- Vista simple del tablero propio con posiciones de tus aviones y marcas.
- CPU realiza tiros aleatorios.

Nota: usa la misma lógica básica que la versión CLI pero con GUI.
"""

import tkinter as tk
from tkinter import messagebox
import random
import string


def create_board(size):
    return [["." for _ in range(size)] for _ in range(size)]


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


def all_ships_sunk(board):
    for row in board:
        if 'A' in row:
            return False
    return True


def take_shot(target_board, view_board, r, c):
    # view_board es para el que dispara (lo que ya ha visto)
    if view_board[r][c] != '.':
        return False, 'repetido'
    if target_board[r][c] == 'A':
        target_board[r][c] = 'X'
        view_board[r][c] = 'X'
        return True, 'impacto'
    else:
        view_board[r][c] = 'o'
        return True, 'agua'


def cpu_choose_shot(seen):
    size = len(seen)
    candidates = [(r, c) for r in range(size) for c in range(size) if seen[r][c] == '.']
    return random.choice(candidates) if candidates else None


class AvionesGUI:
    def __init__(self, master, size=8, ships=None):
        self.master = master
        self.size = size
        self.ships = ships if ships is not None else [4, 3, 3, 2]

        self.player_board = create_board(size)
        self.cpu_board = create_board(size)
        place_fleet_random(self.player_board, self.ships)
        place_fleet_random(self.cpu_board, self.ships)

        self.enemy_view = create_board(size)  # lo que el jugador ve del enemigo
        self.player_seen = create_board(size)  # lo que el CPU ve del jugador

        self.buttons = [[None for _ in range(size)] for _ in range(size)]
        self.player_labels = [[None for _ in range(size)] for _ in range(size)]

        self.turn = 'player'
        self.setup_ui()

    def setup_ui(self):
        self.master.title('Aviones - GUI')

        top_frame = tk.Frame(self.master)
        top_frame.pack(padx=8, pady=8)

        # Enemy grid (click to shoot)
        enemy_frame = tk.LabelFrame(top_frame, text='Enemigo (haz clic para disparar)')
        enemy_frame.grid(row=0, column=0, padx=8)

        letters = string.ascii_uppercase[:self.size]
        # column labels
        for c, letter in enumerate(letters):
            tk.Label(enemy_frame, text=letter).grid(row=0, column=c+1)
        for r in range(self.size):
            tk.Label(enemy_frame, text=str(r+1)).grid(row=r+1, column=0)
            for c in range(self.size):
                b = tk.Button(enemy_frame, text='.', width=2, command=lambda rr=r, cc=c: self.player_shoot(rr, cc))
                b.grid(row=r+1, column=c+1)
                self.buttons[r][c] = b

        # Player board view
        player_frame = tk.LabelFrame(top_frame, text='Tu tablero')
        player_frame.grid(row=0, column=1, padx=8)
        for c, letter in enumerate(letters):
            tk.Label(player_frame, text=letter).grid(row=0, column=c+1)
        for r in range(self.size):
            tk.Label(player_frame, text=str(r+1)).grid(row=r+1, column=0)
            for c in range(self.size):
                label = tk.Label(player_frame, text=self.player_board[r][c] if self.player_board[r][c] == 'A' else '.', width=2, borderwidth=1, relief='solid')
                label.grid(row=r+1, column=c+1)
                self.player_labels[r][c] = label

        # Controls
        ctrl_frame = tk.Frame(self.master)
        ctrl_frame.pack(pady=6)
        self.msg = tk.StringVar()
        self.msg.set('Tu turno: haz clic en el tablero enemigo.')
        tk.Label(ctrl_frame, textvariable=self.msg).pack()

        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=4)
        tk.Button(btn_frame, text='Reiniciar', command=self.reset).pack(side='left', padx=6)
        tk.Button(btn_frame, text='Mostrar flotas (depuración)', command=self.debug_show).pack(side='left')

    def player_shoot(self, r, c):
        if self.turn != 'player':
            return
        ok, result = take_shot(self.cpu_board, self.enemy_view, r, c)
        if not ok and result == 'repetido':
            self.msg.set('Ya disparaste ahí, elige otra casilla.')
            return

        btn = self.buttons[r][c]
        if result == 'impacto':
            btn.config(text='X', bg='red', state='disabled')
            self.msg.set(f'Impacto en {string.ascii_uppercase[c]}{r+1}! Dispara otra vez.')
            if all_ships_sunk(self.cpu_board):
                self.end_game(win=True)
            return
        else:
            btn.config(text='o', bg='light blue', state='disabled')
            self.msg.set('Agua. Turno del CPU...')
            self.turn = 'cpu'
            # dar tiempo visual antes del tiro del CPU
            self.master.after(700, self.cpu_turn)

    def cpu_turn(self):
        shot = cpu_choose_shot(self.player_seen)
        if shot is None:
            messagebox.showinfo('Empate', 'No quedan tiros. Empate técnico.')
            return
        r, c = shot
        ok, result = take_shot(self.player_board, self.player_seen, r, c)
        # Actualizar vista del jugador
        label = self.player_labels[r][c]
        if result == 'impacto':
            label.config(text='X', bg='red')
            self.msg.set(f'CPU impactó en {string.ascii_uppercase[c]}{r+1}! CPU dispara otra vez.')
            if all_ships_sunk(self.player_board):
                self.end_game(win=False)
                return
            # CPU dispara otra vez con pequeño delay
            self.master.after(700, self.cpu_turn)
            return
        else:
            label.config(text='o', bg='light blue')
            self.msg.set('CPU falló. Tu turno.')
            self.turn = 'player'

    def end_game(self, win=True):
        if win:
            self.msg.set('¡Ganaste! Hundiste todos los aviones enemigos.')
            messagebox.showinfo('Victoria', '¡Felicidades! Ganaste.')
        else:
            self.msg.set('Perdiste. El CPU hundió tu flota.')
            messagebox.showinfo('Derrota', 'Has perdido. El CPU ganó.')
        # deshabilitar botones
        for r in range(self.size):
            for c in range(self.size):
                if self.buttons[r][c]:
                    self.buttons[r][c].config(state='disabled')

    def reset(self):
        self.player_board = create_board(self.size)
        self.cpu_board = create_board(self.size)
        place_fleet_random(self.player_board, self.ships)
        place_fleet_random(self.cpu_board, self.ships)
        self.enemy_view = create_board(self.size)
        self.player_seen = create_board(self.size)
        self.turn = 'player'
        for r in range(self.size):
            for c in range(self.size):
                b = self.buttons[r][c]
                b.config(text='.', bg='SystemButtonFace', state='normal')
                label = self.player_labels[r][c]
                label.config(text=self.player_board[r][c] if self.player_board[r][c] == 'A' else '.', bg='SystemButtonFace')
        self.msg.set('Juego reiniciado. Tu turno.')

    def debug_show(self):
        # Revela la flota enemiga (solo para depuración)
        for r in range(self.size):
            for c in range(self.size):
                if self.cpu_board[r][c] == 'A' and self.enemy_view[r][c] == '.':
                    self.buttons[r][c].config(text='A', bg='gray')


def main():
    root = tk.Tk()
    app = AvionesGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
