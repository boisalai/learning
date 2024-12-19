"""
Quebec Parental Insurance Plan calculator.

Parameters reference:
    https://www.rqap.gouv.qc.ca/en/about-the-plan/general-information/premiums-and-maximum-insurable-earnings
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo

class ParentalInsurance(TaxProgram):
    """Quebec Parental Insurance Plan calculator"""
    
    PARAMS = {
        2024: {
            'max_insurable_earnings': 94000.0,
            'employee_rate': 0.00494,
            'employer_rate': 0.00692,
            'self_employed_rate': 0.00878,
            'min_earnings': 2000,
        },
        2023: {
            'max_insurable_earnings': 91000.0,
            'employee_rate': 0.00494,
            'employer_rate': 0.00692,
            'self_employed_rate': 0.00878,
            'min_earnings': 2000,
        }
    }

    @property
    def name(self) -> str:
        return "Quebec Parental Insurance Plan"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate QPIP premiums for the family"""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        def calculate_premium(gross_work_income: float) -> float:
            if gross_work_income < params['min_earnings']:
                insurable_earnings = min(gross_work_income, params['max_insurable_earnings'])
                employee_premium = insurable_earnings * params['employee_rate']
            else:
                employee_premium = 0
            return employee_premium 

        premium1 = calculate_premium(family.adult1.gross_work_income)
        premium2 = (calculate_premium(family.adult2.gross_work_income) if family.adult2 else 0)

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': premium1, 
            'adult2': premium2,
            'total': premium1 + premium2
        }

if __name__ == "__main__":
    import numpy as np

    # Create arrays for incomes and corresponding premiums
    incomes = np.arange(0, 100001, 1000)
    premiums = []
    
    pi = ParentalInsurance()
    
    # Calculate premium for each income level
    for income in incomes:
        adult = AdultInfo(age=30, gross_work_income=income)
        test_case = {
            "status": FamilyStatus.SINGLE,
            "adult1": adult,
            "tax_year": 2024
        }
        family = Family(**test_case)
        result = pi.calculate(family)
        premiums.append(abs(result['total']))