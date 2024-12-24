"""
Canada Child Benefit

The Canada child benefit (CCB) is administered by the Canada Revenue Agency (CRA). 
It is a tax-free monthly payment made to eligible families to help with the cost
of raising children under 18 years of age. 

Parameters:
    - https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-child-benefit-overview.html
    - [Feuilles de calcul](https://www.canada.ca/fr/agence-revenu/services/prestations-enfants-familles/allocation-canadienne-enfants-apercu/feuilles-calcul-allocation-canadienne-enfants.html)
"""

from typing import Dict, List, Any
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo, ChildInfo


class CanadaChildBenefit(TaxProgram):
    PARAMS = {
        2024: {
            'max_amount': {
                'under_6': 7787.0,  # Per year for each child under 6
                'over_6': 6570.0,   # Per year for each child 6-17
            },
            'thresholds': {
                'first': 36502.0,   # First income threshold
                'second': 79087.0,  # Second income threshold
            },
            'reduction_rates': {
                1: {  # One child
                    'first_threshold': 0.07,   # 7% reduction rate
                    'second_threshold': 0.032,  # 3.2% reduction rate
                    'second_base': 2981.0      # Base reduction for second threshold
                },
                2: {  # Two children
                    'first_threshold': 0.135,  # 13.5% reduction rate
                    'second_threshold': 0.057,  # 5.7% reduction rate
                    'second_base': 5749.0      # Base reduction for second threshold
                },
                3: {  # Three children
                    'first_threshold': 0.19,   # 19% reduction rate
                    'second_threshold': 0.08,   # 8% reduction rate
                    'second_base': 8091.0      # Base reduction for second threshold
                },
                4: {  # Four or more children
                    'first_threshold': 0.23,   # 23% reduction rate
                    'second_threshold': 0.095,  # 9.5% reduction rate
                    'second_base': 9795.0      # Base reduction for second threshold
                }
            },
            'disability_benefit': {
                'base_amount': 3322.0,  # Base amount per eligible child
                'threshold': 79087.0,   # Income threshold
                'reduction_rates': {
                    1: 0.032,  # One disabled child
                    2: 0.057   # Two or more disabled children
                }
            }
        },
        2023: {
            # For the July 2023 to June 2024 payments (2022 base year)
            # https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-child-benefit-overview/canada-child-benefit-ccb-calculation-sheet-july-2023-june-2024-payments-2022-tax-year.html
            'max_amount': {
                'under_6': 7437.0,  # Per year for each child under 6
                'over_6': 6275.0,   # Per year for each child 6-17
            },
            'thresholds': {
                'first': 34863.0,   # First income threshold
                'second': 75537.0,  # Second income threshold
            },
            'reduction_rates': {
                1: {  # One child
                    'first_threshold': 0.07,   # 7% reduction rate
                    'second_threshold': 0.032,  # 3.2% reduction rate
                    'second_base': 2847.0      # Base reduction for second threshold
                },
                2: {  # Two children
                    'first_threshold': 0.135,  # 13.5% reduction rate
                    'second_threshold': 0.057,  # 5.7% reduction rate
                    'second_base': 5491.0      # Base reduction for second threshold
                },
                3: {  # Three children
                    'first_threshold': 0.19,   # 19% reduction rate
                    'second_threshold': 0.08,   # 8% reduction rate
                    'second_base': 7728.0      # Base reduction for second threshold
                },
                4: {  # Four or more children
                    'first_threshold': 0.23,   # 23% reduction rate
                    'second_threshold': 0.095,  # 9.5% reduction rate
                    'second_base': 9355.0      # Base reduction for second threshold
                }
            },
            'disability_benefit': {
                'base_amount': 3173.0,  # Base amount per eligible child
                'threshold': 75537.0,   # Income threshold
                'reduction_rates': {
                    1: 0.032,  # One disabled child
                    2: 0.057   # Two or more disabled children
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
        """Calculate base benefit amount before reductions"""
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
        """Calculate benefit reduction based on income"""
        if not family.children:
            return 0.0
            
        # Calculate adjusted family income
        family_income = family.adult1.income
        if family.adult2:
            family_income += family.adult2.income

        num_children = len(family.children)
        if num_children > 4:
            num_children = 4  # Use 4+ children rates for more than 4 children
            
        reduction = 0.0
        
        # No reduction if income below first threshold
        # TODO: Ajuster ici pour utiliser le revenu familial net ajusté (voir https://www.canada.ca/fr/agence-revenu/services/prestations-enfants-familles/allocation-canadienne-enfants-apercu/allocation-canadienne-enfants-comment-calculons-nous-votre-ace.html#family-net-income-definition) 
        if family_income <= params['thresholds']['first']:
            return 0.0
            
        # Calculate reduction for income between thresholds
        rates = params['reduction_rates'][num_children]
        
        if family_income <= params['thresholds']['second']:
            # Only first threshold reduction applies
            reduction = (family_income - params['thresholds']['first']) * rates['first_threshold']
        else:
            # Both threshold reductions apply
            reduction = (
                # First threshold reduction
                (params['thresholds']['second'] - params['thresholds']['first']) 
                * rates['first_threshold']
                # Second threshold reduction
                + (family_income - params['thresholds']['second']) 
                * rates['second_threshold']
                + rates['second_base']
            )
            
        return min(reduction, base_benefit)  # Cannot reduce below zero

    def _calculate_disability_benefit(self, family: Family, params: dict) -> float:
        """Calculate additional benefit for disabled children"""
        if not family.children:
            return 0.0
            
        # Count disabled children
        num_disabled = sum(1 for child in family.children if getattr(child, 'has_disability', False))
        if num_disabled == 0:
            return 0.0
            
        # Calculate base disability benefit
        base_benefit = num_disabled * params['disability_benefit']['base_amount']
        
        # Calculate reduction based on income
        family_income = family.adult1.income + (family.adult2.income if family.adult2 else 0)
        if family_income <= params['disability_benefit']['threshold']:
            return base_benefit
            
        # Apply reduction rate based on number of disabled children
        rate = params['disability_benefit']['reduction_rates'][min(2, num_disabled)]
        reduction = (family_income - params['disability_benefit']['threshold']) * rate
        
        return max(0.0, base_benefit - reduction)

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate CCB benefit for a family"""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]
        
        # Calculate regular CCB benefit
        base_benefit = self._calculate_base_benefit(family, params)
        reduction = self._calculate_reduction(family, base_benefit, params)
        ccb_benefit = max(0.0, base_benefit - reduction)
        
        # Calculate disability supplement if applicable
        disability_benefit = self._calculate_disability_benefit(family, params)
        
        # Total benefit
        total_benefit = ccb_benefit + disability_benefit
        
        # For shared custody, split 50/50
        if family.family_status == FamilyStatus.SINGLE_PARENT:
            total_benefit *= 0.5
            
        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': total_benefit,  # Primary caregiver gets full amount
            'adult2': 0.0,           # Secondary parent gets 0
            'total': total_benefit,
            'details': {
                'base_benefit': base_benefit,
                'reduction': reduction,
                'disability_benefit': disability_benefit
            }
        }

def chart():
    """Visualize Canada Child Benefit calculation"""
    import numpy as np
    import matplotlib.pyplot as plt

    incomes = np.arange(0, 200001, 1000)
    benefits_1child = []
    benefits_2child = []
    benefits_3child = []
    
    ccb = CanadaChildBenefit()
    
    # Calculate benefits for different family sizes
    for income in incomes:
        # One child under 6
        family1 = Family(
            family_status=FamilyStatus.SINGLE_PARENT,
            adult1=AdultInfo(age=30, gross_work_income=income),
            children=[ChildInfo(age=3)]
        )
        result1 = ccb.calculate(family1)
        benefits_1child.append(result1['total'])
        
        # Two children under 6
        family2 = Family(
            family_status=FamilyStatus.SINGLE_PARENT,
            adult1=AdultInfo(age=30, gross_work_income=income),
            children=[ChildInfo(age=3), ChildInfo(age=4)]
        )
        result2 = ccb.calculate(family2)
        benefits_2child.append(result2['total'])
        
        # Three children under 6
        family3 = Family(
            family_status=FamilyStatus.SINGLE_PARENT,
            adult1=AdultInfo(age=30, gross_work_income=income),
            children=[ChildInfo(age=3), ChildInfo(age=4), ChildInfo(age=5)]
        )
        result3 = ccb.calculate(family3)
        benefits_3child.append(result3['total'])

    plt.figure(figsize=(10, 6))
    plt.plot(incomes, benefits_1child, label='One child')
    plt.plot(incomes, benefits_2child, label='Two children')
    plt.plot(incomes, benefits_3child, label='Three children')
    
    plt.xlabel('Family Income ($)')
    plt.ylabel('Annual Benefit ($)')
    plt.title('Canada Child Benefit by Family Income and Number of Children (2024)')
    plt.grid(True)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    chart()