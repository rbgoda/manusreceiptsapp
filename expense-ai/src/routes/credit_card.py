from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from src.services.statement_processor import StatementProcessor
from src.models.expense import CreditCardTransaction, Expense, Category
from src.models.user import db
from sqlalchemy import func, desc

credit_card_bp = Blueprint('credit_card', __name__)

# CORS headers for all routes
@credit_card_bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@credit_card_bp.route('/credit-card/upload-statement', methods=['POST'])
def upload_statement():
    """Upload and process credit card statement"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type
        allowed_extensions = {'csv', 'txt', 'pdf'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Unsupported file type. Please upload CSV, TXT, or PDF files.'}), 400
        
        # Read file content
        file_content = file.read().decode('utf-8')
        filename = secure_filename(file.filename)
        
        # Process statement
        processor = StatementProcessor()
        
        if filename.endswith('.csv'):
            transactions = processor.parse_csv_statement(file_content, filename)
        else:
            # Use AI for other formats
            transactions = processor.extract_transactions_with_ai(file_content)
        
        if not transactions:
            return jsonify({'error': 'No transactions found in the statement'}), 400
        
        # Save transactions
        saved_transactions = processor.save_transactions(transactions, filename)
        
        # Auto-match transactions
        match_results = processor.auto_match_transactions()
        
        return jsonify({
            'message': 'Statement processed successfully',
            'transactions_imported': len(saved_transactions),
            'auto_match_results': match_results,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@credit_card_bp.route('/credit-card/transactions', methods=['GET'])
def get_transactions():
    """Get all credit card transactions"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status', None)
        
        query = CreditCardTransaction.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        transactions = query.order_by(desc(CreditCardTransaction.date)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = []
        for transaction in transactions.items:
            tx_data = {
                'id': transaction.id,
                'date': transaction.date.isoformat(),
                'merchant': transaction.merchant,
                'amount': float(transaction.amount),
                'description': transaction.description,
                'status': transaction.status,
                'category': transaction.category.name if transaction.category else None,
                'matched_expense_id': transaction.matched_expense_id
            }
            result.append(tx_data)
        
        return jsonify({
            'transactions': result,
            'total': transactions.total,
            'pages': transactions.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@credit_card_bp.route('/credit-card/transactions/<int:transaction_id>/create-expense', methods=['POST'])
def create_expense_from_transaction(transaction_id):
    """Create an expense from a credit card transaction"""
    try:
        transaction = CreditCardTransaction.query.get_or_404(transaction_id)
        
        if transaction.status == 'matched':
            return jsonify({'error': 'Transaction is already matched'}), 400
        
        # Create expense from transaction
        expense = Expense(
            date=transaction.date,
            merchant=transaction.merchant,
            amount=transaction.amount,
            description=transaction.description,
            category_id=transaction.category_id
        )
        
        db.session.add(expense)
        db.session.flush()  # Get the expense ID
        
        # Update transaction status
        transaction.status = 'matched'
        transaction.matched_expense_id = expense.id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Expense created successfully',
            'expense_id': expense.id,
            'transaction_id': transaction.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@credit_card_bp.route('/credit-card/run-auto-match', methods=['POST'])
def run_auto_match():
    """Manually trigger auto-matching of transactions"""
    try:
        processor = StatementProcessor()
        results = processor.auto_match_transactions()
        
        return jsonify({
            'message': 'Auto-matching completed',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@credit_card_bp.route('/credit-card/analytics', methods=['GET'])
def get_credit_card_analytics():
    """Get credit card analytics and insights"""
    try:
        # Transaction status breakdown
        status_breakdown = db.session.query(
            CreditCardTransaction.status,
            func.count(CreditCardTransaction.id).label('count'),
            func.sum(CreditCardTransaction.amount).label('total_amount')
        ).group_by(CreditCardTransaction.status).all()
        
        # Monthly transaction trends
        monthly_trends = db.session.query(
            func.strftime('%Y-%m', CreditCardTransaction.date).label('month'),
            func.count(CreditCardTransaction.id).label('count'),
            func.sum(CreditCardTransaction.amount).label('total_amount')
        ).group_by(func.strftime('%Y-%m', CreditCardTransaction.date)).all()
        
        # Category breakdown
        category_breakdown = db.session.query(
            Category.name,
            func.count(CreditCardTransaction.id).label('count'),
            func.sum(CreditCardTransaction.amount).label('total_amount')
        ).join(CreditCardTransaction).group_by(Category.id, Category.name).all()
        
        # Top merchants
        top_merchants = db.session.query(
            CreditCardTransaction.merchant,
            func.count(CreditCardTransaction.id).label('count'),
            func.sum(CreditCardTransaction.amount).label('total_amount')
        ).group_by(CreditCardTransaction.merchant).order_by(
            func.sum(CreditCardTransaction.amount).desc()
        ).limit(10).all()
        
        return jsonify({
            'status_breakdown': [
                {
                    'status': status,
                    'count': count,
                    'total_amount': float(total_amount or 0)
                }
                for status, count, total_amount in status_breakdown
            ],
            'monthly_trends': [
                {
                    'month': month,
                    'count': count,
                    'total_amount': float(total_amount or 0)
                }
                for month, count, total_amount in monthly_trends
            ],
            'category_breakdown': [
                {
                    'category': name,
                    'count': count,
                    'total_amount': float(total_amount or 0)
                }
                for name, count, total_amount in category_breakdown
            ],
            'top_merchants': [
                {
                    'merchant': merchant,
                    'count': count,
                    'total_amount': float(total_amount or 0)
                }
                for merchant, count, total_amount in top_merchants
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

