"""
Quebec Income Tax calculator.

Parameters reference:
    - https://www.revenuquebec.ca/fr/citoyens/declaration-de-revenus/
    - https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/parametres/AUTFR_RegimeImpot2025.pdf
    - https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/parametres/AUTFR_RegimeImpot2024.pdf
    - https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo

@dataclass
class RetirementDetails:
    age: int
    retirement_income: float
    reduced_retirement_amount: float
    age_amount: float
    living_alone_amount: float

@dataclass
class DependentDetails:
    number_minors: int  
    number_students: int
    number_disabilities: int
    childcare_expenses: float

class QuebecIncomeTax(TaxProgram):
    PARAMS = {
        2025: {
            'brackets': [
                (53255, 0.14),
                (106495, 0.19),
                (129590, 0.24),
                (float('inf'), 0.2575)
            ],
            'basic_personal_amount': 18571,
            'living_alone': {
                'base_amount': 2128,
                'supplement_single_parent': 2627
            },
            'age_amount': {
                'max_amount': 3906,
                'age_threshold': 65,
                'income_threshold': 42090, 
                'reduction_rate': 0.185
            },
            'retirement_income': {
                'max_amount': 3470,
                'reduction_rate': 0.185,
                'income_threshold': 42090
            },
            'maximum_deduction_workers': 1420,
            'dependents': {
                'first_child': 4775,
                'subsequent_child': 3011,
                'single_parent_supplement': 2011,
                'disability': 3584,
                'student': 3011
            },
            'medical': {
                'min_expense_rate': 0.03
            },
            'transformation_rate': 0.15
        },
        2024: {
            'brackets': [
                (51780, 0.14),
                (103545, 0.19),
                (126000, 0.24),
                (float('inf'), 0.2575)
            ],
            'basic_personal_amount': 18056,
            'living_alone': {
                'base_amount': 2069,
                'supplement_single_parent': 2554
            },
            'age_amount': {
                'max_amount': 3798,
                'age_threshold': 65,
                'income_threshold': 40924,
                'reduction_rate': 0.185
            },
            'retirement_income': {
                'max_amount': 3374,
                'income_threshold': 40924,
                'reduction_rate': 0.185
            },
            'maximum_deduction_workers': 1380,
            'dependents': {
                'first_child': 4525,
                'subsequent_child': 2855,
                'single_parent_supplement': 1907,
                'disability': 3401,
                'student': 2855
            },
            'medical': {
                'min_expense_rate': 0.03
            },
            'transformation_rate': 0.15
        },
        2023: {
            'brackets': [
                (49275, 0.15),
                (98540, 0.20),
                (119910, 0.24),
                (float('inf'), 0.2575)
            ],
            'basic_personal_amount': 17183,
            'living_alone': {
                'base_amount': 1969,
                'supplement_single_parent': 2431
            },
            'age_amount': {
                'max_amount': 3614,
                'age_threshold': 65,
                'income_threshold': 38945,
                'reduction_rate': 0.185
            },
            'retirement_income': {
                'max_amount': 3614,
                'income_threshold': 38945,
                'reduction_rate': 0.185
            },
            'maximum_deduction_workers': 1315,
            'dependents': {
                'first_child': 4351,
                'subsequent_child': 2746,
                'single_parent_supplement': 1834,
                'disability': 3272,
                'student': 2746
            },
            'medical': {
                'min_expense_rate': 0.03
            },
            'transformation_rate': 0.15
        }
    }

    @property
    def name(self) -> str:
        return "Quebec Income Tax"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def calculate_basic_tax(self, income: float, params: dict) -> float:
        """Calculate basic tax using progressive tax brackets."""
        if income <= 0:
            return 0

        tax = 0
        remaining_income = income
        previous_bracket = 0

        for bracket, rate in params['brackets']:
            taxable_in_bracket = min(remaining_income, bracket - previous_bracket)
            if taxable_in_bracket <= 0:
                break
            tax += taxable_in_bracket * rate
            remaining_income -= taxable_in_bracket
            previous_bracket = bracket

        return round(tax, 2)

    def calculate_non_refundable_credits(self, family: Family, income: float, params: dict) -> float:
        """Calculate all non-refundable tax credits."""
        credits = params['basic_personal_amount']

        # Age amount
        if family.adult1.age >= params['age_amount']['age_threshold']:
            age_amount = params['age_amount']['max_amount']
            if income > params['age_amount']['income_threshold']:
                reduction = (income - params['age_amount']['income_threshold']) * params['age_amount']['reduction_rate']
                age_amount = max(0, age_amount - reduction)
            credits += age_amount

        # Retirement income amount
        if family.adult1.gross_retirement_income > 0:
            retirement_amount = min(params['retirement_income']['max_amount'], family.adult1.gross_retirement_income)
            if income > params['retirement_income']['income_threshold']:
                reduction = (income - params['retirement_income']['income_threshold']) * params['retirement_income']['reduction_rate']
                retirement_amount = max(0, retirement_amount - reduction)
            credits += retirement_amount

        # Living alone amount
        is_single = family.adult2 is None
        has_children = bool(family.children and len(family.children) > 0)
        if is_single:
            credits += params['living_alone']['base_amount']
            if has_children:
                credits += params['living_alone']['supplement_single_parent']

        # Dependent children amounts
        if family.children:
            num_children = len(family.children)
            if num_children > 0:
                credits += params['dependents']['first_child']
                if num_children > 1:
                    credits += (num_children - 1) * params['dependents']['subsequent_child']
                
                # Count children with disabilities and students
                num_disabilities = sum(1 for c in family.children if getattr(c, 'has_disability', False))
                num_students = sum(1 for c in family.children if getattr(c, 'is_student', False))
                
                credits += num_disabilities * params['dependents']['disability']
                credits += num_students * params['dependents']['student']

                # Single parent supplement
                if is_single:
                    credits += params['dependents']['single_parent_supplement']

        # Apply transformation rate
        return credits * params['transformation_rate']

    def calculate_worker_deduction(self, work_income: float, params: dict) -> float:
        """Calculate worker deduction."""
        if work_income <= 0:
            return 0
        return min(work_income * 0.06, params['maximum_deduction_workers'])

    def calculate(self, family: Family, contributions: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate Quebec income tax for a family.
            
            Args:
                family: Family information
                contributions: Pre-calculated contributions including:
                    - employment_insurance
                    - parental_insurance 
                    - quebec_pension_plan
        """        
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        # Calculate total income (line 199)
        # TODO: Fractionnement des revenus de pension
        # TODO: Ajouter les gains en capital.
        # TODO: Ajouter les dividendes de sociétés canadiennes imposables.
        total_income1 = family.adult1.gross_work_income + family.adult1.gross_retirement_income
        total_income2 = family.adult2.gross_work_income + family.adult2.gross_retirement_income if family.adult2 else 0

        # Calculate worker deduction
        worker_deduction1 = self.calculate_worker_deduction(family.adult1.gross_work_income, params)
        worker_deduction2 = self.calculate_worker_deduction(family.adult2.gross_work_income, params) if family.adult2 else 0

        # Calculate net income (line 275) by subtracting:
        # - Worker deduction
        # - QPP contribution
        # - QPIP contribution
        # - EI premium
        net_income1 = total_income1 - (
            worker_deduction1 + 
            abs(contributions['quebec_pension_plan']['adult1']) +
            abs(contributions['parental_insurance']['adult1']) +
            abs(contributions['employment_insurance']['adult1'])
        )

        net_income2 = 0
        if family.adult2:
            net_income2 = total_income2 - (
                worker_deduction2 +
                abs(contributions['quebec_pension_plan']['adult2']) +
                abs(contributions['parental_insurance']['adult2']) +
                abs(contributions['employment_insurance']['adult2'])
            )

        # Calculate family net income
        family_net_income = net_income1 + net_income2

        # Calculate taxable income (line 299)
        taxable_income1 = net_income1
        taxable_income2 = net_income2

        # Calculate non-refundable credits
        credits1 = self.calculate_non_refundable_credits(family, net_income1, params)
        credits2 = 0
        if family.adult2:
            family_copy = Family(
                family_status=family.family_status,
                adult1=family.adult2,
                adult2=None,
                children=None,
                tax_year=family.tax_year
            )
            credits2 = self.calculate_non_refundable_credits(family_copy, net_income2, params)

        # Calculate basic tax
        basic_tax1 = self.calculate_basic_tax(taxable_income1, params)
        basic_tax2 = 0 if not family.adult2 else self.calculate_basic_tax(taxable_income2, params)

        # Calculate final taxes
        tax1 = max(0, basic_tax1 - credits1)
        tax2 = max(0, basic_tax2 - credits2)

        tax1 = -1 * round(tax1, 2)
        tax2 = -1 * round(tax2, 2)

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': tax1,
            'adult2': tax2,
            'total': tax1 + tax2,
            'details': {
                'family_net_income': family_net_income
            }
        }

def main():
    # Example usage
    tax_calc = QuebecIncomeTax()
    
    # Create a test family
    family = Family(
        family_status=FamilyStatus.SINGLE,
        adult1=AdultInfo(
            age=67,
            gross_work_income=0.0,
            gross_retirement_income=40000.0,
            is_retired=True
        ),
        tax_year=2024
    )
    
    # Calculate taxes
    result = tax_calc.calculate(family)
    
    # Print results
    print("\nResults:")
    print(f"Program: {result['program']}")
    print(f"Tax Year: {result['tax_year']}")
    print(f"Total Tax: ${abs(result['total']):,.2f}")
    print(f"\nDetails:")
    for key, value in result['details'].items():
        print(f"  {key}: ${abs(value):,.2f}")

if __name__ == "__main__":
    main()