import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
from src.models.user import db
from src.models.expense import Receipt, Expense, Category
from src.services.receipt_processor import ReceiptProcessor

receipt_bp = Blueprint('receipt', __name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# CORS headers for all routes
@receipt_bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@receipt_bp.route('/receipts/upload', methods=['POST'])
def upload_receipt():
    """Upload and process a receipt"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Create receipt record
        receipt = Receipt(
            filename=original_filename,
            file_path=file_path,
            file_type=file_extension[1:],  # Remove the dot
            is_processed=False
        )
        
        db.session.add(receipt)
        db.session.flush()  # Get the receipt ID
        
        # Process the receipt with AI
        processor = ReceiptProcessor()
        extracted_data = processor.process_receipt_file(file_path, original_filename)
        
        # Update receipt with extracted data
        receipt.extracted_data = extracted_data
        receipt.is_processed = True
        
        db.session.commit()
        
        return jsonify({
            'receipt_id': receipt.id,
            'filename': original_filename,
            'extracted_data': extracted_data,
            'message': 'Receipt uploaded and processed successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Clean up file if it was saved
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': str(e)}), 500

@receipt_bp.route('/receipts/<int:receipt_id>/create-expense', methods=['POST'])
def create_expense_from_receipt(receipt_id):
    """Create an expense from processed receipt data"""
    try:
        receipt = Receipt.query.get_or_404(receipt_id)
        
        if not receipt.is_processed or not receipt.extracted_data:
            return jsonify({'error': 'Receipt not processed or no data available'}), 400
        
        data = receipt.extracted_data
        
        # Get additional data from request if provided
        request_data = request.get_json() or {}
        
        # Find category by name
        category = None
        if data.get('category'):
            category = Category.query.filter_by(name=data['category']).first()
        
        # Create expense
        expense = Expense(
            merchant=request_data.get('merchant', data.get('merchant', 'Unknown Merchant')),
            amount=float(request_data.get('amount', data.get('amount', 0))),
            date=datetime.strptime(
                request_data.get('date', data.get('date', datetime.now().strftime('%Y-%m-%d'))), 
                '%Y-%m-%d'
            ).date(),
            description=request_data.get('description', f"Receipt: {receipt.filename}"),
            category_id=category.id if category else None,
            receipt_id=receipt.id,
            verification_status='pending'
        )
        
        db.session.add(expense)
        db.session.commit()
        
        return jsonify(expense.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@receipt_bp.route('/receipts', methods=['GET'])
def get_receipts():
    """Get all receipts"""
    try:
        receipts = Receipt.query.order_by(Receipt.created_at.desc()).all()
        return jsonify([receipt.to_dict() for receipt in receipts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@receipt_bp.route('/receipts/<int:receipt_id>', methods=['GET'])
def get_receipt(receipt_id):
    """Get a specific receipt"""
    try:
        receipt = Receipt.query.get_or_404(receipt_id)
        return jsonify(receipt.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@receipt_bp.route('/receipts/<int:receipt_id>', methods=['DELETE'])
def delete_receipt(receipt_id):
    """Delete a receipt and its file"""
    try:
        receipt = Receipt.query.get_or_404(receipt_id)
        
        # Delete the file
        if os.path.exists(receipt.file_path):
            os.remove(receipt.file_path)
        
        # Delete from database
        db.session.delete(receipt)
        db.session.commit()
        
        return jsonify({'message': 'Receipt deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@receipt_bp.route('/receipts/<int:receipt_id>/reprocess', methods=['POST'])
def reprocess_receipt(receipt_id):
    """Reprocess a receipt with AI"""
    try:
        receipt = Receipt.query.get_or_404(receipt_id)
        
        if not os.path.exists(receipt.file_path):
            return jsonify({'error': 'Receipt file not found'}), 404
        
        # Reprocess with AI
        processor = ReceiptProcessor()
        extracted_data = processor.process_receipt_file(receipt.file_path, receipt.filename)
        
        # Update receipt
        receipt.extracted_data = extracted_data
        receipt.is_processed = True
        
        db.session.commit()
        
        return jsonify({
            'receipt_id': receipt.id,
            'extracted_data': extracted_data,
            'message': 'Receipt reprocessed successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@receipt_bp.route('/receipts/<int:receipt_id>/update-data', methods=['PUT'])
def update_receipt_data(receipt_id):
    """Update extracted data for a receipt (human validation)"""
    try:
        receipt = Receipt.query.get_or_404(receipt_id)
        data = request.get_json()
        
        # Update extracted data with validated information
        if receipt.extracted_data:
            receipt.extracted_data.update(data.get('extracted_data', {}))
        else:
            receipt.extracted_data = data.get('extracted_data', {})
        
        db.session.commit()
        
        return jsonify({
            'receipt_id': receipt.id,
            'extracted_data': receipt.extracted_data,
            'message': 'Receipt data updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

