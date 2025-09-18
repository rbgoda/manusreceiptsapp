from flask import Blueprint, request, jsonify
from src.models.expense import Receipt, Expense, Category
from src.models.user import db
from sqlalchemy import desc

receipt_review_bp = Blueprint('receipt_review', __name__)

# CORS headers for all routes
@receipt_review_bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@receipt_review_bp.route('/receipt-review/pending', methods=['GET'])
def get_pending_receipts():
    """Get all receipts pending review"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        receipts = Receipt.query.filter_by(review_status='pending').order_by(
            desc(Receipt.created_at)
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for receipt in receipts.items:
            receipt_data = receipt.to_dict()
            # Add expense data if linked
            if receipt.expense:
                receipt_data['expense'] = receipt.expense.to_dict()
            result.append(receipt_data)
        
        return jsonify({
            'receipts': result,
            'total': receipts.total,
            'pages': receipts.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@receipt_review_bp.route('/receipt-review/<int:receipt_id>', methods=['GET'])
def get_receipt_details(receipt_id):
    """Get detailed receipt information for review"""
    try:
        receipt = Receipt.query.get_or_404(receipt_id)
        
        receipt_data = receipt.to_dict()
        
        # Add expense data if linked
        if receipt.expense:
            receipt_data['expense'] = receipt.expense.to_dict()
        
        # Get available categories for dropdown
        categories = Category.query.all()
        receipt_data['available_categories'] = [cat.to_dict() for cat in categories]
        
        return jsonify(receipt_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@receipt_review_bp.route('/receipt-review/<int:receipt_id>/approve', methods=['POST'])
def approve_receipt(receipt_id):
    """Approve receipt with reviewed data"""
    try:
        receipt = Receipt.query.get_or_404(receipt_id)
        data = request.get_json()
        
        # Update receipt with reviewed data
        receipt.review_status = 'approved'
        receipt.reviewed_data = data.get('reviewed_data', receipt.extracted_data)
        
        # Create or update expense based on reviewed data
        reviewed_data = receipt.reviewed_data or receipt.extracted_data
        
        if receipt.expense:
            # Update existing expense
            expense = receipt.expense
        else:
            # Create new expense
            expense = Expense()
            expense.receipt_id = receipt.id
        
        # Update expense with reviewed data
        if reviewed_data:
            expense.merchant = reviewed_data.get('merchant', '')
            expense.amount = float(reviewed_data.get('amount', 0))
            expense.date = reviewed_data.get('date')
            expense.description = reviewed_data.get('description', '')
            
            # Set category
            category_name = reviewed_data.get('category')
            if category_name:
                category = Category.query.filter_by(name=category_name).first()
                if category:
                    expense.category_id = category.id
        
        expense.verification_status = 'verified'
        
        if not receipt.expense:
            db.session.add(expense)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Receipt approved successfully',
            'receipt': receipt.to_dict(),
            'expense': expense.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@receipt_review_bp.route('/receipt-review/<int:receipt_id>/reject', methods=['POST'])
def reject_receipt(receipt_id):
    """Reject receipt"""
    try:
        receipt = Receipt.query.get_or_404(receipt_id)
        data = request.get_json()
        
        receipt.review_status = 'rejected'
        
        # If there's an associated expense, mark it as rejected
        if receipt.expense:
            receipt.expense.verification_status = 'rejected'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Receipt rejected',
            'receipt': receipt.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@receipt_review_bp.route('/receipt-review/<int:receipt_id>/update', methods=['PUT'])
def update_receipt_data(receipt_id):
    """Update receipt extracted data during review"""
    try:
        receipt = Receipt.query.get_or_404(receipt_id)
        data = request.get_json()
        
        # Update the reviewed data
        receipt.reviewed_data = data.get('reviewed_data', {})
        
        db.session.commit()
        
        return jsonify({
            'message': 'Receipt data updated',
            'receipt': receipt.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@receipt_review_bp.route('/receipt-review/stats', methods=['GET'])
def get_review_stats():
    """Get receipt review statistics"""
    try:
        total_receipts = Receipt.query.count()
        pending_receipts = Receipt.query.filter_by(review_status='pending').count()
        approved_receipts = Receipt.query.filter_by(review_status='approved').count()
        rejected_receipts = Receipt.query.filter_by(review_status='rejected').count()
        
        return jsonify({
            'total_receipts': total_receipts,
            'pending_receipts': pending_receipts,
            'approved_receipts': approved_receipts,
            'rejected_receipts': rejected_receipts,
            'approval_rate': (approved_receipts / total_receipts * 100) if total_receipts > 0 else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

