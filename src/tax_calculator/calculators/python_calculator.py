"""
Python implementation of the tax calculator.
Implements all tax calculations in Python based on Quebec and Canada tax rules.
"""

from typing import Dict
from tax_calculator.core import BaseTaxCalculator, Family
from tax_calculator.fiscal_modules.contributions.employment_insurance import EmploymentInsurance
from tax_calculator.fiscal_modules.contributions.parental_insurance import ParentalInsurance

class PythonTaxCalculator(BaseTaxCalculator):    
    def __init__(self):
        """Initialize tax program calculators"""
        self.employment_insurance_calculator = EmploymentInsurance()
        self.parental_insurance_calculator = ParentalInsurance()

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate all tax components for the family"""
        self.validate_inputs(family)
        
        # Calculate Quebec taxation system components
        # TODO: Implement these calculators
        quebec_income_tax = {}  # To be implemented
        amount_before_tax_cut = {}  # To be implemented
        tax_cut = {}  # To be implemented
        social_assistance = {}  # To be implemented
        family_allowance = {}  # To be implemented
        school_supplies_supplement = {}  # To be implemented
        work_premium = {}  # To be implemented
        solidarity_tax_credit = {}
        childcare_expenses_credit = {}
        shelter_allowance = {}
        medical_expenses_credit = {}
        senior_assistance_amount = {}

        quebec_tax_system = {
            'program': 'Quebec Taxation System',
            'tax_year': family.tax_year,
            'adult1': 0.0,
            'adult2': 0.0,
            'total': 0.0,
        }

        # Calculate Federal tax system components
        # TODO: Implement these calculators
        federal_income_tax = {}  # To be implemented
        canada_child_benefit = {}
        gst_credit = {}
        canada_workers_benefit = {}
        old_age_security = {}
        medical_expenses_supplement = {}

        federal_tax_system = {
            'program': 'Federal Taxation System',
            'tax_year': family.tax_year,
            'adult1': 0.0,
            'adult2': 0.0,
            'total': 0.0,
        }

        # Calculate all contributions
        employment_insurance = self.employment_insurance_calculator.calculate(family)
        parental_insurance = self.parental_insurance_calculator.calculate(family)
        quebec_pension_plan = 0.0  # To be implemented
        health_services_fund = 0.0  # To be implemented
        quebec_prescription_drug_insurance = 0.0  # To be implemented

        # Total contributions
        contributions = {
            'program': "Contributions",
            'tax_year': family.tax_year,
            'adult1': employment_insurance['adult1'] + parental_insurance['adult1'],
            'adult2': employment_insurance['adult2'] + parental_insurance['adult2'],
            'total': employment_insurance['total'] + parental_insurance['total'],
        }
        
        # Calculate final disposable income
        disposable_income = quebec_tax_system['total'] + federal_tax_system['total'] + contributions['total']
        
        return {
            # Base results
            'disposable_income': disposable_income,
            
            # Quebec components
            'quebec_tax_system': {}, 
            'quebec_income_tax': {},  # To be implemented
            'amount_before_tax_cut': {},  # To be implemented
            'tax_cut': {},  # To be implemented
            'social_assistance': {},  # To be implemented
            'family_allowance': {},  # To be implemented
            'school_supplies_supplement': {},  # To be implemented
            'work_premium': {},  # To be implemented
            'solidarity_tax_credit': {},  # To be implemented
            'childcare_expenses_credit': {},  # To be implemented
            'shelter_allowance': {},  # To be implemented
            'medical_expenses_credit': {},  # To be implemented
            'senior_assistance_amount': {},  # To be implemented
            
            # Federal components
            'federal_tax_system': {},
            'federal_income_tax': {},
            'canada_child_benefit': {},
            'gst_credit': {},
            'canada_workers_benefit': {},
            'old_age_security': {},
            'medical_expenses_supplement': {},

            # Contributions
            'contributions': contributions,
            'employment_insurance': employment_insurance,
            'parental_insurance': {},
            'quebec_pension_plan': {},
            'health_services_fund': {},
            'quebec_prescription_drug_insurance': {}
        }
    
    def validate_inputs(self, family: Family) -> bool:
        """Validate family composition"""
        family.validate()
        return True
    
    def get_version(self) -> str:
        """Get calculator version"""
        return "PY-1.0"
        

if __name__ == "__main__":
    calculator = PythonTaxCalculator()
    
    # Test standard cases
    calculator.run_standard_test_cases()
    
    # Or test with generated cases
    # calculator.run_generated_test_cases(5)