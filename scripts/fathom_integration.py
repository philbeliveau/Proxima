#!/usr/bin/env python3
"""
Fathom API Integration for Proxima
Automatically extract meeting summaries, transcripts, and action items
from client meetings recorded with Fathom
"""
import os
import requests
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class FathomAPI:
    """
    Fathom.ai API client for accessing meeting recordings, transcripts, and summaries

    Documentation: https://developers.fathom.ai
    API Reference: https://developers.fathom.ai/api-reference
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Fathom API client

        Args:
            api_key: Your Fathom API key (or set FATHOM_API_KEY environment variable)
                    Get your key from: https://app.fathom.video/settings/api
        """
        self.api_key = api_key or os.getenv('FATHOM_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Fathom API key required. Set FATHOM_API_KEY environment variable "
                "or pass api_key parameter. Get your key from: "
                "https://app.fathom.video/settings/api"
            )

        self.base_url = "https://api.fathom.ai/external/v1"
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request to Fathom API"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def list_meetings(self, limit: int = 50, offset: int = 0) -> Dict:
        """
        List all meetings accessible to your API key

        Args:
            limit: Maximum number of meetings to return (default: 50)
            offset: Pagination offset (default: 0)

        Returns:
            Dictionary containing meetings list and pagination info

        Example:
            >>> fathom = FathomAPI()
            >>> meetings = fathom.list_meetings(limit=10)
            >>> for meeting in meetings['data']:
            ...     print(meeting['title'], meeting['start_time'])
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        return self._make_request('GET', 'meetings', params=params)

    def get_meeting(self, meeting_id: str, include_transcript: bool = False,
                    include_summary: bool = False) -> Dict:
        """
        Get details for a specific meeting

        Args:
            meeting_id: The Fathom meeting ID
            include_transcript: Include full transcript in response (default: False)
            include_summary: Include AI summary in response (default: False)

        Returns:
            Dictionary containing meeting details

        Note:
            For OAuth apps, you must fetch transcript and summary separately
            using get_transcript() and get_summary() methods

        Example:
            >>> fathom = FathomAPI()
            >>> meeting = fathom.get_meeting('meeting_123', include_summary=True)
            >>> print(meeting['title'])
            >>> print(meeting['summary'])
        """
        params = {}
        if include_transcript:
            params['include_transcript'] = 'true'
        if include_summary:
            params['include_summary'] = 'true'

        return self._make_request('GET', f'meetings/{meeting_id}', params=params)

    def get_transcript(self, recording_id: str) -> Dict:
        """
        Get the transcript for a specific recording

        Args:
            recording_id: The Fathom recording ID

        Returns:
            Dictionary containing transcript with speaker labels and timestamps

        Example:
            >>> fathom = FathomAPI()
            >>> transcript = fathom.get_transcript('rec_123')
            >>> for segment in transcript['segments']:
            ...     print(f"{segment['speaker']}: {segment['text']}")
        """
        return self._make_request('GET', f'recordings/{recording_id}/transcript')

    def get_summary(self, recording_id: str) -> Dict:
        """
        Get the AI-generated summary for a specific recording

        Args:
            recording_id: The Fathom recording ID

        Returns:
            Dictionary containing AI summary with key points and action items

        Example:
            >>> fathom = FathomAPI()
            >>> summary = fathom.get_summary('rec_123')
            >>> print("Summary:", summary['summary'])
            >>> print("Action Items:", summary['action_items'])
        """
        return self._make_request('GET', f'recordings/{recording_id}/summary')

    def search_meetings(self, query: str = None, start_date: str = None,
                       end_date: str = None, participant: str = None) -> List[Dict]:
        """
        Search meetings by various criteria

        Args:
            query: Search text in meeting titles or content
            start_date: Filter meetings after this date (ISO format: YYYY-MM-DD)
            end_date: Filter meetings before this date (ISO format: YYYY-MM-DD)
            participant: Filter meetings with specific participant email

        Returns:
            List of matching meetings

        Example:
            >>> fathom = FathomAPI()
            >>> # Find all client meetings from January 2025
            >>> meetings = fathom.search_meetings(
            ...     query="client",
            ...     start_date="2025-01-01",
            ...     end_date="2025-01-31"
            ... )
        """
        params = {}
        if query:
            params['query'] = query
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if participant:
            params['participant'] = participant

        result = self._make_request('GET', 'meetings', params=params)
        return result.get('data', [])

    def get_client_meeting_summary(self, meeting_id: str) -> Dict:
        """
        Get a formatted summary specifically for client meetings

        This extracts key information relevant to financial advising:
        - Client name and concerns
        - Financial goals discussed
        - Products mentioned
        - Action items for follow-up
        - Next steps

        Args:
            meeting_id: The Fathom meeting ID

        Returns:
            Formatted dictionary with client meeting information
        """
        meeting = self.get_meeting(meeting_id, include_summary=True)

        # Try to get recording ID from meeting
        recording_id = meeting.get('recording_id') or meeting.get('id')

        summary_data = self.get_summary(recording_id)

        return {
            'meeting_id': meeting_id,
            'title': meeting.get('title', ''),
            'date': meeting.get('start_time', ''),
            'duration_minutes': meeting.get('duration_minutes', 0),
            'participants': meeting.get('participants', []),
            'summary': summary_data.get('summary', ''),
            'action_items': summary_data.get('action_items', []),
            'key_topics': summary_data.get('key_topics', []),
            'decisions': summary_data.get('decisions', []),
        }

    def extract_client_data_from_meeting(self, meeting_id: str) -> Dict:
        """
        Extract structured client data from meeting transcript

        This uses the transcript to identify and extract:
        - Client personal information mentioned
        - Financial goals and objectives
        - Current financial situation discussed
        - Products of interest
        - Follow-up requirements

        Useful for populating client forms automatically!

        Args:
            meeting_id: The Fathom meeting ID

        Returns:
            Structured client data dictionary
        """
        meeting = self.get_meeting(meeting_id)
        recording_id = meeting.get('recording_id') or meeting.get('id')

        transcript = self.get_transcript(recording_id)
        summary = self.get_summary(recording_id)

        # Extract data from transcript and summary
        # In a real implementation, you'd use NLP or LLM to parse this
        client_data = {
            'meeting_date': meeting.get('start_time'),
            'meeting_title': meeting.get('title'),
            'transcript': transcript,
            'summary': summary.get('summary', ''),
            'action_items': summary.get('action_items', []),
            'participants': meeting.get('participants', []),
            # These would be extracted from transcript using NLP/LLM:
            'client_name': None,  # Extract from transcript
            'financial_goals': [],  # Extract from transcript
            'products_discussed': [],  # Extract from transcript
            'next_meeting': None,  # Extract from action items
        }

        return client_data


class FathomToProximaPipeline:
    """
    Pipeline to automatically populate Proxima client forms from Fathom meetings
    """

    def __init__(self, fathom_api_key: str):
        self.fathom = FathomAPI(fathom_api_key)

    def get_recent_client_meetings(self, days: int = 7) -> List[Dict]:
        """
        Get all client meetings from the past N days

        Args:
            days: Number of days to look back (default: 7)

        Returns:
            List of recent client meetings
        """
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        meetings = self.fathom.search_meetings(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        # Filter for client meetings (e.g., contains "client" or "consultation")
        client_meetings = [
            m for m in meetings
            if any(keyword in m.get('title', '').lower()
                   for keyword in ['client', 'consultation', 'meeting', 'discovery'])
        ]

        return client_meetings

    def process_meeting_to_client_form(self, meeting_id: str) -> Dict:
        """
        Process a Fathom meeting and extract data for client form

        This is where the magic happens:
        1. Get meeting transcript and summary
        2. Extract relevant client information
        3. Map to Proxima form fields
        4. Return pre-populated form data

        Args:
            meeting_id: Fathom meeting ID

        Returns:
            Dictionary with client form data ready for PDF population
        """
        # Get meeting data
        client_data = self.fathom.extract_client_data_from_meeting(meeting_id)
        summary = self.fathom.get_client_meeting_summary(meeting_id)

        # Map to Proxima form fields
        # In production, you'd use an LLM to intelligently extract this
        form_data = {
            'date': summary['date'],
            'representant': 'Marc-Olivier Gagnon, Pl.fin',

            # Would be extracted from transcript:
            'client_nom_complet': client_data.get('client_name', ''),

            # Meeting notes and action items
            'meeting_summary': summary['summary'],
            'action_items': '\n'.join(summary['action_items']),
            'key_topics': summary.get('key_topics', []),

            # Products discussed
            'products_of_interest': client_data.get('products_discussed', []),

            # Next steps
            'follow_up_required': len(summary['action_items']) > 0,
            'next_meeting_date': client_data.get('next_meeting'),
        }

        return form_data

    def auto_populate_from_latest_meeting(self, client_email: str) -> Dict:
        """
        Find the latest meeting with a specific client and auto-populate form

        Args:
            client_email: Email address of the client

        Returns:
            Pre-populated form data from most recent meeting
        """
        # Find meetings with this client
        meetings = self.fathom.search_meetings(participant=client_email)

        if not meetings:
            raise ValueError(f"No meetings found with client: {client_email}")

        # Get most recent meeting
        latest_meeting = max(meetings, key=lambda m: m.get('start_time', ''))

        # Process and return form data
        return self.process_meeting_to_client_form(latest_meeting['id'])


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_basic_usage():
    """Basic usage examples"""
    print("=" * 70)
    print("FATHOM API - BASIC USAGE EXAMPLES")
    print("=" * 70)

    # Initialize API client
    fathom = FathomAPI()  # Uses FATHOM_API_KEY from environment

    print("\n1️⃣  List Recent Meetings")
    print("-" * 70)
    meetings = fathom.list_meetings(limit=5)
    for meeting in meetings.get('data', []):
        print(f"  • {meeting['title']}")
        print(f"    Date: {meeting['start_time']}")
        print(f"    Duration: {meeting.get('duration_minutes', 0)} min")
        print()

    print("\n2️⃣  Get Meeting Summary")
    print("-" * 70)
    if meetings.get('data'):
        meeting_id = meetings['data'][0]['id']
        summary = fathom.get_client_meeting_summary(meeting_id)

        print(f"Meeting: {summary['title']}")
        print(f"Date: {summary['date']}")
        print(f"\nSummary:\n{summary['summary']}")
        print(f"\nAction Items:")
        for item in summary['action_items']:
            print(f"  ☐ {item}")

    print("\n3️⃣  Search Client Meetings")
    print("-" * 70)
    client_meetings = fathom.search_meetings(query="client")
    print(f"Found {len(client_meetings)} client meetings")


def example_auto_populate_form():
    """Example: Auto-populate client form from Fathom meeting"""
    print("=" * 70)
    print("AUTO-POPULATE CLIENT FORM FROM FATHOM MEETING")
    print("=" * 70)

    pipeline = FathomToProximaPipeline(fathom_api_key=os.getenv('FATHOM_API_KEY'))

    # Get recent client meetings
    print("\n📅 Getting recent client meetings...")
    recent_meetings = pipeline.get_recent_client_meetings(days=7)

    print(f"Found {len(recent_meetings)} client meetings in the past 7 days:")
    for meeting in recent_meetings:
        print(f"  • {meeting['title']} - {meeting['start_time']}")

    # Process a meeting to populate form
    if recent_meetings:
        print(f"\n🔄 Processing meeting: {recent_meetings[0]['title']}")
        form_data = pipeline.process_meeting_to_client_form(recent_meetings[0]['id'])

        print("\n✅ Extracted Form Data:")
        for key, value in form_data.items():
            print(f"  {key}: {value}")


def example_integration_with_pdf_pipeline():
    """Example: Integrate Fathom with existing Proxima PDF pipeline"""
    print("=" * 70)
    print("FULL INTEGRATION: FATHOM → PROXIMA → PDF")
    print("=" * 70)

    from scripts.smart_field_inference import SmartFieldInference
    from scripts.pdf_populator import populate_single_pdf

    # 1. Get data from Fathom meeting
    print("\n1️⃣  Extracting data from Fathom meeting...")
    pipeline = FathomToProximaPipeline(fathom_api_key=os.getenv('FATHOM_API_KEY'))

    # Get client email (would come from your CRM or user input)
    client_email = "client@example.com"

    try:
        fathom_data = pipeline.auto_populate_from_latest_meeting(client_email)
        print(f"✓ Extracted meeting data for: {fathom_data.get('client_nom_complet')}")
    except ValueError as e:
        print(f"⚠️  {e}")
        # Use demo data
        fathom_data = {
            'client_nom_complet': 'Sophie Gagnon',
            'meeting_summary': 'Client interested in REER and life insurance',
            'products_of_interest': ['REER', 'Life Insurance']
        }

    # 2. Enhance with smart field inference
    print("\n2️⃣  Enhancing with AI-powered field inference...")
    inferencer = SmartFieldInference()
    enhanced_data = inferencer.infer_from_minimal_input(fathom_data)
    print(f"✓ Auto-populated {len(enhanced_data)} fields")

    # 3. Generate PDF
    print("\n3️⃣  Generating PDF...")
    pdf_file = populate_single_pdf(enhanced_data, client_id=999)
    print(f"✓ PDF generated: {pdf_file}")

    print("\n🎉 Complete! Meeting → Form → PDF in 3 steps!")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║            FATHOM API INTEGRATION FOR PROXIMA                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

This module provides integration with Fathom.ai to automatically
extract meeting summaries, transcripts, and action items from
client meetings.

SETUP:
1. Get your API key from: https://app.fathom.video/settings/api
2. Set environment variable: FATHOM_API_KEY=your_key_here

USAGE:
    # Basic API calls
    fathom = FathomAPI()
    meetings = fathom.list_meetings()
    summary = fathom.get_summary(recording_id)

    # Auto-populate forms
    pipeline = FathomToProximaPipeline(api_key)
    form_data = pipeline.auto_populate_from_latest_meeting(client_email)

EXAMPLES:
    Run the example functions to see it in action!
    """)

    # Uncomment to run examples:
    # example_basic_usage()
    # example_auto_populate_form()
    # example_integration_with_pdf_pipeline()
