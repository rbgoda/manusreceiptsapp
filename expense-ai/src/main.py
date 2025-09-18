import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.expense import Category
from src.routes.user import user_bp
from src.routes.expense import expense_bp
from src.routes.receipt import receipt_bp
from src.routes.ai_assistant import ai_assistant_bp
from src.routes.credit_card import credit_card_bp
from src.routes.receipt_review import receipt_review_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(expense_bp, url_prefix='/api')
app.register_blueprint(receipt_bp, url_prefix='/api')
app.register_blueprint(ai_assistant_bp, url_prefix='/api')
app.register_blueprint(credit_card_bp, url_prefix='/api')
app.register_blueprint(receipt_review_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()
    
    # Create default categories if they don't exist
    if Category.query.count() == 0:
        default_categories = [
            Category(name='Meals Dining', color='#f59e0b'),
            Category(name='Transportation', color='#8b5cf6'),
            Category(name='Office Supplies', color='#10b981'),
            Category(name='Software Subscriptions', color='#3b82f6'),
            Category(name='Accommodation', color='#ec4899'),
            Category(name='Entertainment', color='#ef4444'),
            Category(name='Healthcare', color='#06b6d4'),
            Category(name='Education', color='#84cc16'),
            Category(name='Utilities', color='#f97316'),
            Category(name='Other', color='#6b7280')
        ]
        
        for category in default_categories:
            db.session.add(category)
        
        db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
