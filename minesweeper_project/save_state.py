import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import os


class GameSaveManager:
    def __init__(self, save_dir: str = "saves") -> None:
        self.save_dir = save_dir
        # Create saves directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    def save_game(self, game_state: Dict[str, Any], save_name: Optional[str] = None) -> str:
        """
        Save the current game state to a file.

        Args:
            game_state: Dictionary containing the game state
            save_name: Optional name for the save file

        Returns:
            str: The filename used for saving

        Raises:
            IOError: If there's an error saving the file
        """
        if save_name is None:
            # Generate default save name based on timestamp
            save_name = f"minesweeper_save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        filename = os.path.join(self.save_dir, f"{save_name}.json")

        # Add timestamp to save data
        game_state['save_timestamp'] = datetime.now().isoformat()

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(game_state, f)
        except IOError as e:
            raise IOError(f"Failed to save game: {e}") from e

        return filename

    def load_game(self, filename: str) -> Dict[str, Any]:
        """
        Load a game state from a file.

        Args:
            filename: Name of the save file to load

        Returns:
            Dict containing the game state

        Raises:
            FileNotFoundError: If the save file doesn't exist
            json.JSONDecodeError: If the save file is corrupted
        """
        full_path = os.path.join(self.save_dir, filename)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise IOError(f"Failed to load save file: {e}") from e

    def list_saves(self) -> List[Dict[str, Any]]:
        """
        List all available save files with their basic information.

        Returns:
            List of dictionaries containing save file information
        """
        saves: List[Dict[str, Any]] = []
        for filename in os.listdir(self.save_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.save_dir, filename), 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                        saves.append({
                            'filename': filename,
                            'timestamp': save_data.get('save_timestamp', 'Unknown'),
                            'difficulty': save_data.get('difficulty', 'Unknown'),
                            'time': save_data.get('game_time', 0),
                            'board_size': f"{save_data.get('width', '?')}x{save_data.get('height', '?')}"
                        })
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error loading save file {filename}: {e}")
                    continue

        # Sort by timestamp, newest first
        saves.sort(key=lambda x: x['timestamp'], reverse=True)
        return saves

    def delete_save(self, filename: str) -> bool:
        """
        Delete a save file.

        Args:
            filename: Name of the save file to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.remove(os.path.join(self.save_dir, filename))
            return True
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error deleting save file: {e}")
            return False