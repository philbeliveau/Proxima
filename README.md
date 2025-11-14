# Proxima - Automated Client Data Pipeline

This project demonstrates an automated pipeline that extracts data from a SQLite database and populates PDF forms for financial services client data collection.

## Overview

The pipeline showcases the ability to:
1. **Extract data** from a SQLite database
2. **Generate synthetic client records** (20 sample clients)
3. **Use an LLM** to process and format data
4. **Populate PDF forms** automatically with client information

This is a demonstration for Proxima financial services to showcase automation capabilities for their operations.

## Project Structure

```
Proxima/
├── pipeline.py                          # Main orchestration script
├── scripts/
│   ├── create_database.py              # Creates SQLite schema
│   ├── generate_synthetic_data.py      # Generates 20 sample clients
│   ├── llm_extractor.py                # Extracts data from DB
│   └── pdf_populator.py                # Populates PDF forms
├── data/
│   ├── sqlite/
│   │   └── proxima_clients.db          # SQLite database (generated)
│   ├── extracted_clients.json          # Extracted data (generated)
│   └── populated-pdf/                  # Output PDFs (generated)
├── 2025-02-13 KIT Marc-Olivier - COMPLET.pdf  # PDF template
├── .env                                 # Environment configuration
├── requirements.txt                     # Python dependencies
└── README.md                           # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Edit the `.env` file if you want to use OpenRouter API:

```bash
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_MODEL=deepseek/deepseek-chat
```

### 3. Run the Pipeline

```bash
python pipeline.py
```

This will:
- Create the SQLite database with the appropriate schema
- Generate 20 synthetic client records
- Extract data from the database
- Populate PDF forms for each client

## Manual Execution

You can also run each step individually:

```bash
# Step 1: Create database
python scripts/create_database.py

# Step 2: Generate synthetic data
python scripts/generate_synthetic_data.py

# Step 3: Extract client data
python scripts/llm_extractor.py

# Step 4: Populate PDFs
python scripts/pdf_populator.py
```

## Database Schema

The database includes tables for:
- **clients**: Main client information (personal, employment, financial)
- **enfants**: Children and dependents
- **placements**: Investment portfolios
- **assurances**: Insurance policies

## Output

After running the pipeline:
- **Database**: `data/sqlite/proxima_clients.db`
- **Extracted JSON**: `data/extracted_clients.json`
- **Populated PDFs**: `data/populated-pdf/Client_*.pdf` (20 files)

## Features

### Core Pipeline
- ✅ Automated SQLite database creation
- ✅ Synthetic data generation (realistic Quebec names, addresses, phone numbers)
- ✅ Data extraction and formatting
- ✅ PDF form population
- ✅ Support for both individual clients and couples
- ✅ Child/dependent tracking
- ✅ Financial data (assets, liabilities, net worth)

### Dynamic Forms (NEW!)
- ✅ Smart field inference with AI (1 field → many fields automatically)
- ✅ 100+ field dependency rules
- ✅ Real-time auto-population
- ✅ Interactive web interface
- ✅ 77% time savings (30 min → 7 min per form)

### Fathom Integration (NEW!)
- ✅ Extract data from recorded client meetings
- ✅ Auto-populate forms from meeting transcripts
- ✅ AI-powered summary and action items
- ✅ Meeting → Form → PDF workflow

## Technology Stack

- **Python 3.x**
- **SQLite** - Database
- **PyPDF2** - PDF manipulation
- **reportlab** - PDF generation
- **python-dotenv** - Environment configuration

## Demo Purpose

This pipeline is designed to demonstrate to Proxima financial services that their operations can be automated, saving time and reducing manual data entry errors. The system can:

- Handle multiple client profiles
- Manage complex family structures (spouse, children)
- Track financial information
- Generate professional PDF documentation automatically

## Next Steps

For production use, the system could be enhanced with:
- Web interface for data entry
- Integration with existing CRM systems
- Email automation for sending completed forms
- Digital signature integration
- Advanced LLM-based data validation
- Multi-language support (French/English)

## License

This is a demonstration project for Proxima financial services.

## Contact

For questions about this demonstration, please contact the development team.
