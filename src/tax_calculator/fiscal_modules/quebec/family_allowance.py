"""
Quebec Family Allowance Calculator.

A non-taxable refundable tax credit provided to Quebec families with children under 18.
The allowance includes a universal base amount plus additional support for low and
middle-income families.

References
    - https://www.rrq.gouv.qc.ca/fr/programmes/soutien_enfants/paiement/Pages/montant.aspx
    - https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/allocation-famille/
    - https://www.rcgt.com/fr/planiguide/modules/module-02-lindividu-et-la-famille/aide-aux-parents/
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo, ChildInfo

class FamilyAllowance(TaxProgram):
    """Calculator for Quebec Family Allowance."""
    
    PARAMS = {
        2024: {
            'base_amounts': {
                'couple': {
                    'per_child': {
                        'max': 2923,
                        'min': 1163
                    },
                    'reduction': {
                        'threshold': 57822,
                        'rate': 0.04
                    },
                    'exit_thresholds': {
                        1: 101822,  # 1 child
                        2: 145822,  # 2 children
                        3: 189822,  # 3 children
                        4: 233822   # 4+ children
                    }
                },
                'single_parent': {
                    'per_child': {
                        'max': 2923,
                        'min': 1163
                    },
                    'supplement': {
                        'max': 1026,
                        'min': 409
                    },
                    'reduction': {
                        'threshold': 42136,
                        'rate': 0.04
                    },
                    'exit_thresholds': {
                        1: 101561,  # 1 child
                        2: 145561,  # 2 children
                        3: 189561,  # 3 children
                        4: 233561   # 4+ children
                    }
                }
            },
            'school_supplies': {
                'amount': 121,
                'min_age': 4,
                'max_age': 16,
                'reference_date': '09-30'  # September 30th
            },
            'disability': {
                'base': {
                    'monthly': 229,
                    'annual': 2748
                },
                'exceptional_care': {
                    'tier1': {
                        'monthly': 1158,
                        'annual': 13896
                    },
                    'tier2': {
                        'monthly': 770,
                        'annual': 9240
                    }
                }
            }
        }
    }

    @property
    def name(self) -> str:
        return "Family Allowance"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def _get_base_parameters(self, family: Family, params: dict) -> dict:
        """Get base parameters based on family type."""
        if family.family_status == FamilyStatus.SINGLE_PARENT:
            return params['base_amounts']['single_parent']
        return params['base_amounts']['couple']

    def _count_eligible_children(self, family: Family) -> int:
        """Count number of children under 18."""
        if not family.children:
            return 0
        return sum(1 for child in family.children if child.age < 18)

    def _calculate_base_amount(self, family: Family, family_income: float, params: dict) -> float:
        """Calculate base amount before reductions."""
        base_params = self._get_base_parameters(family, params)
        num_children = self._count_eligible_children(family)
        
        if num_children == 0:
            return 0.0

        # Calculate per-child amount
        if family_income <= base_params['reduction']['threshold']:
            per_child = base_params['per_child']['max']
        else:
            # Calculate reduction
            reduction = (family_income - base_params['reduction']['threshold']) * base_params['reduction']['rate']
            per_child = max(
                base_params['per_child']['min'],
                base_params['per_child']['max'] - (reduction / num_children)
            )
        
        base_amount = per_child * num_children

        # Add single parent supplement if applicable
        if family.family_status == FamilyStatus.SINGLE_PARENT:
            if family_income <= base_params['reduction']['threshold']:
                base_amount += base_params['supplement']['max']
            else:
                supp_reduction = (family_income - base_params['reduction']['threshold']) * base_params['reduction']['rate']
                supplement = max(
                    base_params['supplement']['min'],
                    base_params['supplement']['max'] - supp_reduction
                )
                base_amount += supplement

        return base_amount

    def _calculate_school_supplies(self, family: Family, params: dict) -> float:
        """Calculate school supplies supplement."""
        if not family.children:
            return 0.0
            
        eligible_children = sum(
            1 for child in family.children
            if params['school_supplies']['min_age'] <= child.age <= params['school_supplies']['max_age']
        )
        
        return eligible_children * params['school_supplies']['amount']

    def _calculate_disability_supplement(self, family: Family, params: dict) -> Dict[str, float]:
        """Calculate disability supplements."""
        if not family.children:
            return {'base': 0.0, 'exceptional': 0.0}
            
        base_amount = 0.0
        exceptional_amount = 0.0
        
        for child in family.children:
            if child.age >= 18:
                continue
                
            if getattr(child, 'has_disability', False):
                base_amount += params['disability']['base']['annual']
                
            exceptional_care = getattr(child, 'exceptional_care_tier', None)
            if exceptional_care == 1:
                exceptional_amount += params['disability']['exceptional_care']['tier1']['annual']
            elif exceptional_care == 2:
                exceptional_amount += params['disability']['exceptional_care']['tier2']['annual']
                
        return {
            'base': base_amount,
            'exceptional': exceptional_amount
        }

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate family allowance amounts."""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        # Calculate family income
        family_income = family.adult1.income
        if family.adult2:
            family_income += family.adult2.income

        # Calculate components
        base_amount = self._calculate_base_amount(family, family_income, params)
        school_supplies = self._calculate_school_supplies(family, params)
        disability = self._calculate_disability_supplement(family, params)
        
        total = base_amount + school_supplies + disability['base'] + disability['exceptional']

        # For shared custody, split 50-50
        if getattr(family, 'shared_custody', False):
            adult1_share = total / 2
            adult2_share = total / 2
        else:
            adult1_share = total
            adult2_share = 0.0

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(adult1_share, 2),
            'adult2': round(adult2_share, 2),
            'total': round(total, 2),
            'details': {
                'family_income': family_income,
                'base_amount': base_amount,
                'school_supplies': school_supplies,
                'disability_base': disability['base'],
                'disability_exceptional': disability['exceptional']
            }
        }

def chart():
    """Generate visualization of family allowance calculation."""
    import numpy as np
    import matplotlib.pyplot as plt
    
    allowance = FamilyAllowance()
    incomes = np.arange(0, 250001, 1000)
    
    scenarios = {
        'Couple - 1 Child': Family(
            family_status=FamilyStatus.COUPLE,
            adult1=AdultInfo(age=30, gross_work_income=0),
            adult2=AdultInfo(age=30, gross_work_income=0),
            children=[ChildInfo(age=5)],
            tax_year=2024
        ),
        'Couple - 2 Children': Family(
            family_status=FamilyStatus.COUPLE,
            adult1=AdultInfo(age=30, gross_work_income=0),
            adult2=AdultInfo(age=30, gross_work_income=0),
            children=[ChildInfo(age=5), ChildInfo(age=7)],
            tax_year=2024
        ),
        'Single Parent - 1 Child': Family(
            family_status=FamilyStatus.SINGLE_PARENT,
            adult1=AdultInfo(age=30, gross_work_income=0),
            adult2=None,
            children=[ChildInfo(age=5)],
            tax_year=2024
        )
    }
    
    plt.figure(figsize=(12, 6))
    
    for label, base_family in scenarios.items():
        allowances = []
        for income in incomes:
            family = base_family
            # Update income (60-40 split for couples)
            if family.family_status == FamilyStatus.COUPLE:
                family.adult1.gross_work_income = income * 0.6
                family.adult2.gross_work_income = income * 0.4
            else:
                family.adult1.gross_work_income = income
            
            result = allowance.calculate(family)
            allowances.append(result['total'])
            
        plt.plot(incomes, allowances, label=label, linewidth=2)
    
    plt.xlabel('Family Income ($)')
    plt.ylabel('Annual Allowance ($)')
    plt.title('Quebec Family Allowance by Family Type and Income (2024)')
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
    calculator = FamilyAllowance()
    
    test_cases = [
        {
            'name': 'Couple with one child',
            'family': Family(
                family_status=FamilyStatus.COUPLE,
                adult1=AdultInfo(age=30, gross_work_income=40000),
                adult2=AdultInfo(age=30, gross_work_income=20000),
                children=[ChildInfo(age=5)],
                tax_year=2024
            )
        },
        {
            'name': 'Single parent with two children',
            'family': Family(
                family_status=FamilyStatus.SINGLE_PARENT,
                adult1=AdultInfo(age=35, gross_work_income=45000),
                adult2=None,
                children=[
                    ChildInfo(age=6),
                    ChildInfo(age=8)
                ],
                tax_year=2024
            )
        },
        {
            'name': 'Couple with disabled child',
            'family': Family(
                family_status=FamilyStatus.COUPLE,
                adult1=AdultInfo(age=40, gross_work_income=50000),
                adult2=AdultInfo(age=38, gross_work_income=30000),
                children=[
                    ChildInfo(age=10, has_disability=True, exceptional_care_tier=1)
                ],
                tax_year=2024
            )
        }
    ]
    
    print("\nQuebec Family Allowance Test Cases:")
    print("=" * 70)
    
    for case in test_cases:
        print(f"\nScenario: {case['name']}")
        result = calculator.calculate(case['family'])
        print(f"Family Income: ${result['details']['family_income']:,.2f}")
        print(f"Base Amount: ${result['details']['base_amount']:,.2f}")
        if result['details']['school_supplies'] > 0:
            print(f"School Supplies: ${result['details']['school_supplies']:,.2f}")
        if result['details']['disability_base'] > 0:
            print(f"Disability Supplement: ${result['details']['disability_base']:,.2f}")
        if result['details']['disability_exceptional'] > 0:
            print(f"Exceptional Care Supplement: ${result['details']['disability_exceptional']:,.2f}")
        print(f"Total Allowance: ${result['total']:,.2f}")
        print("-" * 70)