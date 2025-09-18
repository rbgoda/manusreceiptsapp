from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models.user import db
from src.models.expense import Expense, Category, Receipt, CreditCardTransaction
import json

expense_bp = Blueprint('expense', __name__)

# CORS headers for all routes
@expense_bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@expense_bp.route('/expenses', methods=['GET'])
def get_expenses():
    """Get all expenses with optional filtering"""
    try:
        # Query parameters for filtering
        category_id = request.args.get('category_id')
        merchant = request.args.get('merchant')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Expense.query
        
        if category_id:
            query = query.filter(Expense.category_id == category_id)
        if merchant:
            query = query.filter(Expense.merchant.ilike(f'%{merchant}%'))
        if start_date:
            query = query.filter(Expense.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Expense.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
            
        expenses = query.order_by(Expense.date.desc()).all()
        return jsonify([expense.to_dict() for expense in expenses])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/expenses', methods=['POST'])
def create_expense():
    """Create a new expense"""
    try:
        data = request.get_json()
        
        expense = Expense(
            merchant=data['merchant'],
            amount=float(data['amount']),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            description=data.get('description', ''),
            category_id=data.get('category_id'),
            reimbursement_status=data.get('reimbursement_status', 'pending'),
            verification_status=data.get('verification_status', 'pending')
        )
        
        db.session.add(expense)
        db.session.commit()
        
        return jsonify(expense.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """Update an existing expense"""
    try:
        expense = Expense.query.get_or_404(expense_id)
        data = request.get_json()
        
        expense.merchant = data.get('merchant', expense.merchant)
        expense.amount = float(data.get('amount', expense.amount))
        expense.date = datetime.strptime(data['date'], '%Y-%m-%d').date() if 'date' in data else expense.date
        expense.description = data.get('description', expense.description)
        expense.category_id = data.get('category_id', expense.category_id)
        expense.reimbursement_status = data.get('reimbursement_status', expense.reimbursement_status)
        expense.verification_status = data.get('verification_status', expense.verification_status)
        
        db.session.commit()
        
        return jsonify(expense.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense"""
    try:
        expense = Expense.query.get_or_404(expense_id)
        db.session.delete(expense)
        db.session.commit()
        
        return jsonify({'message': 'Expense deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Categories endpoints
@expense_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/categories', methods=['POST'])
def create_category():
    """Create a new category"""
    try:
        data = request.get_json()
        
        category = Category(
            name=data['name'],
            color=data.get('color', '#6366f1')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify(category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Analytics endpoints
@expense_bp.route('/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get expense analytics summary"""
    try:
        # Total expenses
        total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
        
        # This month expenses
        current_month = date.today().replace(day=1)
        this_month_expenses = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.date >= current_month
        ).scalar() or 0
        
        # Total receipts
        total_receipts = Receipt.query.count()
        
        # Average per receipt
        avg_per_receipt = total_expenses / total_receipts if total_receipts > 0 else 0
        
        # Recent expenses
        recent_expenses = Expense.query.order_by(Expense.date.desc()).limit(5).all()
        
        # Top categories
        category_spending = db.session.query(
            Category.name,
            db.func.sum(Expense.amount).label('total')
        ).join(Expense).group_by(Category.id, Category.name).order_by(
            db.func.sum(Expense.amount).desc()
        ).limit(3).all()
        
        return jsonify({
            'total_expenses': total_expenses,
            'this_month_expenses': this_month_expenses,
            'total_receipts': total_receipts,
            'avg_per_receipt': avg_per_receipt,
            'recent_expenses': [expense.to_dict() for expense in recent_expenses],
            'top_categories': [{'name': name, 'amount': float(total)} for name, total in category_spending]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/analytics/monthly-spending', methods=['GET'])
def get_monthly_spending():
    """Get monthly spending data for charts"""
    try:
        # Get spending by month for the last 12 months
        monthly_data = db.session.query(
            db.func.strftime('%Y-%m', Expense.date).label('month'),
            db.func.sum(Expense.amount).label('total')
        ).group_by(
            db.func.strftime('%Y-%m', Expense.date)
        ).order_by('month').all()
        
        return jsonify([{
            'month': month,
            'total': float(total)
        } for month, total in monthly_data])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/analytics/category-breakdown', methods=['GET'])
def get_category_breakdown():
    """Get spending breakdown by category"""
    try:
        category_data = db.session.query(
            Category.name,
            Category.color,
            db.func.sum(Expense.amount).label('total')
        ).join(Expense).group_by(Category.id, Category.name, Category.color).all()
        
        return jsonify([{
            'name': name,
            'color': color,
            'amount': float(total)
        } for name, color, total in category_data])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/analytics/merchant-spending', methods=['GET'])
def get_merchant_spending():
    """Get top merchants by spending"""
    try:
        merchant_data = db.session.query(
            Expense.merchant,
            db.func.sum(Expense.amount).label('total')
        ).group_by(Expense.merchant).order_by(
            db.func.sum(Expense.amount).desc()
        ).limit(10).all()
        
        return jsonify([{
            'merchant': merchant,
            'amount': float(total)
        } for merchant, total in merchant_data])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Credit Card Transaction endpoints
@expense_bp.route('/credit-card-transactions', methods=['GET'])
def get_credit_card_transactions():
    """Get all credit card transactions"""
    try:
        transactions = CreditCardTransaction.query.order_by(CreditCardTransaction.date.desc()).all()
        return jsonify([transaction.to_dict() for transaction in transactions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/credit-card-transactions', methods=['POST'])
def create_credit_card_transaction():
    """Create a new credit card transaction"""
    try:
        data = request.get_json()
        
        transaction = CreditCardTransaction(
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            merchant=data['merchant'],
            amount=float(data['amount']),
            category=data.get('category', ''),
            description=data.get('description', '')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify(transaction.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/credit-card-transactions/<int:transaction_id>/create-expense', methods=['POST'])
def create_expense_from_transaction(transaction_id):
    """Create an expense from a credit card transaction"""
    try:
        transaction = CreditCardTransaction.query.get_or_404(transaction_id)
        
        # Create expense from transaction
        expense = Expense(
            merchant=transaction.merchant,
            amount=transaction.amount,
            date=transaction.date,
            description=transaction.description,
            verification_status='pending'
        )
        
        db.session.add(expense)
        db.session.flush()  # Get the expense ID
        
        # Mark transaction as matched
        transaction.is_matched = True
        transaction.matched_expense_id = expense.id
        
        db.session.commit()
        
        return jsonify(expense.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

