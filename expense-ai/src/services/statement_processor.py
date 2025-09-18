import csv
import io
import re
import openai
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.models.expense import CreditCardTransaction, Expense, Category
from src.models.user import db
from sqlalchemy import func

class StatementProcessor:
    def __init__(self):
        self.client = openai.OpenAI()
    
    def parse_csv_statement(self, file_content: str, filename: str) -> List[Dict[str, Any]]:
        """Parse CSV credit card statement and extract transactions"""
        try:
            # Try to detect CSV format and parse
            csv_reader = csv.DictReader(io.StringIO(file_content))
            transactions = []
            
            for row in csv_reader:
                # Common CSV column mappings
                transaction = self._normalize_csv_row(row)
                if transaction:
                    transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            raise Exception(f"Error parsing CSV statement: {str(e)}")
    
    def _normalize_csv_row(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Normalize CSV row to standard transaction format"""
        try:
            # Common column name variations
            date_fields = ['Date', 'Transaction Date', 'Posted Date', 'date']
            description_fields = ['Description', 'Merchant', 'Transaction Description', 'description']
            amount_fields = ['Amount', 'Transaction Amount', 'Debit', 'Credit', 'amount']
            
            # Find the actual column names
            date_col = next((col for col in date_fields if col in row), None)
            desc_col = next((col for col in description_fields if col in row), None)
            amount_col = next((col for col in amount_fields if col in row), None)
            
            if not all([date_col, desc_col, amount_col]):
                return None
            
            # Parse date
            date_str = row[date_col].strip()
            try:
                # Try common date formats
                for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d/%m/%Y']:
                    try:
                        transaction_date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    return None
            except:
                return None
            
            # Parse amount
            amount_str = row[amount_col].strip()
            amount_str = re.sub(r'[^\d.-]', '', amount_str)  # Remove currency symbols
            try:
                amount = abs(float(amount_str))  # Use absolute value
            except ValueError:
                return None
            
            # Clean description
            description = row[desc_col].strip()
            
            return {
                'date': transaction_date,
                'merchant': description,
                'amount': amount,
                'description': description
            }
            
        except Exception:
            return None
    
    def extract_transactions_with_ai(self, file_content: str) -> List[Dict[str, Any]]:
        """Use AI to extract transactions from unstructured text"""
        try:
            system_prompt = """
You are a financial data extraction expert. Extract credit card transactions from the provided text.
Return a JSON array of transactions with the following format:
[
  {
    "date": "YYYY-MM-DD",
    "merchant": "Merchant Name",
    "amount": 123.45,
    "description": "Transaction description"
  }
]

Rules:
- Only extract actual transactions (ignore headers, totals, etc.)
- Use positive amounts for all transactions
- Parse dates to YYYY-MM-DD format
- Clean up merchant names (remove extra spaces, codes)
- If you can't parse a transaction clearly, skip it
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract transactions from this credit card statement:\n\n{file_content[:4000]}"}
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            # Parse JSON response
            import json
            transactions_data = json.loads(response.choices[0].message.content)
            
            # Convert to our format
            transactions = []
            for tx in transactions_data:
                try:
                    transaction = {
                        'date': datetime.strptime(tx['date'], '%Y-%m-%d').date(),
                        'merchant': tx['merchant'],
                        'amount': float(tx['amount']),
                        'description': tx.get('description', tx['merchant'])
                    }
                    transactions.append(transaction)
                except:
                    continue
            
            return transactions
            
        except Exception as e:
            raise Exception(f"Error extracting transactions with AI: {str(e)}")
    
    def categorize_transaction(self, merchant: str, description: str) -> Optional[str]:
        """Use AI to categorize a transaction"""
        try:
            # Get available categories
            categories = Category.query.all()
            category_names = [cat.name for cat in categories]
            
            system_prompt = f"""
You are a transaction categorization expert. Categorize the transaction based on the merchant and description.

Available categories: {', '.join(category_names)}

Return only the category name that best matches the transaction. If no category fits well, return "Other".
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Merchant: {merchant}\nDescription: {description}"}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            category_name = response.choices[0].message.content.strip()
            
            # Validate category exists
            if category_name in category_names:
                return category_name
            else:
                return "Other"
                
        except Exception:
            return "Other"
    
    def save_transactions(self, transactions: List[Dict[str, Any]], filename: str) -> List[CreditCardTransaction]:
        """Save transactions to database"""
        saved_transactions = []
        
        for tx_data in transactions:
            try:
                # Check if transaction already exists
                existing = CreditCardTransaction.query.filter_by(
                    date=tx_data['date'],
                    merchant=tx_data['merchant'],
                    amount=tx_data['amount']
                ).first()
                
                if existing:
                    continue
                
                # Categorize transaction
                category_name = self.categorize_transaction(
                    tx_data['merchant'], 
                    tx_data['description']
                )
                
                category = Category.query.filter_by(name=category_name).first()
                
                # Create transaction
                transaction = CreditCardTransaction(
                    date=tx_data['date'],
                    merchant=tx_data['merchant'],
                    amount=tx_data['amount'],
                    description=tx_data['description'],
                    category_id=category.id if category else None,
                    statement_file=filename,
                    status='unmatched'
                )
                
                db.session.add(transaction)
                saved_transactions.append(transaction)
                
            except Exception as e:
                print(f"Error saving transaction: {e}")
                continue
        
        db.session.commit()
        return saved_transactions
    
    def auto_match_transactions(self) -> Dict[str, int]:
        """Automatically match credit card transactions with existing expenses"""
        unmatched_transactions = CreditCardTransaction.query.filter_by(status='unmatched').all()
        matched_count = 0
        
        for transaction in unmatched_transactions:
            # Look for matching expenses within 3 days and similar amount
            date_range_start = transaction.date
            date_range_end = transaction.date
            
            # Extend date range by a few days
            from datetime import timedelta
            date_range_start = transaction.date - timedelta(days=3)
            date_range_end = transaction.date + timedelta(days=3)
            
            # Find potential matches
            potential_matches = Expense.query.filter(
                Expense.date >= date_range_start,
                Expense.date <= date_range_end,
                Expense.amount.between(
                    transaction.amount * 0.95,  # 5% tolerance
                    transaction.amount * 1.05
                )
            ).all()
            
            # Check for merchant similarity
            for expense in potential_matches:
                if self._merchants_similar(transaction.merchant, expense.merchant):
                    # Match found
                    transaction.status = 'matched'
                    transaction.matched_expense_id = expense.id
                    matched_count += 1
                    break
        
        db.session.commit()
        
        return {
            'total_transactions': len(unmatched_transactions),
            'matched': matched_count,
            'unmatched': len(unmatched_transactions) - matched_count
        }
    
    def _merchants_similar(self, merchant1: str, merchant2: str) -> bool:
        """Check if two merchant names are similar"""
        # Simple similarity check - can be improved
        merchant1 = merchant1.lower().strip()
        merchant2 = merchant2.lower().strip()
        
        # Exact match
        if merchant1 == merchant2:
            return True
        
        # Check if one contains the other
        if merchant1 in merchant2 or merchant2 in merchant1:
            return True
        
        # Check for common words
        words1 = set(merchant1.split())
        words2 = set(merchant2.split())
        
        # If they share significant words
        common_words = words1.intersection(words2)
        if len(common_words) > 0 and len(common_words) >= min(len(words1), len(words2)) * 0.5:
            return True
        
        return False

