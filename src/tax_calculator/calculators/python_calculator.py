"""
Python implementation of the tax calculator.
Implements all tax calculations in Python based on Quebec and Canada tax rules.
"""

from typing import Dict, List
from tax_calculator.core import (
    BaseTaxCalculator,
    FamilyStatus,
    AdultInfo,
    ChildInfo,
    DaycareType,
    Family
)

from tax_calculator.fiscal_modules.quebec.quebec_income_tax import QuebecIncomeTax
from tax_calculator.fiscal_modules.quebec.social_assistance import SocialAssistance
from tax_calculator.fiscal_modules.quebec.childcare_expenses_credit import ChildcareExpensesCredit

from tax_calculator.fiscal_modules.contributions.employment_insurance import EmploymentInsurance
from tax_calculator.fiscal_modules.contributions.health_services_fund import HealthServicesFund
from tax_calculator.fiscal_modules.contributions.parental_insurance import ParentalInsurance
from tax_calculator.fiscal_modules.contributions.quebec_pension_plan import QuebecPensionPlan
from tax_calculator.fiscal_modules.contributions.quebec_prescription_drug_insurance import QuebecPrescriptionDrugInsurance

class PythonTaxCalculator(BaseTaxCalculator):
    """Python implementation of the tax calculator"""

    def __init__(self):
        """Initialize tax program calculators"""
        self.employment_insurance_calculator = EmploymentInsurance()
        self.parental_insurance_calculator = ParentalInsurance()
        self.quebec_pension_plan = QuebecPensionPlan()
        self.health_services_fund = HealthServicesFund()
        self.quebec_prescription_drug_insurance = QuebecPrescriptionDrugInsurance()

        self.quebec_income_tax = QuebecIncomeTax()
        self.social_assistance = SocialAssistance()
        self.childcare_expenses_credit = ChildcareExpensesCredit()


    @property
    def supported_years(self) -> List[int]:
        """List of supported tax years"""
        return [2023, 2024]

    def calculate(self, family: Family) -> dict:
        """Calculate taxes for the given family"""
        family.validate()  # Directly validate the family composition

        # Calculate contributions
        employment_insurance = self.employment_insurance_calculator.calculate(family)
        parental_insurance = self.parental_insurance_calculator.calculate(family)
        quebec_pension_plan = self.quebec_pension_plan.calculate(family)
        health_services_fund = self.health_services_fund.calculate(family)
        quebec_prescription_drug_insurance = self.quebec_prescription_drug_insurance.calculate(family)

        social_assistance = self.social_assistance.calculate(family)
        quebec_income_tax = QuebecIncomeTax().calculate(
            family,
            {
                'social_assistance': social_assistance,
                'employment_insurance': employment_insurance,
                'parental_insurance': parental_insurance,
                'quebec_pension_plan': quebec_pension_plan
            }
        )

        # Calculate childcare credit
        family_net_income = quebec_income_tax['family_net_income']
        childcare_credit = self.childcare_expenses_credit.calculate(family, family_net_income)

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


        # Total contributions
        adult1 = (
            employment_insurance["adult1"]
            + parental_insurance["adult1"]
            + quebec_pension_plan["adult1"]
            + health_services_fund["adult1"]
            + quebec_prescription_drug_insurance["adult1"]
        )
        adult2 = (
            employment_insurance["adult2"]
            + parental_insurance["adult2"]
            + quebec_pension_plan["adult2"]
            + health_services_fund["adult2"]
            + quebec_prescription_drug_insurance["adult2"]
        )

        contributions = {
            'program': "Contributions",
            'tax_year': family.tax_year,
            'adult1': adult1,
            'adult2': adult2,
            'total': adult1 + adult2
        }

        # Calculate total daycare costs
        total_daycare_costs = sum(child.daycare_cost for child in family.children)
        total_daycare_costs = -1 * round(total_daycare_costs, 2)

        # Calculate final disposable income
        disposable_income = (
            quebec_tax_system["total"]
            + federal_tax_system["total"]
            + contributions["total"]
            + total_daycare_costs
        )

        # Proceed with calculations
        results = {
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
            'parental_insurance': parental_insurance,
            'quebec_pension_plan': quebec_pension_plan,
            'health_services_fund': health_services_fund,
            'quebec_prescription_drug_insurance': quebec_prescription_drug_insurance,

            # Daycare costs
            'daycare_costs': total_daycare_costs
        }

        return results

    def get_version(self) -> str:
        """Get calculator version"""
        return "PY-1.0"


if __name__ == "__main__":
    calculator = PythonTaxCalculator()
    
    # Test standard cases
    calculator.run_standard_test_cases()
    
    # Or test with generated cases
    # calculator.run_generated_test_cases(5)
