"""Personal income tax.

References:
    - https://www.canada.ca/en/revenue-agency/services/tax/individuals/frequently-asked-questions-individuals/adjustment-personal-income-tax-benefit-amounts.html
    - https://cqff.com/centre-dinformation/
    - https://turboimpot.intuit.ca/ressources-impot/calculatrice-impot-quebec
    - Indexation de montants aux fins de l’impôt et des prestations des particuliers
       https://www.canada.ca/fr/agence-revenu/services/impot/particuliers/foire-questions-particuliers/rajustement-montants-fonction-indexation-impot-particuliers-prestations.html
    - Courbes Laferrière
      https://www.cqff.com/claude_laferriere/tableaux2020.htm
    - TaxTips. Canadian Financial and Income Tax Calculators
      https://www.taxtips.ca/calculators.htm
    - RCGT. Crédits d’impôt non remboursables 2020
      https://www.rcgt.com/fr/planiguide/tableaux/quebec/credits-dimpot-non-remboursables/

TODO:
    - Inclure les gains en capital
    - Inclure les dividendes de source canadienne
    - Voir https://www.taxtips.ca/taxrates/canada.htm
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo, ChildInfo, generate_standard_test_cases

class FederalIncomeTax(TaxProgram):
    PARAMS = {
        2025: {
            'brackets': [
                (57375, 0.15),
                (114750, 0.205),
                (177882, 0.26),
                (253414, 0.29),
                (float('inf'), 0.33)
            ],
            'basic_personal_amount': 15569
        },
        2024: {
            'brackets': [
                (55867, 0.15),
                (111733, 0.205),
                (173205, 0.26),
                (246752, 0.29),
                (float('inf'), 0.33),
            ],
            'basic_personal_max_amount': 15705.0,
            'basic_personal_min_amount': 14156.0,
            'basic_personal_reduction_threshold': 173205.0,
            'basic_personal_reduction_rate': 0.05,
            'medical_expenses_rate': 0.03,
            'medical_expenses_max': 2759.0,
            'age_amount': 8790.0,
        },
        2023: {
            'brackets': [
                (53359, 0.15),
                (106717, 0.205),
                (165430, 0.26),
                (235675, 0.29),
                (float('inf'), 0.33)
            ],
            'basic_personal_max_amount': 15000.0,
            'basic_personal_min_amount': 13520.0,
            'basic_personal_reduction_threshold': 172000.0,
            'basic_personal_reduction_rate': 0.05,
            'medical_expenses_rate': 0.03,
            'medical_expenses_max': 2635.0,
            'age_amount': 8396.0,
        }
    }

    @property
    def name(self) -> str:
        return "Federal Income Tax"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def calculate_federal_tax(self, taxable_income: float, brackets: List[tuple]) -> float:
        """Calculate federal tax using progressive tax brackets"""
        tax = 0
        remaining = taxable_income
        
        for i, (threshold, rate) in enumerate(brackets):
            if i == 0:
                taxable_in_bracket = min(remaining, threshold)
            else:
                previous_threshold = brackets[i-1][0]
                taxable_in_bracket = min(remaining, threshold - previous_threshold)
            
            if taxable_in_bracket <= 0:
                break
                
            tax += taxable_in_bracket * rate
            remaining -= taxable_in_bracket
            
        return tax

    def calculate_basic_personal_amount(self, net_income: float, params: dict) -> float:
        """Calculate basic personal amount based on income thresholds"""
        if net_income <= params['basic_personal_reduction_threshold']:
            return params['basic_personal_max_amount']
        elif net_income >= params['basic_personal_max_amount']:
            return params['basic_personal_min_amount']
        else:
            reduction = ((net_income - params['basic_personal_reduction_threshold']) 
                        * params['basic_personal_reduction_rate'])
            return max(
                params['basic_personal_min_amount'],
                params['basic_personal_max_amount'] - reduction
            )

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate federal income tax for a family"""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]
        
        # Calculate total and taxable income for each adult
        def calculate_for_adult(adult: AdultInfo) -> tuple:
            if not adult:
                return 0.0, 0.0, 0.0
                
            total_income = adult.gross_work_income + adult.gross_retirement_income
            # For simplicity, assume net income equals total income
            net_income = total_income
            # For simplicity, assume taxable income equals net income
            taxable_income = net_income
            
            return total_income, net_income, taxable_income

        # Calculate for primary adult
        total_income1, net_income1, taxable_income1 = calculate_for_adult(family.adult1)
        
        # Calculate for secondary adult if present
        total_income2, net_income2, taxable_income2 = calculate_for_adult(family.adult2)

        # Calculate federal tax for each adult
        federal_tax1 = self.calculate_federal_tax(taxable_income1, params['brackets'])
        federal_tax2 = self.calculate_federal_tax(taxable_income2, params['brackets'])
        
        # Calculate basic personal amount for each adult
        credits1 = self.calculate_basic_personal_amount(net_income1, params) if net_income1 > 0 else 0
        credits2 = self.calculate_basic_personal_amount(net_income2, params) if net_income2 > 0 else 0
        
        # Apply credits and calculate final tax
        net_tax1 = max(0, federal_tax1 - (credits1 * params['brackets'][0][1]))
        net_tax2 = max(0, federal_tax2 - (credits2 * params['brackets'][0][1]))

        tax1 = -1 * round(net_tax1, 2)  # Negative because it's a deduction
        tax2 = -1 * round(net_tax2, 2)  # Negative because it's a deduction
        
        return {
            "program": self.name,
            "tax_year": family.tax_year,
            "adult1": tax1,
            "adult2": tax2,
            "total": tax1 + tax2,
            "details": {
                "total_income1": total_income1,
                "net_income1": net_income1,
                "taxable_income1": taxable_income1,
                "federal_tax1": federal_tax1,
                "credits1": credits1,
                "total_income2": total_income2,
                "net_income2": net_income2,
                "taxable_income2": taxable_income2,
                "federal_tax2": federal_tax2,
                "credits2": credits2
            }
        }


if __name__ == "__main__":
    # Create calculator instance
    calculator = FederalIncomeTax()
    
    # Generate and run standard test cases
    test_cases = generate_standard_test_cases()
    
    print("\nRunning standard test cases for Federal Income Tax Calculator")
    print("=" * 80)
    
    for i, family in enumerate(test_cases, 1):
        print(f"\nTest Case #{i}:")
        print(f"Family Status: {family.family_status.name}")
        print(f"Adult 1: Age {family.adult1.age}, Work Income ${family.adult1.gross_work_income:,.2f}, "
              f"Retirement Income ${family.adult1.gross_retirement_income:,.2f}")
        
        if family.adult2:
            print(f"Adult 2: Age {family.adult2.age}, Work Income ${family.adult2.gross_work_income:,.2f}, "
                  f"Retirement Income ${family.adult2.gross_retirement_income:,.2f}")
            
        if family.children:
            print(f"Number of children: {len(family.children)}")
            for j, child in enumerate(family.children, 1):
                print(f"Child {j}: Age {child.age}")
                
        results = calculator.calculate(family)
        print("\nResults:")
        print(f"Adult 1 Federal Tax: ${abs(results['adult1']):,.2f}")
        if family.adult2:
            print(f"Adult 2 Federal Tax: ${abs(results['adult2']):,.2f}")
        print(f"Total Federal Tax: ${abs(results['total']):,.2f}")
        print("\nDetails:")
        for key, value in results['details'].items():
            if isinstance(value, (int, float)):
                print(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
        print("-" * 80)

"""
// Étape 2 – Revenu total

// L10100 Revenus d'emploi.
var revenuTotal1 = type.revenuEmploi1;
var revenuTotal2 = type.revenuEmploi2;

// L11300 Pension de sécurité de la vieillesse.
revenuTotal1 += type.tax[year].caPsv.psv1;
revenuTotal2 += type.tax[year].caPsv.psv2;

// L11500 Autres pensions et pensions de retraite.
revenuTotal1 += type.revenuPension1;
revenuTotal2 += type.revenuPension2;

// L11600 Choix du montant de pension fractionné.
// TODO

// L12000 Montant imposable des dividendes (déterminés et autres que déterminés) de sociétés canadiennes imposables.
// TODO.

// L12100 Intérêts et autres revenus de placements.
// TODO.

// L12700 Gains en capital imposables.
// TODO.

// L12900 Revenus d'un REER.
// TODO.

// L14500 Prestations d'aide sociale.
// La prestation d'aide sociale est déduite à la ligne 25000.
revenuTotal1 += type.tax[year].qcAdr.prestation;

// L15000 Revenu total.

// Étape 3 – Revenu net.

// L20800 Déduction pour REER.
// TODO

// L21000 Déduction pour le choix du montant de pension fractionné.
// TODO

// L21400 Frais de garde d'enfants.
var deductionFraisGarde1 = type.tax[year].fraisGarde.fraisTotal;

// L22215 Déduction pour les cotisations bonifiées au RPC ou au RRQ sur un revenu d'emploi.
var deductionRrqSupp1 = type.tax[year].qcRrq.supp1;
var deductionRrqSupp2 = type.tax[year].qcRrq.supp2;

// 23600 Revenu net.
var revenuNet1 = Math.max(0, revenuTotal1 - deductionRrqSupp1 - deductionFraisGarde1);
var revenuNet2 = Math.max(0, revenuTotal2 - deductionRrqSupp2);
var revenuNet = revenuNet1 + revenuNet2;
myLogger.debug("revenuNet1=" + revenuNet1);
myLogger.debug("revenuNet2=" + revenuNet2);
myLogger.debug("revenuNet=" + revenuNet);

// Étape 4 – Revenu imposable 

// L25000 Déductions pour autres paiements.
var deductionAdr1 = type.tax[year].qcAdr.prestation;

// L25400 Déduction pour gains en capital.
// TODO.

// L26000 Revenu imposable.
var revenuImposable1 = Math.max(0, revenuNet1 - deductionAdr1);
var revenuImposable2 = revenuNet2;

myLogger.debug("revenuImposable1=" + revenuImposable1);
myLogger.debug("revenuImposable2=" + revenuImposable2);

// Étape 5 – Impôt fédéral.

// Partie A – Impôt fédéral sur le revenu imposable.
var impotSurRevenuImposable1 = Math.min(revenuImposable1, p.seuil1) * p.taux1;
if (revenuImposable1 > p.seuil1) {
    impotSurRevenuImposable1 += Math.min(revenuImposable1 - p.seuil1, p.seuil2 - p.seuil1) * p.taux2;
    if (revenuImposable1 > p.seuil2) {
        impotSurRevenuImposable1 += Math.min(revenuImposable1 - p.seuil2, p.seuil3 - p.seuil2) * p.taux3;
        if (revenuImposable1 > p.seuil3) {
            impotSurRevenuImposable1 += Math.min(revenuImposable1 - p.seuil3, p.seuil4 - p.seuil3) * p.taux4;
            if (revenuImposable1 > p.seuil4) {
                impotSurRevenuImposable1 += (revenuImposable1 - p.seuil4) * p.taux5;
            }
        }
    }
}
myLogger.debug("impotSurRevenuImposable1=" + impotSurRevenuImposable1);

var impotSurRevenuImposable2 = Math.min(revenuImposable2, p.seuil1) * p.taux1;
if (revenuImposable2 > p.seuil1) {
    impotSurRevenuImposable2 += Math.min(revenuImposable2 - p.seuil1, p.seuil2 - p.seuil1) * p.taux2;
    if (revenuImposable2 > p.seuil2) {
        impotSurRevenuImposable2 += Math.min(revenuImposable2 - p.seuil2, p.seuil3 - p.seuil2) * p.taux3;
        if (revenuImposable2 > p.seuil3) {
            impotSurRevenuImposable2 += Math.min(revenuImposable2 - p.seuil3, p.seuil4 - p.seuil3) * p.taux4;
            if (revenuImposable2 > p.seuil4) {
                impotSurRevenuImposable2 += (revenuImposable2 - p.seuil4) * p.taux5;
            }
        }
    }
}

// Partie B – Crédits d'impôt non remboursables fédéraux.

// L30000 Montant personnel de base.
var montantPersonnelBase1 = 0;
if (year < 2020) {
    montantPersonnelBase1 = p.base;
} else {
    if (revenuNet1 <= p.seuil3) {
        montantPersonnelBase1 = p.base29;
    } else if (revenuNet1 >= p.seuil4) {
        montantPersonnelBase1 = p.base33;
    } else {
        montantPersonnelBase1 = p.base29 - (revenuNet1 - p.seuil3) / (p.seuil4 - p.seuil3) * (p.base29 - p.base33);
    }
}

// Conjoint ou personne à charge admissible.
var montantPersonnelBase2 = 0;
if (type.nbAdultes == 2) {
    if (year < 2020) {
        montantPersonnelBase2 = p.base;
    } else {
        if (revenuNet2 <= p.seuil3) {
            montantPersonnelBase2 = p.base29;
        } else if (revenuNet1 >= p.seuil4) {
            montantPersonnelBase2 = p.base33;
        } else {
            montantPersonnelBase2 = p.base29 - (revenuNet2 - p.seuil3) / (p.seuil4 - p.seuil3) * (p.base29 - p.base33);
        }
    }
}

// L30100 Montant en raison de l'âge.
var montantAge1 = 0;
if (type.age1 >= 65) {
    montantAge1 = Math.max(0, p.montantAge - Math.max(0, revenuNet1 - p.seuilAge) * p.tauxAge);
}

var montantAge2 = 0;
if (type.age2 >= 65) {
    montantAge2 = Math.max(0, p.montantAge - Math.max(0, revenuNet2 - p.seuilAge) * p.tauxAge);
}

// L30300 Montant pour époux ou conjoint de fait.
var montantConjoint1 = 0;
var montantConjoint2 = 0;
if (type.nbAdultes == 2) {
    var conjoint1;
    if (year < 2020) {
        conjoint1 = p.conjoint;
    } else {
        if (revenuNet2 <= p.seuil3) {
            conjoint1 = p.conjoint29;
        } else if (revenuNet2 >= p.seuil4) {
            conjoint1 = p.conjoint33;
        } else {
            conjoint1 = p.conjoint29 - (revenuNet2 - p.seuil3) / (p.seuil4 - p.seuil3) * (p.conjoint29 - p.conjoint33);
        }
    }

    var conjoint2;
    if (year < 2020) {
        conjoint2 = p.conjoint;
    } else {
        if (revenuNet1 <= p.seuil3) {
            conjoint2 = p.conjoint29;
        } else if (revenuNet1 >= p.seuil4) {
            conjoint2 = p.conjoint33;
        } else {
            conjoint2 = p.conjoint29 - (revenuNet1 - p.seuil3) / (p.seuil4 - p.seuil3) * (p.conjoint29 - p.conjoint33);
        }
    }

    montantConjoint1 = Math.max(0, conjoint1 - revenuNet2);
    montantConjoint2 = Math.max(0, conjoint2 - revenuNet1);
}

// L30400 Montant pour une personne à charge admissible.
var montantPersonneAdmissible = 0;
if (type.nbAdultes == 1 && type.nbEnfants > 0) {
    if (year < 2020) {
        montantPersonneAdmissible = p.conjoint;
    } else {
        // On suppose que le revenu net des enfants à charge est toujours 0.
        var r = 0;
        if (r <= p.seuil3) {
            montantPersonneAdmissible = p.conjoint29;
        } else if (r >= p.seuil4) {
            montantPersonneAdmissible = p.conjoint33;
        } else {
            montantPersonneAdmissible = p.conjoint29 - (r - p.seuil3) / (p.seuil4 - p.seuil3) * (p.conjoint29 - p.conjoint33);
        }
    }
}

// L30800 Cotisations de base au RPC ou au RRQ pour les revenus d'emploi.
var rrq1 = type.tax[year].qcRrq.base1;
var rrq2 = type.tax[year].qcRrq.base2;

// L31200 Cotisations à l'assurance-emploi.
var ae1 = type.tax[year].caAe.cotisation1;
var ae2 = type.tax[year].caAe.cotisation2;

// L31205 Cotisations au Régime provincial d'assurance parentale (RPAP).
var rqap1 = type.tax[year].qcRqap.cotisation1;
var rqap2 = type.tax[year].qcRqap.cotisation2;

// L31260 Montant canadien pour emploi.
var montantEmploi1 = Math.min(type.revenuEmploi1, p.emploi);
var montantEmploi2 = Math.min(type.revenuEmploi2, p.emploi);

// L31400 Montant pour revenu de pension.
var montantPension1 = Math.min(type.revenuPension1, p.pension);
var montantPension2 = Math.min(type.revenuPension2, p.pension);

// L32600 Montants transférés de votre époux ou conjoint de fait.
var annexe2_l6 = montantAge2 + montantPension2;
var annexe2_l7 = (annexe2_l6 <= p.seuil1) ? revenuImposable2 : impotSurRevenuImposable2 / p.taux1;
var annexe2_l8 = montantPersonnelBase2 + rrq2 + ae2 + rqap2 + montantEmploi2;
var annexe2_l10 = Math.max(0, annexe2_l6 - Math.max(0, annexe2_l7 - annexe2_l8));
var montantTransfereConjoint1 = annexe2_l10;

// L33500 Frais médicaux.
// Les frais médicaux donnent généralement droit à un crédit d’impôt non remboursable s’ils dépassent 
// 2 302 $ (en 2020) ou 3 % de votre revenu net (le moins élevé des deux). 
var fraisMedicaux1 = type.tax[year].qcRamq.cotisation;
var montantFraisMedicaux1 = Math.max(0, fraisMedicaux1 - Math.min(p.tauxFraisMedicaux, 0.03 * revenuNet1));

// L33500 Total des montants non remboursables.
var montantNonRemboursable1 = montantPersonnelBase1 + montantAge1 + montantConjoint1 + montantPersonneAdmissible 
    + rrq1 + ae1 + rqap1
    + montantEmploi1 + montantPension1 + montantTransfereConjoint1 + montantFraisMedicaux1;
var montantNonRemboursable2 = montantPersonnelBase2 + montantAge2 + montantConjoint2 + rrq2 + ae2 + rqap2
    + montantEmploi2 + montantPension2;

myLogger.debug("montantPersonnelBase1=" + montantPersonnelBase1);
myLogger.debug("montantAge1=" + montantAge1);
myLogger.debug("montantConjoint1=" + montantConjoint1);
myLogger.debug("rrq1=" + rrq1);
myLogger.debug("ae1=" + ae1);
myLogger.debug("rqap1=" + rqap1);
myLogger.debug("montantEmploi1=" + montantEmploi1);
myLogger.debug("montantPension1=" + montantPension1);
myLogger.debug("montantTransfereConjoint1=" + montantTransfereConjoint1);
myLogger.debug("montantFraisMedicaux1=" + montantFraisMedicaux1);

myLogger.debug("montantNonRemboursable1=" + montantNonRemboursable1);
myLogger.debug("montantNonRemboursable2=" + montantNonRemboursable2);

// L35000 Total des crédits d'impôt non remboursables.
var creditNonRemboursable1 = montantNonRemboursable1 * p.tauxCredit;
var creditNonRemboursable2 = montantNonRemboursable2 * p.tauxCredit;

myLogger.debug("creditNonRemboursable1=" + creditNonRemboursable1);
myLogger.debug("creditNonRemboursable2=" + creditNonRemboursable2);

// Partie C – Impôt fédéral net.

// L40424 Impôt fédéral sur le revenu fractionné.

// L40425 Crédit d'impôt fédéral pour dividendes.

// L42000 Impôt fédéral net.
var impotBase1 = Math.max(0, impotSurRevenuImposable1 - creditNonRemboursable1);
var impotBase2 = Math.max(0, impotSurRevenuImposable2 - creditNonRemboursable2);

myLogger.debug("impotBase1=" + impotBase1);
myLogger.debug("impotBase2=" + impotBase2);

// Étape 6 – Impôt provincial ou territorial.

// Étape 7 – Remboursement ou solde dû.

// L43500 Total à payer.

// L44000 Abattement du Québec remboursable.
var abattement1 = impotBase1 * p.abattement;
var abattement2 = impotBase2 * p.abattement;

myLogger.debug("abattement1=" + abattement1);
myLogger.debug("abattement2=" + abattement2);

// L45200 Supplément remboursable pour frais médicaux.

// L45300 Allocation canadienne pour les travailleurs (ACT).

// Remboursement ou solde dû.
var impot1 = impotBase1 - abattement1;
var impot2 = impotBase2 - abattement2;
var impot = impot1 + impot2;

myLogger.debug("impot1=" + impot1);
myLogger.debug("impot2=" + impot2);
myLogger.debug("impot=" + impot);

type.tax[year].caImpot = {};
type.tax[year].caImpot.revenuFamilialNet = revenuNet;
type.tax[year].caImpot.impot1 = impot1;
type.tax[year].caImpot.impot2 = impot2;
type.tax[year].caImpot.impot = impot;
"""