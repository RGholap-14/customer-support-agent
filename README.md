# 🤖 Customer Support Agent

An AI-powered customer support agent built with **LangGraph, LangChain, PostgreSQL, and Streamlit**.

The agent handles customer requests, retrieves order and policy information from PostgreSQL, determines refund eligibility, and uses **human-in-the-loop approval** for high-value refunds.

## 🚀 Features

- 🧠 LLM-based intent classification
- 📦 PostgreSQL-backed order lookup
- 📋 Database-backed refund policies
- 💰 Automatic processing for refunds below ₹5,000
- 👤 Human approval for refunds of ₹5,000 or more
- ✅ Approve / ❌ Reject refund workflow
- 🗄️ PostgreSQL persistence
- 🌐 Streamlit user interface
- 🛠️ LangChain tools
- 🔄 LangGraph conditional routing
- 👨‍💼 Admin interface for adding customers and orders
- 🔐 Parameterized SQL queries

## 🏗️ Architecture

```text
                    ┌──────────────────┐
                    │   Streamlit UI   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    LangGraph     │
                    │     Workflow     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Intent Classify  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Get Order      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Search Policy   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Refund Decision  │
                    └────────┬─────────┘
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
             Resolve    Auto Refund   Human Approval
                                           │
                                      ┌────┴────┐
                                      ▼         ▼
                                   Approve    Reject
                                      │         │
                                      ▼         ▼
                                Process     Rejected
                                 Refund

💰 Refund Workflow

The current business rule is:
Refund < ₹5,000
      → Automatically processed

Refund ≥ ₹5,000
      → Human approval required

🗄️ PostgreSQL

PostgreSQL is used as the persistent data store.

Main tables:

customers
orders
policies
refunds

Customer and order data can be added through the Streamlit admin interface instead of being hardcoded in the application.

📁 Project Structure
customer-support-agent/
│
├── app.py
├── database.py
├── frontend.py
├── graph.py
├── nodes.py
├── state.py
├── tools.py
├── requirements.txt
├── README.md
│
├── .env
└── .gitignore


| File          | Purpose                         |
| ------------- | ------------------------------- |
| `app.py`      | Runs the LangGraph workflow     |
| `frontend.py` | Streamlit application           |
| `graph.py`    | LangGraph workflow and routing  |
| `nodes.py`    | Workflow node implementations   |
| `tools.py`    | Database-backed LangChain tools |
| `database.py` | PostgreSQL operations           |
| `state.py`    | Shared LangGraph state          |




🛠️ Tech Stack
Python
LangGraph
LangChain
PostgreSQL
Psycopg
Streamlit
python-dotenv
⚙️ Setup
1. Clone the repository
git clone <your-repository-url>
cd customer-support-agent
2. Create a virtual environment

Windows:

python -m venv .venv
.venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables

Create a .env file:

DATABASE_URL=postgresql://username:password@localhost:5432/customer_support
OPENAI_API_KEY=your_api_key

Never commit .env or API keys to GitHub.

5. Initialize the database

Make sure PostgreSQL is running, then:

python database.py
6. Run the application
streamlit run frontend.py
🧪 Example Test Cases
Automatic Refund
Amount: ₹4,999
Condition: damaged

Expected:

Refund processed automatically
Human Approval — Approve
Amount: ₹75,000
Condition: damaged

Expected:

Human approval required
        ↓
Approve
        ↓
Refund processed
Human Approval — Reject
Amount: ₹75,000
Condition: damaged

Expected:

Human approval required
        ↓
Reject
        ↓
Refund rejected

No refund should be processed when the request is rejected.

🔐 Security

The application uses parameterized SQL queries to safely handle user input.

Example:

cur.execute(
    """
    SELECT order_id
    FROM orders
    WHERE order_id = %s
    """,
    (order_id,),
)

Sensitive configuration is stored in environment variables.

🚧 Future Improvements
PostgreSQL-backed LangGraph checkpointing
Authentication and role-based access
Customer history
Refund status tracking
Automated tests
Logging and monitoring
Docker support
Production deployment


👩‍💻 Author

Rutuja Gholap

Built as a GenAI project demonstrating:

LLM + LangGraph + LangChain Tools + PostgreSQL + Human-in-the-Loop + Streamlit
