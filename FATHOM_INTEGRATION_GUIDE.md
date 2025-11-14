# Fathom API Integration Guide

## 🎯 Overview

This guide shows you how to integrate **Fathom.ai** (meeting recording & transcription) with the Proxima PDF population pipeline. Automatically extract client information from recorded meetings and populate forms.

---

## 🔑 Getting Started

### 1. Get Your Fathom API Key

1. Log in to Fathom: https://app.fathom.video
2. Go to **Settings** → **API Access**
3. Click **"Generate API Key"**
4. Copy your API key

### 2. Configure Environment

Add your API key to `.env`:

```bash
FATHOM_API_KEY=your_api_key_here
```

### 3. Install (Already Included)

The `requests` library is already in `requirements.txt`, so you're ready to go!

---

## 💡 What You Can Do

### 1. **List All Meetings**
```python
from scripts.fathom_integration import FathomAPI

fathom = FathomAPI()
meetings = fathom.list_meetings(limit=10)

for meeting in meetings['data']:
    print(f"{meeting['title']} - {meeting['start_time']}")
```

### 2. **Get Meeting Summary & Action Items**
```python
# Get AI-generated summary
summary = fathom.get_client_meeting_summary(meeting_id)

print("Summary:", summary['summary'])
print("\nAction Items:")
for item in summary['action_items']:
    print(f"  ☐ {item}")
```

### 3. **Get Full Transcript**
```python
# Get transcript with speaker labels
transcript = fathom.get_transcript(recording_id)

for segment in transcript['segments']:
    print(f"{segment['speaker']}: {segment['text']}")
```

### 4. **Search Meetings**
```python
# Find all client meetings from January
meetings = fathom.search_meetings(
    query="client",
    start_date="2025-01-01",
    end_date="2025-01-31"
)
```

### 5. **Auto-Populate Forms from Meetings** ⭐
```python
from scripts.fathom_integration import FathomToProximaPipeline

pipeline = FathomToProximaPipeline(fathom_api_key)

# Get form data from latest meeting with client
form_data = pipeline.auto_populate_from_latest_meeting("client@example.com")

# form_data now contains:
# - Client name (extracted from transcript)
# - Meeting summary
# - Action items
# - Products discussed
# - Next steps
```

---

## 🔗 Full Integration: Meeting → Form → PDF

### Complete Workflow

```python
from scripts.fathom_integration import FathomToProximaPipeline
from scripts.smart_field_inference import SmartFieldInference
from scripts.pdf_populator import populate_single_pdf

# 1. Extract data from Fathom meeting
pipeline = FathomToProximaPipeline(fathom_api_key)
meeting_data = pipeline.auto_populate_from_latest_meeting("client@example.com")

# 2. Enhance with AI-powered inference
inferencer = SmartFieldInference()
complete_data = inferencer.infer_from_minimal_input(meeting_data)

# 3. Generate PDF
pdf_file = populate_single_pdf(complete_data, client_id=1)

print(f"✅ PDF generated: {pdf_file}")
```

**Result:** Your client meeting is automatically converted into a filled PDF form!

---

## 📋 Available API Methods

### FathomAPI Class

| Method | Description | Example |
|--------|-------------|---------|
| `list_meetings()` | Get all accessible meetings | `meetings = fathom.list_meetings(limit=50)` |
| `get_meeting(id)` | Get meeting details | `meeting = fathom.get_meeting('meeting_123')` |
| `get_transcript(id)` | Get meeting transcript | `transcript = fathom.get_transcript('rec_123')` |
| `get_summary(id)` | Get AI summary | `summary = fathom.get_summary('rec_123')` |
| `search_meetings()` | Search meetings | `results = fathom.search_meetings(query="client")` |
| `get_client_meeting_summary(id)` | Formatted client meeting summary | `summary = fathom.get_client_meeting_summary(id)` |
| `extract_client_data_from_meeting(id)` | Extract structured client data | `data = fathom.extract_client_data_from_meeting(id)` |

### FathomToProximaPipeline Class

| Method | Description |
|--------|-------------|
| `get_recent_client_meetings(days)` | Get client meetings from past N days |
| `process_meeting_to_client_form(id)` | Convert meeting to form data |
| `auto_populate_from_latest_meeting(email)` | Auto-fill form from latest meeting with client |

---

## 🎬 Use Cases

### Use Case 1: Post-Meeting Form Population

**Scenario:** After a client meeting, automatically populate the client intake form.

```python
# After your Fathom-recorded meeting
fathom = FathomAPI()

# Get the meeting that just ended
meetings = fathom.list_meetings(limit=1)
latest_meeting = meetings['data'][0]

# Extract and populate form
pipeline = FathomToProximaPipeline(api_key)
form_data = pipeline.process_meeting_to_client_form(latest_meeting['id'])

# Generate PDF
from scripts.pdf_populator import populate_single_pdf
pdf = populate_single_pdf(form_data, client_id)
```

### Use Case 2: Weekly Client Meeting Summary

**Scenario:** Generate a weekly report of all client meetings.

```python
pipeline = FathomToProximaPipeline(api_key)

# Get all client meetings from past 7 days
meetings = pipeline.get_recent_client_meetings(days=7)

for meeting in meetings:
    summary = fathom.get_client_meeting_summary(meeting['id'])

    print(f"\n📅 {summary['title']}")
    print(f"   Date: {summary['date']}")
    print(f"   Summary: {summary['summary']}")
    print(f"   Action Items: {len(summary['action_items'])}")
```

### Use Case 3: Action Item Tracking

**Scenario:** Extract all action items across client meetings for follow-up.

```python
fathom = FathomAPI()

# Get all meetings
meetings = fathom.search_meetings(query="client")

all_action_items = []
for meeting in meetings:
    summary = fathom.get_summary(meeting['recording_id'])
    for item in summary.get('action_items', []):
        all_action_items.append({
            'meeting': meeting['title'],
            'date': meeting['start_time'],
            'action': item
        })

# Now you have all follow-up tasks in one place!
```

### Use Case 4: Client Discovery Sessions

**Scenario:** Extract client goals and concerns from discovery meetings.

```python
# Find discovery/consultation meetings
discovery_meetings = fathom.search_meetings(query="discovery")

for meeting in discovery_meetings:
    # Get full transcript
    transcript = fathom.get_transcript(meeting['recording_id'])

    # Extract client information
    # In production, use an LLM to parse transcript for:
    # - Financial goals
    # - Current situation
    # - Risk tolerance
    # - Timeline
    # - Concerns

    # Use this to pre-populate client forms!
```

---

## 🔧 Advanced Features

### Custom Data Extraction

You can customize the data extraction logic:

```python
class CustomFathomPipeline(FathomToProximaPipeline):
    def extract_financial_goals(self, transcript):
        """Extract financial goals from transcript using LLM"""
        # Use your LLM (OpenRouter, etc.) to parse transcript
        # and extract specific information
        pass

    def identify_product_interests(self, summary):
        """Identify which products the client is interested in"""
        products = []

        # Check summary for product mentions
        if 'REER' in summary or 'retirement' in summary.lower():
            products.append('REER')
        if 'CELI' in summary or 'TFSA' in summary:
            products.append('CELI')
        if 'insurance' in summary.lower():
            products.append('Life Insurance')

        return products
```

### Webhook Integration (Future)

Fathom supports webhooks for real-time notifications when:
- A meeting is recorded
- A transcript is ready
- A summary is generated

```python
# Webhook endpoint (Flask example)
from flask import Flask, request

app = Flask(__name__)

@app.route('/fathom/webhook', methods=['POST'])
def fathom_webhook():
    data = request.json

    if data['event'] == 'recording.completed':
        # Automatically process new recording
        meeting_id = data['meeting_id']
        pipeline = FathomToProximaPipeline(api_key)
        form_data = pipeline.process_meeting_to_client_form(meeting_id)

        # Generate PDF automatically
        populate_single_pdf(form_data, client_id)

    return {'status': 'success'}
```

---

## 📊 API Response Examples

### Meeting Object
```json
{
  "id": "meeting_abc123",
  "title": "Client Discovery - Sophie Gagnon",
  "start_time": "2025-01-15T14:00:00Z",
  "duration_minutes": 45,
  "recording_id": "rec_xyz789",
  "participants": [
    {
      "email": "advisor@proxima.com",
      "name": "Marc-Olivier Gagnon"
    },
    {
      "email": "sophie.gagnon@example.com",
      "name": "Sophie Gagnon"
    }
  ]
}
```

### Summary Object
```json
{
  "summary": "Discussion about retirement planning and REER contributions. Client interested in maximizing tax benefits...",
  "action_items": [
    "Prepare REER contribution analysis",
    "Send insurance quote for $500K coverage",
    "Schedule follow-up for next week"
  ],
  "key_topics": [
    "Retirement Planning",
    "REER Optimization",
    "Life Insurance"
  ],
  "decisions": [
    "Client wants to maximize REER this year",
    "Will review insurance options next meeting"
  ]
}
```

### Transcript Segment
```json
{
  "speaker": "Marc-Olivier Gagnon",
  "text": "So, Sophie, what are your main financial goals for the next 5 years?",
  "start_time": 125.5,
  "end_time": 130.2
}
```

---

## 🔐 Security & Best Practices

### API Key Security
✅ **DO:**
- Store API key in `.env` file
- Add `.env` to `.gitignore`
- Use environment variables in production
- Rotate keys periodically

❌ **DON'T:**
- Commit API keys to Git
- Share keys in code
- Use same key across multiple environments

### Rate Limits
- Fathom API has rate limits (check current limits in docs)
- Implement exponential backoff for retries
- Cache meeting data when possible

### Data Privacy
- Meeting transcripts contain sensitive client information
- Ensure GDPR/Quebec Bill 64 compliance
- Implement proper access controls
- Delete old transcripts per retention policy

---

## 🚀 Quick Start Commands

```bash
# 1. Set up API key
echo "FATHOM_API_KEY=your_key_here" >> .env

# 2. Test connection
python -c "from scripts.fathom_integration import FathomAPI; f = FathomAPI(); print('✓ Connected!', f.list_meetings(limit=1))"

# 3. List recent meetings
python scripts/fathom_integration.py
```

---

## 📚 Additional Resources

- **Fathom API Docs:** https://developers.fathom.ai
- **API Reference:** https://developers.fathom.ai/api-reference
- **Get API Key:** https://app.fathom.video/settings/api
- **Fathom Support:** help@fathom.video

---

## 🎯 Next Steps

1. **Get your API key** from Fathom settings
2. **Configure `.env`** with your key
3. **Run test script** to verify connection
4. **Try the examples** to see it in action
5. **Integrate with your workflow** using the pipeline

---

## 💡 Pro Tips

### Tip 1: Name Your Meetings Consistently
Use a naming convention like:
- `Client Discovery - [Client Name]`
- `Follow-up - [Client Name]`
- `Consultation - [Topic] - [Client Name]`

This makes searching and filtering much easier!

### Tip 2: Use Tags in Meeting Notes
Add tags in your Fathom notes during meetings:
- `#REER` - Client interested in REER
- `#insurance` - Insurance discussion
- `#action` - Action item mentioned
- `#followup` - Requires follow-up

Then search by these tags later!

### Tip 3: Combine with Smart Inference
```python
# Get minimal data from Fathom
fathom_data = pipeline.auto_populate_from_latest_meeting(client_email)

# Enhance with AI
from scripts.smart_field_inference import SmartFieldInference
inferencer = SmartFieldInference()
complete_data = inferencer.infer_from_minimal_input(fathom_data)

# Now you have a fully populated form!
```

### Tip 4: Automate the Workflow
Set up a daily cron job:
```bash
# Daily at 6 PM, process all meetings from today
0 18 * * * cd /home/user/Proxima && python scripts/process_daily_meetings.py
```

---

## 🆘 Troubleshooting

### Error: "Invalid API Key"
- Check that `FATHOM_API_KEY` is set in `.env`
- Verify key is active in Fathom settings
- Make sure there are no extra spaces in the key

### Error: "Meeting not found"
- Verify you have access to the meeting
- Check if meeting was shared to your Team
- Try using a different meeting ID

### Error: "Rate limit exceeded"
- Implement request throttling
- Add delays between API calls
- Contact Fathom for higher limits

---

**Ready to transform your client meetings into auto-filled forms?** 🚀

Get your API key and start integrating!
