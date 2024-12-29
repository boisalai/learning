"""
Canada Child Benefit (CCB) Calculator

The Canada Child Benefit (CCB) is administered by the Canada Revenue Agency (CRA). 
It is a tax-free monthly payment made to eligible families to help with the cost
of raising children under 18 years of age. 

References:
    - https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-child-benefit-overview.html
    - https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-child-benefit-overview/canada-child-benefit-we-calculate-your-ccb.html
    - https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-child-benefit-overview/canada-child-benefit-ccb-calculation-sheet-july-2023-june-2024-payments-2022-tax-year.html
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo, ChildInfo

class CanadaChildBenefit(TaxProgram):
    """Calculator for Canada Child Benefit"""
    
    PARAMS = {
        2025: {
            'max_amount': {
                'under_6': 7787.0,    # Maximum annual amount per child under 6
                'over_6': 6570.0      # Maximum annual amount per child 6-17
            },
            'thresholds': {
                'first': 36502.0,     # First income threshold
                'second': 79087.0     # Second income threshold
            },
            'reduction_rates': {
                1: {  # One child
                    'first': 0.07,    # 7% reduction rate for first threshold
                    'second': 0.032,  # 3.2% reduction rate for second threshold
                    'second_base': 2981.0  # Base reduction amount for second threshold
                },
                2: {  # Two children
                    'first': 0.135,   # 13.5% reduction rate
                    'second': 0.057,  # 5.7% reduction rate
                    'second_base': 5749.0
                },
                3: {  # Three children
                    'first': 0.19,    # 19% reduction rate
                    'second': 0.08,   # 8% reduction rate
                    'second_base': 8091.0
                },
                4: {  # Four or more children
                    'first': 0.23,    # 23% reduction rate
                    'second': 0.095,  # 9.5% reduction rate
                    'second_base': 9795.0
                }
            }
        },
        2024: {
            'max_amount': {
                'under_6': 7437.0,
                'over_6': 6275.0
            },
            'thresholds': {
                'first': 34863.0,
                'second': 75537.0
            },
            'reduction_rates': {
                1: {
                    'first': 0.07,
                    'second': 0.032,
                    'second_base': 2847.0
                },
                2: {
                    'first': 0.135,
                    'second': 0.057,
                    'second_base': 5491.0
                },
                3: {
                    'first': 0.19,
                    'second': 0.08,
                    'second_base': 7728.0
                },
                4: {
                    'first': 0.23,
                    'second': 0.095,
                    'second_base': 9355.0
                }
            }
        },
        2023: {
            'max_amount': {
                'under_6': 7097.0,
                'over_6': 5986.0
            },
            'thresholds': {
                'first': 33997.0, 
                'second': 73656.0
            },
            'reduction_rates': {
                1: {
                    'first': 0.07,
                    'second': 0.032,
                    'second_base': 2776.0
                },
                2: {
                    'first': 0.135,
                    'second': 0.057,
                    'second_base': 5356.0
                },
                3: {
                    'first': 0.19,
                    'second': 0.08,
                    'second_base': 7536.0
                },
                4: {
                    'first': 0.23,
                    'second': 0.095,
                    'second_base': 9126.0
                }
            }
        }
    }

    @property
    def name(self) -> str:
        return "Canada Child Benefit"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def _calculate_base_benefit(self, family: Family, params: dict) -> float:
        """Calculate base benefit amount before reductions."""
        if not family.children:
            return 0.0
            
        total = 0.0
        for child in family.children:
            if child.age < 6:
                total += params['max_amount']['under_6']
            elif child.age <= 17:
                total += params['max_amount']['over_6']
                
        return total

    def _calculate_reduction(self, family: Family, base_benefit: float, params: dict) -> float:
        """Calculate benefit reduction based on family income."""
        if not family.children:
            return 0.0
            
        # Calculate adjusted family net income
        family_income = (family.adult1.gross_work_income + family.adult1.gross_retirement_income +
                      (family.adult2.gross_work_income + family.adult2.gross_retirement_income if family.adult2 else 0))

        # Determine number of children (max 4 for reduction rates)
        num_children = min(len(family.children), 4)
        
        # No reduction if income below first threshold
        if family_income <= params['thresholds']['first']:
            return 0.0
            
        # Get reduction rates for number of children
        rates = params['reduction_rates'][num_children]
        
        # Calculate reduction based on income thresholds
        if family_income <= params['thresholds']['second']:
            # Only first threshold reduction applies
            reduction = (family_income - params['thresholds']['first']) * rates['first']
        else:
            # Both threshold reductions apply
            reduction = (
                # First threshold reduction
                (params['thresholds']['second'] - params['thresholds']['first']) 
                * rates['first']
                # Second threshold reduction
                + (family_income - params['thresholds']['second']) 
                * rates['second']
                + rates['second_base']
            )
            
        return min(reduction, base_benefit)  # Cannot reduce below zero

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate CCB benefit for a family."""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]
        
        # Calculate regular CCB benefit
        base_benefit = self._calculate_base_benefit(family, params)
        reduction = self._calculate_reduction(family, base_benefit, params)
        total_benefit = max(0.0, base_benefit - reduction)
        
        # For shared custody, split 50/50
        if family.family_status == FamilyStatus.SINGLE_PARENT and getattr(family, 'shared_custody', False):
            total_benefit *= 0.5
            
        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': total_benefit,  # Primary caregiver gets full amount
            'adult2': 0.0,           # Secondary parent gets 0
            'total': total_benefit,
            'details': {
                'base_benefit': base_benefit,
                'reduction': reduction
            }
        }

def chart():
    """Generate visualization of CCB calculation."""
    import numpy as np
    import matplotlib.pyplot as plt
    
    ccb = CanadaChildBenefit()
    incomes = np.arange(0, 200001, 1000)
    
    # Calculate benefits for different family compositions
    scenarios = {
        '1 child under 6': [ChildInfo(age=3)],
        '2 children under 6': [ChildInfo(age=3), ChildInfo(age=4)],
        '3 children under 6': [ChildInfo(age=3), ChildInfo(age=4), ChildInfo(age=5)]
    }
    
    benefits = {}
    for label, children in scenarios.items():
        benefits[label] = []
        for income in incomes:
            family = Family(
                family_status=FamilyStatus.SINGLE_PARENT,
                adult1=AdultInfo(age=30, gross_work_income=income),
                adult2=None,
                children=children,
                tax_year=2024
            )
            result = ccb.calculate(family)
            benefits[label].append(result['total'])
    
    # Create visualization
    plt.figure(figsize=(12, 6))
    for label, vals in benefits.items():
        plt.plot(incomes, vals, label=label, linewidth=2)
    
    plt.xlabel('Family Net Income ($)')
    plt.ylabel('Annual Benefit ($)')
    plt.title('Canada Child Benefit by Family Income and Number of Children (2024)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Format axis labels
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.show()

# For testing
if __name__ == "__main__":
    # Generate visualization
    chart()
    
    # Test with a sample family
    calculator = CanadaChildBenefit()
    
    test_family = Family(
        family_status=FamilyStatus.SINGLE_PARENT,
        adult1=AdultInfo(age=35, gross_work_income=40000),
        adult2=None,
        children=[
            ChildInfo(age=4),
            ChildInfo(age=7)
        ],
        tax_year=2024
    )
    
    result = calculator.calculate(test_family)
    print("\nTest Case Results:")
    print(f"Base Benefit: ${result['details']['base_benefit']:,.2f}")
    print(f"Reduction: ${result['details']['reduction']:,.2f}")
    print(f"Total Benefit: ${result['total']:,.2f}")