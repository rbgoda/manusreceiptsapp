import openai
from datetime import datetime, date
from typing import Dict, Any, List
from src.models.expense import Expense, Category, CreditCardTransaction
from src.models.user import db
from sqlalchemy import func

class AIAssistant:
    def __init__(self):
        self.client = openai.OpenAI()
    
    def get_expense_context(self) -> str:
        """Get current expense data to provide context for AI responses"""
        try:
            # Get total expenses
            total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
            
            # Get this month's expenses
            current_month = date.today().replace(day=1)
            this_month_expenses = db.session.query(func.sum(Expense.amount)).filter(
                Expense.date >= current_month
            ).scalar() or 0
            
            # Get expense count
            expense_count = Expense.query.count()
            
            # Get recent expenses
            recent_expenses = Expense.query.order_by(Expense.date.desc()).limit(5).all()
            
            # Get category breakdown
            category_breakdown = db.session.query(
                Category.name,
                func.sum(Expense.amount).label('total')
            ).join(Expense).group_by(Category.id, Category.name).all()
            
            # Get top merchants
            top_merchants = db.session.query(
                Expense.merchant,
                func.sum(Expense.amount).label('total')
            ).group_by(Expense.merchant).order_by(
                func.sum(Expense.amount).desc()
            ).limit(5).all()
            
            context = f"""
Current Expense Data Summary:
- Total expenses: ${total_expenses:.2f}
- This month's expenses: ${this_month_expenses:.2f}
- Total number of expenses: {expense_count}

Recent Expenses:
"""
            for expense in recent_expenses:
                context += f"- {expense.merchant}: ${expense.amount:.2f} on {expense.date} ({expense.category.name if expense.category else 'No category'})\n"
            
            context += "\nCategory Breakdown:\n"
            for category_name, total in category_breakdown:
                context += f"- {category_name}: ${float(total):.2f}\n"
            
            context += "\nTop Merchants:\n"
            for merchant, total in top_merchants:
                context += f"- {merchant}: ${float(total):.2f}\n"
            
            return context
            
        except Exception as e:
            return f"Error retrieving expense data: {str(e)}"
    
    def process_query(self, user_message: str) -> str:
        """Process user query and return AI response"""
        try:
            # Get current expense context
            expense_context = self.get_expense_context()
            
            # Create system prompt
            system_prompt = f"""
You are an AI assistant for an expense management application called ExpenseAI. 
You help users understand and analyze their expense data.

Current user's expense data:
{expense_context}

Guidelines:
- Be helpful and conversational
- Provide specific insights based on the actual data
- If asked about data not available, explain what data is available
- Suggest actionable insights when appropriate
- Keep responses concise but informative
- Use dollar amounts and percentages when relevant
- If the user asks about trends, explain what you can see from the data
"""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I'm sorry, I encountered an error while processing your request: {str(e)}"
    
    def get_expense_insights(self) -> List[str]:
        """Generate automatic insights about user's expenses"""
        try:
            expense_context = self.get_expense_context()
            
            system_prompt = f"""
Based on the following expense data, provide 3-5 brief insights or observations about the user's spending patterns. 
Each insight should be one sentence and actionable or informative.

{expense_context}

Format as a simple list of insights.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            # Parse response into list
            insights_text = response.choices[0].message.content
            insights = [insight.strip() for insight in insights_text.split('\n') if insight.strip() and not insight.strip().startswith('-')]
            
            return insights[:5]  # Limit to 5 insights
            
        except Exception as e:
            return [f"Unable to generate insights: {str(e)}"]

