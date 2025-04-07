import os
import time
import logging
from flask import Flask, request, jsonify
from vicidial_client import ViciDialClient
from ai_voice_client import AIVoiceClient
from database import CallDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app for webhook handling
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize clients
vicidial = ViciDialClient(
    os.environ.get("VICIDIAL_URL"),
    os.environ.get("VICIDIAL_USER"),
    os.environ.get("VICIDIAL_PASS")
)

ai_voice = AIVoiceClient(
    os.environ.get("AI_VOICE_API_KEY"),
    os.environ.get("AI_VOICE_SERVICE", "retell")
)

# Initialize database
db = CallDatabase()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

@app.route('/webhooks/call_status', methods=['POST'])
def call_status_webhook():
    """Handle call status updates from AI voice service"""
    try:
        data = request.json
        call_id = data.get('call_id')
        status = data.get('status')
        
        logger.info(f"Received status update for call {call_id}: {status}")
        
        # Retrieve call details from database
        call_info = db.get_call(call_id)
        if not call_info:
            logger.error(f"Call {call_id} not found in database")
            return jsonify({'error': 'Call not found'}), 404

        # Update call record
        update_data = {
            'status': status,
        }
        
        if status in ['completed', 'ended', 'failed']:
            update_data['end_time'] = time.time()
            
            # Get transcript and analytics if available
            try:
                transcript = ai_voice.get_call_transcript(call_id)
                analytics = ai_voice.get_call_analytics(call_id)
                update_data.update({
                    'transcript': transcript.get('text'),
                    'analytics': analytics
                })
            except Exception as e:
                logger.error(f"Error fetching call data: {str(e)}")

            # Update lead status in ViciDial
            vicidial_status = 'AICOMPL' if status == 'completed' else 'AINOANS'
            try:
                vicidial.update_lead_status(call_info['lead_id'], vicidial_status)
            except Exception as e:
                logger.error(f"Error updating ViciDial status: {str(e)}")

        # Update database
        db.update_call(call_id, update_data)
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

def process_campaign(campaign_id, script_id, max_concurrent=5):
    """Process a campaign by initiating AI calls for eligible leads"""
    try:
        # Get active call count
        active_calls = db.get_active_calls_count()
        
        # Calculate how many new calls we can make
        available_slots = max_concurrent - active_calls
        
        if available_slots <= 0:
            logger.info("Maximum concurrent calls reached")
            return
        
        # Get leads from ViciDial
        leads = vicidial.get_leads(campaign_id, limit=available_slots)
        
        webhook_url = os.environ.get("WEBHOOK_BASE_URL") + "/webhooks/call_status"
        
        # Process each lead
        for lead in leads:
            try:
                # Create call in AI voice platform
                ai_call = ai_voice.create_call(
                    lead['phone_number'],
                    script_id,
                    webhook_url
                )
                
                # Store call information in database
                db.create_call({
                    'call_id': ai_call['id'],
                    'lead_id': lead['lead_id'],
                    'phone_number': lead['phone_number'],
                    'campaign_id': campaign_id,
                    'status': 'initiated',
                    'start_time': time.time()
                })
                
                # Update lead status in ViciDial
                vicidial.update_lead_status(lead['lead_id'], 'AICALL')
                
                logger.info(f"Initiated call for lead {lead['lead_id']}")
                
            except Exception as e:
                logger.error(f"Error processing lead {lead['lead_id']}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error processing campaign {campaign_id}: {str(e)}")

if __name__ == '__main__':
    # Start the webhook server
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)