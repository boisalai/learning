import json
import argparse
from decimal import Decimal, ROUND_HALF_UP
import unittest
from typing import Dict, List, Set, Tuple
from revdisp import (
    HouseholdType, 
    Person, 
    Household,
    RevenuDisponibleCalculator
)

class BaseCalculatorTest(unittest.TestCase):
    """Base class for calculator tests with common functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Load test data and extract years"""
        cls.test_cases = load_test_cases()
        cls.earlier_year, cls.later_year = extract_years(cls.test_cases)
        
        # Initialize calculators for both years
        cls.calculators = {
            cls.earlier_year: RevenuDisponibleCalculator(int(cls.earlier_year)),
            cls.later_year: RevenuDisponibleCalculator(int(cls.later_year))
        }
        
        # Define household type mapping
        cls.household_map = {
            "Personne vivant seule": HouseholdType.SINGLE,
            "Famille monoparentale": HouseholdType.SINGLE_PARENT,
            "Couple": HouseholdType.COUPLE,
            "Retraité vivant seul": HouseholdType.RETIRED_SINGLE,
            "Couple de retraités": HouseholdType.RETIRED_COUPLE
        }

    def create_person(self, params: Dict, is_primary: bool = True) -> Person:
        """Create a Person object from test case parameters with separate income types"""
        suffix = "1" if is_primary else "2"
        
        age_key = f'age_adulte{suffix}'
        household_type = params['situation']
        is_retired = 'retraité' in household_type.lower()
        
        work_income_key = f'revenu_brut_travail{suffix}'
        retirement_income_key = f'revenu_brut_retraite{suffix}'
    
        return Person(
            age=int(float(params[age_key])), 
            gross_work_income=Decimal(params[work_income_key]).quantize(Decimal('1'), rounding=ROUND_HALF_UP),
            self_employed_income=Decimal('0'),
            gross_retirement_income=Decimal(params[retirement_income_key]).quantize(Decimal('1'), rounding=ROUND_HALF_UP),
            is_retired=is_retired
        )

    def create_household(self, params: Dict) -> Household:
        """Create a Household object from test case parameters"""
        household_type = self.household_map[params['situation']]
        
        primary_person = self.create_person(params, is_primary=True)
        
        spouse = None
        if household_type in [HouseholdType.COUPLE, HouseholdType.RETIRED_COUPLE]:
            spouse = self.create_person(params, is_primary=False)
            
        enfants = [
            'Aucun enfant',
            'Un enfant',
            'Deux enfants',
            'Trois enfants',
            'Quatre enfants',
            'Cinq enfants'
        ]
        nb_enfants = params['nb_enfants']
        nb_enfants_int = enfants.index(nb_enfants)
        
        return Household(
            household_type=household_type,
            primary_person=primary_person,
            spouse=spouse,
            num_children=nb_enfants_int
        )

    def round_to_integer(self, value: Decimal) -> Decimal:
        """Round decimal to integer using ROUND_HALF_UP"""
        return Decimal(value).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

    def assertAmountEqual(self, calculated: Decimal, expected: Decimal, 
                         tolerance: Decimal = Decimal('1'), msg: str = ''):
        """Compare monetary amounts with tolerance"""
        difference = abs(calculated - expected)
        if difference > tolerance:
            standardMsg = f'Amounts differ by {difference}, which exceeds tolerance of {tolerance}'
            self.fail(self._formatMessage(msg, standardMsg))

class TestRevenuDisponible(BaseCalculatorTest):
    """Test all calculations against test data"""
    
    # Définir les programmes implémentés
    IMPLEMENTED_CONTRIBUTIONS = ['rrq', 'assurance_emploi', 'rqap', 'fss', 'ramq']
    IMPLEMENTED_QUEBEC = []  # Aucun programme québécois implémenté pour l'instant
    IMPLEMENTED_CANADA = []  # Aucun programme fédéral implémenté pour l'instant
    IMPLEMENTED_SUMMARY = []  # Aucun sommaire implémenté pour l'instant
    
    def test_calculations(self):
        """Test all calculations for each test case"""
        for test_case in self.test_cases:
            params = test_case['parametres']
            test_name = (f"Case {test_case['id']} - {params['situation']} - "
                        f"Revenu1: {params['revenu_brut_travail1']} + {params['revenu_brut_retraite1']}, "
                        f"Revenu2: {params['revenu_brut_travail2']} + {params['revenu_brut_retraite2']}, "
                        f"Ages: {params['age_adulte1']}/{params['age_adulte2']}")

            with self.subTest(test_name):
                household = self.create_household(params)
                expected = test_case['resultats']

                for year in [self.earlier_year, self.later_year]:
                    # Calculer tous les résultats
                    results = self.calculators[year].calculate(household)

                    # Comparer uniquement les composantes implémentées
                    if self.IMPLEMENTED_CONTRIBUTIONS:
                        self._compare_cotisations(results, expected, year, test_case['id'], params)
                    if self.IMPLEMENTED_QUEBEC:
                        self._compare_quebec(results, expected, year, test_case['id'], params)
                    if self.IMPLEMENTED_CANADA:
                        self._compare_canada(results, expected, year, test_case['id'], params)
                    if self.IMPLEMENTED_SUMMARY:
                        self._compare_summary(results, expected, year, test_case['id'], params)

    def _compare_cotisations(self, calculated: Dict, expected: Dict, 
                           year: str, case_id: int, params: Dict):
        """Compare social insurance contributions"""
        for program in self.IMPLEMENTED_CONTRIBUTIONS:
            calc_value = abs(calculated['cotisations'].get(program, 0))
            exp_value = abs(expected['cotisations'][program][year])
            
            self.assertAmountEqual(
                Decimal(str(calc_value)),
                Decimal(str(exp_value)),
                msg=f"\nMismatch for {program} in year {year}"
                    f"\nCase ID: {case_id}"
                    f"\nSituation: {params['situation']}"
                    f"\nRevenu1: {params['revenu_brut_travail1']} + {params['revenu_brut_retraite1']}"
                    f"\nRevenu2: {params['revenu_brut_travail2']} + {params['revenu_brut_retraite2']}"
                    f"\nExpected: {exp_value}"
                    f"\nGot: {calc_value}"
            )

    def _compare_quebec(self, calculated: Dict, expected: Dict, 
                       year: str, case_id: int, params: Dict):
        """Compare Quebec tax components"""
        for comp in self.IMPLEMENTED_QUEBEC:
            calc_value = abs(calculated['quebec'].get(comp, 0))
            exp_value = abs(expected['quebec'][comp][year])
            
            self.assertAmountEqual(
                Decimal(str(calc_value)),
                Decimal(str(exp_value)),
                msg=f"\nMismatch for Quebec {comp} in year {year}"
                    f"\nCase ID: {case_id}"
                    f"\nSituation: {params['situation']}"
                    f"\nExpected: {exp_value}"
                    f"\nGot: {calc_value}"
            )

    def _compare_canada(self, calculated: Dict, expected: Dict, 
                       year: str, case_id: int, params: Dict):
        """Compare federal components"""
        for comp in self.IMPLEMENTED_CANADA:
            calc_value = abs(calculated['canada'].get(comp, 0))
            exp_value = abs(expected['canada'][comp][year])
            
            self.assertAmountEqual(
                Decimal(str(calc_value)),
                Decimal(str(exp_value)),
                msg=f"\nMismatch for federal {comp} in year {year}"
                    f"\nCase ID: {case_id}"
                    f"\nSituation: {params['situation']}"
                    f"\nExpected: {exp_value}"
                    f"\nGot: {calc_value}"
            )

    def _compare_summary(self, calculated: Dict, expected: Dict, 
                        year: str, case_id: int, params: Dict):
        """Compare summary values"""
        for key in self.IMPLEMENTED_SUMMARY:
            calc_value = abs(calculated.get(key, 0))
            exp_value = abs(expected[key][year])
            
            self.assertAmountEqual(
                Decimal(str(calc_value)),
                Decimal(str(exp_value)),
                msg=f"\nMismatch for {key} in year {year}"
                    f"\nCase ID: {case_id}"
                    f"\nSituation: {params['situation']}"
                    f"\nExpected: {exp_value}"
                    f"\nGot: {calc_value}"
            )
            
def load_test_cases() -> List[Dict]:
    """Load test cases from resultats_{nobs}_cas.json"""
    parser = argparse.ArgumentParser(description='Test framework with configurable number of cases')
    parser.add_argument('--nobs', type=int, default=5,
                        help='Number of cases to test (default: 5)')
    args = parser.parse_args()

    input_filename = f'resultats_{args.nobs}_cas.json'
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File {input_filename} not found. Make sure to run script.py with --nobs {args.nobs} first.")

def extract_years(test_cases: List[Dict]) -> Tuple[str, str]:
    """Extract the years from the test cases results."""
    years = set()
    for case in test_cases:
        rrq_data = case['resultats']['cotisations']['rrq']
        years.update(str(year) for year in rrq_data.keys() if str(year).isdigit())
    
    if len(years) != 2:
        raise ValueError(f"Expected exactly 2 years in test data, found: {years}")
    
    years_list = sorted(list(years))
    return years_list[0], years_list[1]

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], verbosity=2)