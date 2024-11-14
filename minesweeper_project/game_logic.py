import random
from typing import List, Tuple, Set, Dict, Any
from datetime import datetime

class MinesweeperLogic:
    def __init__(self, width: int, height: int, num_mines: int):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.grid: List[List[int]] = []
        self.mine_positions: Set[Tuple[int, int]] = set()
        self.first_move = True
        self.revealed: Set[Tuple[int, int]] = set()
        self.flagged: Set[Tuple[int, int]] = set()
        self.game_over = False
        self.won = False
        self.time_started = None
        self.game_time = 0
        self.mines_remaining = num_mines
        self.initialize_grid()

    def initialize_grid(self) -> None:
        """Initialize an empty grid."""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def place_mines(self, first_click_x: int, first_click_y: int) -> None:
        """Place mines randomly, ensuring first click is safe."""
        self.mine_positions.clear()
        safe_zone = set(self.get_adjacent_squares(first_click_x, first_click_y))
        safe_zone.add((first_click_x, first_click_y))

        available_positions = [
            (x, y) for x in range(self.width) for y in range(self.height)
            if (x, y) not in safe_zone
        ]

        selected_positions = random.sample(available_positions, min(self.num_mines, len(available_positions)))
        self.mine_positions = set(selected_positions)

        # Place mines and calculate numbers
        for x, y in self.mine_positions:
            self.grid[y][x] = -1  # -1 represents a mine

        # Calculate numbers for adjacent squares
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.mine_positions:
                    count = self.count_adjacent_mines(x, y)
                    self.grid[y][x] = count

    def toggle_flag(self, x: int, y: int) -> bool:
        """Toggle flag on a square. Returns True if flag was placed, False if removed."""
        if (x, y) in self.revealed:
            return False

        if (x, y) in self.flagged:
            self.flagged.remove((x, y))
            self.mines_remaining += 1
            return False
        else:
            self.flagged.add((x, y))
            self.mines_remaining -= 1
            return True

    def reveal_square(self, x: int, y: int) -> Set[Tuple[int, int]]:
        """Reveal a square and return set of all newly revealed squares."""
        if (x, y) in self.revealed or (x, y) in self.flagged:
            return set()

        newly_revealed = set()
        newly_revealed.add((x, y))
        self.revealed.add((x, y))

        if self.grid[y][x] == 0:
            stack = [(x, y)]
            while stack:
                curr_x, curr_y = stack.pop()
                for adj_x, adj_y in self.get_adjacent_squares(curr_x, curr_y):
                    if ((adj_x, adj_y) not in self.revealed and
                            (adj_x, adj_y) not in self.flagged):
                        self.revealed.add((adj_x, adj_y))
                        newly_revealed.add((adj_x, adj_y))
                        if self.grid[adj_y][adj_x] == 0:
                            stack.append((adj_x, adj_y))

        return newly_revealed

    def count_adjacent_mines(self, x: int, y: int) -> int:
        """Count mines in adjacent squares."""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.width and
                        0 <= new_y < self.height and
                        (dx, dy) != (0, 0) and
                        (new_x, new_y) in self.mine_positions):
                    count += 1
        return count

    def get_adjacent_squares(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all valid adjacent square coordinates."""
        adjacent = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.width and
                        0 <= new_y < self.height and
                        (dx, dy) != (0, 0)):
                    adjacent.append((new_x, new_y))
        return adjacent

    def is_mine(self, x: int, y: int) -> bool:
        """Check if a square contains a mine."""
        return (x, y) in self.mine_positions

    def get_value(self, x: int, y: int) -> int:
        """Get the value of a square."""
        return self.grid[y][x]

    def get_save_state(self) -> Dict[str, Any]:
        """Get the current game state for saving."""
        return {
            'width': self.width,
            'height': self.height,
            'num_mines': self.num_mines,
            'grid': self.grid,
            'mine_positions': list(self.mine_positions),
            'first_move': self.first_move,
            'revealed': list(self.revealed),
            'flagged': list(self.flagged),
            'game_over': self.game_over,
            'won': self.won,
            'game_time': self.game_time,
            'mines_remaining': self.mines_remaining
        }

    def load_save_state(self, state: Dict[str, Any]) -> None:
        """Load a saved game state."""
        self.width = state['width']
        self.height = state['height']
        self.num_mines = state['num_mines']
        self.grid = state['grid']
        self.mine_positions = set(tuple(pos) for pos in state['mine_positions'])
        self.first_move = state['first_move']
        self.revealed = set(tuple(pos) for pos in state['revealed'])
        self.flagged = set(tuple(pos) for pos in state['flagged'])
        self.game_over = state['game_over']
        self.won = state['won']
        self.game_time = state['game_time']
        self.mines_remaining = state['mines_remaining']