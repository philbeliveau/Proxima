#!/usr/bin/env python3
"""
Smart Field Inference System
Uses LLM to intelligently populate fields based on minimal input
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv("/home/user/Proxima/.env")

class SmartFieldInference:
    """Intelligently infer and populate PDF fields using LLM and rules"""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")

        # Rule-based inference patterns
        self.inference_rules = {
            # Address patterns
            'address_province': self._infer_province_from_address,
            'address_city': self._infer_city_from_address,
            'postal_code': self._infer_postal_code_from_city,

            # Name patterns
            'spouse_last_name': self._infer_spouse_last_name,
            'children_last_names': self._infer_children_last_names,

            # Employment patterns
            'employment_duration': self._calculate_employment_duration,
            'tax_implications': self._infer_tax_implications,

            # Financial patterns
            'net_worth': self._calculate_net_worth,
            'financial_profile': self._infer_financial_profile,
            'recommended_products': self._recommend_financial_products,
        }

    def _infer_province_from_address(self, data):
        """Infer province from city or postal code"""
        address = data.get('client_adresse_residence', '')

        quebec_cities = [
            'Montréal', 'Québec', 'Laval', 'Gatineau', 'Longueuil',
            'Sherbrooke', 'Trois-Rivières', 'Boisbriand', 'Terrebonne'
        ]

        for city in quebec_cities:
            if city.lower() in address.lower():
                return 'Québec'

        # Check postal code pattern (Quebec: H, J, G)
        if any(code in address.upper() for code in ['H', 'J', 'G']):
            return 'Québec'

        return 'Québec'  # Default for this application

    def _infer_city_from_address(self, data):
        """Extract city from full address"""
        address = data.get('client_adresse_residence', '')
        # Pattern: "123 Street Name, City, QC"
        parts = address.split(',')
        if len(parts) >= 2:
            return parts[-2].strip()
        return ''

    def _infer_postal_code_from_city(self, data):
        """Generate or validate postal code format"""
        # Quebec postal code patterns
        postal_codes = {
            'Montréal': 'H',
            'Laval': 'H',
            'Longueuil': 'J',
            'Boisbriand': 'J',
            'Québec': 'G',
            'Gatineau': 'J',
        }

        city = data.get('city', '')
        for key, prefix in postal_codes.items():
            if key.lower() in city.lower():
                return f"{prefix}XX XXX"  # Placeholder pattern
        return ''

    def _infer_spouse_last_name(self, data):
        """Infer spouse's last name based on marital status and regime"""
        client_name = data.get('client_nom_complet', '')
        spouse_name = data.get('conjoint_nom_complet', '')
        regime = data.get('client_regime_matrimonial', '')

        if not spouse_name:
            return None

        # If married with traditional regime, spouse might share last name
        if 'Marié' in data.get('client_etat_civil', ''):
            client_last = client_name.split()[-1] if client_name else ''
            return client_last

        return None

    def _infer_children_last_names(self, data):
        """Infer children's last names based on parents"""
        client_name = data.get('client_nom_complet', '')
        client_last = client_name.split()[-1] if client_name else ''

        # In Quebec, children typically take father's or both parents' names
        return client_last

    def _calculate_employment_duration(self, data):
        """Calculate years of employment"""
        from datetime import datetime

        emploi_depuis = data.get('client_emploi_depuis', '')
        if emploi_depuis:
            try:
                start_date = datetime.strptime(emploi_depuis, '%Y-%m-%d')
                years = (datetime.now() - start_date).days / 365.25
                return f"{years:.1f} ans"
            except:
                pass
        return ''

    def _infer_tax_implications(self, data):
        """Infer tax bracket and implications"""
        salary = data.get('client_salaire_annuel_brut', 0)

        # Quebec tax brackets (simplified 2024)
        if salary < 49275:
            return "Taux d'imposition: ~28% (provincial + fédéral)"
        elif salary < 98540:
            return "Taux d'imposition: ~38% (provincial + fédéral)"
        elif salary < 119910:
            return "Taux d'imposition: ~43% (provincial + fédéral)"
        else:
            return "Taux d'imposition: ~48%+ (provincial + fédéral)"

    def _calculate_net_worth(self, data):
        """Calculate total net worth"""
        client_actif = data.get('client_total_actif', 0) or 0
        client_passif = data.get('client_total_passif', 0) or 0
        conjoint_actif = data.get('conjoint_total_actif', 0) or 0
        conjoint_passif = data.get('conjoint_total_passif', 0) or 0

        return (client_actif - client_passif) + (conjoint_actif - conjoint_passif)

    def _infer_financial_profile(self, data):
        """Determine financial profile/risk tolerance"""
        age = self._calculate_age(data.get('client_date_naissance', ''))
        salary = data.get('client_salaire_annuel_brut', 0) or 0
        net_worth = self._calculate_net_worth(data)

        # Simple profile inference
        if age < 35 and net_worth < 100000:
            return "Profil: Accumulateur - Focus croissance"
        elif age < 50 and net_worth < 500000:
            return "Profil: Bâtisseur - Équilibre croissance/protection"
        elif age < 60:
            return "Profil: Consolidateur - Protection et croissance modérée"
        else:
            return "Profil: Préservateur - Protection du capital"

    def _calculate_age(self, date_naissance):
        """Calculate age from birth date"""
        from datetime import datetime
        if not date_naissance:
            return 45  # Default
        try:
            birth = datetime.strptime(date_naissance, '%Y-%m-%d')
            age = (datetime.now() - birth).days / 365.25
            return int(age)
        except:
            return 45

    def _recommend_financial_products(self, data):
        """Recommend financial products based on profile"""
        age = self._calculate_age(data.get('client_date_naissance', ''))
        salary = data.get('client_salaire_annuel_brut', 0) or 0
        has_spouse = bool(data.get('conjoint_nom_complet'))
        has_children = len(data.get('enfants', []))

        recommendations = []

        # Life insurance
        if has_spouse or has_children:
            recommendations.append("Assurance vie: Recommandé (protection familiale)")

        # REER
        if salary > 50000:
            recommendations.append("REER: Maximiser cotisations (économie d'impôt)")

        # CELI
        recommendations.append("CELI: Investissement libre d'impôt")

        # RESP
        if has_children:
            recommendations.append("REEE: Épargne-études avec subventions")

        # Disability insurance
        if salary > 40000:
            recommendations.append("Assurance invalidité: Protection du revenu")

        return " | ".join(recommendations)

    def infer_from_minimal_input(self, minimal_data):
        """
        Given minimal client data, infer all related fields

        Example input:
        {
            'client_nom_complet': 'Jean Tremblay',
            'client_date_naissance': '1985-05-15',
            'client_adresse_residence': '123 Rue Principale, Boisbriand, QC',
            'client_salaire_annuel_brut': 75000
        }
        """
        enhanced_data = minimal_data.copy()

        # Apply rule-based inferences
        enhanced_data['client_province_imposition'] = self._infer_province_from_address(minimal_data)
        enhanced_data['city'] = self._infer_city_from_address(minimal_data)
        enhanced_data['age'] = self._calculate_age(minimal_data.get('client_date_naissance', ''))
        enhanced_data['tax_bracket'] = self._infer_tax_implications(minimal_data)
        enhanced_data['financial_profile'] = self._infer_financial_profile(minimal_data)
        enhanced_data['product_recommendations'] = self._recommend_financial_products(minimal_data)

        # Calculate defaults
        enhanced_data['client_reer_non_cotise'] = self._calculate_reer_room(minimal_data)
        enhanced_data['client_celi_non_cotise'] = 95000  # 2024 max cumulative

        return enhanced_data

    def _calculate_reer_room(self, data):
        """Calculate REER contribution room"""
        salary = data.get('client_salaire_annuel_brut', 0) or 0
        # 18% of previous year's income, up to annual limit
        return min(salary * 0.18, 31560)  # 2024 limit

    def infer_with_llm(self, minimal_data):
        """
        Use LLM to infer missing fields with intelligent reasoning
        This provides more sophisticated inference than rules alone
        """
        if not self.api_key:
            print("Warning: No OpenRouter API key configured. Using rule-based inference only.")
            return self.infer_from_minimal_input(minimal_data)

        prompt = f"""You are a financial advisor assistant for Proxima, a Quebec-based financial services firm.

Given the following client information, infer and suggest values for missing fields:

CLIENT DATA:
{json.dumps(minimal_data, indent=2, ensure_ascii=False)}

Please infer the following based on Quebec context and financial planning best practices:
1. Likely employment sector based on name/age/salary
2. Recommended insurance coverage amounts
3. Investment profile (Conservative/Moderate/Balanced/Aggressive/Dynamic)
4. Tax optimization opportunities
5. Financial goals based on age and situation
6. Recommended REER contribution for this year
7. Recommended emergency fund amount

Provide your response as a JSON object with these fields clearly labeled.
Keep recommendations specific to Quebec regulations and French-Canadian context."""

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                llm_suggestions = result['choices'][0]['message']['content']

                # Combine rule-based and LLM-based inference
                enhanced_data = self.infer_from_minimal_input(minimal_data)
                enhanced_data['llm_suggestions'] = llm_suggestions

                return enhanced_data
            else:
                print(f"LLM API error: {response.status_code}")
                return self.infer_from_minimal_input(minimal_data)

        except Exception as e:
            print(f"Error calling LLM: {e}")
            return self.infer_from_minimal_input(minimal_data)


def demo_smart_inference():
    """Demonstrate smart field inference"""
    print("=" * 70)
    print("SMART FIELD INFERENCE DEMO")
    print("=" * 70)

    # Minimal input - just a few fields
    minimal_input = {
        'client_nom_complet': 'Sophie Gagnon',
        'client_date_naissance': '1988-03-22',
        'client_adresse_residence': '456 Boulevard de la Grande-Allée, Boisbriand, QC',
        'client_salaire_annuel_brut': 85000,
        'client_etat_civil': 'Marié(e)',
        'conjoint_nom_complet': 'Martin Leblanc',
        'client_total_actif': 450000,
        'client_total_passif': 180000,
    }

    print("\n📝 MINIMAL INPUT (8 fields):")
    for key, value in minimal_input.items():
        print(f"  {key}: {value}")

    # Run inference
    inferencer = SmartFieldInference()
    enhanced_data = inferencer.infer_from_minimal_input(minimal_input)

    print("\n🧠 INFERRED FIELDS:")
    inferred_fields = {k: v for k, v in enhanced_data.items() if k not in minimal_input}
    for key, value in inferred_fields.items():
        print(f"  {key}: {value}")

    print(f"\n✓ Expanded from {len(minimal_input)} to {len(enhanced_data)} fields!")
    print("=" * 70)


if __name__ == "__main__":
    demo_smart_inference()
