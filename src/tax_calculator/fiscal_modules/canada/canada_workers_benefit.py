"""
Canada Workers Benefit (CWB)

References:
    - [Canada Workers Benefit](https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-workers-benefit.html)
"""

from typing import Dict, List, Any
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo


class CanadaWorkersBenefit(TaxProgram):
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
        return "Canada Worker's Benefit"

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
