"""
Senior Assistance Amount

Parameters
    https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/allocation-famille/#:~:text=Le%20seuil%20du%20revenu%20familial,de%20r%C3%A9duction%20est%20de%204%20%25.
"""

from typing import Dict, List, Any
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo


class SeniorAssistanceAmount(TaxProgram):
    PARAMS = {
        2025: {
            '?': 65700.0,
        },
        2024: {
            '?': 65700.0,
        },
        2023: {
            '?': 65700.0,
        }
    }

    @property
    def name(self) -> str:
        return "Senior Assistance Amount"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def calculate(self, family: Family) -> Dict[str, float]:
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        benefit1 = 0.0
        benefit2 = 0.0
        
        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': benefit1,
            'adult2': benefit2,
            'total': benefit1 + benefit2,
        }


