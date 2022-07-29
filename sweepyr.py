from tkinter import *
from tkinter.font import Font
from tkinter.messagebox import *
from functools import partial
import random


class Tile:
    def __init__(self):
        self.cleared = False
        self.flagged = False
        self.mine = False
        self.n_adj = 0
        self.label = None # Label object for quick access
    
    # Reveal tile, return True if mine revealed
    def reveal(self):
        if self.flagged or self.cleared:
            return False
        
        self.cleared = True
        return self.mine
    
    # Flag tile, return change in flag number
    def flag(self):
        if not self.cleared:
            self.flagged = not self.flagged
            return -1 if self.flagged else 1
        return 0
    
    # Plant a mine in this tile, return if operation happenned successfully
    def plant(self):
        if self.mine:
            return False
        self.mine = True
        return True
    
    # Representation of the tile
    def __str__(self):
        if self.mine:
            return "*"
        
        if self.n_adj == 0:
            return ""
        
        return str(self.n_adj)
    
    # Color of the tile's number
    def color(self):
        if self.mine:
            return "black"
        
        c = {
            1: "blue",
            2: "green",
            3: "red",
            4: "indigo",
            5: "maroon",
            6: "cyan",
            7: "gray7",
            8: "yellow"
        }
        
        return c.get(self.n_adj, "black")


class Board:
    def __init__(self, n_rows=7, n_cols=7, n_mines=10):
        self.tiles = [[Tile() for c in range(n_cols)] for r in range(n_rows)] # Make board
        self.n_flags = n_mines
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.game_over = False
        self.first = True # For some minesweeper convenience features
        
        # Add Mines
        for i in range(n_mines):
            r, c = random.randrange(n_rows), random.randrange(n_cols)
            while not self.tiles[r][c].plant():
                r, c = random.randrange(n_rows), random.randrange(n_cols)
            
            # Adjancent mines update
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if dr == 0 and dc == 0:
                        continue
                        
                    if 0 <= r+dr < n_rows and 0 <= c+dc < n_cols:
                        self.tiles[r+dr][c+dc].n_adj += 1
    
    # Perform filling reveal
    def reveal(self, r, c):
        tile = self.tiles[r][c]
        
        if tile.reveal():
            self.game_over = True
            return
        
        if tile.flagged:
            return
        
        self.first = False
        
        yield tile
        
        # Perform recurse
        if tile.n_adj == 0:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if dr == 0 and dc == 0:
                        continue
                    
                    if 0 <= r+dr < self.n_rows and 0 <= c+dc < self.n_cols:
                        if self.tiles[r+dr][c+dc].mine or self.tiles[r+dr][c+dc].cleared or self.tiles[r+dr][c+dc].flagged:
                            continue
                        
                        for t in self.reveal(r+dr, c+dc):
                            yield t
        
        return    
    
    # Flag box
    def flag(self, r, c):
        self.n_flags += self.tiles[r][c].flag()
        self.first = False
        return self.tiles[r][c]
    
    # Check if board is winning
    def check(self):
        for row in self.tiles:
            for tile in row:
                if not tile.mine and not tile.cleared:
                    return False
        return True
    
    # Perform quick reveal
    def quick_adj(self, r, c):
        tile = self.tiles[r][c]
        adj_flag = 0
        
        # Adjacent flags count
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0:
                    continue

                if 0 <= r+dr < self.n_rows and 0 <= c+dc < self.n_cols:
                    if self.tiles[r+dr][c+dc].flagged:
                        adj_flag+=1
        
        # Check flags = mines
        if adj_flag != tile.n_adj:
            return
        
        # Reveal adjacent tiles
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0:
                    continue

                if 0 <= r+dr < self.n_rows and 0 <= c+dc < self.n_cols:
                    for t in self.reveal(r+dr, c+dc):
                        yield t
        
        return  


class Sweepyr:
    def __init__(self):
        
        # Window
        self.window = Tk()
        self.window.title("Sweepyr")
        self.window.configure(bg="dim gray")
        
        # Fonts
        self.tile_font = Font(family="MINE-SWEEPER", size=32)
        self.header_font = Font(family="MINE-SWEEPER", size=18)
        
        # Images
        self.hidden = PhotoImage(file="hidden.gif")
        self.revealed = PhotoImage(file="revealed.gif")
        self.alive = PhotoImage(file="happy.gif")
        self.win = PhotoImage(file="win.gif")
        self.lose = PhotoImage(file="lose.gif")
        
        # Header
        self.header = Frame(self.window, bg="dim gray", width=200, height=200)
        self.header.pack()
        
        # String Vars
        self.n_rows = IntVar(value=7)
        self.n_cols = IntVar(value=7)
        self.n_mines = IntVar(value=10)
        self.n_flags = IntVar(value=0)
        
        # Entry
        self.row_entry = Entry(self.header, textvariable=self.n_rows, font=self.header_font, bg="dim gray", width=2, justify=RIGHT)
        self.col_entry = Entry(self.header, textvariable=self.n_cols, font=self.header_font, bg="dim gray", width=2, justify=RIGHT)
        self.mine_entry = Entry(self.header, textvariable=self.n_mines, font=self.header_font, bg="dim gray", width=2, justify=RIGHT)
        
        # Labels
        self.flags_display = Label(self.header, textvariable=self.n_flags, font=self.header_font, bg="dim gray")
        self.title = Label(self.header, text="sweepyr", font=self.header_font, bg="dim gray")
        self.row_label = Label(self.header, text="rows", font=self.header_font, bg="dim gray")
        self.col_label = Label(self.header, text="cols", font=self.header_font, bg="dim gray")
        self.mine_label = Label(self.header, text="mines", font=self.header_font, bg="dim gray")
        
        # Button
        self.reset_button = Button(self.header, image=self.alive, command=self.generate_board, bg="dim gray")
        
        # Build Header
        self.flags_display.grid(row=0, column=0, columnspan=2)
        self.reset_button.grid(row=0, column=2, columnspan=2)
        self.title.grid(row=0, column=4, columnspan=2)
        
        self.row_label.grid(row=1, column=0)
        self.row_entry.grid(row=1, column=1)
        self.col_label.grid(row=1, column=2)
        self.col_entry.grid(row=1, column=3)
        self.mine_label.grid(row=1, column=4)
        self.mine_entry.grid(row=1, column=5)
        
        # Main frame
        self.frame = Frame(self.window, bg="dim gray")
        self.frame.pack()
        
        # Initialize state
        self.generate_board()
        self.window.mainloop()
    
    # Make a new board
    def generate_board(self):
        n_cols = self.n_cols.get() 
        n_rows = self.n_rows.get()
        n_mines = self.n_mines.get()
        
        # Validity check
        if n_cols * n_rows <= n_mines or n_mines < 0 or n_cols <= 0 or n_rows <= 0:
            showwarning(title="Warning", message="The invalid parameters.")
            return
        
        # Clear main frame
        for widgets in self.frame.winfo_children():
            widgets.destroy()
        
        self.reset_button.configure(image=self.alive)
        self.board = Board(n_rows, n_cols, n_mines)
        self.n_flags.set(n_mines)
        
        # Create Elements for grid
        for r in range(n_rows):
            for c in range(n_cols):
                l = Label(self.frame, font=self.tile_font, image=self.hidden, bg="dim gray", compound='center')
                l.grid(row=r, column=c)
                tile = self.board.tiles[r][c]
                tile.label = l 
        
        # Reveal tile helper
        def reveal(tile):
            tile.label.configure(image=self.revealed, text=str(tile), fg=tile.color())
        
        # Perform end checks
        def end_routine(row, col):
            # Game over routine
            if self.board.game_over:
                for r in self.board.tiles:
                    for t in r:
                        reveal(t)
                self.board.tiles[row][col].label.configure(bg="red")
                self.reset_button.configure(image=self.lose)
            
            # Win routine
            if self.board.check():
                self.reset_button.configure(image=self.win)
        
        # Left Click Command helper
        def left_click(event, row, col):
            if self.board.game_over or self.board.check():
                return
            
            # Reveal
            for t in self.board.reveal(row, col):
                reveal(t)
            
            # First time conveinence
            while self.board.first:
                self.board.game_over = False
                new_board = Board(n_rows, n_cols, n_mines)
                
                for r in range(n_rows):
                    for c in range(n_cols):
                        new_board.tiles[r][c].label = self.board.tiles[r][c].label
                
                self.board = new_board
                
                for t in self.board.reveal(row, col):
                    reveal(t)
            end_routine(row, col)
        
        # Right Click Command helper
        def right_click(event, row, col):
            if self.board.game_over or self.board.check():
                return
            
            self.board.flag(row, col)
            self.n_flags.set(self.board.n_flags)
            tile = self.board.tiles[row][col]
            l = tile.label
            
            if not tile.cleared:
                if tile.flagged:
                    l.configure(text="`")
                else:
                    l.configure(text="")
            else:
                for t in self.board.quick_adj(row, col):
                    reveal(t)
                end_routine(row, col)      
        
        # Bind commands
        for r in range(n_rows):
            for c in range(n_cols):
                l = self.board.tiles[r][c].label
                l.bind("<Button-1>", partial(left_click, row=r, col=c))
                l.bind("<Button-2>", partial(right_click, row=r, col=c))
                l.bind("<Button-3>", partial(right_click, row=r, col=c))

                
if __name__ == "__main__":
    m = Sweepyr()
