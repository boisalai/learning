"""
Quebec Shelter Allowance Calculator.

A program that provides financial assistance to low-income households who spend a large portion 
of their income on housing. The amount varies based on family composition, income level, and 
housing costs.

References
    - https://www.revenuquebec.ca/fr/citoyens/votre-situation/faible-revenu/programme-allocation-logement/
    - https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/allocation-logement/
    - https://cdn-contenu.quebec.ca/cdn-contenu/gouvernement/MCE/dossiers-soumis-conseil-ministres/2022-2041.pdf 
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo, ChildInfo

class ShelterAllowance(TaxProgram):
    """Calculator for Quebec's Shelter Allowance Program"""
    
    PARAMS = {
        2024: {
            'income_thresholds': {
                'single_50_plus': 24440,
                'couple_50_plus': 33540,
                'couple_one_child': 40740,
                'single_parent_1_2_children': 40740,
                'couple_multiple_children': 46640,
                'single_parent_3plus_children': 46640
            },
            'housing_cost_threshold': 0.30,  # 30% of family income
            'benefit_amounts': {
                'low_burden': 100,  # For 30-49.9% housing cost ratio
                'medium_burden': 150,  # For 50-79.9% housing cost ratio
                'high_burden': 170   # For 80%+ housing cost ratio
            },
            'minimum_age': 50,
            'asset_limit': 50000,  # Excluding registered savings
        },
        2023: {
            'income_thresholds': {
                'single_50_plus': 23285,
                'couple_50_plus': 31990,
                'couple_one_child': 38835,
                'single_parent_1_2_children': 38835,
                'couple_multiple_children': 44485,
                'single_parent_3plus_children': 44485
            },
            'housing_cost_threshold': 0.30,
            'benefit_amounts': {
                'low_burden': 100,
                'medium_burden': 150,
                'high_burden': 170
            },
            'minimum_age': 50,
            'asset_limit': 50000
        }
    }

    @property
    def name(self) -> str:
        return "Shelter Allowance"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def _get_family_category(self, family: Family) -> str:
        """Determine the family category for threshold lookup"""
        num_children = len(family.children) if family.children else 0
        
        if not family.adult2:  # Single adult
            if num_children == 0 and family.adult1.age >= self.PARAMS[family.tax_year]['minimum_age']:
                return 'single_50_plus'
            elif num_children <= 2:
                return 'single_parent_1_2_children'
            else:
                return 'single_parent_3plus_children'
        else:  # Couple
            has_50_plus = (family.adult1.age >= self.PARAMS[family.tax_year]['minimum_age'] or 
                          family.adult2.age >= self.PARAMS[family.tax_year]['minimum_age'])
            
            if num_children == 0 and has_50_plus:
                return 'couple_50_plus'
            elif num_children == 1:
                return 'couple_one_child'
            else:
                return 'couple_multiple_children'

    def _calculate_housing_cost_ratio(self, family: Family) -> float:
        """Calculate ratio of housing costs to family income"""
        # Get annual housing costs
        annual_housing_cost = getattr(family, 'annual_housing_cost', 0.0)
        
        # Calculate family income
        family_income = family.adult1.income
        if family.adult2:
            family_income += family.adult2.income
            
        if family_income <= 0:
            return 0.0
            
        return annual_housing_cost / family_income

    def _get_benefit_amount(self, housing_cost_ratio: float, params: dict) -> float:
        """Determine benefit amount based on housing cost ratio"""
        if housing_cost_ratio < params['housing_cost_threshold']:
            return 0.0
        elif housing_cost_ratio < 0.50:
            return params['benefit_amounts']['low_burden']
        elif housing_cost_ratio < 0.80:
            return params['benefit_amounts']['medium_burden']
        else:
            return params['benefit_amounts']['high_burden']

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate shelter allowance for a family"""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        # Check basic eligibility
        if not hasattr(family, 'annual_housing_cost') or family.annual_housing_cost <= 0:
            return self._zero_response(family.tax_year)

        # Get family category and income threshold
        category = self._get_family_category(family)
        income_threshold = params['income_thresholds'].get(category)
        
        if not income_threshold:
            return self._zero_response(family.tax_year)

        # Calculate family income
        family_income = family.adult1.income
        if family.adult2:
            family_income += family.adult2.income

        # Check income eligibility
        if family_income > income_threshold:
            return self._zero_response(family.tax_year)

        # Calculate housing cost ratio
        housing_cost_ratio = self._calculate_housing_cost_ratio(family)
        
        # Get benefit amount
        benefit = self._get_benefit_amount(housing_cost_ratio, params)

        # Split benefit for couples
        if family.adult2:
            adult1_share = benefit / 2
            adult2_share = benefit / 2
        else:
            adult1_share = benefit
            adult2_share = 0.0

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(adult1_share, 2),
            'adult2': round(adult2_share, 2),
            'total': round(benefit, 2),
            'details': {
                'family_category': category,
                'family_income': family_income, 
                'income_threshold': income_threshold,
                'housing_cost_ratio': round(housing_cost_ratio * 100, 1),
                'is_eligible': benefit > 0
            }
        }

    def _zero_response(self, tax_year: int) -> Dict[str, float]:
        """Return a zero-value response"""
        return {
            'program': self.name,
            'tax_year': tax_year,
            'adult1': 0.0,
            'adult2': 0.0,
            'total': 0.0
        }