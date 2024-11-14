import tkinter as tk
from tkinter import ttk, messagebox
from game_logic import MinesweeperLogic
from high_score import HighScores
from typing import List, Set, Tuple, Callable, Dict
from save_state import GameSaveManager
import json

class MinesweeperGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Minesweeper")
        self.current_difficulty = "Easy"
        self.difficulty_var = tk.StringVar(value=self.current_difficulty)
        self.difficulties: Dict[str, Tuple[int, int, int]] = {
            "Easy": (9, 9, 10),
            "Medium": (16, 16, 40),
            "Hard": (30, 16, 99)
        }
        self.buttons: List[List[tk.Button]] = []
        self.revealed: Set[Tuple[int, int]] = set()
        self.flagged: Set[Tuple[int, int]] = set()
        self.game_logic: MinesweeperLogic | None = None
        self.timer_id = None
        self.time_label = None
        self.mines_label = None
        self.game_time = -1
        self.high_scores = HighScores()
        self.create_menu()
        self.save_manager = GameSaveManager()

    def create_menu(self) -> None:
        """Create the main menu interface."""
        # Stop timer if running
        self.stop_timer()

        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create menu frame
        menu_frame = ttk.Frame(self.root, padding="20")
        menu_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(menu_frame, text="Minesweeper", font=('Arial', 24))
        title_label.grid(row=0, column=0, pady=20)

        # Difficulty selection
        diff_frame = ttk.LabelFrame(menu_frame, text="Select Difficulty", padding="10")
        diff_frame.grid(row=1, column=0, pady=10)

        self.difficulty_var = tk.StringVar(value=self.current_difficulty)
        for i, diff in enumerate(self.difficulties.keys()):
            ttk.Radiobutton(diff_frame, text=diff, value=diff,
                            variable=self.difficulty_var).grid(row=i, column=0, pady=5)

        # Custom difficulty button
        ttk.Button(diff_frame, text="Custom...",
                   command=self.show_custom_difficulty).grid(row=len(self.difficulties), column=0, pady=5)

        # Buttons
        ttk.Button(menu_frame, text="Start Game",
                   command=self.start_game).grid(row=2, column=0, pady=10)
        ttk.Button(menu_frame, text="High Scores",
                   command=self.show_high_scores).grid(row=3, column=0, pady=10)
        ttk.Button(menu_frame, text="Quit",
                   command=self.root.quit).grid(row=4, column=0, pady=10)

    def show_custom_difficulty(self) -> None:
        """Show dialog for custom difficulty settings."""
        custom_window = tk.Toplevel(self.root)
        custom_window.title("Custom Difficulty")
        custom_window.transient(self.root)
        custom_window.grab_set()

        # Create input fields
        ttk.Label(custom_window, text="Width (8-50):").grid(row=0, column=0, padx=5, pady=5)
        width_var = tk.StringVar(value="16")
        width_entry = ttk.Entry(custom_window, textvariable=width_var)
        width_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(custom_window, text="Height (8-50):").grid(row=1, column=0, padx=5, pady=5)
        height_var = tk.StringVar(value="16")
        height_entry = ttk.Entry(custom_window, textvariable=height_var)
        height_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(custom_window, text="Mines:").grid(row=2, column=0, padx=5, pady=5)
        mines_var = tk.StringVar(value="40")
        mines_entry = ttk.Entry(custom_window, textvariable=mines_var)
        mines_entry.grid(row=2, column=1, padx=5, pady=5)

        def validate_and_set():
            try:
                width = int(width_var.get())
                height = int(height_var.get())
                mines = int(mines_var.get())

                if not (8 <= width <= 50 and 8 <= height <= 50):
                    raise ValueError("Width and height must be between 8 and 50")

                max_mines = (width * height) - 9  # Ensure first click and surroundings are safe
                if not (1 <= mines <= max_mines):
                    raise ValueError(f"Mines must be between 1 and {max_mines}")

                self.difficulties["Custom"] = (width, height, mines)
                self.difficulty_var.set("Custom")
                custom_window.destroy()

            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))

        ttk.Button(custom_window, text="OK", command=validate_and_set).grid(row=3, column=0, columnspan=2, pady=10)

    def show_high_scores(self) -> None:
        """Show high scores window."""
        scores_window = tk.Toplevel(self.root)
        scores_window.title("High Scores")
        scores_window.transient(self.root)

        # Create notebook for different difficulties
        notebook = ttk.Notebook(scores_window)
        notebook.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create a tab for each difficulty
        for difficulty in self.difficulties.keys():
            frame = ttk.Frame(notebook, padding="10")
            notebook.add(frame, text=difficulty)

            # Create headers
            ttk.Label(frame, text="Time", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5)
            ttk.Label(frame, text="Date", font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=5)
            ttk.Label(frame, text="Board", font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=5)
            ttk.Label(frame, text="Mines", font=('Arial', 10, 'bold')).grid(row=0, column=3, padx=5)

            # Add scores
            scores = self.high_scores.get_scores(difficulty)
            for i, score in enumerate(scores, 1):
                ttk.Label(frame, text=f"{score['time']}s").grid(row=i, column=0, padx=5)
                ttk.Label(frame, text=score['date']).grid(row=i, column=1, padx=5)
                ttk.Label(frame, text=score['board_size']).grid(row=i, column=2, padx=5)
                ttk.Label(frame, text=score['mines']).grid(row=i, column=3, padx=5)

    def start_game(self) -> None:
        """Initialize and start a new game."""
        # Stop existing timer if running
        self.stop_timer()

        # Reset game time
        self.game_time = 0

        self.current_difficulty = self.difficulty_var.get()
        width, height, mines = self.difficulties[self.current_difficulty]
        self.game_logic = MinesweeperLogic(width, height, mines)
        self.create_game_board()
        self.start_timer()

    def create_game_board(self) -> None:
        """Create the game board interface with status bar."""
        if not self.game_logic:
            return

        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0)

        # Create status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Mine counter
        self.mines_label = ttk.Label(status_frame, text=f"Mines: {self.game_logic.mines_remaining}")
        self.mines_label.grid(row=0, column=0, padx=5)

        # Timer
        self.time_label = ttk.Label(status_frame, text="Time: 0")
        self.time_label.grid(row=0, column=1, padx=5)

        # Create game frame
        game_frame = ttk.Frame(main_frame)
        game_frame.grid(row=1, column=0)

        # Create buttons grid
        self.buttons = []
        for y in range(self.game_logic.height):
            row = []
            for x in range(self.game_logic.width):
                btn = tk.Button(game_frame, width=2, height=1, relief=tk.RAISED)
                btn.grid(row=y, column=x)
                btn.bind('<Button-1>', self.create_click_handler(x, y))
                btn.bind('<Button-3>', self.create_right_click_handler(x, y))
                row.append(btn)
            self.buttons.append(row)

        # Menu button
        ttk.Button(main_frame, text="Back to Menu",
                   command=self.create_menu).grid(row=2, column=0, pady=10)

        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)

        # Add Save/Load buttons
        ttk.Button(button_frame, text="Save Game",
                   command=self.save_game).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Load Game",
                   command=self.show_load_dialog).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Back to Menu",
                   command=self.create_menu).grid(row=0, column=2, padx=5)

    def save_game(self) -> None:
        """Show save game dialog."""
        if not self.game_logic or self.game_logic.game_over:
            return

        save_window = tk.Toplevel(self.root)
        save_window.title("Save Game")
        save_window.transient(self.root)
        save_window.grab_set()

        ttk.Label(save_window, text="Save name:").grid(row=0, column=0, padx=5, pady=5)
        save_name = tk.StringVar()
        entry = ttk.Entry(save_window, textvariable=save_name)
        entry.grid(row=0, column=1, padx=5, pady=5)

        def do_save():
            name = save_name.get().strip()
            if name:
                state = self.game_logic.get_save_state()
                state['difficulty'] = self.current_difficulty
                self.save_manager.save_game(state, name)
                save_window.destroy()
                messagebox.showinfo("Success", "Game saved successfully!")
            else:
                messagebox.showerror("Error", "Please enter a save name")

        ttk.Button(save_window, text="Save",
                   command=do_save).grid(row=1, column=0, columnspan=2, pady=10)

    def show_load_dialog(self) -> None:
        """Show load game dialog."""
        load_window = tk.Toplevel(self.root)
        load_window.title("Load Game")
        load_window.transient(self.root)
        load_window.grab_set()

        # Create treeview for saves
        columns = ('Filename', 'Date', 'Difficulty', 'Time', 'Board Size')
        tree = ttk.Treeview(load_window, columns=columns, show='headings')

        # Set column headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(load_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Load saves
        saves = self.save_manager.list_saves()
        for save in saves:
            tree.insert('', 'end', values=(
                save['filename'],
                save['timestamp'],
                save['difficulty'],
                f"{save['time']}s",
                save['board_size']
            ))

        def do_load():
            selection = tree.selection()
            if not selection:
                messagebox.showerror("Error", "Please select a save file")
                return

            filename = tree.item(selection[0])['values'][0]
            try:
                save_state = self.save_manager.load_game(filename)
                self.current_difficulty = save_state['difficulty']
                self.game_logic = MinesweeperLogic(
                    save_state['width'],
                    save_state['height'],
                    save_state['num_mines']
                )
                self.game_logic.load_save_state(save_state)
                self.create_game_board()
                # Update all buttons to match saved state
                self.update_board_from_save()
                load_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load save: {str(e)}")

        def delete_save():
            selection = tree.selection()
            if not selection:
                messagebox.showerror("Error", "Please select a save file")
                return

            filename = tree.item(selection[0])['values'][0]
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this save?"):
                if self.save_manager.delete_save(filename):
                    tree.delete(selection[0])

        # Pack widgets
        tree.grid(row=0, column=0, padx=5, pady=5)
        scrollbar.grid(row=0, column=1, sticky='ns')

        button_frame = ttk.Frame(load_window)
        button_frame.grid(row=1, column=0, columnspan=2, pady=5)

        ttk.Button(button_frame, text="Load", command=do_load).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_save).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Cancel",
                   command=load_window.destroy).grid(row=0, column=2, padx=5)

    def update_board_from_save(self) -> None:
        """Update the board display to match a loaded save state."""
        if not self.game_logic:
            return

        # Update revealed squares
        for x, y in self.game_logic.revealed:
            value = self.game_logic.get_value(x, y)
            btn = self.buttons[y][x]
            btn.configure(
                relief=tk.SUNKEN,
                state=tk.DISABLED,
                disabledforeground='black'
            )
            if value > 0:
                colors = ['blue', 'green', 'red', 'purple', 'maroon', 'turquoise', 'black', 'gray']
                btn.configure(text=str(value), disabledforeground=colors[value - 1])
            else:
                btn.configure(text="")

        # Update flagged squares
        for x, y in self.game_logic.flagged:
            self.buttons[y][x].configure(text="🚩")

        # Update timer and mine counter
        if self.time_label:
            self.time_label.configure(text=f"Time: {self.game_logic.game_time}")
        if self.mines_label:
            self.mines_label.configure(text=f"Mines: {self.game_logic.mines_remaining}")

        # Restart timer if game is not over
        if not self.game_logic.game_over:
            self.game_time = self.game_logic.game_time
            self.start_timer()

    def start_timer(self) -> None:
        """Start the game timer."""
        # Reset game time if not loading a saved game
        if not hasattr(self.game_logic, 'game_time'):
            self.game_time = 0
        self.update_timer()

    def update_timer(self):
        if not self.game_logic or self.game_logic.game_over:
            return
        self.game_time += 1
        self.time_label.config(text=f"Time: {self.game_time}")
        self.timer_id = self.root.after(1000, self.update_timer)

    def stop_timer(self) -> None:
        """Stop the game timer."""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def create_click_handler(self, x: int, y: int) -> Callable[[tk.Event], None]:
        """Create a click handler function for a specific button."""
        return lambda event: self.handle_click(x, y)

    def create_right_click_handler(self, x: int, y: int) -> Callable[[tk.Event], None]:
        """Create a right-click handler function for a specific button."""
        return lambda event: self.handle_right_click(x, y)

    def handle_click(self, x: int, y: int) -> None:
        """Handle left-click on a square with enhanced feedback."""
        if not self.game_logic:
            return

        # Don't allow clicking on flagged squares
        if (x, y) in self.game_logic.flagged:
            return

        if self.game_logic.first_move:
            self.game_logic.place_mines(x, y)
            self.game_logic.first_move = False

        if self.game_logic.is_mine(x, y):
            self.stop_timer()
            self.game_over(x, y)
            return

        newly_revealed = self.game_logic.reveal_square(x, y)
        for rx, ry in newly_revealed:
            value = self.game_logic.get_value(rx, ry)
            btn = self.buttons[ry][rx]
            # Disable the button to remove clicking animation and change appearance
            btn.configure(
                relief=tk.SUNKEN,  # Flat appearance instead of sunken
                bg='#d1d1d1',  # Use system default button face color
                state=tk.DISABLED,  # Disable the button
                disabledforeground='black'  # Keep text visible when disabled
            )
            if value > 0:
                colors = ['blue', 'green', 'red', 'purple', 'maroon', 'turquoise', 'black', 'gray']
                # For disabled buttons, we need to use disabled foreground instead of fg
                btn.configure(text=str(value), disabledforeground=colors[value - 1])
            else:
                btn.configure(text="")

        if self.check_win():
            self.stop_timer()
            self.show_win_message()

    def handle_right_click(self, x: int, y: int) -> None:
        """Handle right-click (flagging) on a square with mine counter."""
        if not self.game_logic:
            return

        if self.game_logic.toggle_flag(x, y):
            self.buttons[y][x].configure(text="🚩")
        else:
            self.buttons[y][x].configure(text="")

        # Update mine counter
        if self.mines_label:
            self.mines_label.configure(text=f"Mines: {self.game_logic.mines_remaining}")

    def check_win(self) -> bool:
        """Check if the player has won."""
        if not self.game_logic:
            return False

        total_squares = self.game_logic.width * self.game_logic.height
        return len(self.game_logic.revealed) == total_squares - self.game_logic.num_mines

    def game_over(self, trigger_x: int, trigger_y: int) -> None:
        """Handle game over state with enhanced visual feedback."""
        if not self.game_logic:
            return

        # Show all mines
        for x, y in self.game_logic.mine_positions:
            btn = self.buttons[y][x]
            if (x, y) == (trigger_x, trigger_y):
                btn.configure(text="💥", background="red")  # Triggered mine
            elif (x, y) in self.flagged:
                btn.configure(text="✅")  # Correctly flagged mine
            else:
                btn.configure(text="💣")  # Hidden mine

        # Show incorrect flags
        for x, y in self.flagged:
            if (x, y) not in self.game_logic.mine_positions:
                self.buttons[y][x].configure(text="❌", background="orange")  # Wrong flag

        messagebox.showinfo("Game Over", f"Game Over! Time: {self.game_time} seconds")
        self.create_menu()

    def show_win_message(self) -> None:
        """Display win message, save high score, and return to menu."""
        is_high_score = self.high_scores.add_score(
            self.current_difficulty,
            self.game_time,
            (self.game_logic.width, self.game_logic.height),
            self.game_logic.num_mines
        )

        message = f"Congratulations! You won!\nTime: {self.game_time} seconds"
        if is_high_score:
            message += "\nNew High Score!"

        messagebox.showinfo("Victory", message)
        self.create_menu()

    def run(self) -> None:
        """Start the game."""
        self.root.mainloop()