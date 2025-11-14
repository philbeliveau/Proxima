#!/usr/bin/env python3
"""
Main Pipeline Script for Proxima Client Data Processing
This script orchestrates the entire workflow:
1. Create SQLite database
2. Generate 20 synthetic client records
3. Extract data from database
4. Populate PDF forms with client data
"""

import sys
import os
import subprocess
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

def run_step(step_name, script_path):
    """Run a pipeline step and handle errors"""
    print(f"\n{'='*70}")
    print(f"STEP: {step_name}")
    print(f"{'='*70}")

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✓ {step_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error in {step_name}: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error in {step_name}: {e}")
        return False

def main():
    """Run the complete pipeline"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║              PROXIMA CLIENT DATA PIPELINE                        ║
║        Automated PDF Form Population System                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    steps = [
        ("Create Database", SCRIPTS_DIR / "create_database.py"),
        ("Generate Synthetic Data", SCRIPTS_DIR / "generate_synthetic_data.py"),
        ("Extract Client Data", SCRIPTS_DIR / "llm_extractor.py"),
        ("Populate PDF Forms", SCRIPTS_DIR / "pdf_populator.py"),
    ]

    results = []
    for step_name, script_path in steps:
        success = run_step(step_name, script_path)
        results.append((step_name, success))

        if not success:
            print(f"\n✗ Pipeline failed at: {step_name}")
            print("Please check the error messages above and try again.")
            return 1

    # Print summary
    print(f"\n{'='*70}")
    print("PIPELINE SUMMARY")
    print(f"{'='*70}")

    for step_name, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status:12} | {step_name}")

    print(f"{'='*70}")

    all_success = all(success for _, success in results)
    if all_success:
        print("\n🎉 Pipeline completed successfully!")
        print(f"\n📁 Output Location:")
        print(f"   - Database: /home/user/Proxima/data/sqlite/proxima_clients.db")
        print(f"   - Extracted Data: /home/user/Proxima/data/extracted_clients.json")
        print(f"   - Populated PDFs: /home/user/Proxima/data/populated-pdf/")
        print(f"\n💡 Next Steps:")
        print(f"   - Review the generated PDFs in data/populated-pdf/")
        print(f"   - Check the database with: sqlite3 data/sqlite/proxima_clients.db")
        print(f"   - View extracted data: cat data/extracted_clients.json")
        return 0
    else:
        print("\n✗ Pipeline completed with errors")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
