"""
Quebec Income Tax calculator implementation.
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family

class QuebecTax(TaxProgram):
    """Quebec income tax calculator"""
    
    PARAMS = {
        2024: {
            'brackets': [16495, 49275, 98540, 119910],
            'rates': [0.14, 0.19, 0.24, 0.2575, 0.2575],
            'basic_amount': 17183
        },
        2023: {
            'brackets': [16143, 48295, 96580, 117392],
            'rates': [0.14, 0.19, 0.24, 0.2575, 0.2575],
            'basic_amount': 17183
        }
    }

    @property
    def name(self) -> str:
        return "Quebec Income Tax"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate Quebec income tax for the family"""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        # Calculate tax for primary adult
        tax1 = self._calculate_individual_tax(
            family.adult1.income,
            params
        )

        # Calculate tax for second adult if present
        tax2 = (self._calculate_individual_tax(
            family.adult2.income,
            params
        ) if family.adult2 else 0.0)

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'total': tax1 + tax2,
            'net_family_income': 0.0,
            'details': {
                'adult1_tax': tax1,
                'adult2_tax': tax2,
                'basic_amount': params['basic_amount']
            }
        }
