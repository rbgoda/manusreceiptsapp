from flask import Blueprint, request, jsonify
from src.services.ai_assistant import AIAssistant

ai_assistant_bp = Blueprint('ai_assistant', __name__)

# CORS headers for all routes
@ai_assistant_bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@ai_assistant_bp.route('/ai-assistant/chat', methods=['POST'])
def chat_with_assistant():
    """Send a message to the AI assistant and get a response"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        
        if not user_message.strip():
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Initialize AI assistant
        assistant = AIAssistant()
        
        # Process the query
        response = assistant.process_query(user_message)
        
        return jsonify({
            'response': response,
            'timestamp': '2024-01-15T10:30:00Z'  # You could use datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_assistant_bp.route('/ai-assistant/insights', methods=['GET'])
def get_expense_insights():
    """Get AI-generated insights about user's expenses"""
    try:
        assistant = AIAssistant()
        insights = assistant.get_expense_insights()
        
        return jsonify({
            'insights': insights,
            'generated_at': '2024-01-15T10:30:00Z'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_assistant_bp.route('/ai-assistant/suggestions', methods=['GET'])
def get_expense_suggestions():
    """Get AI suggestions for expense management"""
    try:
        # Predefined suggestions for now
        suggestions = [
            "What was my total spending last month?",
            "Which category do I spend the most on?",
            "Show me my top 5 merchants by spending",
            "How much did I spend on meals this month?",
            "What's my average expense amount?",
            "Which expenses are pending reimbursement?",
            "How does this month compare to last month?",
            "What are my largest expenses this year?"
        ]
        
        return jsonify({
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

