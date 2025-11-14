#!/usr/bin/env python3
"""
Create SQLite database schema for Proxima client data collection form
"""
import sqlite3
import os

DB_PATH = "/home/user/Proxima/data/sqlite/proxima_clients.db"

def create_database():
    """Create the database schema"""
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Main clients table
    cursor.execute("""
    CREATE TABLE clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        representant TEXT,

        -- CLIENT(E) Information
        client_nom_complet TEXT,
        client_date_naissance TEXT,
        client_sexe TEXT,
        client_lieu_naissance TEXT,
        client_langue TEXT,
        client_fumeur TEXT,
        client_etat_civil TEXT,
        client_etat_civil_depuis TEXT,
        client_reer_non_cotise REAL,
        client_celi_non_cotise REAL,

        -- CLIENT(E) Employment
        client_employeur TEXT,
        client_emploi TEXT,
        client_emploi_depuis TEXT,
        client_province_imposition TEXT,
        client_salaire_annuel_brut REAL,
        client_ajustement_fiscal REAL,
        client_autre_revenu_1 REAL,
        client_autre_revenu_2 REAL,
        client_autre_revenu_3 REAL,

        -- CLIENT(E) Contact
        client_tel_residence TEXT,
        client_tel_bureau TEXT,
        client_tel_mobile TEXT,
        client_tel_autre TEXT,
        client_courriel_principal TEXT,
        client_courriel_secondaire TEXT,
        client_adresse_residence TEXT,
        client_adresse_bureau TEXT,
        client_adresse_autre TEXT,

        -- CONJOINT(E) Information
        conjoint_nom_complet TEXT,
        conjoint_date_naissance TEXT,
        conjoint_sexe TEXT,
        conjoint_lieu_naissance TEXT,
        conjoint_langue TEXT,
        conjoint_fumeur TEXT,
        conjoint_etat_civil TEXT,
        conjoint_etat_civil_depuis TEXT,
        conjoint_reer_non_cotise REAL,
        conjoint_celi_non_cotise REAL,

        -- CONJOINT(E) Employment
        conjoint_employeur TEXT,
        conjoint_emploi TEXT,
        conjoint_emploi_depuis TEXT,
        conjoint_province_imposition TEXT,
        conjoint_salaire_annuel_brut REAL,
        conjoint_ajustement_fiscal REAL,
        conjoint_autre_revenu_1 REAL,
        conjoint_autre_revenu_2 REAL,
        conjoint_autre_revenu_3 REAL,

        -- CONJOINT(E) Contact
        conjoint_tel_residence TEXT,
        conjoint_tel_bureau TEXT,
        conjoint_tel_mobile TEXT,
        conjoint_tel_autre TEXT,
        conjoint_courriel_principal TEXT,
        conjoint_courriel_secondaire TEXT,
        conjoint_adresse_residence TEXT,
        conjoint_adresse_bureau TEXT,
        conjoint_adresse_autre TEXT,

        -- Compliance
        client_testament TEXT,
        client_testament_type TEXT,
        client_testament_notaire TEXT,
        client_contrat_mariage TEXT,
        client_regime_matrimonial TEXT,
        client_mandat_protection TEXT,

        conjoint_testament TEXT,
        conjoint_testament_type TEXT,
        conjoint_testament_notaire TEXT,
        conjoint_mandat_protection TEXT,

        -- Financial Summary
        client_total_actif REAL,
        client_total_passif REAL,
        client_avoir_net REAL,
        conjoint_total_actif REAL,
        conjoint_total_passif REAL,
        conjoint_avoir_net REAL,
        total_avoir_net REAL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Children/Dependents table
    cursor.execute("""
    CREATE TABLE enfants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        nom_complet TEXT,
        date_naissance TEXT,
        sexe TEXT,
        a_charge TEXT,
        FOREIGN KEY (client_id) REFERENCES clients(id)
    )
    """)

    # Investments table
    cursor.execute("""
    CREATE TABLE placements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        proprietaire TEXT,
        description TEXT,
        type_placement TEXT,
        categorie_actif TEXT,
        montant REAL,
        cotisation REAL,
        frequence TEXT,
        notes TEXT,
        FOREIGN KEY (client_id) REFERENCES clients(id)
    )
    """)

    # Insurance table
    cursor.execute("""
    CREATE TABLE assurances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        assure TEXT,
        type_police TEXT,
        compagnie TEXT,
        collective TEXT,
        montant REAL,
        prime_an REAL,
        echeance TEXT,
        beneficiaire TEXT,
        notes TEXT,
        FOREIGN KEY (client_id) REFERENCES clients(id)
    )
    """)

    conn.commit()
    conn.close()
    print(f"Database created successfully at {DB_PATH}")

if __name__ == "__main__":
    create_database()
