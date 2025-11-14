#!/usr/bin/env python3
"""
Generate 20 synthetic client records for Proxima database
"""
import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "/home/user/Proxima/data/sqlite/proxima_clients.db"

# Sample data for generation
PRENOMS_HOMME = ["Marc-Olivier", "Jean", "Pierre", "Luc", "Martin", "Philippe", "François", "Michel", "André", "Robert", "Daniel", "Alain", "Claude", "Éric", "Benoit", "Mathieu", "Stéphane", "David", "Simon", "Nicolas"]
PRENOMS_FEMME = ["Marie", "Sophie", "Julie", "Caroline", "Isabelle", "Nathalie", "Sylvie", "Catherine", "Louise", "Diane", "Chantal", "Nicole", "Hélène", "Lucie", "Véronique", "Annie", "Johanne", "Brigitte", "Patricia", "Martine"]
NOMS = ["Gagnon", "Roy", "Bouchard", "Tremblay", "Côté", "Fortin", "Gauthier", "Morin", "Lavoie", "Girard", "Leblanc", "Bergeron", "Paquette", "Beaulieu", "Caron", "Lefebvre", "Pelletier", "Bélanger", "Martin", "Fournier"]

VILLES_QC = ["Montréal", "Québec", "Laval", "Gatineau", "Sherbrooke", "Trois-Rivières", "Boisbriand", "Longueuil", "Terrebonne", "Saint-Jean-sur-Richelieu"]
RUES = ["Boulevard de la Grande-Allée", "Rue Saint-Denis", "Avenue du Parc", "Chemin de la Côte-des-Neiges", "Boulevard René-Lévesque", "Rue Sainte-Catherine", "Avenue Papineau", "Rue Saint-Hubert", "Boulevard Henri-Bourassa", "Rue Sherbrooke"]

EMPLOIS = ["Ingénieur", "Comptable", "Enseignant", "Infirmière", "Programmeur", "Gestionnaire", "Consultant", "Technicien", "Analyste", "Designer", "Architecte", "Médecin", "Avocat", "Pharmacien", "Électricien"]
EMPLOYEURS = ["Hydro-Québec", "Desjardins", "Banque Nationale", "SAQ", "Bombardier", "CAE", "CGI", "Bell Canada", "Air Canada", "Gouvernement du Québec", "Ville de Montréal", "CIUSSS", "Intact Assurance", "Molson Coors", "Metro Inc"]

def random_date(start_year, end_year):
    """Generate random date"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")

def random_phone():
    """Generate random Quebec phone number"""
    area_codes = ["514", "438", "450", "579", "418", "581", "819", "873"]
    return f"{random.choice(area_codes)}-{random.randint(200,999)}-{random.randint(1000,9999)}"

def random_email(prenom, nom):
    """Generate random email"""
    domains = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.ca", "videotron.ca"]
    return f"{prenom.lower().replace('-', '')}.{nom.lower()}@{random.choice(domains)}"

def generate_client_data():
    """Generate one client record"""
    sexe = random.choice(["H", "F"])
    if sexe == "H":
        prenom = random.choice(PRENOMS_HOMME)
    else:
        prenom = random.choice(PRENOMS_FEMME)

    nom = random.choice(NOMS)
    nom_complet = f"{prenom} {nom}"

    # Generate spouse data (70% chance of having spouse)
    has_spouse = random.random() < 0.7
    conjoint_data = {}

    if has_spouse:
        conjoint_sexe = "F" if sexe == "H" else "H"
        if conjoint_sexe == "H":
            conjoint_prenom = random.choice(PRENOMS_HOMME)
        else:
            conjoint_prenom = random.choice(PRENOMS_FEMME)
        conjoint_nom = random.choice(NOMS)
        conjoint_nom_complet = f"{conjoint_prenom} {conjoint_nom}"

        conjoint_data = {
            'conjoint_nom_complet': conjoint_nom_complet,
            'conjoint_date_naissance': random_date(1965, 1995),
            'conjoint_sexe': conjoint_sexe,
            'conjoint_lieu_naissance': random.choice(VILLES_QC),
            'conjoint_langue': random.choice(["Français", "Anglais", "Français"]),
            'conjoint_fumeur': random.choice(["Oui", "Non", "Non", "Non"]),
            'conjoint_etat_civil': "Marié(e)",
            'conjoint_etat_civil_depuis': random_date(1995, 2020),
            'conjoint_reer_non_cotise': round(random.uniform(5000, 50000), 2),
            'conjoint_celi_non_cotise': round(random.uniform(3000, 20000), 2),
            'conjoint_employeur': random.choice(EMPLOYEURS),
            'conjoint_emploi': random.choice(EMPLOIS),
            'conjoint_emploi_depuis': random_date(2005, 2023),
            'conjoint_province_imposition': "Québec",
            'conjoint_salaire_annuel_brut': round(random.uniform(45000, 120000), 2),
            'conjoint_ajustement_fiscal': round(random.uniform(-5000, 5000), 2),
            'conjoint_autre_revenu_1': round(random.uniform(0, 10000), 2) if random.random() < 0.3 else 0,
            'conjoint_autre_revenu_2': 0,
            'conjoint_autre_revenu_3': 0,
            'conjoint_tel_residence': random_phone(),
            'conjoint_tel_bureau': random_phone(),
            'conjoint_tel_mobile': random_phone(),
            'conjoint_tel_autre': "",
            'conjoint_courriel_principal': random_email(conjoint_prenom, conjoint_nom),
            'conjoint_courriel_secondaire': "",
            'conjoint_adresse_residence': f"{random.randint(100, 9999)} {random.choice(RUES)}, {random.choice(VILLES_QC)}, QC",
            'conjoint_adresse_bureau': "",
            'conjoint_adresse_autre': "",
            'conjoint_testament': random.choice(["Oui", "Non"]),
            'conjoint_testament_type': random.choice(["Notarié", "Olographe", "Devant témoins"]) if random.random() < 0.6 else "",
            'conjoint_testament_notaire': f"Me {random.choice(PRENOMS_HOMME)} {random.choice(NOMS)}" if random.random() < 0.5 else "",
            'conjoint_mandat_protection': random.choice(["Oui", "Non"]),
            'conjoint_total_actif': round(random.uniform(100000, 800000), 2),
            'conjoint_total_passif': round(random.uniform(20000, 200000), 2),
        }
        conjoint_data['conjoint_avoir_net'] = conjoint_data['conjoint_total_actif'] - conjoint_data['conjoint_total_passif']
        etat_civil = "Marié(e)"
    else:
        etat_civil = random.choice(["Célibataire", "Divorcé(e)", "Séparé(e)"])
        conjoint_data = {k: None for k in [
            'conjoint_nom_complet', 'conjoint_date_naissance', 'conjoint_sexe', 'conjoint_lieu_naissance',
            'conjoint_langue', 'conjoint_fumeur', 'conjoint_etat_civil', 'conjoint_etat_civil_depuis',
            'conjoint_reer_non_cotise', 'conjoint_celi_non_cotise', 'conjoint_employeur', 'conjoint_emploi',
            'conjoint_emploi_depuis', 'conjoint_province_imposition', 'conjoint_salaire_annuel_brut',
            'conjoint_ajustement_fiscal', 'conjoint_autre_revenu_1', 'conjoint_autre_revenu_2',
            'conjoint_autre_revenu_3', 'conjoint_tel_residence', 'conjoint_tel_bureau', 'conjoint_tel_mobile',
            'conjoint_tel_autre', 'conjoint_courriel_principal', 'conjoint_courriel_secondaire',
            'conjoint_adresse_residence', 'conjoint_adresse_bureau', 'conjoint_adresse_autre',
            'conjoint_testament', 'conjoint_testament_type', 'conjoint_testament_notaire',
            'conjoint_mandat_protection', 'conjoint_total_actif', 'conjoint_total_passif', 'conjoint_avoir_net'
        ]}

    client_actif = round(random.uniform(100000, 1000000), 2)
    client_passif = round(random.uniform(20000, 300000), 2)
    client_avoir_net = client_actif - client_passif

    total_avoir_net = client_avoir_net + (conjoint_data.get('conjoint_avoir_net') or 0)

    data = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'representant': "Marc-Olivier Gagnon, Pl.fin",
        'client_nom_complet': nom_complet,
        'client_date_naissance': random_date(1960, 1995),
        'client_sexe': sexe,
        'client_lieu_naissance': random.choice(VILLES_QC),
        'client_langue': random.choice(["Français", "Anglais", "Français"]),
        'client_fumeur': random.choice(["Oui", "Non", "Non", "Non"]),
        'client_etat_civil': etat_civil,
        'client_etat_civil_depuis': random_date(1995, 2020) if etat_civil != "Célibataire" else "",
        'client_reer_non_cotise': round(random.uniform(5000, 60000), 2),
        'client_celi_non_cotise': round(random.uniform(3000, 25000), 2),
        'client_employeur': random.choice(EMPLOYEURS),
        'client_emploi': random.choice(EMPLOIS),
        'client_emploi_depuis': random_date(2000, 2023),
        'client_province_imposition': "Québec",
        'client_salaire_annuel_brut': round(random.uniform(50000, 150000), 2),
        'client_ajustement_fiscal': round(random.uniform(-5000, 5000), 2),
        'client_autre_revenu_1': round(random.uniform(0, 15000), 2) if random.random() < 0.4 else 0,
        'client_autre_revenu_2': round(random.uniform(0, 8000), 2) if random.random() < 0.2 else 0,
        'client_autre_revenu_3': 0,
        'client_tel_residence': random_phone(),
        'client_tel_bureau': random_phone(),
        'client_tel_mobile': random_phone(),
        'client_tel_autre': "",
        'client_courriel_principal': random_email(prenom, nom),
        'client_courriel_secondaire': "",
        'client_adresse_residence': f"{random.randint(100, 9999)} {random.choice(RUES)}, {random.choice(VILLES_QC)}, QC",
        'client_adresse_bureau': "",
        'client_adresse_autre': "",
        'client_testament': random.choice(["Oui", "Non", "Oui"]),
        'client_testament_type': random.choice(["Notarié", "Olographe", "Devant témoins"]) if random.random() < 0.7 else "",
        'client_testament_notaire': f"Me {random.choice(PRENOMS_HOMME)} {random.choice(NOMS)}" if random.random() < 0.5 else "",
        'client_contrat_mariage': "Oui" if has_spouse else "Non",
        'client_regime_matrimonial': random.choice(["Société d'aquêts", "Séparation de biens"]) if has_spouse else "",
        'client_mandat_protection': random.choice(["Oui", "Non"]),
        'client_total_actif': client_actif,
        'client_total_passif': client_passif,
        'client_avoir_net': client_avoir_net,
        'total_avoir_net': total_avoir_net,
    }

    data.update(conjoint_data)
    return data

def populate_database():
    """Generate and insert 20 client records"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get column names
    columns = list(generate_client_data().keys())
    placeholders = ','.join(['?' for _ in columns])
    column_names = ','.join(columns)

    print("Generating 20 synthetic client records...")
    for i in range(20):
        data = generate_client_data()
        values = [data[col] for col in columns]

        cursor.execute(f"INSERT INTO clients ({column_names}) VALUES ({placeholders})", values)
        client_id = cursor.lastrowid

        # Add 0-3 children per family
        num_children = random.randint(0, 3)
        for j in range(num_children):
            child_sexe = random.choice(["H", "F"])
            if child_sexe == "H":
                child_prenom = random.choice(PRENOMS_HOMME)
            else:
                child_prenom = random.choice(PRENOMS_FEMME)

            child_nom = data['client_nom_complet'].split()[-1]  # Use client's last name

            cursor.execute("""
                INSERT INTO enfants (client_id, nom_complet, date_naissance, sexe, a_charge)
                VALUES (?, ?, ?, ?, ?)
            """, (client_id, f"{child_prenom} {child_nom}", random_date(2000, 2020), child_sexe, "Oui"))

        print(f"  Created client {i+1}: {data['client_nom_complet']}")

    conn.commit()
    conn.close()
    print(f"\n✓ Successfully populated database with 20 client records")

if __name__ == "__main__":
    populate_database()
