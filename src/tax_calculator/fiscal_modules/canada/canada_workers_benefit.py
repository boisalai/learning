"""
Canada Workers Benefit (CWB) Calculator

The Canada Workers Benefit (CWB) is a refundable tax credit intended to supplement 
the earnings of low-income workers. It contains a basic benefit plus a supplement
for individuals eligible for the disability tax credit.

References:
    - https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-45300-canada-workers-benefit.html
    - https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-workers-benefit.html
    - https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/allocation-canadienne-travailleurs/
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo, ChildInfo

class CanadaWorkersBenefit(TaxProgram):
    """Calculator for Canada Workers Benefit"""
    
    PARAMS = {
        2024: {
            'basic': {
                'single': {
                    'excluded_income': 2400,
                    'rate': 0.373,
                    'max_amount': 3705,
                    'reduction_threshold': 13380,
                    'reduction_rate': 0.20,
                    'exit_threshold': 32357
                },
                'couple_no_child': {
                    'excluded_income': 3600,
                    'rate': 0.373,
                    'max_amount': 5779,
                    'reduction_threshold': 21257,
                    'reduction_rate': 0.20,
                    'exit_threshold': 50150
                },
                'single_parent': {
                    'excluded_income': 2400,
                    'rate': 0.20,
                    'max_amount': 1987,
                    'reduction_threshold': 13982,
                    'reduction_rate': 0.20,
                    'exit_threshold': 23916
                },
                'couple_with_child': {
                    'excluded_income': 3600,
                    'rate': 0.239,
                    'max_amount': 3703,
                    'reduction_threshold': 21457,
                    'reduction_rate': 0.20,
                    'exit_threshold': 39970
                },
                'second_earner_exemption': 15955
            },
            'disability': {
                'single': {
                    'excluded_income': 1200,
                    'rate': 0.40,
                    'max_amount': 828,
                    'reduction_threshold': 32357,
                    'reduction_rate': 0.20,
                    'exit_threshold': 36495
                },
                'couple_no_child': {
                    'excluded_income': 1200,
                    'rate': 0.20,
                    'max_amount': 828,
                    'reduction_threshold': 50150,
                    'reduction_rate': 0.20,
                    'exit_threshold': 54289,
                    'joint_disability_threshold': 58427,
                    'joint_disability_rate': 0.10
                },
                'single_parent': {
                    'excluded_income': 1200,
                    'rate': 0.40,
                    'max_amount': 828,
                    'reduction_threshold': 23916,
                    'reduction_rate': 0.20,
                    'exit_threshold': 28054
                },
                'couple_with_child': {
                    'excluded_income': 1200,
                    'rate': 0.20,
                    'max_amount': 828,
                    'reduction_threshold': 39670,
                    'reduction_rate': 0.20,
                    'exit_threshold': 44108,
                    'joint_disability_threshold': 48247,
                    'joint_disability_rate': 0.10
                }
            }
        },
        # Add similar structures for 2023 and 2025
    }

    @property
    def name(self) -> str:
        return "Canada Workers Benefit"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())
    
    def _get_family_type(self, family: Family) -> str:
        """Determine family type for parameter selection."""
        has_children = bool(family.children and len(family.children) > 0)
        has_partner = family.adult2 is not None

        if has_partner:
            if has_children:
                return 'couple_with_child'
            return 'couple_no_child'
        else:
            if has_children:
                return 'single_parent'
            return 'single'

    def _calculate_basic_benefit(self, family: Family, params: dict) -> float:
        """Calculate CWB basic amount."""
        family_type = self._get_family_type(family)
        basic_params = params['basic'][family_type]
        
        # Calculate working income
        working_income = family.adult1.gross_work_income
        if family.adult2:
            if family_type in ['couple_with_child', 'couple_no_child']:
                # Apply second earner exemption
                secondary_income = min(family.adult2.gross_work_income,
                                    params['basic']['second_earner_exemption'])
                working_income += family.adult2.gross_work_income - secondary_income
            else:
                working_income += family.adult2.gross_work_income

        # No benefit if income below excluded amount
        if working_income <= basic_params['excluded_income']:
            return 0.0
            
        # Calculate base benefit
        base_amount = min(
            basic_params['max_amount'],
            (working_income - basic_params['excluded_income']) * basic_params['rate']
        )
        
        # Calculate reduction based on family income
        family_income = (family.adult1.income + 
                        (family.adult2.income if family.adult2 else 0))
        
        if family_income <= basic_params['reduction_threshold']:
            return base_amount
            
        # Apply reduction rate
        reduction = (family_income - basic_params['reduction_threshold']) * basic_params['reduction_rate']
        return max(0, base_amount - reduction)

    def _calculate_disability_supplement(self, family: Family, params: dict) -> float:
        """Calculate CWB disability supplement."""
        has_disability = getattr(family.adult1, 'has_disability', False)
        partner_has_disability = family.adult2 and getattr(family.adult2, 'has_disability', False)
        
        if not (has_disability or partner_has_disability):
            return 0.0
            
        family_type = self._get_family_type(family)
        disability_params = params['disability'][family_type]
        
        # Calculate working income (similar logic as basic benefit)
        working_income = family.adult1.gross_work_income
        if family.adult2:
            working_income += family.adult2.gross_work_income

        # Calculate base supplement
        if working_income <= disability_params['excluded_income']:
            return 0.0
            
        base_amount = min(
            disability_params['max_amount'],
            (working_income - disability_params['excluded_income']) * disability_params['rate']
        )
        
        # Calculate reduction based on family income
        family_income = (family.adult1.income +
                        (family.adult2.income if family.adult2 else 0))
                        
        if family_income <= disability_params['reduction_threshold']:
            return base_amount
            
        # Determine reduction rate - lower if both partners have disability
        reduction_rate = (disability_params['joint_disability_rate'] 
                         if has_disability and partner_has_disability 
                         else disability_params['reduction_rate'])
            
        reduction = (family_income - disability_params['reduction_threshold']) * reduction_rate
        return max(0, base_amount - reduction)

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate CWB for a family."""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        # Basic eligibility checks
        if family.adult1.age < 19 and not family.children and not family.adult2:
            return {
                'program': self.name,
                'tax_year': family.tax_year,
                'adult1': 0.0,
                'adult2': 0.0,
                'total': 0.0
            }

        # Calculate benefits
        basic_benefit = self._calculate_basic_benefit(family, params)
        disability_supplement = self._calculate_disability_supplement(family, params)
        total_benefit = basic_benefit + disability_supplement

        # Split between partners if applicable
        if family.adult2:
            adult1_income = family.adult1.gross_work_income
            adult2_income = family.adult2.gross_work_income
            total_income = adult1_income + adult2_income
            
            if total_income > 0:
                adult1_share = (adult1_income / total_income) * total_benefit
                adult2_share = (adult2_income / total_income) * total_benefit
            else:
                adult1_share = total_benefit / 2
                adult2_share = total_benefit / 2
        else:
            adult1_share = total_benefit
            adult2_share = 0.0

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(adult1_share, 2),
            'adult2': round(adult2_share, 2),
            'total': round(total_benefit, 2),
            'details': {
                'basic_benefit': basic_benefit,
                'disability_supplement': disability_supplement
            }
        }

def chart():
    """Generate visualization of CWB calculation for different scenarios."""
    import numpy as np
    import matplotlib.pyplot as plt
    
    cwb = CanadaWorkersBenefit()
    incomes = np.arange(0, 60001, 1000)
    
    scenarios = {
        'Single': [AdultInfo(age=30, gross_work_income=0)],
        'Single Parent': [
            AdultInfo(age=30, gross_work_income=0),
            ChildInfo(age=5)
        ],
        'Couple': [
            AdultInfo(age=30, gross_work_income=0),
            AdultInfo(age=30, gross_work_income=0)
        ],
        'Couple with Children': [
            AdultInfo(age=30, gross_work_income=0),
            AdultInfo(age=30, gross_work_income=0),
            ChildInfo(age=5)
        ]
    }
    
    plt.figure(figsize=(12, 6))
    
    for label, scenario in scenarios.items():
        benefits = []
        for income in incomes:
            if len(scenario) == 1:  # Single
                adult = scenario[0]
                adult.gross_work_income = income
                family = Family(
                    family_status=FamilyStatus.SINGLE,
                    adult1=adult,
                    adult2=None,
                    children=None,
                    tax_year=2024
                )
            elif len(scenario) == 2 and isinstance(scenario[1], ChildInfo):  # Single parent
                adult = scenario[0]
                adult.gross_work_income = income
                family = Family(
                    family_status=FamilyStatus.SINGLE_PARENT,
                    adult1=adult,
                    adult2=None,
                    children=[scenario[1]],
                    tax_year=2024
                )
            else:  # Couples
                adult1, adult2 = scenario[0], scenario[1]
                adult1.gross_work_income = income * 0.6  # 60-40 split
                adult2.gross_work_income = income * 0.4
                children = [scenario[2]] if len(scenario) > 2 else None
                family = Family(
                    family_status=FamilyStatus.COUPLE,
                    adult1=adult1,
                    adult2=adult2,
                    children=children,
                    tax_year=2024
                )
                
            result = cwb.calculate(family)
            benefits.append(result['total'])
    
        plt.plot(incomes, benefits, label=label, linewidth=2)
    
    plt.xlabel('Family Work Income ($)')
    plt.ylabel('Annual Benefit ($)')
    plt.title('Canada Workers Benefit by Family Type (2024)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # Generate visualization
    chart()
    
    # Test with sample families
    calculator = CanadaWorkersBenefit()
    
    # Test case 1: Single person
    test_family1 = Family(
        family_status=FamilyStatus.SINGLE,
        adult1=AdultInfo(age=30, gross_work_income=20000),
        adult2=None,
        children=None,
        tax_year=2024
    )
    
    print("\nTest Case 1 - Single person making $20,000")
    result1 = calculator.calculate(test_family1)
    print(f"Basic Benefit: ${result1['details']['basic_benefit']:,.2f}")
    print(f"Total Benefit: ${result1['total']:,.2f}")
    
    # Test case 2: Couple with children
    test_family2 = Family(
        family_status=FamilyStatus.COUPLE,
        adult1=AdultInfo(age=35, gross_work_income=25000),
        adult2=AdultInfo(age=33, gross_work_income=15000),
        children=[ChildInfo(age=5), ChildInfo(age=7)],
        tax_year=2024
    )
    
    print("\nTest Case 2 - Couple with children making $40,000 combined")
    result2 = calculator.calculate(test_family2)
    print(f"Basic Benefit: ${result2['details']['basic_benefit']:,.2f}")
    print(f"Total Benefit: ${result2['total']:,.2f}")