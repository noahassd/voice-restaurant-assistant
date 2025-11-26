import json
from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class ReservationResult:
    success: bool
    message: str
    table_id: Optional[int] = None
    alternative: Optional[int] = None


class ReservationAgent:
    def __init__(self, tables_path: str = "data/tables.json") -> None:
        self.tables_path = tables_path
        self.tables = self._load_tables()

    def _load_tables(self) -> List[Dict]:
        with open(self.tables_path, "r") as f:
            return json.load(f)

    def find_table(self, num_people: int) -> ReservationResult:
        # 1. Cherche une table parfaite
        for t in self.tables:
            if t["available"] and t["capacity"] >= num_people:
                return ReservationResult(
                    success=True,
                    message=f"Table trouvée : {t['table_id']}",
                    table_id=t["table_id"]
                )

        # 2. Cherche une alternative (table trop grande mais dispo)
        possible_alternatives = [
            t for t in self.tables if t["available"]
        ]

        if possible_alternatives:
            alt = possible_alternatives[0]
            return ReservationResult(
                success=False,
                message="Aucune table parfaite disponible, mais alternative trouvée.",
                alternative=alt["table_id"]
            )

        # 3. Aucune table du tout
        return ReservationResult(
            success=False,
            message="Aucune table n’est disponible."
        )
