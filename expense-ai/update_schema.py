#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.user import db
from src.models.expense import Receipt, Expense, Category, CreditCardTransaction
from src.main import app

def update_database_schema():
    """Update database schema to include new columns"""
    with app.app_context():
        # Drop and recreate all tables to ensure schema is up to date
        db.drop_all()
        db.create_all()
        
        # Create default categories
        default_categories = [
            {'name': 'Meals Dining', 'color': '#f59e0b'},
            {'name': 'Transportation', 'color': '#8b5cf6'},
            {'name': 'Office Supplies', 'color': '#10b981'},
            {'name': 'Software Subscriptions', 'color': '#3b82f6'},
            {'name': 'Accommodation', 'color': '#ec4899'},
            {'name': 'Entertainment', 'color': '#f97316'},
            {'name': 'Healthcare', 'color': '#06b6d4'},
            {'name': 'Utilities', 'color': '#84cc16'}
        ]
        
        for cat_data in default_categories:
            existing = Category.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = Category(name=cat_data['name'], color=cat_data['color'])
                db.session.add(category)
        
        # Add some sample receipts for testing
        sample_receipts = [
            {
                'filename': 'starbucks_receipt_001.jpg',
                'file_path': '/uploads/starbucks_receipt_001.jpg',
                'file_type': 'jpg',
                'extracted_data': {
                    'merchant': 'Starbucks Coffee',
                    'amount': '15.75',
                    'date': '2024-01-20',
                    'category': 'Meals Dining',
                    'description': 'Coffee and pastry',
                    'confidence': 0.95
                },
                'is_processed': True,
                'review_status': 'pending'
            },
            {
                'filename': 'uber_receipt_002.pdf',
                'file_path': '/uploads/uber_receipt_002.pdf',
                'file_type': 'pdf',
                'extracted_data': {
                    'merchant': 'Uber Technologies',
                    'amount': '32.50',
                    'date': '2024-01-19',
                    'category': 'Transportation',
                    'description': 'Ride to airport',
                    'confidence': 0.88
                },
                'is_processed': True,
                'review_status': 'pending'
            },
            {
                'filename': 'office_depot_receipt.png',
                'file_path': '/uploads/office_depot_receipt.png',
                'file_type': 'png',
                'extracted_data': {
                    'merchant': 'Office Depot',
                    'amount': '127.99',
                    'date': '2024-01-18',
                    'category': 'Office Supplies',
                    'description': 'Office supplies and equipment',
                    'confidence': 0.92
                },
                'is_processed': True,
                'review_status': 'pending'
            }
        ]
        
        for receipt_data in sample_receipts:
            receipt = Receipt(
                filename=receipt_data['filename'],
                file_path=receipt_data['file_path'],
                file_type=receipt_data['file_type'],
                extracted_data=receipt_data['extracted_data'],
                is_processed=receipt_data['is_processed'],
                review_status=receipt_data['review_status']
            )
            db.session.add(receipt)
        
        db.session.commit()
        print("Database schema updated successfully!")
        print(f"Added {len(default_categories)} categories")
        print(f"Added {len(sample_receipts)} sample receipts for testing")

if __name__ == '__main__':
    update_database_schema()

