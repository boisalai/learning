"""
Solidarity Tax Credit

References
    - https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/credit-impot-solidarite/
    - https://www.revenuquebec.ca/fr/citoyens/credits-dimpot/credit-dimpot-pour-solidarite/
    - https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/parametres/AUTFR_RegimeImpot2024.pdf
    - https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/parametres/AUTFR_RegimeImpot2025.pdf
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus

class SolidarityTaxCredit(TaxProgram):
    """Quebec Solidarity Tax Credit calculator"""
    
    PARAMS = {
        2025: {
            'GST': {
                'base_amount': 356.0,
                'spouse_amount': 356.0,
                'single_supplement': 169.0
            },
            'housing': {
                'couple_amount': 888.0,
                'single_amount': 731.0,
                'child_supplement': 155.0,
                'shared_custody_supplement': 75.50  # Half of child supplement
            },
            'northern': {
                'base_amount': 2091.0,
                'spouse_amount': 2091.0,
                'child_amount': 452.0,
                'shared_custody_amount': 256.0  # Half of child amount
            },
            'reduction': {
                'threshold': 42325.0,
                'rate_single': 0.03,
                'rate_multiple': 0.06
            },
            'debt_threshold': 25665.0  # Only 50% of credit can be used for debt if income <= this amount
        },
        2024: {
            'GST': {
                'base_amount': 346.0,
                'spouse_amount': 346.0,
                'single_supplement': 164.0
            },
            'housing': {
                'couple_amount': 863.0,
                'single_amount': 711.0,
                'child_supplement': 151.0,
                'shared_custody_supplement': 75.50  # Half of child supplement
            },
            'northern': {
                'base_amount': 2033.0,
                'spouse_amount': 2033.0,
                'child_amount': 439.0,
                'shared_custody_amount': 219.50  # Half of child amount
            },
            'reduction': {
                'threshold': 41150.0,
                'rate_single': 0.03,
                'rate_multiple': 0.06
            },
            'debt_threshold': 24955.0  # Only 50% of credit can be used for debt if income <= this amount
        },
        2023: {
            'GST': {
                'base_amount': 329.0,
                'spouse_amount': 329.0,
                'single_supplement': 156.0
            },
            'housing': {
                'couple_amount': 821.0,
                'single_amount': 677.0,
                'child_supplement': 144.0,
                'shared_custody_supplement': 72.0
            },
            'northern': {
                'base_amount': 1935.0,
                'spouse_amount': 1935.0,
                'child_amount': 418.0,
                'shared_custody_amount': 209.0
            },
            'reduction': {
                'threshold': 39160.0,
                'rate_single': 0.03,
                'rate_multiple': 0.06
            },
            'debt_threshold': 23750.0
        }
    }

    @property
    def name(self) -> str:
        return "Solidarity Tax Credit"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def calculate_gst_component(self, family: Family, params: dict) -> float:
        """Calculate GST component of solidarity tax credit"""
        amount = params['GST']['base_amount']
        
        if family.adult2:
            # Add spouse amount for couples
            amount += params['GST']['spouse_amount']
        elif not family.adult2:
            # Add single person supplement for those living alone
            amount += params['GST']['single_supplement']

        return amount

    def calculate_housing_component(self, family: Family, params: dict) -> float:
        """Calculate housing component of solidarity tax credit"""
        # Base amount depends on family composition
        if family.adult2:
            amount = params['housing']['couple_amount']
        else:
            amount = params['housing']['single_amount']
            
        # Add supplement for each child
        if family.children:
            for child in family.children:
                if hasattr(child, 'shared_custody') and child.shared_custody:
                    amount += params['housing']['shared_custody_supplement']
                else:
                    amount += params['housing']['child_supplement']
            
        return amount

    def calculate_northern_component(self, family: Family, params: dict) -> float:
        """Calculate northern village component of solidarity tax credit"""
        # Skip if not in northern village
        if not hasattr(family, 'in_northern_village') or not family.in_northern_village:
            return 0.0
            
        amount = params['northern']['base_amount']
        
        # Add spouse amount if applicable
        if family.adult2:
            amount += params['northern']['spouse_amount']
            
        # Add amount for each child
        if family.children:
            for child in family.children:
                if hasattr(child, 'shared_custody') and child.shared_custody:
                    amount += params['northern']['shared_custody_amount']
                else:
                    amount += params['northern']['child_amount']
                
        return amount
        
    def calculate_reduction(self, total_components: float, family_income: float, num_components: int, params: dict) -> float:
        """Calculate reduction based on family income"""
        if family_income <= params['reduction']['threshold']:
            return 0.0
            
        excess_income = family_income - params['reduction']['threshold']
        rate = params['reduction']['rate_multiple'] if num_components > 1 else params['reduction']['rate_single']
        
        reduction = excess_income * rate
        return min(reduction, total_components)  # Reduction cannot exceed total components

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate solidarity tax credit for a family"""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        # Calculate each component
        gst_component = self.calculate_gst_component(family, params)
        housing_component = self.calculate_housing_component(family, params) 
        northern_component = self.calculate_northern_component(family, params)

        # Count number of non-zero components for reduction rate
        components = [gst_component, housing_component, northern_component]
        num_components = sum(1 for x in components if x > 0)
        
        # Calculate total before reduction
        total_before_reduction = sum(components)

        # Calculate family income
        family_income = family.adult1.income
        if family.adult2:
            family_income += family.adult2.income

        # Apply reduction
        reduction = self.calculate_reduction(
            total_before_reduction,
            family_income,
            num_components,
            params
        )
        
        # Calculate final amount after reduction
        total_after_reduction = max(0, total_before_reduction - reduction)
        
        # The credit cannot be less than the GST component
        total = max(total_after_reduction, gst_component)
        
        # Split between adults if couple
        if family.adult2:
            adult1_amount = total / 2
            adult2_amount = total / 2
        else:
            adult1_amount = total
            adult2_amount = 0.0

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(adult1_amount, 2),
            'adult2': round(adult2_amount, 2),
            'total': round(total, 2),
            'details': {
                'gst_component': round(gst_component, 2),
                'housing_component': round(housing_component, 2),
                'northern_component': round(northern_component, 2),
                'total_before_reduction': round(total_before_reduction, 2),
                'reduction': round(reduction, 2),
                'family_income': round(family_income, 2)
            }
        }