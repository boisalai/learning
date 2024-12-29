"""
Senior Assistance Amount

References
    - https://www.revenuquebec.ca/fr/citoyens/credits-dimpot/credit-dimpot-pour-soutien-aux-aines/
    - https://www.budget.finances.gouv.qc.ca/budget/outils/depenses-fiscales/fiches/fiche-110108.asp
    - https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/credit-impot-soutien-aines/
    - https://www.rcgt.com/fr/planiguide/modules/module-04-sante-aines-et-aidants-naturels/autres-mesures-daide-aux-aines/
    - https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/parametres/AUTFR_RegimeImpot2024.pdf
    - https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/parametres/AUTFR_RegimeImpot2025.pdf
"""
"""
Senior Assistance Amount Calculator 

A refundable tax credit that provides financial support to low-income seniors aged 70
or older in Quebec.

References:
    - https://www.revenuquebec.ca/fr/citoyens/credits-dimpot/credit-dimpot-pour-soutien-aux-aines/
    - https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/credit-impot-soutien-aines/
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus

class SeniorAssistanceAmount(TaxProgram):
    """Calculator for Quebec's Senior Assistance Amount"""
    
    PARAMS = {
        2025: {
            'max_amount': {
                'single': 2000.0,
                'couple': 4000.0,
            },
            'reduction': {
                'single': {
                    'threshold': 27835.0,
                    'rate': 0.054
                },
                'couple': {
                    'threshold': 45370.0,
                    'rate': 0.0540
                }
            }
        },
        2024: {
            'max_amount': {
                'single': 2000.0,          # Maximum amount for single person
                'couple': 4000.0,          # Maximum amount for couple (2000$ x 2)
            },
            'reduction': {
                'single': {
                    'threshold': 27065.0,  # Income threshold for single person
                    'rate': 0.0531         # 5.31% reduction rate
                },
                'couple': {
                    'threshold': 44015.0,  # Income threshold for couple
                    'rate': 0.0531         # 5.31% reduction rate
                }
            }
        },
        2023: {
            'max_amount': {
                'single': 2000.0,
                'couple': 4000.0,
            },
            'reduction': {
                'single': {
                    'threshold': 25755.0,
                    'rate': 0.0516        # 5.16% reduction rate
                },
                'couple': {
                    'threshold': 41885.0,
                    'rate': 0.0516
                }
            }
        }
    }

    @property
    def name(self) -> str:
        return "Senior Assistance Amount"

    @property 
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())
        
    def _get_base_parameters(self, family: Family, params: dict) -> dict:
        """Get base parameters based on family type"""
        if not family.adult2:
            return {
                'max_amount': params['max_amount']['single'],
                'threshold': params['reduction']['single']['threshold'],
                'rate': params['reduction']['single']['rate']
            }
        return {
            'max_amount': params['max_amount']['couple'],
            'threshold': params['reduction']['couple']['threshold'],
            'rate': params['reduction']['couple']['rate']
        }

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate senior assistance amount for a family.
        
        The amount depends on:
        - Age of adults (must be 70+)
        - Family status (single/couple) 
        - Family income (for reduction calculation)
        """
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]
        
        # Basic eligibility - at least one adult must be 70+
        if family.adult1.age < 70 and (not family.adult2 or family.adult2.age < 70):
            return {
                'program': self.name,
                'tax_year': family.tax_year,
                'adult1': 0.0,
                'adult2': 0.0,
                'total': 0.0
            }

        # Get parameters based on family type
        base_params = self._get_base_parameters(family, params)
        
        # Calculate family income 
        family_income = family.adult1.income
        if family.adult2:
            family_income += family.adult2.income

        # Calculate reduction if income exceeds threshold
        if family_income <= base_params['threshold']:
            credit = base_params['max_amount']
        else:
            reduction = (family_income - base_params['threshold']) * base_params['rate']
            credit = max(0.0, base_params['max_amount'] - reduction)
            
        # Split between partners if couple where both are 70+
        if family.adult2 and family.adult1.age >= 70 and family.adult2.age >= 70:
            adult1_amount = credit / 2
            adult2_amount = credit / 2
        # Full amount to eligible adult in other cases
        elif family.adult2:
            if family.adult1.age >= 70:
                adult1_amount = credit
                adult2_amount = 0.0
            else:
                adult1_amount = 0.0
                adult2_amount = credit
        else:
            adult1_amount = credit
            adult2_amount = 0.0

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(adult1_amount, 2),
            'adult2': round(adult2_amount, 2),
            'total': round(credit, 2),
            'details': {
                'family_income': family_income,
                'base_amount': base_params['max_amount'],
                'reduction': None if family_income <= base_params['threshold'] else round(reduction, 2)
            }
        }

def chart():
    """Generate visualization of senior assistance amount calculation."""
    import numpy as np
    import matplotlib.pyplot as plt
    
    calc = SeniorAssistanceAmount()
    incomes = np.arange(0, 150001, 1000)
    
    scenarios = {
        'Single Person (age 70+)': Family(
            family_status=FamilyStatus.SINGLE,
            adult1=AdultInfo(age=70, gross_work_income=0),
            adult2=None,
            children=None,
            tax_year=2024
        ),
        'Couple (both 70+)': Family(
            family_status=FamilyStatus.COUPLE,
            adult1=AdultInfo(age=70, gross_work_income=0),
            adult2=AdultInfo(age=70, gross_work_income=0),
            children=None,
            tax_year=2024
        ),
        'Couple (one 70+)': Family(
            family_status=FamilyStatus.COUPLE,
            adult1=AdultInfo(age=70, gross_work_income=0),
            adult2=AdultInfo(age=60, gross_work_income=0),
            children=None,
            tax_year=2024
        )
    }
    
    plt.figure(figsize=(12, 6))
    
    for label, family in scenarios.items():
        benefits = []
        for income in incomes:
            family.adult1.gross_work_income = income/2 if family.adult2 else income
            if family.adult2:
                family.adult2.gross_work_income = income/2
            
            result = calc.calculate(family)
            benefits.append(result['total'])
            
        plt.plot(incomes, benefits, label=label, linewidth=2)
    
    plt.xlabel('Family Income ($)')
    plt.ylabel('Annual Benefit ($)')
    plt.title('Senior Assistance Amount by Family Type and Income (2024)')
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
    calculator = SeniorAssistanceAmount()
    
    test_cases = [
        {
            'name': 'Single senior',
            'family': Family(
                family_status=FamilyStatus.SINGLE,
                adult1=AdultInfo(age=75, gross_work_income=20000),
                adult2=None,
                children=None,
                tax_year=2024
            )
        },
        {
            'name': 'Senior couple (both 70+)',
            'family': Family(
                family_status=FamilyStatus.COUPLE,
                adult1=AdultInfo(age=72, gross_work_income=25000),
                adult2=AdultInfo(age=71, gross_work_income=15000),
                children=None,
                tax_year=2024
            )
        },
        {
            'name': 'Couple (one senior)',
            'family': Family(
                family_status=FamilyStatus.COUPLE,
                adult1=AdultInfo(age=70, gross_work_income=30000),
                adult2=AdultInfo(age=65, gross_work_income=20000),
                children=None,
                tax_year=2024
            )
        }
    ]
    
    print("\nSenior Assistance Amount Test Cases:")
    print("=" * 70)
    
    for case in test_cases:
        print(f"\nScenario: {case['name']}")
        result = calculator.calculate(case['family'])
        print(f"Family Income: ${result['details']['family_income']:,.2f}")
        print(f"Base Amount: ${result['details']['base_amount']:,.2f}")
        if result['details']['reduction']:
            print(f"Reduction: ${result['details']['reduction']:,.2f}")
        print(f"Total Benefit: ${result['total']:,.2f}")
        print("-" * 70)