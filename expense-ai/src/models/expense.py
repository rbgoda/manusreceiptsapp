from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), default='#6366f1')  # hex color
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    merchant = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipt.id'), nullable=True)
    reimbursement_status = db.Column(db.String(20), default='pending')  # pending, approved, reimbursed
    verification_status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('Category', backref='expenses')
    receipt = db.relationship('Receipt', backref='expense', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'merchant': self.merchant,
            'amount': self.amount,
            'date': self.date.isoformat() if self.date else None,
            'description': self.description,
            'category_id': self.category_id,
            'category': self.category.to_dict() if self.category else None,
            'receipt_id': self.receipt_id,
            'reimbursement_status': self.reimbursement_status,
            'verification_status': self.verification_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # jpg, png, pdf
    extracted_data = db.Column(db.JSON)  # AI extracted data
    is_processed = db.Column(db.Boolean, default=False)
    review_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    reviewed_data = db.Column(db.JSON)  # Human-reviewed/corrected data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'extracted_data': self.extracted_data,
            'is_processed': self.is_processed,
            'review_status': self.review_status,
            'reviewed_data': self.reviewed_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CreditCardTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    merchant = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_matched = db.Column(db.Boolean, default=False)
    matched_expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    matched_expense = db.relationship('Expense', backref='credit_card_transaction', foreign_keys=[matched_expense_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'merchant': self.merchant,
            'amount': self.amount,
            'category': self.category,
            'description': self.description,
            'is_matched': self.is_matched,
            'matched_expense_id': self.matched_expense_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

