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
from tax_calculator.fiscal_modules.quebec.family_allowance import FamilyAllowance
from tax_calculator.fiscal_modules.quebec.school_supplies_supplement import SchoolSuppliesSupplement
from tax_calculator.fiscal_modules.quebec.work_premium import WorkPremium
from tax_calculator.fiscal_modules.quebec.solidarity_tax_credit import SolidarityTaxCredit
from tax_calculator.fiscal_modules.quebec.childcare_expenses_credit import ChildcareExpensesCredit
from tax_calculator.fiscal_modules.quebec.shelter_allowance import ShelterAllowance
from tax_calculator.fiscal_modules.quebec.medical_expenses_credit import MedicalExpensesCredit
from tax_calculator.fiscal_modules.quebec.senior_assistance_amount import SeniorAssistanceAmount

from tax_calculator.fiscal_modules.canada.federal_income_tax import FederalIncomeTax
from tax_calculator.fiscal_modules.canada.canada_child_benefit import CanadaChildBenefit
from tax_calculator.fiscal_modules.canada.gst_credit import GSTCredit
from tax_calculator.fiscal_modules.canada.canada_workers_benefit import CanadaWorkersBenefit
from tax_calculator.fiscal_modules.canada.old_age_security import OldAgeSecurity
from tax_calculator.fiscal_modules.canada.medical_expenses_supplement import MedicalExpensesSupplement

from tax_calculator.fiscal_modules.contributions.employment_insurance import EmploymentInsurance
from tax_calculator.fiscal_modules.contributions.parental_insurance import ParentalInsurance
from tax_calculator.fiscal_modules.contributions.quebec_pension_plan import QuebecPensionPlan
from tax_calculator.fiscal_modules.contributions.health_services_fund import HealthServicesFund
from tax_calculator.fiscal_modules.contributions.quebec_prescription_drug_insurance import QuebecPrescriptionDrugInsurance

class PythonTaxCalculator(BaseTaxCalculator):
    """Python implementation of the tax calculator"""

    def __init__(self):
        """Initialize tax program calculators"""        
        self.quebec_income_tax = QuebecIncomeTax()
        self.social_assistance = SocialAssistance()
        self.family_allowance = FamilyAllowance()
        self.school_supplies_supplement = SchoolSuppliesSupplement()
        self.work_premium = WorkPremium()
        self.solidarity_tax_credit = SolidarityTaxCredit()
        self.childcare_expenses_credit = ChildcareExpensesCredit()
        self.shelter_allowance = ShelterAllowance()
        self.medical_expenses_credit = MedicalExpensesCredit()
        self.senior_assistance_amount = SeniorAssistanceAmount()

        self.federal_income_tax = FederalIncomeTax()
        self.canada_child_benefit = CanadaChildBenefit()
        self.gst_credit = GSTCredit()
        self.canada_workers_benefit = CanadaWorkersBenefit()
        self.old_age_security = OldAgeSecurity()
        self.medical_expenses_supplement = MedicalExpensesSupplement()
        
        self.employment_insurance_calculator = EmploymentInsurance()
        self.parental_insurance_calculator = ParentalInsurance()
        self.quebec_pension_plan = QuebecPensionPlan()
        self.health_services_fund = HealthServicesFund()
        self.quebec_prescription_drug_insurance = QuebecPrescriptionDrugInsurance()

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

        # Federal tax system components
        federal_income_tax = self.federal_income_tax.calculate(family)
        canada_child_benefit = self.canada_child_benefit.calculate(family)
        gst_credit = self.gst_credit.calculate(family)
        canada_workers_benefit = self.canada_workers_benefit.calculate(family)
        old_age_security = self.old_age_security.calculate(family)
        medical_expenses_supplement = self.medical_expenses_supplement.calculate(family)

        federal_tax_system = {
            'program': 'Federal Taxation System',
            'tax_year': family.tax_year,
            'adult1': 0.0,
            'adult2': 0.0,
            'total': 0.0,
        }

        # Quebec tax system components
        social_assistance = self.social_assistance.calculate(family)
        work_premium = self.work_premium.calculate(family)
        quebec_income_tax = QuebecIncomeTax().calculate(
            family,
            {
                'social_assistance': social_assistance,
                'employment_insurance': employment_insurance,
                'parental_insurance': parental_insurance,
                'quebec_pension_plan': quebec_pension_plan
            }
        )

        family_net_income = quebec_income_tax['family_net_income']
        family_allowance = self.family_allowance.calculate(family, family_net_income)
        solidarity_tax_credit = self.solidarity_tax_credit.calculate(family, family_net_income)        
        childcare_credit = self.childcare_expenses_credit.calculate(family, family_net_income)
        shelter_allowance = self.shelter_allowance.calculate(family, family_net_income)
        medical_expenses_credit = self.medical_expenses_credit.calculate(family, family_net_income)
        senior_assistance_amount = self.senior_assistance_amount.calculate(family, family_net_income)

        quebec_tax_system = {
            'program': 'Quebec Taxation System',
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
