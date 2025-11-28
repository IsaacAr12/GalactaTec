import json
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime


class HallOfFameEntry:
    """Representa una entrada en el Salón de la Fama"""
    
    DIFFICULTY_NAMES = ["RECLUTA", "SARGENTO", "COMANDANTE"]
    
    def __init__(self, player_name: str, score: int, difficulty: int, date: str = None):
        self.player_name = player_name
        self.score = score
        self.difficulty = difficulty
        self.date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @property
    def difficulty_name(self) -> str:
        """Retorna el nombre de la dificultad"""
        return self.DIFFICULTY_NAMES[self.difficulty] if self.difficulty < len(self.DIFFICULTY_NAMES) else "DESCONOCIDO"
    
    def to_dict(self) -> Dict:
        return {
            "player_name": self.player_name,
            "score": self.score,
            "difficulty": self.difficulty,
            "difficulty_name": self.difficulty_name,
            "date": self.date
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "HallOfFameEntry":
        return HallOfFameEntry(
            player_name=data["player_name"],
            score=data["score"],
            difficulty=data["difficulty"],
            date=data["date"]
        )


class HallOfFameRepository:
    """Gestiona la persistencia del Salón de la Fama"""
    
    def __init__(self, file_path: str = "data/hall_of_fame.json"):
        current_dir = Path(__file__).parent.parent.parent
        self._file_path = current_dir / file_path
        self._entries: List[HallOfFameEntry] = []
        self._load_entries()
    
    def _load_entries(self):
        """Carga las entradas desde el archivo JSON"""
        if self._file_path.exists():
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._entries = [HallOfFameEntry.from_dict(entry) for entry in data]
                    self._entries.sort(key=lambda x: x.score, reverse=True)
            except (json.JSONDecodeError, IOError):
                self._entries = []
        else:
            self._entries = []
    
    def _save_entries(self):
        """Guarda las entradas en el archivo JSON"""
        self._file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(self._file_path, "w", encoding="utf-8") as f:
            data = [entry.to_dict() for entry in self._entries]
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_entry(self, entry: HallOfFameEntry) -> bool:
        """
        Añade una entrada y retorna True si entra en el top 5
        """
        self._entries.append(entry)
        self._entries.sort(key=lambda x: x.score, reverse=True)
        
        entered_top_5 = len(self._entries) <= 5 and self._entries.index(entry) < 5
        
        self._entries = self._entries[:5]
        self._save_entries()
        
        return entered_top_5
    
    def get_top_5(self) -> List[HallOfFameEntry]:
        """Retorna las mejores 5 entradas"""
        return self._entries[:5]
    
    def get_rank_for_score(self, score: int) -> Optional[int]:
        """Retorna la posición que tendría un score en el ranking (1-5) o None si no entra"""
        for idx, entry in enumerate(self.get_top_5()):
            if score > entry.score:
                return idx + 1
        if len(self.get_top_5()) < 5:
            return len(self.get_top_5()) + 1
        return None
    
    def is_top_5(self, score: int) -> bool:
        """Verifica si un score entraría en el top 5"""
        return self.get_rank_for_score(score) is not None
