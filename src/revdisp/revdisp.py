from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Dict, Optional
import unittest
import csv
from pathlib import Path

class HouseholdType(Enum):
    """Types de ménages possibles"""
    SINGLE = "single"                         # Personne vivant seule
    SINGLE_PARENT = "single_parent"           # Famille monoparentale
    COUPLE = "couple"                         # Couple
    RETIRED_SINGLE = "retired_single"         # Retraité vivant seul
    RETIRED_COUPLE = "retired_couple"         # Couple de retraités

@dataclass
class Person:
    """Représente une personne avec ses caractéristiques pertinentes pour le calcul fiscal"""
    age: int
    gross_work_income: Decimal = Decimal('0')      # Revenus de travail bruts
    self_employed_income: Decimal = Decimal('0')   # Revenus de travail autonome
    gross_retirement_income: Decimal = Decimal('0') # Revenus de retraite bruts
    is_retired: bool = False

@dataclass
class Household:
    """Représente un ménage fiscal"""
    household_type: HouseholdType
    primary_person: Person
    spouse: Optional[Person] = None
    num_children: int = 0
    
    def validate(self) -> bool:
        """Valide la cohérence du ménage"""
        if self.household_type in [HouseholdType.COUPLE, HouseholdType.RETIRED_COUPLE] and not self.spouse:
            return False
        if self.household_type in [HouseholdType.RETIRED_SINGLE, HouseholdType.RETIRED_COUPLE]:
            if not self.primary_person.is_retired:
                return False
            if self.spouse and not self.spouse.is_retired:
                return False
        return True

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional, List

class QcTaxCalculator:
    """
    Calculateur d'impôt du Québec, incluant le calcul du revenu familial net
    qui est nécessaire pour plusieurs autres calculs (dont la RAMQ).
    """
    def __init__(self, tax_year: int = 2024):
        if tax_year not in [2023, 2024]:
            raise ValueError("Année d'imposition doit être 2023 ou 2024")
            
        self.tax_year = tax_year
        
        # Paramètres des tranches d'imposition
        self.tax_brackets = {
            2024: [
                (Decimal('0'), Decimal('49275'), Decimal('0.14')),
                (Decimal('49275'), Decimal('98540'), Decimal('0.19')),
                (Decimal('98540'), Decimal('119910'), Decimal('0.24')),
                (Decimal('119910'), Decimal('999999999'), Decimal('0.2575'))
            ],
            2023: [
                (Decimal('0'), Decimal('46295'), Decimal('0.14')),
                (Decimal('46295'), Decimal('92580'), Decimal('0.19')),
                (Decimal('92580'), Decimal('112655'), Decimal('0.24')),
                (Decimal('112655'), Decimal('999999999'), Decimal('0.2575'))
            ]
        }
        
        # Montants personnels de base et déductions
        self.constants = {
            2024: {
                'basic_amount': Decimal('17183'),
                'age_65_amount': Decimal('3395'),
                'pension_amount': Decimal('3017'),
                'living_alone_amount': Decimal('1890'),
                'cpp_deduction_rate': Decimal('1.0'),
                'ei_deduction_rate': Decimal('1.0'),
                'qpip_deduction_rate': Decimal('1.0'),
            },
            2023: {
                'basic_amount': Decimal('16495'),
                'age_65_amount': Decimal('3211'),
                'pension_amount': Decimal('3017'),
                'living_alone_amount': Decimal('1890'),
                'cpp_deduction_rate': Decimal('1.0'),
                'ei_deduction_rate': Decimal('1.0'),
                'qpip_deduction_rate': Decimal('1.0'),
            }
        }
    
    def _calculate_deductions(self, person: Person, contributions: Dict) -> Decimal:
        """Calcule les déductions d'emploi standards (RRQ, AE, RQAP)"""
        params = self.constants[self.tax_year]
        
        deductions = Decimal('0')
        
        # RRQ/QPP
        if 'rrq' in contributions:
            deductions += contributions['rrq'] * params['cpp_deduction_rate']
            
        # Assurance-emploi
        if 'assurance_emploi' in contributions:
            deductions += contributions['assurance_emploi'] * params['ei_deduction_rate']
            
        # RQAP
        if 'rqap' in contributions:
            deductions += contributions['rqap'] * params['qpip_deduction_rate']
            
        return deductions.quantize(Decimal('0.01'))
    
    def _calculate_tax_credits(self, person: Person) -> Decimal:
        """Calcule les crédits d'impôt non-remboursables"""
        params = self.constants[self.tax_year]
        credits = Decimal('0')
        
        # Montant personnel de base
        credits += params['basic_amount']
        
        # Montant en raison de l'âge (65 ans et plus)
        if person.age >= 65:
            credits += params['age_65_amount']
            
            # Montant pour revenus de retraite
            if person.gross_retirement_income > 0:
                pension_amount = min(
                    person.gross_retirement_income,
                    params['pension_amount']
                )
                credits += pension_amount
        
        return credits.quantize(Decimal('0.01'))
    
    def calculate_net_income(self, person: Person, contributions: Dict) -> Decimal:
        """
        Calcule le revenu net pour l'impôt du Québec.
        C'est ce montant qui sera utilisé pour le calcul de la RAMQ.
        """
        total_income = (person.gross_work_income + 
                       person.self_employed_income +
                       person.gross_retirement_income)
        
        # Déductions d'emploi standards
        deductions = self._calculate_deductions(person, contributions)
        
        net_income = total_income - deductions
        return max(Decimal('0'), net_income).quantize(Decimal('0.01'))
    
    def calculate(self, household: Household, contributions: Dict) -> Dict:
        """
        Calcule l'impôt du Québec pour le ménage.
        Retourne aussi le revenu familial net nécessaire pour la RAMQ.
        """
        # Calcul du revenu net pour chaque personne
        primary_net_income = self.calculate_net_income(
            household.primary_person,
            contributions.get('primary', {})
        )
        
        spouse_net_income = Decimal('0')
        if household.spouse:
            spouse_net_income = self.calculate_net_income(
                household.spouse,
                contributions.get('spouse', {})
            )
        
        # Revenu familial net (nécessaire pour RAMQ)
        family_net_income = primary_net_income + spouse_net_income
        
        # Calcul des crédits d'impôt
        primary_credits = self._calculate_tax_credits(household.primary_person)
        spouse_credits = Decimal('0')
        if household.spouse:
            spouse_credits = self._calculate_tax_credits(household.spouse)
        
        return {
            "net_income": {
                "primary": primary_net_income,
                "spouse": spouse_net_income,
                "family": family_net_income
            },
            "credits": {
                "primary": primary_credits,
                "spouse": spouse_credits
            }
            # D'autres détails du calcul d'impôt peuvent être ajoutés ici
        }
    
class EiCalculator:
    """Calculateur de la cotisation à l'assurance-emploi (Employment Insurance)"""
    
    def __init__(self, tax_year: int = 2024):
        if tax_year not in [2023, 2024]:
            raise ValueError("Année d'imposition doit être 2023 ou 2024")
            
        self.tax_year = tax_year
        self.constants = {
            2024: {
                'max_insurable_earnings': Decimal('63200'),
                'employee_rate': Decimal('0.0132'),
                'max_employee_contribution': Decimal('834.24'),
                'min_insurable_earnings': Decimal('2000'),  # Seuil minimum
                'employer_rate_multiplier': Decimal('1.4')
            },
            2023: {
                'max_insurable_earnings': Decimal('61500'),
                'employee_rate': Decimal('0.0127'),
                'max_employee_contribution': Decimal('781.05'),
                'min_insurable_earnings': Decimal('2000'),
                'employer_rate_multiplier': Decimal('1.4')
            }
        }

    def get_employer_rate(self) -> Decimal:
        """Retourne le taux de cotisation de l'employeur"""
        return self.constants[self.tax_year]['employee_rate'] * self.constants[self.tax_year]['employer_rate_multiplier']
    
    def get_max_employer_contribution(self) -> Decimal:
        """Retourne la cotisation maximale de l'employeur"""
        return self.constants[self.tax_year]['max_employee_contribution'] * self.constants[self.tax_year]['employer_rate_multiplier']
    
    def calculate(self, person: Person) -> Dict:
        """Calcule la cotisation à l'assurance-emploi pour une personne"""
        # Les retraités de 65 ans et plus ne cotisent pas à l'AE
        if person.is_retired and person.age >= 65:
            return {
                "employee": Decimal('0'),
                "employer": Decimal('0'),
                "total": Decimal('0')
            }

        params = self.constants[self.tax_year]
        
        # Si le revenu est inférieur au seuil minimum, pas de cotisation
        if person.gross_work_income < params['min_insurable_earnings']:
            return {
                "employee": Decimal('0'),
                "employer": Decimal('0'),
                "total": Decimal('0')
            }
        
        # Le revenu assurable est le minimum entre le revenu de travail 
        # et le maximum assurable
        insurable_earnings = min(
            person.gross_work_income,
            params['max_insurable_earnings']
        )
        
        employee_contribution = min(
            insurable_earnings * params['employee_rate'],
            params['max_employee_contribution']
        )
        
        employer_contribution = min(
            insurable_earnings * self.get_employer_rate(),
            self.get_max_employer_contribution()
        )

        # Les travailleurs autonomes ne cotisent pas à l'AE
        if person.self_employed_income > 0 and person.gross_work_income == 0:
            employee_contribution = Decimal('0')
            employer_contribution = Decimal('0')

        return {
            "employee": employee_contribution.quantize(Decimal('0.01')),
            "employer": employer_contribution.quantize(Decimal('0.01')), 
            "total": (employee_contribution + employer_contribution).quantize(Decimal('0.01'))
        }

class QpipCalculator:
    """Calculateur des cotisations au RQAP"""
    
    def __init__(self, tax_year: int = 2024):
        if tax_year not in [2023, 2024]:
            raise ValueError("Année d'imposition doit être 2023 ou 2024")
            
        self.tax_year = tax_year
        self.constants = {
            2024: {
                'max_insurable_earnings': Decimal('94000'),
                'employee_rate': Decimal('0.00494'),
                'employer_rate': Decimal('0.00692'),
                'self_employed_rate': Decimal('0.00878'),
                'min_earnings': Decimal('2000')
            },
            2023: {
                'max_insurable_earnings': Decimal('91000'),
                'employee_rate': Decimal('0.00494'),
                'employer_rate': Decimal('0.00692'),
                'self_employed_rate': Decimal('0.00878'),
                'min_earnings': Decimal('2000')
            }
        }

    def calculate(self, person: Person) -> Dict:
        """Calcule la cotisation RQAP pour une personne"""
        # Les retraités de 65 ans et plus ne cotisent pas au RQAP  
        if person.is_retired and person.age >= 65:
            return {
                "employee": Decimal('0'),
                "employer": Decimal('0'),
                "self_employed": Decimal('0'),
                "total": Decimal('0')
            }

        params = self.constants[self.tax_year]

        # Revenu assurable = min(revenu total, maximum assurable)
        total_income = person.gross_work_income + person.self_employed_income
        insurable_earnings = min(
            total_income,
            params['max_insurable_earnings']
        )

        if person.gross_work_income > 0:
            employee_contribution = (
                min(person.gross_work_income, params['max_insurable_earnings']) * 
                params['employee_rate']
            )
            employer_contribution = (
                min(person.gross_work_income, params['max_insurable_earnings']) * 
                params['employer_rate']
            )
        else:
            employee_contribution = Decimal('0')
            employer_contribution = Decimal('0')

        if person.self_employed_income > 0:
            self_employed_contribution = (
                min(person.self_employed_income, params['max_insurable_earnings']) * 
                params['self_employed_rate']
            )
        else:
            self_employed_contribution = Decimal('0')
            
        # Si revenu total < 2000$, remboursement des cotisations employé/autonome
        if total_income < params['min_earnings']:
            employee_contribution = Decimal('0')
            self_employed_contribution = Decimal('0')

        total = employee_contribution + employer_contribution + self_employed_contribution

        return {
            "employee": employee_contribution.quantize(Decimal('0.01')),
            "employer": employer_contribution.quantize(Decimal('0.01')),
            "self_employed": self_employed_contribution.quantize(Decimal('0.01')),
            "total": total.quantize(Decimal('0.01'))
        }

class QppCalculator:
    """Calculateur des cotisations au RRQ"""
    
    def __init__(self, tax_year: int = 2024):
        if tax_year not in [2023, 2024]:
            raise ValueError("Année d'imposition doit être 2023 ou 2024")
            
        self.tax_year = tax_year
        self.constants = {
            2024: {
                'basic_exemption': Decimal('3500'),
                'max_pensionable_earnings': Decimal('68500'),
                'max_additional_earnings': Decimal('73200'),
                'base_rate': Decimal('0.054'),
                'additional_rate_first': Decimal('0.01'),
                'additional_rate_second': Decimal('0.04'),
                'self_employed_multiplier': Decimal('2.0')
            },
            2023: {
                'basic_exemption': Decimal('3500'),
                'max_pensionable_earnings': Decimal('66600'),
                'base_rate': Decimal('0.054'),
                'additional_rate': Decimal('0.01'),
                'self_employed_multiplier': Decimal('2.0')
            }
        }
    
    def calculate_base_contribution(self, income: Decimal, is_self_employed: bool = False) -> Decimal:
        """Calcule la cotisation de base au RRQ"""
        params = self.constants[self.tax_year]

        if income <= params['basic_exemption']:
            return Decimal('0')
            
        max_contributory_earnings = params['max_pensionable_earnings']
        pensionable_earnings = min(income, max_contributory_earnings) - params['basic_exemption']
        
        rate = params['base_rate']
        if is_self_employed:
            rate *= params['self_employed_multiplier']

        base_contribution = (pensionable_earnings * rate).quantize(Decimal('0.01'))

        return base_contribution
        
    def calculate_additional_contribution(self, income: Decimal, is_self_employed: bool = False) -> Decimal:
        """Calcule la cotisation supplémentaire au RRQ"""
        params = self.constants[self.tax_year]
        if income <= params['basic_exemption']:
            return Decimal('0')
            
        # 2024: nouvelle structure à deux paliers
        if self.tax_year == 2024:
            # Premier palier (jusqu'au MGA)
            first_tier_earnings = min(income, params['max_pensionable_earnings']) - params['basic_exemption']
            first_tier_rate = params['additional_rate_first']
            if is_self_employed:
                first_tier_rate *= params['self_employed_multiplier']
            contribution = first_tier_earnings * first_tier_rate
            
            # Deuxième palier (entre MGA et maximum additionnel)
            if income > params['max_pensionable_earnings']:
                second_tier_earnings = min(income - params['max_pensionable_earnings'],
                                        params['max_additional_earnings'] - params['max_pensionable_earnings'])
                second_tier_rate = params['additional_rate_second']
                if is_self_employed:
                    second_tier_rate *= params['self_employed_multiplier']
                contribution += second_tier_earnings * second_tier_rate
                
        # 2023: structure simple
        else:
            max_contributory_earnings = params['max_pensionable_earnings']
            pensionable_earnings = min(income, max_contributory_earnings) - params['basic_exemption']
            rate = params['additional_rate']
            if is_self_employed:
                rate *= params['self_employed_multiplier']
            contribution = pensionable_earnings * rate
        
        contribution = contribution.quantize(Decimal('0.01'))

        return contribution

    def calculate_contribution(self, income: Decimal, is_self_employed: bool = False) -> Decimal:
        """Calcule la cotisation totale au RRQ"""
        base = self.calculate_base_contribution(income, is_self_employed)
        additional = self.calculate_additional_contribution(income, is_self_employed)
        contribution = (base + additional).quantize(Decimal('0.01'))
        return contribution

    def calculate(self, person: Person) -> Dict:
        """Calcule la cotisation RRQ totale pour une personne"""
        # Les retraités de 65 ans et plus ne cotisent pas au RRQ
        if person.is_retired and person.age >= 65:
            return {
                "employment": Decimal('0'),
                "self_employed": Decimal('0'),
                "total": Decimal('0')
            }
        
        # Calcul des cotisations selon le type de revenu
        employment_contrib = self.calculate_contribution(person.gross_work_income)
        self_employed_contrib = self.calculate_contribution(
            person.self_employed_income, 
            is_self_employed=True
        )
        
        return {
            "employment": employment_contrib,
            "self_employed": self_employed_contrib,
            "total": employment_contrib + self_employed_contrib
        }
    
class FssCalculator:
    """Calculateur de la cotisation au FSS"""
    
    def __init__(self, tax_year: int = 2024):
        if tax_year not in [2023, 2024]:
            raise ValueError("Année d'imposition doit être 2023 ou 2024")
            
        self.tax_year = tax_year
        self.constants = {
            2024: {
                'first_threshold': Decimal('17630'),
                'second_threshold': Decimal('61315'),
                'rate': Decimal('0.01'),
                'base_contribution': Decimal('150'),
                'max_contribution': Decimal('1000')
            },
            2023: {
                'first_threshold': Decimal('16780'),
                'second_threshold': Decimal('58350'),
                'rate': Decimal('0.01'),
                'base_contribution': Decimal('150'),
                'max_contribution': Decimal('1000'),
            }
        }

    def calculate(self, person: Person) -> Dict:
        """Calcule la cotisation au FSS pour une personne"""
        if not person.is_retired or person.age < 65:
            return {"contribution": Decimal('0')}
            
        # Calculer sur la base du revenu de retraite uniquement
        total_income = person.gross_retirement_income + person.self_employed_income

        # Capturer les paramètres de calcul
        params = self.constants[self.tax_year]

        # Aucune cotisation en dessous du premier seuil
        if total_income <= params['first_threshold']:
            return {"contribution": Decimal('0')}
        
        # Si le revenu sous le second seuil
        if total_income <= params['second_threshold']:
            # Première partie: 1% du revenu excédent le premier seuil
            contribution = (total_income - params['first_threshold']) * params['rate']
            contribution = min(contribution, params['base_contribution'])

        # Au-delà du second seuil
        else:
            contribution = params['base_contribution'] + (total_income - params['second_threshold']) * params['rate']
            contribution = min(contribution, params['max_contribution'])
        
        return {
            "contribution": contribution.quantize(Decimal('0.01'))
        }

class RamqCalculator:
    """
    Calculateur de la cotisation au Régime d'assurance médicaments du Québec (RAMQ)
    basé sur la documentation officielle et les paramètres 2023-2024.
    """
    def __init__(self, tax_year: int = 2024):
        if tax_year not in [2023, 2024]:
            raise ValueError("Année d'imposition doit être 2023 ou 2024")
            
        self.tax_year = tax_year
        self.constants = {
            2024: {
                'max_contribution': Decimal('731'),
                'exemption_single': Decimal('19790'),
                'exemption_couple': Decimal('32080'),
                'exemption_single_one_child': Decimal('32080'),
                'exemption_single_multiple_children': Decimal('36185'),
                'exemption_couple_one_child': Decimal('36185'),
                'exemption_couple_multiple_children': Decimal('39975'),
                'first_threshold': Decimal('5000'),
                'base_rate_single': Decimal('0.0747'),  # r11 pour personne seule 
                'additional_rate_single': Decimal('0.1122'),  # r12 pour personne seule
                'base_rate_couple': Decimal('0.0375'),  # r21 pour couple
                'additional_rate_couple': Decimal('0.0562'),  # r22 pour couple
                'base_max_single': Decimal('373.50'),
                'base_max_couple': Decimal('186.75'),
                'monthly_adjustment': Decimal('60.92')
            },
            2023: {
                'max_contribution': Decimal('720.50'),
                'exemption_single': Decimal('18910'),
                'exemption_couple': Decimal('30640'),
                'exemption_single_one_child': Decimal('30640'),
                'exemption_single_multiple_children': Decimal('34545'),
                'exemption_couple_one_child': Decimal('34545'),
                'exemption_couple_multiple_children': Decimal('38150'),
                'first_threshold': Decimal('5000'),
                'base_rate_single': Decimal('0.0747'),
                'additional_rate_single': Decimal('0.1122'),
                'base_rate_couple': Decimal('0.0375'),
                'additional_rate_couple': Decimal('0.0562'),
                'base_max_single': Decimal('373.50'),
                'base_max_couple': Decimal('186.75'),
                'monthly_adjustment': Decimal('60.04')
            }
        }
        
    def _get_exemption_threshold(self, household_type: HouseholdType, num_children: int) -> Decimal:
        """Détermine le seuil d'exemption selon le type de ménage et le nombre d'enfants"""
        params = self.constants[self.tax_year]
        
        if household_type in [HouseholdType.SINGLE, HouseholdType.RETIRED_SINGLE]:
            if num_children == 0:
                return params['exemption_single']
            elif num_children == 1:
                return params['exemption_single_one_child']
            else:
                return params['exemption_single_multiple_children']
        else:  # Couple ou couple retraité
            if num_children == 0:
                return params['exemption_couple']
            elif num_children == 1:
                return params['exemption_couple_one_child']
            else:
                return params['exemption_couple_multiple_children']

    def _calculate_single_contribution(self, income: Decimal) -> Decimal:
        """Calcule la contribution pour une personne seule"""
        params = self.constants[self.tax_year]
        
        if income <= Decimal('0'):
            return Decimal('0')
            
        if income <= params['first_threshold']:
            return min(
                income * params['base_rate_single'],
                params['base_max_single']
            )
            
        base_contribution = params['first_threshold'] * params['base_rate_single']
        additional_contribution = (income - params['first_threshold']) * params['additional_rate_single']
        
        contribution = min(
            base_contribution + additional_contribution,
            params['max_contribution']
        )
        
        return contribution

    def _calculate_couple_contribution(self, income: Decimal) -> Decimal:
        """Calcule la contribution pour un membre d'un couple"""
        params = self.constants[self.tax_year]
        
        if income <= Decimal('0'):
            return Decimal('0')
            
        if income <= params['first_threshold']:
            return min(
                income * params['base_rate_couple'],
                params['base_max_couple']
            )
            
        base_contribution = params['first_threshold'] * params['base_rate_couple']
        additional_contribution = (income - params['first_threshold']) * params['additional_rate_couple']
        
        contribution = min(
            base_contribution + additional_contribution,
            params['max_contribution']
        )
        
        return contribution

    def calculate(self, household: Household, qc_tax_result: Dict) -> Dict:
        """
        Calcule la cotisation RAMQ pour un ménage en utilisant le revenu familial net
        calculé par le calculateur d'impôt du Québec.
        """
        params = self.constants[self.tax_year]
        
        # Utiliser le revenu familial net calculé par l'impôt du Québec
        total_income = qc_tax_result['net_income']['family']

        # Déterminer le seuil d'exemption
        exemption = self._get_exemption_threshold(household.household_type, household.num_children)
        
        # Si le revenu est sous le seuil d'exemption, pas de cotisation
        if total_income <= exemption:
            return {"contribution": Decimal('0')}
            
        # Calculer le revenu servant au calcul de la cotisation
        income_for_calculation = total_income - exemption
        
        is_couple = household.household_type in [HouseholdType.COUPLE, HouseholdType.RETIRED_COUPLE]
        
        if is_couple:
            contribution = self._calculate_couple_contribution(income_for_calculation)
            contribution *= Decimal('2')
        else:
            contribution = self._calculate_single_contribution(income_for_calculation)
            
        return {
            "contribution": contribution.quantize(Decimal('0.01'))
        }
    
class RevenuDisponibleCalculator:
    """
    Calculateur principal qui coordonne tous les calculs d'impôts, 
    de cotisations et de transferts aux particuliers.
    """
    def __init__(self, tax_year: int = 2024):
        if tax_year not in [2023, 2024]:
            raise ValueError("Année d'imposition doit être 2023 ou 2024")
            
        self.tax_year = tax_year
        
        # Initialiser tous les calculateurs nécessaires
        self.ei_calculator = EiCalculator(tax_year)
        self.qpip_calculator = QpipCalculator(tax_year)
        self.qpp_calculator = QppCalculator(tax_year)
        self.qc_tax_calculator = QcTaxCalculator(tax_year)
        self.fss_calculator = FssCalculator(tax_year)
        self.ramq_calculator = RamqCalculator(tax_year)

    def calculate(self, household: Household) -> Dict:
        """
        Calcule tous les éléments du revenu disponible dans l'ordre approprié.
        """
        results = {
            'cotisations': {},
            'quebec': {},
            'canada': {},
            'revenu_disponible': Decimal('0')
        }
        
        # 1. Calculer les cotisations de base
        # RRQ/QPP
        qpp_primary = self.qpp_calculator.calculate(household.primary_person)
        results['cotisations']['rrq'] = qpp_primary['total']

        if household.spouse:
            qpp_spouse = self.qpp_calculator.calculate(household.spouse)
            results['cotisations']['rrq'] += qpp_spouse['total']

        # Assurance emploi
        ei_primary = self.ei_calculator.calculate(household.primary_person)
        results['cotisations']['assurance_emploi'] = ei_primary['employee']

        if household.spouse:
            ei_spouse = self.ei_calculator.calculate(household.spouse)
            results['cotisations']['assurance_emploi'] += ei_spouse['employee']

        # RQAP
        qpip_primary = self.qpip_calculator.calculate(household.primary_person)
        results['cotisations']['rqap'] = qpip_primary['employee']

        if household.spouse:
            qpip_spouse = self.qpip_calculator.calculate(household.spouse)
            results['cotisations']['rqap'] += qpip_spouse['employee']

        # 2. Calculer l'impôt du Québec (nécessaire pour RAMQ)
        contributions = {
            'primary': {
                'rrq': results['cotisations']['rrq'],
                'assurance_emploi': results['cotisations']['assurance_emploi'],
                'rqap': results['cotisations']['rqap']
            }
        }
        if household.spouse:
            contributions['spouse'] = contributions['primary'].copy()

        qc_tax_result = self.qc_tax_calculator.calculate(household, contributions)
        results['quebec'].update(qc_tax_result)

        # 3. Calculer FSS (basé sur le revenu de retraite)
        fss_primary = self.fss_calculator.calculate(household.primary_person)
        results['cotisations']['fss'] = fss_primary['contribution']

        if household.spouse:
            fss_spouse = self.fss_calculator.calculate(household.spouse)
            results['cotisations']['fss'] += fss_spouse['contribution']

        # 4. Calculer RAMQ (utilise le revenu familial net de l'impôt du Québec)
        ramq_result = self.ramq_calculator.calculate(household, qc_tax_result)
        results['cotisations']['ramq'] = ramq_result['contribution']

        # Calculer le total des cotisations
        results['cotisations']['total'] = sum(
            abs(amount) for amount in results['cotisations'].values()
            if isinstance(amount, (Decimal, int, float))
        )

        # TODO: Ajouter les autres calculs (transferts, crédits, etc.)

        return results
    
