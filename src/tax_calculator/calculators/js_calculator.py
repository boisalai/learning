"""
Wrapper class for the JavaScript tax calculator implementation.
Provides a Python interface to the existing JavaScript calculator.

2024-12-18: This code is completed.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from selenium.common.exceptions import WebDriverException
from tax_calculator.core import (
    BaseTaxCalculator,
    FamilyStatus,
    AdultInfo,
    ChildInfo,
    DaycareType,
    Family
)

class JSTaxCalculator(BaseTaxCalculator):
    """JavaScript implementation of the tax calculator"""
    
    def __init__(self):
        """Initialize the JavaScript calculator wrapper"""
        from selenium import webdriver
        from selenium.webdriver.firefox.service import Service
        
        project_root_path = Path(__file__).parent.parent
        static_folder_path = project_root_path / "static" 
        html_path = static_folder_path / "revdisp" / "html" / "calculator.html"
        print(html_path)

        if not html_path.exists():
            raise FileNotFoundError(f"Calculator HTML not found at: {html_path}")
            
        try:
            self.driver = webdriver.Firefox()
            self.driver.get(f"file://{html_path}")
        except WebDriverException as e:
            raise RuntimeError(f"Failed to initialize browser: {str(e)}")
            
    def __del__(self):
        """Cleanup browser when object is destroyed"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            
    def _select_by_text(self, element_id: str, text: str):
        """Select dropdown option by text"""
        from selenium.webdriver.common.by import By
        
        element = self.driver.find_element(By.ID, element_id)
        for option in element.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == text.strip():
                option.click()
                break
        self.driver.execute_script(f"recalc_onclick('{element_id}')")
        
    def _fill_field(self, selector: str, value: Any):
        """Fill input field with value"""
        from selenium.webdriver.common.by import By
        
        element = self.driver.find_element(By.ID, selector)
        element.clear()
        element.send_keys(str(value))
        self.driver.execute_script(f"recalc_onclick('{selector}')")
        
    def _extract_results(self) -> Dict[str, float]:
        """Extract calculation results from the page"""
        from selenium.webdriver.common.by import By
        
        results = {}
        result_fields = [
            # Revenus disponibles
            'RD_old', 'RD_new', 'RD_ecart',
            
            # Québec
            'QC_total_old', 'QC_total_new', 'QC_total_ecart',
            'QC_impot_st_old', 'QC_impot_st_new', 'QC_impot_st_ecart',
            'QC_impot_old', 'QC_impot_new', 'QC_impot_ecart',
            'QC_impot_bonif_old', 'QC_imppot_bonif_new', 'QC_impot_bonif_ecart',
            'QC_adr_old', 'QC_adr_new', 'QC_adr_ecart',
            'QC_sae_old', 'QC_sae_new', 'QC_sae_ecart',
            'SFS_old', 'SFS_new', 'SFS_ecart',
            'QC_pt_old', 'QC_pt_new', 'QC_pt_ecart',
            'QC_sol_old', 'QC_sol_new', 'QC_sol_ecart',
            'QC_garde_old', 'QC_garde_new', 'QC_garde_ecart',
            'QC_al_old', 'QC_al_new', 'QC_al_ecart',
            'QC_medic_old', 'QC_medic_new', 'QC_medic_ecart',
            'QC_aines_old', 'QC_aines_new', 'QC_aines_ecart',
            
            # Canada
            'CA_total_old', 'CA_total_new', 'CA_total_ecart',
            'CA_impot_old', 'CA_impot_new', 'CA_impot_ecart',
            'CA_ace_old', 'CA_ace_new', 'CA_ace_ecart',
            'CA_tps_old', 'CA_tps_new', 'CA_tps_ecart',
            'CA_pfrt_old', 'CA_pfrt_new', 'CA_pfrt_ecart',
            'CA_psv_old', 'CA_psv_new', 'CA_psv_ecart',
            'CA_medic_old', 'CA_medic_new', 'CA_medic_ecart',
            
            # Cotisations
            'Cotisation_old', 'Cotisation_new', 'Cotisation_ecart',
            'CA_ae_old', 'CA_ae_new', 'CA_ae_ecart',
            'QC_rqap_old', 'QC_rqap_new', 'QC_rqap_ecart',
            'CA_rrq_old', 'CA_rrq_new', 'CA_rrq_ecart',
            'QC_fss_old', 'QC_fss_new', 'QC_fss_ecart',
            'QC_ramq_old', 'QC_ramq_new', 'QC_ramq_ecart',
            
            # Frais
            'Frais_garde_old', 'Frais_garde_new', 'Frais_garde_ecart'
        ]
        
        for field in result_fields:
            element = self.driver.find_element(By.ID, field)
            value = element.get_attribute('value')
            
            # Handle empty or special characters
            if value.strip() in ['―', '−', '-', '']:
                results[field] = 0.0
                continue
                
            cleaned_value = (value.replace('−', '-')  # Replace Unicode minus with ASCII minus
                            .replace('―', '-')      # Replace horizontal bar with ASCII minus
                            .replace(' ', '')      # Remove spaces
                            .replace(',', '.'))    # Replace comma with dot
            try:
                results[field] = float(cleaned_value)
            except ValueError as e:
                raise ValueError(f"Could not convert value '{value}' for field '{field}': {str(e)}")            
        
        return results
        
    @property
    def supported_years(self) -> List[int]:
        """List of supported tax years"""
        return [2023, 2024]

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate using the JavaScript implementation"""
        family.validate()

        family_status = family.family_status
        adult1 = family.adult1
        adult2 = family.adult2
        children = family.children

        try:
            # Set family situation
            self._select_by_text('Situation', family_status.value)
            
            # Set primary adult info
            self._fill_field('Revenu1', adult1.gross_work_income + adult1.gross_retirement_income)
            self._fill_field('AgeAdulte1', adult1.age)
            
            # Set secondary adult info if present
            if adult2 is not None:
                self._fill_field('Revenu2', adult2.gross_work_income + adult2.gross_retirement_income)
                self._fill_field('AgeAdulte2', adult2.age)
            
            # Set children info if present
            num_children = len(children) if children else 0
            child_text = ('Aucun enfant' if num_children == 0 else
                         f"{num_children} enfant{'s' if num_children > 1 else ''}")
            self._select_by_text('NbEnfants', child_text)
            
            if children:
                for i, child in enumerate(children, 1):
                    self._fill_field(f'AgeEnfant{i}', child.age)
                    if child.daycare_cost > 0:
                        self._fill_field(f'Frais{i}', child.daycare_cost)
                        self._select_by_text(f'type_garde{i}', 
                                           child.daycare_type.value)
            
            # Get results after a short delay to ensure calculations complete
            import time
            time.sleep(0.01)
            return self._extract_results()
            
        except Exception as e:
            raise ValueError(f"JavaScript calculation failed: {str(e)}")

    def get_version(self) -> str:
        """Get the version identifier"""
        return "JS-1.0"  # You might want to extract this from your JS files


if __name__ == "__main__":
    calculator = JSTaxCalculator()
    
    # Test standard cases
    calculator.run_standard_test_cases()
    
    # Or test with generated cases
    # calculator.run_generated_test_cases(5)