"""
Medical Expenses Supplement Calculator

This supplement helps offset medical expenses for low-income families and individuals.
Any reimbursement of eligible medical expenses received from an employer or other 
health care plan reduces the medical expense.

References:
    - https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/supplement-remboursable-frais-medicaux-et-credit-impot-remboursable-frais-medicaux/
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo, ChildInfo

class MedicalExpensesSupplement(TaxProgram):
    """Calculator for Medical Expenses Supplement"""
    
    PARAMS = {
        2024: {
            'max_supplement': 1464.0,
            'rate': 0.25,
            'admissibility_threshold': 4275.0,  # Minimum employment income required
            'income_threshold': 32419.0,        # Income at which reduction begins
            'reduction_rate': 0.05              # Reduction rate above threshold
        },
        2023: {
            'max_supplement': 1400.0,           # Placeholder values for 2023
            'rate': 0.25,
            'admissibility_threshold': 4200.0,
            'income_threshold': 31068.0,
            'reduction_rate': 0.05
        }
    }

    @property
    def name(self) -> str:
        return "Medical Expenses Supplement"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def _calculate_employment_income(self, family: Family) -> float:
        """Calculate total family employment income."""
        employment_income = family.adult1.gross_work_income
        if family.adult2:
            employment_income += family.adult2.gross_work_income
        return employment_income

    def _calculate_family_income(self, family: Family) -> float:
        """Calculate total family net income."""
        income = family.adult1.income
        if family.adult2:
            income += family.adult2.income
        return income

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate medical expenses supplement for a family.
        
        The supplement is:
        1. Only available if employment income >= threshold
        2. 25% of eligible medical expenses up to maximum
        3. Reduced by 5% of family income above threshold
        """
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        # Get family medical expenses
        medical_expenses = getattr(family, 'medical_expenses', 0.0)
        if medical_expenses <= 0:
            return self._zero_response(family.tax_year)

        # Check employment income requirement
        employment_income = self._calculate_employment_income(family)
        if employment_income < params['admissibility_threshold']:
            return self._zero_response(family.tax_year)

        # Calculate base supplement (25% of medical expenses)
        base_supplement = min(
            medical_expenses * params['rate'],
            params['max_supplement']
        )

        # Calculate reduction based on family income
        family_income = self._calculate_family_income(family)
        if family_income > params['income_threshold']:
            reduction = (family_income - params['income_threshold']) * params['reduction_rate']
            supplement = max(0, base_supplement - reduction)
        else:
            reduction = 0
            supplement = base_supplement

        # Split between partners if applicable
        if family.adult2:
            adult1_share = supplement / 2
            adult2_share = supplement / 2
        else:
            adult1_share = supplement
            adult2_share = 0.0

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(adult1_share, 2),
            'adult2': round(adult2_share, 2),
            'total': round(supplement, 2),
            'details': {
                'employment_income': employment_income,
                'family_income': family_income,
                'medical_expenses': medical_expenses,
                'base_supplement': base_supplement,
                'reduction': reduction,
                'is_eligible': employment_income >= params['admissibility_threshold']
            }
        }

    def _zero_response(self, tax_year: int) -> Dict[str, float]:
        """Return a zero-value response."""
        return {
            'program': self.name,
            'tax_year': tax_year,
            'adult1': 0.0,
            'adult2': 0.0,
            'total': 0.0
        }

def chart():
    """Generate visualization of medical expenses supplement calculation."""
    import numpy as np
    import matplotlib.pyplot as plt
    
    supplement = MedicalExpensesSupplement()
    incomes = np.arange(0, 70001, 1000)
    
    scenarios = {
        '5000': 5000,
        '10000': 10000,
        '15000': 15000
    }
    
    plt.figure(figsize=(12, 6))
    
    for label, expenses in scenarios.items():
        benefits = []
        for income in incomes:
            # Create test family with sufficient employment income
            family = Family(
                family_status=FamilyStatus.SINGLE,
                adult1=AdultInfo(
                    age=30, 
                    gross_work_income=max(income/2, 4500)  # Ensure minimum employment income
                ),
                adult2=None,
                children=None,
                tax_year=2024
            )
            setattr(family, 'medical_expenses', float(expenses))
            
            result = supplement.calculate(family)
            benefits.append(result['total'])
            
        plt.plot(incomes, benefits, 
                label=f'Medical Expenses: ${expenses:,}',
                linewidth=2)
    
    # Add key thresholds
    params = supplement.PARAMS[2024]
    plt.axvline(x=params['income_threshold'], 
                color='gray', linestyle='--', alpha=0.5,
                label='Reduction Threshold')
    
    plt.xlabel('Family Income ($)')
    plt.ylabel('Annual Supplement ($)')
    plt.title('Medical Expenses Supplement by Income and Expense Level (2024)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # Generate visualization
    chart()
    
    # Test with sample cases
    calculator = MedicalExpensesSupplement()
    
    test_cases = [
        {
            'name': 'Single person with low income - Eligible',
            'family': Family(
                family_status=FamilyStatus.SINGLE,
                adult1=AdultInfo(age=30, gross_work_income=25000),
                adult2=None,
                children=None,
                tax_year=2024
            ),
            'medical_expenses': 5000
        },
        {
            'name': 'Single person - Below employment threshold',
            'family': Family(
                family_status=FamilyStatus.SINGLE,
                adult1=AdultInfo(age=30, gross_work_income=3000),
                adult2=None,
                children=None,
                tax_year=2024
            ),
            'medical_expenses': 5000
        },
        {
            'name': 'Family with high income - Partial benefit',
            'family': Family(
                family_status=FamilyStatus.COUPLE,
                adult1=AdultInfo(age=35, gross_work_income=35000),
                adult2=AdultInfo(age=33, gross_work_income=15000),
                children=[ChildInfo(age=5)],
                tax_year=2024
            ),
            'medical_expenses': 8000
        }
    ]
    
    print("\nMedical Expenses Supplement Test Cases:")
    print("=" * 70)
    
    for case in test_cases:
        print(f"\nScenario: {case['name']}")
        setattr(case['family'], 'medical_expenses', case['medical_expenses'])
        
        result = calculator.calculate(case['family'])
        
        print(f"Employment Income: ${result['details'].get('employment_income', 0):,.2f}")
        print(f"Family Income: ${result['details'].get('family_income', 0):,.2f}")
        print(f"Medical Expenses: ${result['details'].get('medical_expenses', 0):,.2f}")
        if result['details'].get('is_eligible', False):
            print(f"Base Supplement: ${result['details'].get('base_supplement', 0):,.2f}")
            print(f"Reduction: ${result['details'].get('reduction', 0):,.2f}")
        print(f"Final Supplement: ${result['total']:,.2f}")
        print("-" * 70)