#!/usr/bin/env python3
"""
Extract client data from database using OpenRouter LLM
This script queries the database and formats data for PDF population
"""
import sqlite3
import os
import json
from dotenv import load_dotenv

DB_PATH = "/home/user/Proxima/data/sqlite/proxima_clients.db"

# Load environment variables
load_dotenv("/home/user/Proxima/.env")

def get_client_data(client_id):
    """Extract a single client's data from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()

    # Get client data
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()

    if not client:
        print(f"Client ID {client_id} not found")
        return None

    # Convert to dictionary
    client_data = dict(client)

    # Get children data
    cursor.execute("SELECT * FROM enfants WHERE client_id = ?", (client_id,))
    children = cursor.fetchall()
    client_data['enfants'] = [dict(child) for child in children]

    # Get placements data
    cursor.execute("SELECT * FROM placements WHERE client_id = ?", (client_id,))
    placements = cursor.fetchall()
    client_data['placements'] = [dict(p) for p in placements]

    # Get assurances data
    cursor.execute("SELECT * FROM assurances WHERE client_id = ?", (client_id,))
    assurances = cursor.fetchall()
    client_data['assurances'] = [dict(a) for a in assurances]

    conn.close()
    return client_data

def get_all_client_ids():
    """Get all client IDs from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM clients ORDER BY id")
    ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ids

def format_for_pdf(client_data):
    """Format client data for PDF population"""
    # This function prepares the data in a format suitable for PDF filling
    # Returns a structured dictionary with all fields needed for the PDF

    formatted = {
        'header': {
            'date': client_data.get('date', ''),
            'representant': client_data.get('representant', '')
        },
        'client': {
            'nom_complet': client_data.get('client_nom_complet', ''),
            'date_naissance': client_data.get('client_date_naissance', ''),
            'sexe': client_data.get('client_sexe', ''),
            'lieu_naissance': client_data.get('client_lieu_naissance', ''),
            'langue': client_data.get('client_langue', ''),
            'fumeur': client_data.get('client_fumeur', ''),
            'etat_civil': client_data.get('client_etat_civil', ''),
            'etat_civil_depuis': client_data.get('client_etat_civil_depuis', ''),
            'reer_non_cotise': client_data.get('client_reer_non_cotise', 0),
            'celi_non_cotise': client_data.get('client_celi_non_cotise', 0),
            'employeur': client_data.get('client_employeur', ''),
            'emploi': client_data.get('client_emploi', ''),
            'emploi_depuis': client_data.get('client_emploi_depuis', ''),
            'province_imposition': client_data.get('client_province_imposition', ''),
            'salaire_annuel_brut': client_data.get('client_salaire_annuel_brut', 0),
            'ajustement_fiscal': client_data.get('client_ajustement_fiscal', 0),
            'autre_revenu_1': client_data.get('client_autre_revenu_1', 0),
            'autre_revenu_2': client_data.get('client_autre_revenu_2', 0),
            'autre_revenu_3': client_data.get('client_autre_revenu_3', 0),
            'tel_residence': client_data.get('client_tel_residence', ''),
            'tel_bureau': client_data.get('client_tel_bureau', ''),
            'tel_mobile': client_data.get('client_tel_mobile', ''),
            'courriel_principal': client_data.get('client_courriel_principal', ''),
            'adresse_residence': client_data.get('client_adresse_residence', ''),
            'testament': client_data.get('client_testament', ''),
            'testament_type': client_data.get('client_testament_type', ''),
            'contrat_mariage': client_data.get('client_contrat_mariage', ''),
            'regime_matrimonial': client_data.get('client_regime_matrimonial', ''),
            'total_actif': client_data.get('client_total_actif', 0),
            'total_passif': client_data.get('client_total_passif', 0),
            'avoir_net': client_data.get('client_avoir_net', 0),
        },
        'conjoint': {
            'nom_complet': client_data.get('conjoint_nom_complet', ''),
            'date_naissance': client_data.get('conjoint_date_naissance', ''),
            'sexe': client_data.get('conjoint_sexe', ''),
            'lieu_naissance': client_data.get('conjoint_lieu_naissance', ''),
            'langue': client_data.get('conjoint_langue', ''),
            'fumeur': client_data.get('conjoint_fumeur', ''),
            'etat_civil': client_data.get('conjoint_etat_civil', ''),
            'reer_non_cotise': client_data.get('conjoint_reer_non_cotise', 0),
            'celi_non_cotise': client_data.get('conjoint_celi_non_cotise', 0),
            'employeur': client_data.get('conjoint_employeur', ''),
            'emploi': client_data.get('conjoint_emploi', ''),
            'province_imposition': client_data.get('conjoint_province_imposition', ''),
            'salaire_annuel_brut': client_data.get('conjoint_salaire_annuel_brut', 0),
            'tel_residence': client_data.get('conjoint_tel_residence', ''),
            'tel_mobile': client_data.get('conjoint_tel_mobile', ''),
            'courriel_principal': client_data.get('conjoint_courriel_principal', ''),
            'adresse_residence': client_data.get('conjoint_adresse_residence', ''),
            'total_actif': client_data.get('conjoint_total_actif', 0),
            'total_passif': client_data.get('conjoint_total_passif', 0),
            'avoir_net': client_data.get('conjoint_avoir_net', 0),
        },
        'enfants': client_data.get('enfants', []),
        'total_avoir_net': client_data.get('total_avoir_net', 0)
    }

    return formatted

def extract_all_clients():
    """Extract all clients from database and return formatted data"""
    client_ids = get_all_client_ids()
    all_clients = []

    print(f"Extracting data for {len(client_ids)} clients...")

    for client_id in client_ids:
        client_data = get_client_data(client_id)
        if client_data:
            formatted_data = format_for_pdf(client_data)
            all_clients.append({
                'id': client_id,
                'data': formatted_data
            })
            print(f"  ✓ Extracted client {client_id}: {client_data['client_nom_complet']}")

    return all_clients

if __name__ == "__main__":
    clients = extract_all_clients()
    print(f"\n✓ Successfully extracted {len(clients)} client records")

    # Save to JSON for debugging
    output_file = "/home/user/Proxima/data/extracted_clients.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clients, f, indent=2, ensure_ascii=False)

    print(f"✓ Data saved to {output_file}")
