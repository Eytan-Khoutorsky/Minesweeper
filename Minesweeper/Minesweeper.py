import tkinter as tk
from tkinter import messagebox
import random

### cell class ###
class Cell:
    #Represets oe square on the board
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0

### board class (game logic) ###
class Board:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.grid = [[Cell(r,c) for c in range(cols)] for r in range(rows)]
        self.first_click = True
        self.remaining_cells = rows*cols - mines

    def place_mines(self, first_row, first_col):
        #places mines everywhere except the first clicked cell
        positions = [(r,c) for r in range(self.rows) for c in range(self.cols) if not (first_row == r and first_col == c)]
        for (r,c) in random.sample(positions, self.mines):
            self.grid[r][c].is_mine = True

        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c].adjacent_mines = self.count_adjacent_mines(r,c)

    def count_adjacent_mines(self,r,c):
        #counts the adjacent mines number for every cell
        count = 0
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.grid[nr][nc].is_mine:
                        count+=1
        return count

    
    def reveal(self, r, c):
        #Handle cases of flagged/revealed, first click, and mine
        cell = self.grid[r][c]
        if cell.is_flagged or cell.is_revealed:
            return True
        if self.first_click:
            self.place_mines(r,c)
            self.first_click = False
        if cell.is_mine:
            return False

        #if safe cell
        cell.is_revealed = True
        self.remaining_cells -= 1

        #recursively reveals cells for empty cells
        if cell.adjacent_mines == 0:
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if not self.grid[nr][nc].is_revealed:
                            self.reveal(nr,nc)
        return True

    def toggle_flag(self,r,c):
        #toggles the flag
        cell = self.grid[r][c]
        if not cell.is_revealed:
            cell.is_flagged = not cell.is_flagged #opposite of current condition

    def check_win(self):
        #checks if all safe cells are revealed
        return self.remaining_cells == 0


### game class (UI + interaction) ###
class Game:
    def __init__(self, master, rows=15, cols=15, mines=20):
        self.master = master
        self.frame = tk.Frame(master)
        self.frame.pack()
        self.board = Board(rows, cols, mines)
        self.buttons = [[None for x in range(cols)] for y in range(rows)]
        self.create_ui(rows,cols)
        self.game_active = True
        
        
    def create_ui(self,rows,cols):
        #creates each button and binds them to left and right click
        for r in range(rows):
            for c in range(cols):
                btn = tk.Button(self.frame, width=3, height=1, command=lambda r=r, c=c: self.left_click(r,c))
                btn.bind("<Button-3>", lambda event, r=r, c=c: self.right_click(r,c))
                
                btn.grid(row=r, column=c)
                self.buttons[r][c] = btn

    def left_click(self,r,c):
        #ignores if game has already ended
        if not self.game_active:
            return
        #tries to reveal the cell
        if not self.board.reveal(r,c):
            self.show_mines()
            self.game_over(" You hit a mine! Game over.)")
        self.update_ui()
        #checks if all safe cells are revealed
        if self.board.check_win():
            self.game_over(" You win!")

    def right_click(self, r, c):
        #toggles flag on right click
        if not self.game_active:
            return
        self.board.toggle_flag(r,c)
        self.update_ui()

    def update_ui(self):
        #toggles all buttons to reflect game state
        if not self.game_active:
            return
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                cell = self.board.grid[r][c]
                btn = self.buttons[r][c]


                if cell.is_revealed:
                    btn.config(state=tk.DISABLED, relief=tk.SUNKEN)
                    if cell.adjacent_mines > 0:
                        btn.config(text=str(cell.adjacent_mines))
                    else:
                        btn.config(text="")
                elif cell.is_flagged:
                    btn.config(text="F")
                else:
                    btn.config(text="")
                    
                    

    def show_mines(self):
        #reveals all mines when the player loses
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.grid[r][c].is_mine:
                    self.buttons[r][c].config(text="*")

    def game_over(self, message):
        #disables the game and shows win/lose message
        self.game_active = False
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                self.buttons[r][c].config(state=tk.DISABLED)
        messagebox.showinfo("Minesweeper", message)
        #restart option

        if messagebox.askyesno("Play Again?", "Do you want to play again?"):
            self.frame.destroy()
            difficulty_screen(self.master)
        else:
            self.master.destroy()
            

### Difficulty selection screen ###
def difficulty_screen(root):
    menu = tk.Frame(root)
    menu.pack()
    
    tk.Label(menu, text="Select Difficulty", font=("Arial", 16)).pack(pady=10)

    def start(rows, cols, mines):
        menu.destroy()
        Game(root, rows, cols, mines)

    tk.Button(menu, text="Easy (8x8, 10 mines)", width=25, command=lambda: start(8,8,10)).pack(pady=5)
    tk.Button(menu, text="Medium (15x15, 20 mines)", width=25, command=lambda: start(15,15,20)).pack(pady=5)

    tk.Button(menu, text="Hard (20x20, 40 mines)", width=25, command=lambda: start(20,20,40)).pack(pady=5)
        
        
        


#program start                       
root = tk.Tk()
root.title("Minesweeper")
difficulty_screen(root)
root.mainloop()


