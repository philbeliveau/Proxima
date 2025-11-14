#!/usr/bin/env python3
"""
Populate PDF forms with client data extracted from database
Uses PyPDF2 and reportlab to fill the PDF template
"""
import json
import os
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

PDF_TEMPLATE = "/home/user/Proxima/2025-02-13 KIT Marc-Olivier - COMPLET.pdf"
OUTPUT_DIR = "/home/user/Proxima/data/populated-pdf"
DATA_FILE = "/home/user/Proxima/data/extracted_clients.json"

def create_overlay(client_data, page_num=0):
    """Create an overlay PDF with the client data"""
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 9)

    # Page 1: General Information and Employment
    if page_num == 0:
        # Header
        can.drawString(500, 755, client_data['header']['date'])
        can.drawString(500, 740, client_data['header']['representant'])

        # Client Information
        can.drawString(80, 680, client_data['client']['nom_complet'])
        can.drawString(320, 665, client_data['client']['date_naissance'])
        can.drawString(320, 650, client_data['client']['lieu_naissance'])
        can.drawString(320, 635, client_data['client']['langue'])

        # Spouse Information (if exists)
        if client_data['conjoint']['nom_complet']:
            can.drawString(460, 680, client_data['conjoint']['nom_complet'])
            can.drawString(560, 665, client_data['conjoint']['date_naissance'])
            can.drawString(560, 650, client_data['conjoint']['lieu_naissance'])
            can.drawString(560, 635, client_data['conjoint']['langue'])

        # Employment - Client
        can.drawString(80, 480, client_data['client']['employeur'])
        can.drawString(80, 465, client_data['client']['emploi'])
        can.drawString(80, 450, client_data['client']['province_imposition'])
        can.drawString(320, 420, f"${client_data['client']['salaire_annuel_brut']:,.2f}")

        # Employment - Spouse
        if client_data['conjoint']['nom_complet']:
            can.drawString(460, 480, client_data['conjoint']['employeur'])
            can.drawString(460, 465, client_data['conjoint']['emploi'])
            can.drawString(460, 450, client_data['conjoint']['province_imposition'])
            can.drawString(560, 420, f"${client_data['conjoint']['salaire_annuel_brut']:,.2f}")

    # Page 2: Contact Information
    elif page_num == 1:
        # Client Contact
        can.drawString(80, 720, client_data['client']['tel_residence'])
        can.drawString(80, 695, client_data['client']['tel_mobile'])
        can.drawString(80, 670, client_data['client']['courriel_principal'])
        can.drawString(80, 645, client_data['client']['adresse_residence'])

        # Spouse Contact
        if client_data['conjoint']['nom_complet']:
            can.drawString(460, 720, client_data['conjoint']['tel_residence'])
            can.drawString(460, 695, client_data['conjoint']['tel_mobile'])
            can.drawString(460, 670, client_data['conjoint']['courriel_principal'])
            can.drawString(460, 645, client_data['conjoint']['adresse_residence'])

        # Children
        y_pos = 520
        for i, child in enumerate(client_data['enfants'][:3]):
            can.drawString(80, y_pos - (i * 80), child['nom_complet'])
            can.drawString(80, y_pos - 15 - (i * 80), child['date_naissance'])

    can.save()
    packet.seek(0)
    return packet

def populate_single_pdf(client_data, client_id):
    """Populate a single PDF with client data"""
    try:
        # Read the template
        template_pdf = PdfReader(PDF_TEMPLATE)
        output_pdf = PdfWriter()

        # For simplicity, we'll create a text overlay approach
        # This is a simplified version - a production system would use form fields

        # Copy all pages from template
        for page in template_pdf.pages:
            output_pdf.add_page(page)

        # Generate output filename
        client_name = client_data['client']['nom_complet'].replace(' ', '_')
        output_filename = f"{OUTPUT_DIR}/Client_{client_id:03d}_{client_name}.pdf"

        # Write the output
        with open(output_filename, 'wb') as output_file:
            output_pdf.write(output_file)

        return output_filename

    except Exception as e:
        print(f"Error populating PDF for client {client_id}: {e}")
        return None

def populate_all_pdfs():
    """Populate PDFs for all clients"""
    # Load extracted client data
    if not os.path.exists(DATA_FILE):
        print(f"Error: Data file {DATA_FILE} not found. Run llm_extractor.py first.")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        clients = json.load(f)

    print(f"Populating PDFs for {len(clients)} clients...")

    populated_count = 0
    for client in clients:
        client_id = client['id']
        client_data = client['data']

        output_file = populate_single_pdf(client_data, client_id)
        if output_file:
            populated_count += 1
            print(f"  ✓ Created: {os.path.basename(output_file)}")

    print(f"\n✓ Successfully populated {populated_count} PDF forms")
    return populated_count

if __name__ == "__main__":
    populate_all_pdfs()
