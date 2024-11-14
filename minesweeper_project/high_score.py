import json
import os
from typing import List, Dict, Tuple, TextIO, Any
from datetime import datetime


class HighScores:
    def __init__(self) -> None:
        self.scores_file = "minesweeper_scores.json"
        self.scores: Dict[str, List[Dict[str, Any]]] = self.load_scores()

    def load_scores(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load high scores from file."""
        default_scores: Dict[str, List[Dict[str, Any]]] = {
            "Easy": [], "Medium": [], "Hard": [], "Custom": []
        }

        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading scores: {e}")
                return default_scores
        return default_scores

    def save_scores(self) -> None:
        """Save high scores to file."""
        try:
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f)
        except IOError as e:
            print(f"Error saving scores: {e}")

    def add_score(self, difficulty: str, time: int, board_size: Tuple[int, int], mines: int) -> bool:
        """
        Add a new score. Returns True if it's a high score.

        Args:
            difficulty: Difficulty level of the game
            time: Time taken to complete the game
            board_size: Tuple of (width, height)
            mines: Number of mines in the game

        Returns:
            bool: True if score is in top 10, False otherwise
        """
        score_entry = {
            "time": time,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "board_size": f"{board_size[0]}x{board_size[1]}",
            "mines": mines
        }

        if difficulty not in self.scores:
            self.scores[difficulty] = []

        # Keep only top 10 scores per difficulty, sorted by time
        self.scores[difficulty].append(score_entry)
        self.scores[difficulty].sort(key=lambda x: x["time"])
        self.scores[difficulty] = self.scores[difficulty][:10]

        self.save_scores()

        # Return True if score is in top 10
        return score_entry in self.scores[difficulty]

    def get_scores(self, difficulty: str) -> List[Dict[str, Any]]:
        """
        Get high scores for a specific difficulty.

        Args:
            difficulty: Difficulty level to get scores for

        Returns:
            List of score dictionaries
        """
        return self.scores.get(difficulty, [])