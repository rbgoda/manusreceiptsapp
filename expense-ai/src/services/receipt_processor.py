import os
import json
import base64
from datetime import datetime
from typing import Dict, Any, Optional
import openai
from PIL import Image
import io

class ReceiptProcessor:
    def __init__(self):
        self.client = openai.OpenAI()
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_receipt_data(self, image_path: str) -> Dict[str, Any]:
        """Extract expense data from receipt image using OpenAI Vision API"""
        try:
            # Encode the image
            base64_image = self.encode_image(image_path)
            
            # Create the prompt for expense data extraction
            prompt = """
            Analyze this receipt image and extract the following information in JSON format:
            
            {
                "merchant": "Name of the business/merchant",
                "amount": "Total amount as a number (e.g., 25.99)",
                "date": "Date in YYYY-MM-DD format",
                "items": ["List of items purchased"],
                "category": "Suggested expense category (e.g., 'Meals Dining', 'Transportation', 'Office Supplies', 'Software Subscriptions', 'Accommodation', 'Entertainment', 'Healthcare', 'Education', 'Utilities', 'Other')",
                "tax": "Tax amount as a number if visible",
                "tip": "Tip amount as a number if visible",
                "payment_method": "Payment method if visible (e.g., 'Credit Card', 'Cash', 'Debit Card')",
                "address": "Business address if visible",
                "phone": "Business phone number if visible",
                "confidence": "Confidence level from 0.0 to 1.0 for the extraction accuracy"
            }
            
            If any information is not clearly visible or cannot be determined, use null for that field.
            Make sure the amount is the total amount paid.
            For the category, choose the most appropriate one from the list provided.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            
            # Extract JSON from the response (in case there's extra text)
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                extracted_data = json.loads(json_str)
                
                # Validate and clean the data
                return self._validate_extracted_data(extracted_data)
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            print(f"Error extracting receipt data: {str(e)}")
            return {
                "error": str(e),
                "confidence": 0.0
            }
    
    def _validate_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted data"""
        validated_data = {}
        
        # Merchant name
        validated_data['merchant'] = data.get('merchant', 'Unknown Merchant')
        
        # Amount - ensure it's a float
        try:
            amount = data.get('amount')
            if amount is not None:
                # Remove any currency symbols and convert to float
                if isinstance(amount, str):
                    amount = amount.replace('$', '').replace(',', '').strip()
                validated_data['amount'] = float(amount)
            else:
                validated_data['amount'] = 0.0
        except (ValueError, TypeError):
            validated_data['amount'] = 0.0
        
        # Date - validate format
        try:
            date_str = data.get('date')
            if date_str:
                # Try to parse the date to validate format
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                validated_data['date'] = date_str
            else:
                validated_data['date'] = datetime.now().strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            validated_data['date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Items
        validated_data['items'] = data.get('items', [])
        if not isinstance(validated_data['items'], list):
            validated_data['items'] = []
        
        # Category
        valid_categories = [
            'Meals Dining', 'Transportation', 'Office Supplies', 
            'Software Subscriptions', 'Accommodation', 'Entertainment',
            'Healthcare', 'Education', 'Utilities', 'Other'
        ]
        category = data.get('category', 'Other')
        validated_data['category'] = category if category in valid_categories else 'Other'
        
        # Optional fields
        validated_data['tax'] = self._safe_float(data.get('tax'))
        validated_data['tip'] = self._safe_float(data.get('tip'))
        validated_data['payment_method'] = data.get('payment_method')
        validated_data['address'] = data.get('address')
        validated_data['phone'] = data.get('phone')
        
        # Confidence
        try:
            confidence = data.get('confidence', 0.5)
            validated_data['confidence'] = max(0.0, min(1.0, float(confidence)))
        except (ValueError, TypeError):
            validated_data['confidence'] = 0.5
        
        return validated_data
    
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                value = value.replace('$', '').replace(',', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def process_receipt_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process a receipt file and return extracted data"""
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {"error": "File not found", "confidence": 0.0}
            
            # Get file extension
            file_ext = os.path.splitext(filename)[1].lower()
            
            # For now, we'll handle images. PDF support can be added later
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                return self.extract_receipt_data(file_path)
            elif file_ext == '.pdf':
                # For PDF files, we'd need to convert to images first
                # This is a placeholder for PDF processing
                return {
                    "error": "PDF processing not yet implemented",
                    "confidence": 0.0
                }
            else:
                return {
                    "error": f"Unsupported file type: {file_ext}",
                    "confidence": 0.0
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "confidence": 0.0
            }

