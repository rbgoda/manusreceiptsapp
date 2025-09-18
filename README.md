# ExpenseAI: Premium AI-Powered Expense Management App

![ExpenseAI Dashboard](https://github.com/your-username/expense-ai/blob/main/docs/dashboard.png?raw=true)

ExpenseAI is a premium, AI-powered expense management application designed to simplify tracking, categorizing, and analyzing your expenditures. It features intelligent receipt scanning, human-in-the-loop validation, visual analytics, an AI chat assistant, and seamless credit card statement integration.

## ✨ Key Features

*   **Smart Receipt Scanner**: Upload photos or PDFs of receipts, and our AI automatically extracts all relevant expense details (merchant, amount, date, category, description).
*   **Human-in-the-Loop Validation**: Review and edit AI-extracted data before saving, ensuring 100% accuracy for your expense records.
*   **Interactive Expense Dashboard**: Get a beautiful overview of your spending with key metrics, recent transactions, and top spending categories.
*   **Visual Analytics**: Dive deep into your financial habits with interactive charts showing spending patterns by category, time, and merchants.
*   **AI Chat Assistant**: Ask natural language questions about your expenses and receive intelligent, data-driven answers.
*   **Comprehensive Expense Management**: Easily filter, search, and organize all your expenses. Track verification status and manage reimbursements.
*   **Credit Card Statement Integration**: Upload credit card statements (CSV, PDF, TXT), and our AI extracts all transactions. Features include:
    *   **Auto-Matching**: Automatically links credit card transactions to existing expense receipts.
    *   **Missing Receipt Alerts**: Identifies transactions that require receipt uploads.
    *   **One-Click Expense Creation**: Convert unmatched transactions into new expense entries.
    *   **Visual Status Tracking**: See matched, unmatched, and pending receipts at a glance.

## 🚀 Technologies Used

**Backend (Flask API)**:
*   Python 3.9+
*   Flask (Web Framework)
*   SQLAlchemy (ORM)
*   SQLite (Database)
*   Google Gemini API (for AI capabilities)
*   Flask-CORS

**Frontend (React Application)**:
*   React.js (JavaScript Library)
*   Vite (Build Tool)
*   pnpm (Package Manager)
*   Recharts (for Data Visualization)
*   Tailwind CSS (for Styling - *implied from screenshots, actual implementation might vary*)

## 💻 Local Setup Instructions (for MacBook)

To get ExpenseAI up and running on your local MacBook, please follow the detailed instructions in the `macbook_setup_instructions.md` file. This includes:

1.  **Prerequisites**: Installing Homebrew, Python, Node.js, pnpm, and Git.
2.  **Getting the Codebase**: Extracting the provided `expense-ai-app.zip` archive.
3.  **Backend Setup**: Creating a Python virtual environment, installing dependencies, setting up your `GEMINI_API_KEY` in a `.env` file, initializing the database, and starting the Flask server.
4.  **Frontend Setup**: Installing pnpm dependencies and starting the React development server.
5.  **Accessing the Application**: Navigating to `http://localhost:5173` in your browser.

## 🧠 AI Model Details

ExpenseAI leverages **Google Gemini API** for its core AI functionalities:

*   **Receipt Scanning**: The `gemini-pro-vision` model is used to analyze receipt images/PDFs and extract structured data like merchant, amount, date, and category. It excels at understanding visual information and converting it into actionable data.
*   **AI Chat Assistant**: The `gemini-pro` model powers the conversational AI assistant, allowing users to query their expense data using natural language and receive intelligent, context-aware responses.

**Note on Model Training**: This application utilizes pre-trained Google Gemini models. It does not involve custom model training or fine-tuning of these foundational models. The intelligence comes from effective prompt engineering and leveraging the advanced capabilities of the Gemini API.

## 🤝 Human-in-the-Loop (HITL) Approval

The Human-in-the-Loop (HITL) system is a critical component for ensuring data accuracy and continuous improvement:

*   **Validation**: After AI extracts data from a receipt, it enters a 
