"""
Core definitions for the tax calculator system.
Contains base classes and common data structures used across all calculator implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List
from pathlib import Path

class FamilyStatus(Enum):
    """Enumeration of possible family situations"""
    SINGLE = "Personne vivant seule"
    SINGLE_PARENT = "Famille monoparentale"
    COUPLE = "Couple"
    RETIRED_SINGLE = "Retraité vivant seul"
    RETIRED_COUPLE = "Couple de retraités"

class DaycareType(Enum):
    """Enumeration of possible daycare types"""
    SUBSIDIZED = "Subventionnée"
    NON_SUBSIDIZED = "Non subventionnée"

@dataclass
class AdultInfo:
    """Information about an adult"""
    age: int
    _income: float = 0.0  # Total income (private)
    _gross_work_income: float = 0.0
    _self_employed_income: float = 0.0
    _gross_retirement_income: float = 0.0
    is_retired: bool = False

    def __init__(
        self,
        age: int,
        gross_work_income: float = 0.0,
        self_employed_income: float = 0.0,
        gross_retirement_income: float = 0.0,
        is_retired: bool = False
    ):
        """
        Initialize an adult's information.
        
        Args:
            age: Age of the adult
            gross_work_income: Income from employment
            self_employed_income: Income from self-employment
            gross_retirement_income: Income from retirement
            is_retired: Whether the adult is retired
        """
        self.age = age
        self._gross_work_income = gross_work_income
        self._self_employed_income = self_employed_income
        self._gross_retirement_income = gross_retirement_income
        self.is_retired = is_retired
        self._update_total_income()

    @property
    def income(self) -> float:
        return self._income

    @property
    def gross_work_income(self) -> float:
        return self._gross_work_income

    @gross_work_income.setter
    def gross_work_income(self, value: float) -> None:
        self._gross_work_income = value
        self._update_total_income()

    @property
    def self_employed_income(self) -> float:
        return self._self_employed_income

    @self_employed_income.setter
    def self_employed_income(self, value: float) -> None:
        self._self_employed_income = value
        self._update_total_income()

    @property
    def gross_retirement_income(self) -> float:
        return self._gross_retirement_income

    @gross_retirement_income.setter
    def gross_retirement_income(self, value: float) -> None:
        self._gross_retirement_income = value
        self._update_total_income()

    def _update_total_income(self) -> None:
        """Update total income when any income source changes"""
        self._income = (
            self._gross_work_income +
            self._self_employed_income +
            self._gross_retirement_income
        )

@dataclass
class ChildInfo:
    """Information about a child"""
    age: int
    daycare_cost: float = 0.0
    daycare_type: Optional[DaycareType] = None

@dataclass
class Family:
    """Represents a family unit for tax calculations"""
    status: FamilyStatus
    adult1: AdultInfo
    adult2: Optional[AdultInfo] = None
    children: Optional[List[ChildInfo]] = None
    tax_year: int = 2024

    def validate(self) -> None:
        """
        Validate family composition based on family status.
        
        Raises:
            ValueError: If the family composition is invalid
        """
        if 'Couple' in self.status.value and self.adult2 is None:
            raise ValueError("Second adult required for couple status")
            
        if 'Couple' not in self.status.value and self.adult2 is not None:
            raise ValueError("Second adult not allowed for single status")
            
        if 'retraité' in self.status.value:
            if self.adult1.age < 65:
                raise ValueError("Primary adult must be 65+ for retired status")
            if self.adult2 and self.adult2.age < 65:
                raise ValueError("Secondary adult must be 65+ for retired status")
                
        if self.children and 'retraité' in self.status.value:
            raise ValueError("Retired status cannot have children")
            
        if self.children and self.status == FamilyStatus.SINGLE:
            raise ValueError("Single person cannot have children")

class TaxProgram(ABC):
    """
    Abstract base class for all tax programs.
    All fiscal programs (taxes, contributions, benefits) must inherit from this class.
    """
    
    @abstractmethod
    def calculate(self, family: Family) -> Dict[str, float]:
        """
        Calculate program amounts for a family.
        
        Args:
            family: Family information
            
        Returns:
            Dictionary containing calculation results with standardized keys:
            - program: Name of the program
            - tax_year: Year of calculation
            - total: Total amount calculated
            - details: Dictionary of detailed amounts
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Program name"""
        pass
    
    @property
    @abstractmethod
    def supported_years(self) -> List[int]:
        """List of supported tax years"""
        pass

    def validate_year(self, year: int) -> None:
        """Validate if tax year is supported"""
        if year not in self.supported_years:
            raise ValueError(
                f"Tax year {year} not supported for {self.name}. "
                f"Supported years: {sorted(self.supported_years)}"
            )

class BaseTaxCalculator(ABC):
    """
    Abstract base class for calculator implementations.
    Defines the interface that must be implemented by all calculator classes.
    """
    
    @abstractmethod
    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate tax results for given inputs"""
        pass

    @abstractmethod
    def validate_inputs(self, family: Family) -> bool:
        """Validate input combination"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get calculator version identifier"""
        pass

    def run_standard_test_cases(self):
        """Run standard test cases"""
        test_cases = [
            {
                "status": FamilyStatus.SINGLE,
                "adult1": AdultInfo(age=30, gross_work_income=45000),
                "name": "Single person"
            },
            {
                "status": FamilyStatus.SINGLE_PARENT,
                "adult1": AdultInfo(age=35, gross_work_income=50000),
                "children": [
                    ChildInfo(
                        age=4,
                        daycare_cost=8000,
                        daycare_type=DaycareType.SUBSIDIZED
                    )
                ],
                "name": "Single parent, one child"
            },
            {
                "status": FamilyStatus.COUPLE,
                "adult1": AdultInfo(age=40, gross_work_income=75000),
                "adult2": AdultInfo(age=38, gross_work_income=65000),
                "name": "Working couple, no children"
            },
            {
                "status": FamilyStatus.COUPLE,
                "adult1": AdultInfo(age=42, gross_work_income=80000),
                "adult2": AdultInfo(age=41, gross_work_income=55000),
                "children": [
                    ChildInfo(age=6, daycare_cost=9500, daycare_type=DaycareType.NON_SUBSIDIZED),
                    ChildInfo(age=3, daycare_cost=8500, daycare_type=DaycareType.SUBSIDIZED)
                ],
                "name": "Couple with two children"
            },
            {
                "status": FamilyStatus.RETIRED_COUPLE,
                "adult1": AdultInfo(age=68, gross_retirement_income=45000, is_retired=True),
                "adult2": AdultInfo(age=66, gross_retirement_income=40000, is_retired=True),
                "name": "Retired couple"
            },
        ]
        return self._run_test_cases(test_cases)

    def run_generated_test_cases(self, num_cases: int = 5):
        """Run randomly generated test cases"""
        from test_case_generator import generate_test_cases
        raw_cases = generate_test_cases(num_cases)
        structured_cases = self._convert_raw_cases(raw_cases)
        return self._run_test_cases(structured_cases)

    def _convert_raw_cases(self, raw_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert raw test cases to structured format"""
        structured_cases = []
        for raw_case in raw_cases:
            case = {
                "status": FamilyStatus(raw_case["situation"]),
                "adult1": AdultInfo(
                    age=raw_case["age1"],
                    income=raw_case["income1"]
                ),
                "name": raw_case["situation"]
            }
            
            if raw_case.get("income2", 0) > 0:
                case["adult2"] = AdultInfo(
                    age=raw_case["age2"],
                    income=raw_case["income2"]
                )
                
            if raw_case["num_children"] > 0:
                children = []
                for i in range(1, raw_case["num_children"] + 1):
                    child = ChildInfo(
                        age=raw_case[f"child_age{i}"],
                        daycare_cost=raw_case.get(f"daycare_fee{i}", 0),
                        daycare_type=DaycareType(
                            raw_case.get(f"daycare_type{i}", "Subventionnée")
                        )
                    )
                    children.append(child)
                case["children"] = children
                
            structured_cases.append(case)
        return structured_cases

    def _run_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run test cases and return results"""
        results = []
        for case in test_cases:
            print(f"\nTesting: {case['name']}")
            print("-" * 50)
            
            try:
                # Créer un objet Family avec les données du cas de test
                family = Family(
                    status=case["status"],
                    adult1=case["adult1"],
                    adult2=case.get("adult2"),
                    children=case.get("children", None)
                )
                
                # Passer l'objet Family à calculate()
                calc_results = self.calculate(family)
                
                self._print_results(calc_results)
                results.append({
                    "case": case,
                    "results": calc_results,
                    "success": True
                })
                
            except Exception as e:
                print(f"Error: {str(e)}")
                results.append({
                    "case": case,
                    "error": str(e),
                    "success": False
                })
        return results

    def _print_results(self, results: Dict[str, Any]) -> None:
        """Print calculation results in a formatted way"""
        print("\nResults:")
        print("-" * 20)
        for key, value in results.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for sub_key, sub_value in value.items():
                    # Skip non-numeric values or handle them differently
                    if isinstance(sub_value, (int, float)):
                        print(f"  {sub_key}: ${sub_value:,.2f}")
                    else:
                        print(f"  {sub_key}: {sub_value}")
            elif isinstance(value, (int, float)):
                print(f"{key}: ${value:,.2f}")
            else:
                print(f"{key}: {value}")
