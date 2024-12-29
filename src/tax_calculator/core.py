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
    family_status: FamilyStatus
    adult1: AdultInfo
    adult2: Optional[AdultInfo] = None
    children: Optional[List[ChildInfo]] = None
    tax_year: int = 2024

    def __post_init__(self):
        """
        Post-initialization hook to set retirement status based on family status
        and perform validation
        """
        # Set retirement status based on family status
        is_retired = 'retraité' in self.family_status.value.lower()
        self.adult1.is_retired = is_retired
        if self.adult2:
            self.adult2.is_retired = is_retired

        # Validate family composition
        self.validate()
        
    def validate(self) -> None:
        """
        Validate family composition based on family status.
        
        Raises:
            ValueError: If the family composition is invalid
        """
        if 'Couple' in self.family_status.value and self.adult2 is None:
            raise ValueError("Second adult required for couple status")
            
        if 'Couple' not in self.family_status.value and self.adult2 is not None:
            raise ValueError("Second adult not allowed for single status")
            
        if 'retraité' in self.family_status.value:
            if self.adult1.age < 65:
                raise ValueError("Primary adult must be 65+ for retired status")
            if self.adult2 and self.adult2.age < 65:
                raise ValueError("Secondary adult must be 65+ for retired status")
                
        if self.children and 'retraité' in self.family_status.value:
            raise ValueError("Retired status cannot have children")
            
        if self.children and self.family_status == FamilyStatus.SINGLE:
            raise ValueError("Single person cannot have children")

    def describe(self) -> str:
        """Return a string describing the family and its main characteristics"""
        description = f"Family Status: {self.family_status.name}\n"
        description += f"Tax Year: {self.tax_year}\n"
        description += f"Adult 1: Age {self.adult1.age}, "
        description += f"Gross Work Income: ${self.adult1.gross_work_income}, "
        description += f"Gross Retirement Income: ${self.adult1.gross_retirement_income}, "
        description += f"Retired: {'Yes' if self.adult1.is_retired else 'No'}\n"
        
        if self.adult2:
            description += f"Adult 2: Age {self.adult2.age}, "
            description += f"Gross Work Income: ${self.adult2.gross_work_income}, "
            description += f"Gross Retirement Income: ${self.adult2.gross_retirement_income}, "
            description += f"Retired: {'Yes' if self.adult2.is_retired else 'No'}\n"
        
        if self.children:
            description += f"Children: {len(self.children)}\n"
            for i, child in enumerate(self.children, start=1):
                description += f"  Child {i}: Age {child.age}, "
                description += f"Daycare Cost: ${child.daycare_cost}, "
                description += f"Daycare Type: {child.daycare_type.name}\n"
        else:
            description += "Children: None\n"
        
        return description

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
    def get_version(self) -> str:
        """Get calculator version identifier"""
        pass

    def run_standard_test_cases(self):
        """Run standard test cases"""
        test_cases = generate_standard_test_cases()
        return self._run_test_cases(test_cases)

    def run_generated_test_cases(self, num_cases: int = 5):
        """Run randomly generated test cases"""
        test_cases = generate_random_test_cases(num_cases)
        return self._run_test_cases(test_cases)

    def _run_test_cases(self, test_cases: List[Family]) -> List[Dict[str, Any]]:
        """Run test cases and return results"""
        results = []
        for family in test_cases:
            print(f"\nTesting: {family.describe()}")
            
            try:
                # Passer l'objet Family à calculate()
                calc_results = self.calculate(family)
                
                self._print_results(calc_results)
                results.append({
                    "family": family,
                    "results": calc_results,
                    "success": True
                })
                
            except Exception as e:
                print(f"Error: {str(e)}")
                results.append({
                    "family": family,
                    "error": str(e),
                    "success": False
                })
        return results

    def _print_results(self, results: Dict[str, Any]) -> None:
        """Print calculation results in a formatted way"""
        for key, value in results.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    # Skip non-numeric values or handle them differently
                    if isinstance(sub_value, (int, float)):
                        print(f"  {sub_key}: {sub_value:,.2f}")
                    else:
                        print(f"  {sub_key}: {sub_value}")
            elif isinstance(value, (int, float)):
                print(f"{key}: {value:,.2f}")
            else:
                print(f"{key}: {value}")

from typing import List

def generate_standard_test_cases() -> List[Family]:
    """Generate standard test cases and return a list of Family objects"""
    test_cases = [
        Family(
            family_status=FamilyStatus.SINGLE,
            adult1=AdultInfo(age=30, gross_work_income=45000)
        ),
        Family(
            family_status=FamilyStatus.RETIRED_SINGLE,
            adult1=AdultInfo(age=35, gross_retirement_income=25000, is_retired=True)
        ),
        Family(
            family_status=FamilyStatus.COUPLE,
            adult1=AdultInfo(age=40, gross_work_income=75000),
            adult2=AdultInfo(age=38, gross_work_income=65000)
        ),
        Family(
            family_status=FamilyStatus.COUPLE,
            adult1=AdultInfo(age=42, gross_work_income=80000),
            adult2=AdultInfo(age=41, gross_work_income=55000),
            children=[
                ChildInfo(age=6, daycare_cost=9500, daycare_type=DaycareType.NON_SUBSIDIZED),
                ChildInfo(age=3, daycare_cost=8500, daycare_type=DaycareType.SUBSIDIZED)
            ]
        ),
        Family(
            family_status=FamilyStatus.RETIRED_COUPLE,
            adult1=AdultInfo(age=68, gross_retirement_income=45000, is_retired=True),
            adult2=AdultInfo(age=66, gross_retirement_income=40000, is_retired=True)
        ),
    ]
    return test_cases

import random
from typing import List
from tax_calculator.core import Family, FamilyStatus, AdultInfo, ChildInfo, DaycareType

def generate_random_test_cases(num_cases: int = 10) -> List[Family]:
    """
    Generates random test cases for the tax calculator
    
    Args:
        num_cases: Number of test cases to generate
        
    Returns:
        List of Family objects
    """
    
    family_situations = [
        FamilyStatus.SINGLE,
        FamilyStatus.SINGLE_PARENT,
        FamilyStatus.COUPLE,
        FamilyStatus.RETIRED_SINGLE,
        FamilyStatus.RETIRED_COUPLE
    ]
    
    incomes = list(range(0, 125001, 1000))
    worker_ages = [25, 35, 45, 55]
    retirement_ages = [65, 75, 85]
    child_ages = [2, 5, 10, 15]
    num_children = range(6)  # 0 to 5 children
    daycare_fees = [0, 8000, 15000]
    daycare_types = [DaycareType.SUBSIDIZED, DaycareType.NON_SUBSIDIZED]

    test_cases = []
    
    for _ in range(num_cases):
        family_status = random.choice(family_situations)
        is_retired = 'retraité' in family_status.value.lower()
        is_couple = 'Couple' in family_status.value
        can_have_children = not is_retired and family_status != FamilyStatus.SINGLE

        adult1 = AdultInfo(
            age=random.choice(retirement_ages if is_retired else worker_ages),
            gross_work_income=random.choice(incomes) if not is_retired else 0,
            gross_retirement_income=random.choice(incomes) if is_retired else 0,
            is_retired=is_retired
        )

        adult2 = None
        if is_couple:
            adult2 = AdultInfo(
                age=random.choice(retirement_ages if is_retired else worker_ages),
                gross_work_income=random.choice(incomes) if not is_retired else 0,
                gross_retirement_income=random.choice(incomes) if is_retired else 0,
                is_retired=is_retired
            )

        children = []
        if can_have_children:
            num_kids = random.choice(num_children)
            for i in range(num_kids):
                child_age = random.choice(child_ages)
                daycare_cost = random.choice(daycare_fees) if child_age <= 5 else 0
                daycare_type = random.choice(daycare_types) if child_age <= 5 else DaycareType.SUBSIDIZED
                children.append(ChildInfo(
                    age=child_age,
                    daycare_cost=daycare_cost,
                    daycare_type=daycare_type
                ))

        family = Family(
            family_status=family_status,
            adult1=adult1,
            adult2=adult2,
            children=children
        )
        
        test_cases.append(family)
    
    return test_cases