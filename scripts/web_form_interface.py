#!/usr/bin/env python3
"""
Interactive Web Form with Auto-Population
Flask-based web interface for dynamic PDF form filling
"""
from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import sys

# Add scripts to path
sys.path.insert(0, os.path.dirname(__file__))

from field_dependency_map import FieldDependencyMap
from smart_field_inference import SmartFieldInference

app = Flask(__name__)
dependency_map = FieldDependencyMap()
smart_inference = SmartFieldInference()

# Store session data (in production, use proper session management)
form_data = {}


@app.route('/')
def index():
    """Main form interface"""
    return render_template('index.html')


@app.route('/api/autocomplete', methods=['POST'])
def autocomplete():
    """
    Auto-complete endpoint
    Receives a field update and returns all auto-populated fields
    """
    data = request.json
    field_name = data.get('field_name')
    field_value = data.get('field_value')

    # Update form data
    form_data[field_name] = field_value

    # Auto-populate dependent fields
    updated_data = dependency_map.auto_populate(form_data, field_name)

    # Get only the newly calculated fields
    new_fields = {k: v for k, v in updated_data.items() if k not in form_data}

    # Update stored data
    form_data.update(updated_data)

    return jsonify({
        'success': True,
        'updated_fields': new_fields,
        'dependent_fields': dependency_map.get_dependent_fields(field_name)
    })


@app.route('/api/smart_inference', methods=['POST'])
def smart_inference_endpoint():
    """
    Smart inference endpoint using LLM
    Takes minimal data and returns comprehensive suggestions
    """
    data = request.json
    minimal_data = data.get('data', {})

    # Run smart inference
    enhanced_data = smart_inference.infer_from_minimal_input(minimal_data)

    return jsonify({
        'success': True,
        'enhanced_data': enhanced_data
    })


@app.route('/api/save', methods=['POST'])
def save_form():
    """Save form data"""
    data = request.json
    form_data.update(data)

    # Save to JSON file
    output_file = '/home/user/Proxima/data/web_form_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(form_data, f, indent=2, ensure_ascii=False)

    return jsonify({
        'success': True,
        'message': 'Form data saved successfully'
    })


@app.route('/api/generate_pdf', methods=['POST'])
def generate_pdf():
    """Generate PDF from current form data"""
    # This would call the PDF population script
    from pdf_populator import populate_single_pdf

    client_id = form_data.get('id', 999)
    formatted_data = {
        'header': {
            'date': form_data.get('date', ''),
            'representant': form_data.get('representant', 'Marc-Olivier Gagnon, Pl.fin')
        },
        'client': {k.replace('client_', ''): v for k, v in form_data.items() if k.startswith('client_')},
        'conjoint': {k.replace('conjoint_', ''): v for k, v in form_data.items() if k.startswith('conjoint_')},
        'enfants': form_data.get('enfants', [])
    }

    pdf_file = populate_single_pdf(formatted_data, client_id)

    if pdf_file and os.path.exists(pdf_file):
        return send_file(pdf_file, as_attachment=True)
    else:
        return jsonify({'success': False, 'error': 'PDF generation failed'}), 500


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get financial product recommendations"""
    data = request.json
    recommendations = smart_inference._recommend_financial_products(data)

    return jsonify({
        'success': True,
        'recommendations': recommendations
    })


def create_html_template():
    """Create the HTML template for the web form"""
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    os.makedirs(template_dir, exist_ok=True)

    html_content = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proxima - Formulaire Client Intelligent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }

        .form-container {
            padding: 40px;
        }

        .form-section {
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            border-left: 5px solid #667eea;
        }

        .form-section h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8em;
        }

        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .form-group {
            position: relative;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #34495e;
            font-weight: 600;
            font-size: 0.95em;
        }

        .form-group input,
        .form-group select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: all 0.3s ease;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .auto-populated {
            background-color: #e3f2fd !important;
            border-color: #2196f3 !important;
        }

        .auto-populated::after {
            content: '✨ Auto';
            position: absolute;
            right: 15px;
            top: 38px;
            font-size: 0.75em;
            color: #2196f3;
            font-weight: bold;
        }

        .inference-panel {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }

        .inference-panel h3 {
            color: #d84315;
            margin-bottom: 15px;
        }

        .recommendation-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #ff5722;
        }

        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-right: 15px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .btn-secondary {
            background: #ecf0f1;
            color: #2c3e50;
        }

        .btn-secondary:hover {
            background: #bdc3c7;
        }

        .actions {
            margin-top: 40px;
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
        }

        .status-message {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 500;
        }

        .status-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .field-count {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 10px;
            margin-bottom: 20px;
        }

        .field-count h3 {
            font-size: 2em;
            color: #2c3e50;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Formulaire Client Intelligent</h1>
            <p>Système de remplissage automatique avec IA</p>
        </div>

        <div class="form-container">
            <div class="field-count">
                <h3><span id="filled-count">0</span> / <span id="total-count">50</span> champs remplis</h3>
                <p>Auto-remplis: <strong id="auto-count">0</strong></p>
            </div>

            <form id="client-form">
                <!-- Section: Informations Générales -->
                <div class="form-section">
                    <h2>👤 Informations Générales</h2>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="client_nom_complet">Nom complet *</label>
                            <input type="text" id="client_nom_complet" name="client_nom_complet" required>
                        </div>
                        <div class="form-group">
                            <label for="client_date_naissance">Date de naissance *</label>
                            <input type="date" id="client_date_naissance" name="client_date_naissance" required>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="age">Âge</label>
                            <input type="number" id="age" name="age" readonly class="auto-field">
                        </div>
                        <div class="form-group">
                            <label for="client_sexe">Sexe</label>
                            <select id="client_sexe" name="client_sexe">
                                <option value="">Sélectionner...</option>
                                <option value="H">Homme</option>
                                <option value="F">Femme</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Section: Adresse -->
                <div class="form-section">
                    <h2>📍 Adresse</h2>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="client_adresse_residence">Adresse de résidence *</label>
                            <input type="text" id="client_adresse_residence" name="client_adresse_residence"
                                   placeholder="123 Rue Principale, Ville, QC">
                        </div>
                        <div class="form-group">
                            <label for="client_province_imposition">Province d'imposition</label>
                            <input type="text" id="client_province_imposition" name="client_province_imposition"
                                   readonly class="auto-field">
                        </div>
                    </div>
                </div>

                <!-- Section: Emploi et Revenus -->
                <div class="form-section">
                    <h2>💼 Emploi et Revenus</h2>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="client_employeur">Employeur</label>
                            <input type="text" id="client_employeur" name="client_employeur">
                        </div>
                        <div class="form-group">
                            <label for="client_emploi">Emploi</label>
                            <input type="text" id="client_emploi" name="client_emploi">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="client_salaire_annuel_brut">Salaire annuel brut *</label>
                            <input type="number" id="client_salaire_annuel_brut" name="client_salaire_annuel_brut"
                                   min="0" step="1000">
                        </div>
                        <div class="form-group">
                            <label for="tax_bracket">Taux d'imposition</label>
                            <input type="text" id="tax_bracket" name="tax_bracket" readonly class="auto-field">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="reer_contribution_room">Droits de cotisation REER</label>
                            <input type="text" id="reer_contribution_room" name="reer_contribution_room"
                                   readonly class="auto-field">
                        </div>
                    </div>
                </div>

                <!-- Section: État Civil -->
                <div class="form-section">
                    <h2>💑 État Civil</h2>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="client_etat_civil">État civil *</label>
                            <select id="client_etat_civil" name="client_etat_civil">
                                <option value="">Sélectionner...</option>
                                <option value="Célibataire">Célibataire</option>
                                <option value="Marié(e)">Marié(e)</option>
                                <option value="Conjoint(e) de fait">Conjoint(e) de fait</option>
                                <option value="Divorcé(e)">Divorcé(e)</option>
                                <option value="Séparé(e)">Séparé(e)</option>
                                <option value="Veuf/veuve">Veuf/veuve</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="client_regime_matrimonial">Régime matrimonial</label>
                            <input type="text" id="client_regime_matrimonial" name="client_regime_matrimonial"
                                   readonly class="auto-field">
                        </div>
                    </div>
                </div>

                <!-- Section: Finances -->
                <div class="form-section">
                    <h2>💰 Situation Financière</h2>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="client_total_actif">Total Actif ($)</label>
                            <input type="number" id="client_total_actif" name="client_total_actif"
                                   min="0" step="1000">
                        </div>
                        <div class="form-group">
                            <label for="client_total_passif">Total Passif ($)</label>
                            <input type="number" id="client_total_passif" name="client_total_passif"
                                   min="0" step="1000">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="client_avoir_net">Avoir Net ($)</label>
                            <input type="text" id="client_avoir_net" name="client_avoir_net"
                                   readonly class="auto-field">
                        </div>
                        <div class="form-group">
                            <label for="debt_to_income_ratio">Ratio d'endettement (%)</label>
                            <input type="text" id="debt_to_income_ratio" name="debt_to_income_ratio"
                                   readonly class="auto-field">
                        </div>
                    </div>
                </div>

                <!-- Recommendations Panel -->
                <div class="inference-panel">
                    <h3>💡 Recommandations Intelligentes</h3>
                    <div id="recommendations"></div>
                </div>

                <!-- Actions -->
                <div class="actions">
                    <button type="button" class="btn btn-primary" onclick="runSmartInference()">
                        🧠 Remplissage Intelligent (IA)
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="saveForm()">
                        💾 Sauvegarder
                    </button>
                    <button type="button" class="btn btn-primary" onclick="generatePDF()">
                        📄 Générer PDF
                    </button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let formData = {};
        let autoPopulatedCount = 0;

        // Listen for changes on all form fields
        document.querySelectorAll('input, select').forEach(field => {
            field.addEventListener('change', async (e) => {
                const fieldName = e.target.name;
                const fieldValue = e.target.value;

                if (!e.target.classList.contains('auto-field')) {
                    await autoComplete(fieldName, fieldValue);
                }
                updateFieldCount();
            });
        });

        async function autoComplete(fieldName, fieldValue) {
            formData[fieldName] = fieldValue;

            try {
                const response = await fetch('/api/autocomplete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ field_name: fieldName, field_value: fieldValue })
                });

                const result = await response.json();

                if (result.success && result.updated_fields) {
                    // Populate auto-calculated fields
                    for (const [key, value] of Object.entries(result.updated_fields)) {
                        const field = document.getElementById(key);
                        if (field) {
                            field.value = value;
                            field.classList.add('auto-populated');
                            autoPopulatedCount++;
                        }
                    }
                    updateFieldCount();
                }
            } catch (error) {
                console.error('Auto-complete error:', error);
            }
        }

        async function runSmartInference() {
            const data = collectFormData();

            try {
                const response = await fetch('/api/smart_inference', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ data })
                });

                const result = await response.json();

                if (result.success) {
                    // Populate all inferred fields
                    for (const [key, value] of Object.entries(result.enhanced_data)) {
                        const field = document.getElementById(key);
                        if (field && !field.value) {
                            field.value = value;
                            field.classList.add('auto-populated');
                        }
                    }

                    showMessage('Remplissage intelligent complété!', 'success');
                    updateFieldCount();
                }
            } catch (error) {
                console.error('Smart inference error:', error);
            }
        }

        function collectFormData() {
            const data = {};
            document.querySelectorAll('input, select').forEach(field => {
                if (field.value) {
                    data[field.name] = field.value;
                }
            });
            return data;
        }

        async function saveForm() {
            const data = collectFormData();

            try {
                const response = await fetch('/api/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    showMessage('Formulaire sauvegardé avec succès!', 'success');
                }
            } catch (error) {
                console.error('Save error:', error);
            }
        }

        async function generatePDF() {
            const data = collectFormData();

            try {
                const response = await fetch('/api/generate_pdf', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'formulaire_client.pdf';
                    a.click();
                    showMessage('PDF généré avec succès!', 'success');
                }
            } catch (error) {
                console.error('PDF generation error:', error);
            }
        }

        function updateFieldCount() {
            const allFields = document.querySelectorAll('input, select');
            const filledFields = Array.from(allFields).filter(f => f.value).length;
            const autoFields = document.querySelectorAll('.auto-populated').length;

            document.getElementById('filled-count').textContent = filledFields;
            document.getElementById('total-count').textContent = allFields.length;
            document.getElementById('auto-count').textContent = autoFields;
        }

        function showMessage(message, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `status-message status-${type}`;
            messageDiv.textContent = message;

            const container = document.querySelector('.form-container');
            container.insertBefore(messageDiv, container.firstChild);

            setTimeout(() => messageDiv.remove(), 3000);
        }

        // Initialize
        updateFieldCount();
    </script>
</body>
</html>'''

    template_file = os.path.join(template_dir, 'index.html')
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✓ HTML template created at {template_file}")


if __name__ == "__main__":
    print("Creating web interface templates...")
    create_html_template()

    print("\n" + "=" * 70)
    print("PROXIMA WEB FORM - Interactive PDF Population")
    print("=" * 70)
    print("\nStarting Flask server...")
    print("Access the form at: http://localhost:5000")
    print("\nFeatures:")
    print("  ✓ Real-time auto-population")
    print("  ✓ Smart field inference with AI")
    print("  ✓ Field dependency tracking")
    print("  ✓ PDF generation")
    print("=" * 70)

    app.run(debug=True, host='0.0.0.0', port=5000)
