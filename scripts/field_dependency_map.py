#!/usr/bin/env python3
"""
Field Dependency Mapping System
Defines which fields auto-populate based on other fields
"""
import json
from datetime import datetime

class FieldDependencyMap:
    """
    Maps field dependencies and auto-population rules
    When one field is filled, it can trigger auto-population of related fields
    """

    def __init__(self):
        # Define field dependencies as: trigger_field -> [dependent_fields]
        self.dependencies = {
            # Name triggers
            'client_nom_complet': [
                'client_adresse_bureau',  # Can infer company email format
                'default_beneficiaire',    # Default beneficiary
            ],

            # Address triggers
            'client_adresse_residence': [
                'client_province_imposition',  # Auto-detect province
                'conjoint_adresse_residence',  # Default same as client
                'postal_code',
                'city',
                'region',
            ],

            # Marital status triggers
            'client_etat_civil': [
                'requires_spouse_info',        # Show/hide spouse fields
                'client_contrat_mariage',      # Marriage contract relevance
                'client_regime_matrimonial',   # Matrimonial regime
                'tax_filing_status',           # Tax implications
            ],

            # Spouse name triggers
            'conjoint_nom_complet': [
                'conjoint_adresse_residence',  # Default same as client
                'joint_beneficiaries',         # Setup joint beneficiaries
                'combined_income',             # Calculate household income
            ],

            # Birth date triggers
            'client_date_naissance': [
                'age',
                'retirement_age',              # Calculate target retirement
                'life_insurance_need',         # Age-based insurance calc
                'investment_horizon',          # Investment time horizon
                'reer_eligibility',            # REER contribution eligibility
                'recommended_risk_profile',    # Age-based risk tolerance
            ],

            # Employment triggers
            'client_employeur': [
                'client_adresse_bureau',       # Company address lookup
                'group_insurance_eligible',    # May have group benefits
                'pension_plan_type',           # Company pension info
            ],

            # Salary triggers
            'client_salaire_annuel_brut': [
                'client_province_imposition',  # Confirm tax province
                'tax_bracket',                 # Calculate tax bracket
                'reer_contribution_room',      # 18% of salary
                'recommended_reer_contribution',
                'recommended_insurance_coverage',  # 5-10x salary
                'monthly_budget_capacity',
                'financial_capacity_score',
            ],

            # Assets/Liabilities triggers
            'client_total_actif': [
                'client_avoir_net',            # Calculate net worth
                'wealth_category',
                'estate_planning_needs',
            ],

            'client_total_passif': [
                'client_avoir_net',            # Calculate net worth
                'debt_to_income_ratio',
                'debt_consolidation_opportunity',
            ],

            # Children triggers
            'nombre_enfants': [
                'resp_recommendation',         # RESP for education
                'life_insurance_multiplier',   # More coverage needed
                'estate_planning_priority',
                'trust_recommendation',
            ],

            # Investment type triggers
            'type_placement': [
                'tax_treatment',               # REER vs CELI vs Non-reg
                'contribution_limits',
                'withdrawal_rules',
                'recommended_allocation',
            ],
        }

        # Auto-calculation formulas
        self.calculations = {
            'age': self._calculate_age,
            'client_avoir_net': self._calculate_net_worth,
            'combined_income': self._calculate_combined_income,
            'tax_bracket': self._calculate_tax_bracket,
            'reer_contribution_room': self._calculate_reer_room,
            'recommended_insurance_coverage': self._calculate_insurance_need,
            'debt_to_income_ratio': self._calculate_debt_ratio,
            'retirement_age': self._calculate_retirement_age,
            'investment_horizon': self._calculate_investment_horizon,
        }

    def get_dependent_fields(self, field_name):
        """Get all fields that depend on the given field"""
        return self.dependencies.get(field_name, [])

    def auto_populate(self, data, changed_field):
        """
        Auto-populate dependent fields when a field changes
        Returns updated data dictionary
        """
        updated_data = data.copy()
        dependent_fields = self.get_dependent_fields(changed_field)

        for dep_field in dependent_fields:
            if dep_field in self.calculations:
                # Calculate the dependent field value
                calc_func = self.calculations[dep_field]
                updated_data[dep_field] = calc_func(updated_data)
            else:
                # Apply rule-based population
                updated_data[dep_field] = self._apply_rule(dep_field, updated_data)

        return updated_data

    def _calculate_age(self, data):
        """Calculate age from birth date"""
        dob = data.get('client_date_naissance', '')
        if not dob:
            return None

        try:
            birth_date = datetime.strptime(dob, '%Y-%m-%d')
            age = (datetime.now() - birth_date).days // 365
            return age
        except:
            return None

    def _calculate_net_worth(self, data):
        """Calculate net worth"""
        actif = data.get('client_total_actif', 0) or 0
        passif = data.get('client_total_passif', 0) or 0
        conjoint_actif = data.get('conjoint_total_actif', 0) or 0
        conjoint_passif = data.get('conjoint_total_passif', 0) or 0

        client_net = actif - passif
        conjoint_net = conjoint_actif - conjoint_passif

        data['client_avoir_net'] = client_net
        data['conjoint_avoir_net'] = conjoint_net
        data['total_avoir_net'] = client_net + conjoint_net

        return client_net + conjoint_net

    def _calculate_combined_income(self, data):
        """Calculate household income"""
        client_income = data.get('client_salaire_annuel_brut', 0) or 0
        conjoint_income = data.get('conjoint_salaire_annuel_brut', 0) or 0
        return client_income + conjoint_income

    def _calculate_tax_bracket(self, data):
        """Determine tax bracket"""
        salary = data.get('client_salaire_annuel_brut', 0) or 0

        # Quebec + Federal combined marginal rates (2024 approx)
        if salary < 49275:
            return "Taux marginal: ~28%"
        elif salary < 98540:
            return "Taux marginal: ~38%"
        elif salary < 119910:
            return "Taux marginal: ~43%"
        elif salary < 173205:
            return "Taux marginal: ~48%"
        else:
            return "Taux marginal: ~53%"

    def _calculate_reer_room(self, data):
        """Calculate REER contribution room"""
        salary = data.get('client_salaire_annuel_brut', 0) or 0
        # 18% of previous year income, max $31,560 (2024)
        room = min(salary * 0.18, 31560)
        return round(room, 2)

    def _calculate_insurance_need(self, data):
        """Calculate recommended insurance coverage"""
        salary = data.get('client_salaire_annuel_brut', 0) or 0
        num_children = len(data.get('enfants', []))
        has_spouse = bool(data.get('conjoint_nom_complet'))

        # Base: 5-10x salary
        multiplier = 5

        # Increase for dependents
        if has_spouse:
            multiplier += 2
        if num_children > 0:
            multiplier += num_children * 1.5

        coverage = salary * min(multiplier, 15)  # Cap at 15x
        return round(coverage, -3)  # Round to nearest thousand

    def _calculate_debt_ratio(self, data):
        """Calculate debt-to-income ratio"""
        income = data.get('client_salaire_annuel_brut', 0) or 0
        debt = data.get('client_total_passif', 0) or 0

        if income == 0:
            return 0

        ratio = (debt / income) * 100
        return round(ratio, 1)

    def _calculate_retirement_age(self, data):
        """Estimate target retirement age"""
        age = self._calculate_age(data)
        if not age:
            return 65

        # Standard retirement age
        return 65

    def _calculate_investment_horizon(self, data):
        """Calculate investment time horizon"""
        age = self._calculate_age(data)
        if not age:
            return 20

        retirement_age = self._calculate_retirement_age(data)
        horizon = retirement_age - age

        return max(horizon, 1)  # At least 1 year

    def _apply_rule(self, field_name, data):
        """Apply specific rules for field population"""

        # Province inference from address
        if field_name == 'client_province_imposition':
            address = data.get('client_adresse_residence', '')
            if any(city in address for city in ['Montréal', 'Laval', 'Boisbriand', 'Québec']):
                return 'Québec'
            return 'Québec'  # Default

        # Spouse address defaults to same as client
        if field_name == 'conjoint_adresse_residence':
            if data.get('client_etat_civil') == 'Marié(e)':
                return data.get('client_adresse_residence', '')

        # Marriage contract required if married
        if field_name == 'client_contrat_mariage':
            if data.get('client_etat_civil') == 'Marié(e)':
                return 'Oui (recommandé)'

        # Default matrimonial regime for Quebec
        if field_name == 'client_regime_matrimonial':
            if data.get('client_etat_civil') == 'Marié(e)':
                return "Société d'aquêts"  # Default in Quebec

        # RESP recommendation if has children
        if field_name == 'resp_recommendation':
            if len(data.get('enfants', [])) > 0:
                return 'Recommandé - Subventions gouvernementales disponibles'

        # Risk profile based on age and horizon
        if field_name == 'recommended_risk_profile':
            age = self._calculate_age(data)
            if age and age < 35:
                return 'Dynamique'
            elif age and age < 50:
                return 'Accéléré'
            elif age and age < 60:
                return 'Équilibré'
            else:
                return 'Modéré'

        return None


def demo_field_dependencies():
    """Demonstrate auto-population based on field dependencies"""
    print("=" * 70)
    print("FIELD DEPENDENCY AUTO-POPULATION DEMO")
    print("=" * 70)

    dependency_map = FieldDependencyMap()

    # Start with minimal data
    data = {}

    print("\n1️⃣  User enters NAME:")
    data['client_nom_complet'] = 'Marie Tremblay'
    print(f"   Input: {data['client_nom_complet']}")

    print("\n2️⃣  User enters BIRTH DATE:")
    data['client_date_naissance'] = '1985-06-15'
    data = dependency_map.auto_populate(data, 'client_date_naissance')
    print(f"   Input: {data['client_date_naissance']}")
    print(f"   ✓ Auto-calculated AGE: {data.get('age')} years")
    print(f"   ✓ Auto-calculated RETIREMENT AGE: {data.get('retirement_age')}")
    print(f"   ✓ Auto-calculated INVESTMENT HORIZON: {data.get('investment_horizon')} years")

    print("\n3️⃣  User enters SALARY:")
    data['client_salaire_annuel_brut'] = 85000
    data = dependency_map.auto_populate(data, 'client_salaire_annuel_brut')
    print(f"   Input: ${data['client_salaire_annuel_brut']:,.2f}")
    print(f"   ✓ Auto-calculated TAX BRACKET: {data.get('tax_bracket')}")
    print(f"   ✓ Auto-calculated REER ROOM: ${data.get('reer_contribution_room'):,.2f}")

    print("\n4️⃣  User enters MARITAL STATUS:")
    data['client_etat_civil'] = 'Marié(e)'
    data = dependency_map.auto_populate(data, 'client_etat_civil')
    print(f"   Input: {data['client_etat_civil']}")
    print(f"   ✓ Auto-suggested CONTRACT: {data.get('client_contrat_mariage')}")
    print(f"   ✓ Auto-suggested REGIME: {data.get('client_regime_matrimonial')}")

    print("\n5️⃣  User enters SPOUSE NAME:")
    data['conjoint_nom_complet'] = 'Pierre Tremblay'
    data = dependency_map.auto_populate(data, 'conjoint_nom_complet')
    print(f"   Input: {data['conjoint_nom_complet']}")

    print("\n6️⃣  User enters ASSETS and LIABILITIES:")
    data['client_total_actif'] = 450000
    data['client_total_passif'] = 180000
    data = dependency_map.auto_populate(data, 'client_total_actif')
    data = dependency_map.auto_populate(data, 'client_total_passif')
    print(f"   Input: Assets ${data['client_total_actif']:,.2f}")
    print(f"   Input: Liabilities ${data['client_total_passif']:,.2f}")
    print(f"   ✓ Auto-calculated NET WORTH: ${data.get('client_avoir_net'):,.2f}")
    print(f"   ✓ Auto-calculated DEBT RATIO: {data.get('debt_to_income_ratio')}%")

    print("\n7️⃣  Add children:")
    data['enfants'] = [
        {'nom_complet': 'Sophie Tremblay', 'age': 8},
        {'nom_complet': 'Lucas Tremblay', 'age': 5}
    ]
    data = dependency_map.auto_populate(data, 'nombre_enfants')
    print(f"   Input: 2 children")
    print(f"   ✓ Auto-calculated INSURANCE NEED: ${data.get('recommended_insurance_coverage'):,.0f}")
    print(f"   ✓ Auto-suggested: {data.get('resp_recommendation', 'RESP for education')}")

    print("\n" + "=" * 70)
    print(f"RESULT: From 7 manual inputs → {len(data)} populated fields!")
    print("=" * 70)


if __name__ == "__main__":
    demo_field_dependencies()
