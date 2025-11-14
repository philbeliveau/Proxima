#!/usr/bin/env python3
"""Quick verification script for pipeline output"""
import sqlite3
import os
import json

print("=" * 70)
print("PIPELINE OUTPUT VERIFICATION")
print("=" * 70)

# Check database
db_path = "/home/user/Proxima/data/sqlite/proxima_clients.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM clients')
    total_clients = cursor.fetchone()[0]
    print(f"\n✓ Database: {total_clients} client records")

    cursor.execute('SELECT id, client_nom_complet, client_emploi, client_salaire_annuel_brut FROM clients LIMIT 5')
    print("\n  Sample records:")
    for row in cursor.fetchall():
        print(f"    ID {row[0]:2d}: {row[1]:25s} | {row[2]:15s} | ${row[3]:,.2f}/year")

    cursor.execute('SELECT COUNT(*) FROM enfants')
    total_children = cursor.fetchone()[0]
    print(f"\n✓ Children/Dependents: {total_children} records")

    conn.close()
else:
    print("\n✗ Database not found")

# Check extracted JSON
json_path = "/home/user/Proxima/data/extracted_clients.json"
if os.path.exists(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    print(f"\n✓ Extracted JSON: {len(data)} client records")
else:
    print("\n✗ Extracted JSON not found")

# Check PDFs
pdf_dir = "/home/user/Proxima/data/populated-pdf"
if os.path.exists(pdf_dir):
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    print(f"\n✓ Populated PDFs: {len(pdf_files)} files")
    print(f"\n  First 5 PDFs:")
    for pdf in sorted(pdf_files)[:5]:
        size_mb = os.path.getsize(os.path.join(pdf_dir, pdf)) / (1024 * 1024)
        print(f"    {pdf} ({size_mb:.1f} MB)")
else:
    print("\n✗ PDF directory not found")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
