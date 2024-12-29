"""
Medical Expenses Credit

References
    - https://www.revenuquebec.ca/fr/citoyens/declaration-de-revenus/produire-votre-declaration-de-revenus/comment-remplir-votre-declaration/aide-par-ligne/451-a-480-remboursement-ou-solde-a-payer/ligne-462/point-1/
    
"""

from typing import Dict, List, Any
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo


class MedicalExpensesCredit(TaxProgram):
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
        return "Medical Expenses Credit"

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


