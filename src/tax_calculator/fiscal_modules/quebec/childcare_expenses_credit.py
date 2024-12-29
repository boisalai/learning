"""
Quebec Childcare Expenses Tax Credit Calculator

A refundable tax credit that helps offset childcare costs for Quebec residents who
incur such expenses while working, studying, or looking for work.

References:
    - https://www.revenuquebec.ca/fr/citoyens/credits-dimpot/credit-dimpot-pour-frais-de-garde-denfants/
    - https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/parametres/AUTFR_RegimeImpot2025.pdf
    - https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/parametres/AUTFR_RegimeImpot2024.pdf
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo, ChildInfo

class ChildcareExpensesCredit(TaxProgram):
    """Calculator for Quebec's Childcare Expenses Tax Credit"""

    PARAMS = {
        2025: {
            'expense_limits': {
                'disabled': 16800,           # Child with severe disability
                'under_7': 12275,            # Child under 7 years old
                'other': 6180                # Any other eligible child
            },
            'camp_limits': {
                'under_7': -1,              # Per week, child under 7
                'disabled': -1,             # Per week, disabled child
                'other': -1                 # Per week, other eligible child
            },
            'child_income_limit': 13658,
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
                'disabled': 16335,           # Child with severe disability
                'under_7': 11935,            # Child under 7 years old
                'other': 6010                # Any other eligible child
            },
            'camp_limits': {
                'under_7': 200,              # Per week, child under 7
                'disabled': 275,             # Per week, disabled child
                'other': 125                 # Per week, other eligible child
            },
            'child_income_limit': 13280,    # Maximum income for dependent child
            'rate_schedule': [
                (24110, 0.78),              # Up to $24,110: 78%
                (42515, 0.75),              # $24,110 to $42,515: 75%
                (44085, 0.74),              # And so on...
                (45670, 0.73),
                (47225, 0.72),
                (48805, 0.71),
                (116515, 0.70),
                (float('inf'), 0.67)        # Over $116,515: 67%
            ]
        },
        2023: {
            'expense_limits': {
                'disabled': 15545,           # Child with severe disability
                'under_7': 11360,            # Child under 7 years old
                'other': 5720                # Any other eligible child
            },
            'camp_limits': {
                'under_7': -1,              # Per week, child under 7
                'disabled': -1,             # Per week, disabled child
                'other': -1                 # Per week, other eligible child
            },
            'child_income_limit': 12638,    # Maximum income for dependent child
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
        return "Childcare Expenses Tax Credit"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())
        
    def _validate_expenses(self, child: ChildInfo) -> bool:
        """Validate if childcare expenses are eligible."""
        if not hasattr(child, 'daycare_expenses'):
            return False
            
        if not hasattr(child, 'daycare_type'):
            return False
            
        # Check if expenses are for eligible care types
        # (would need to expand this based on specific rules)
        return True

    def _get_applicable_limit(self, child: ChildInfo, params: dict) -> float:
        """Determine the applicable expense limit for a child."""
        if getattr(child, 'has_disability', False):
            return params['expense_limits']['disabled']
        elif child.age < 7:
            return params['expense_limits']['under_7']
        else:
            return params['expense_limits']['other']

    def _get_credit_rate(self, family_income: float, params: dict) -> float:
        """Determine the applicable credit rate based on family income."""
        for threshold, rate in params['rate_schedule']:
            if family_income <= threshold:
                return rate
        return params['rate_schedule'][-1][1]  # Return lowest rate if above all thresholds

    def _calculate_eligible_expenses(self, family: Family, params: dict) -> Dict[str, float]:
        """Calculate total eligible expenses considering limits."""
        if not family.children:
            return {'total': 0, 'details': {}}
            
        total_eligible = 0
        details = {}
        
        for i, child in enumerate(family.children):
            child_id = f'child_{i+1}'
            
            # Skip if no childcare expenses
            if not hasattr(child, 'daycare_expenses') or child.daycare_expenses <= 0:
                details[child_id] = 0
                continue
                
            # Validate expense eligibility
            if not self._validate_expenses(child):
                details[child_id] = 0
                continue
                
            # Get and apply applicable limit
            limit = self._get_applicable_limit(child, params)
            eligible_amount = min(child.daycare_expenses, limit)
            
            # Add to total
            details[child_id] = eligible_amount
            total_eligible += eligible_amount
            
        return {
            'total': total_eligible,
            'details': details
        }

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate childcare expenses credit for the family."""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        # Calculate family income
        family_income = family.adult1.income
        if family.adult2:
            family_income += family.adult2.income

        # Calculate eligible expenses
        expense_calc = self._calculate_eligible_expenses(family, params)
        eligible_expenses = expense_calc['total']

        if eligible_expenses <= 0:
            return {
                'program': self.name,
                'tax_year': family.tax_year,
                'adult1': 0.0,
                'adult2': 0.0,
                'total': 0.0
            }

        # Get applicable credit rate
        rate = self._get_credit_rate(family_income, params)
        
        # Calculate credit
        credit = eligible_expenses * rate

        # Split between partners if applicable
        if family.adult2:
            adult1_share = credit / 2
            adult2_share = credit / 2
        else:
            adult1_share = credit
            adult2_share = 0.0

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(adult1_share, 2),
            'adult2': round(adult2_share, 2),
            'total': round(credit, 2),
            'details': {
                'family_income': family_income,
                'eligible_expenses': expense_calc['details'],
                'total_eligible_expenses': eligible_expenses,
                'credit_rate': rate
            }
        }

def chart():
    """Generate visualization of childcare expenses credit calculation."""
    import numpy as np
    import matplotlib.pyplot as plt
    
    credit = ChildcareExpensesCredit()
    incomes = np.arange(0, 150001, 1000)
    
    scenarios = {
        '1 Child Under 7': (11935, [ChildInfo(age=5, daycare_expenses=11935)]),
        '2 Children Under 7': (23870, [
            ChildInfo(age=3, daycare_expenses=11935),
            ChildInfo(age=5, daycare_expenses=11935)
        ]),
        'Child with Disability': (16335, [
            ChildInfo(age=5, daycare_expenses=16335, has_disability=True)
        ])
    }
    
    plt.figure(figsize=(12, 6))
    
    for label, (expenses, children) in scenarios.items():
        credits = []
        for income in incomes:
            # Create test family
            family = Family(
                family_status=FamilyStatus.SINGLE_PARENT,
                adult1=AdultInfo(age=30, gross_work_income=income),
                adult2=None,
                children=children,
                tax_year=2024
            )
            
            result = credit.calculate(family)
            credits.append(result['total'])
            
        plt.plot(incomes, credits, 
                label=f'{label} (${expenses:,} expenses)',
                linewidth=2)

    plt.xlabel('Family Income ($)')
    plt.ylabel('Tax Credit ($)')
    plt.title('Quebec Childcare Expenses Credit by Income and Scenario (2024)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Format axis labels
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # Generate visualization
    chart()
    
    # Test with sample cases
    calculator = ChildcareExpensesCredit()
    
    test_cases = [
        {
            'name': 'Single parent, one child in daycare',
            'family': Family(
                family_status=FamilyStatus.SINGLE_PARENT,
                adult1=AdultInfo(age=35, gross_work_income=45000),
                adult2=None,
                children=[
                    ChildInfo(age=4, daycare_expenses=12000)
                ],
                tax_year=2024
            )
        },
        {
            'name': 'Couple, two children in daycare',
            'family': Family(
                family_status=FamilyStatus.COUPLE,
                adult1=AdultInfo(age=35, gross_work_income=60000),
                adult2=AdultInfo(age=33, gross_work_income=40000),
                children=[
                    ChildInfo(age=3, daycare_expenses=11935),
                    ChildInfo(age=5, daycare_expenses=11935)
                ],
                tax_year=2024
            )
        },
        {
            'name': 'Single parent, child with disability',
            'family': Family(
                family_status=FamilyStatus.SINGLE_PARENT,
                adult1=AdultInfo(age=40, gross_work_income=50000),
                adult2=None,
                children=[
                    ChildInfo(age=6, daycare_expenses=16335, has_disability=True)
                ],
                tax_year=2024
            )
        }
    ]
    
    print("\nChildcare Expenses Credit Test Cases:")
    print("=" * 70)
    
    for case in test_cases:
        print(f"\nScenario: {case['name']}")
        result = calculator.calculate(case['family'])
        print(f"Family Income: ${result['details']['family_income']:,.2f}")
        print(f"Total Eligible Expenses: ${result['details']['total_eligible_expenses']:,.2f}")
        print(f"Credit Rate: {result['details']['credit_rate']*100:.1f}%")
        print(f"Credit Amount: ${result['total']:,.2f}")
        print("-" * 70)
