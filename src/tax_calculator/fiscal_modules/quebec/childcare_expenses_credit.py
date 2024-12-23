"""
Childcare Expenses Credit

Parameters reference:
    - https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/parametres/AUTFR_RegimeImpot2025.pdf
    - https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/parametres/AUTFR_RegimeImpot2024.pdf
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo

class ChildcareExpensesCredit(TaxProgram):
    PARAMS = {
        2025: {
            'expense_limits': {
                'child_under_7': 12275,
                'child_with_disabilities': 16800,
                'other_children': 6180
            },
            'qualifying_child_max_income': 13658,
            'rate_schedule': [
                (24795, 0.78),
                (42725, 0.75),
                (45340, 0.74),
                (46970, 0.73),
                (48570, 0.72),
                (50195, 0.71),
                (119835, 0.70),
                (float('inf'), 0.67)
            ]
        },
        2024: {            
            'expense_limits': {
                'child_under_7': 11935,
                'child_with_disabilities': 16335,
                'other_children': 6010
            },
            'qualifying_child_max_income': 13280,
            'rate_schedule': [
                (24110, 0.78),
                (42515, 0.75),
                (44085, 0.74),
                (45670, 0.73),
                (47225, 0.72),
                (48805, 0.71),
                (116515, 0.70),
                (float('inf'), 0.67)
            ]
        },
        2023: {
            'expense_limits': {
                'child_under_7': 11360,
                'child_with_disabilities': 15545,
                'other_children': 5720
            },
            'qualifying_child_max_income': 12638,
            'rate_schedule': [
                (22945, 0.78),
                (40460, 0.75),
                (41955, 0.74),
                (43460, 0.73),
                (44940, 0.72),
                (46445, 0.71),
                (110880, 0.70),
                (float('inf'), 0.67)
            ]
        },
    }

    @property
    def name(self) -> str:
        return "Quebec Income Tax"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def calculate(self, family: Family, family_net_income: float) -> float:
        """Calculate childcare expenses credit."""
        if not family.children:
            return 0

        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        total_expenses = 0
        for child in family.children:
            if not hasattr(child, 'daycare_cost') or child.daycare_cost <= 0:
                continue

            # Determine expense limit based on child's age and disability status
            if getattr(child, 'has_disability', False):
                limit = params['childcare_expenses_credit']['expense_limits']['child_with_disabilities']
            elif child.age < 7:
                limit = params['childcare_expenses_credit']['expense_limits']['child_under_7']
            else:
                limit = params['childcare_expenses_credit']['expense_limits']['other_children']

            total_expenses += min(child.daycare_cost, limit)

        if total_expenses <= 0:
            return 0

        # Determine credit rate based on family income
        credit_rate = 0
        for threshold, rate in params['childcare_expenses_credit']['rate_schedule']:
            if family_income <= threshold:
                credit_rate = rate
                break

        # Split childcare credit proportionally if both adults
        if family.adult2:
            childcare_credit1 = childcare_credit * credit_rate * (family.adult1.income / family_income)
            childcare_credit2 = childcare_credit - childcare_credit1
        else:
            childcare_credit1 = childcare_credit * credit_rate
            childcare_credit2 = 0

        return total_expenses * credit_rate


        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'childcare_credit1': childcare_credit1,
            'childcare_credit1': childcare_credit2,
            'childcare_credit': childcare_credit
        }
