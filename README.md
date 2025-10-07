# 🤖 Mikasa: Conversational AI Financial Manager

Mikasa is an intelligent, multi-channel financial management platform that uses a powerful conversational AI agent (accessible via WhatsApp) with a comprehensive web dashboard for data visualization and personalized financial guidance.

This project is built using an **Agentic AI architecture** powered by LangGraph and Google Gemini models, leveraging the **MERN Stack** (or equivalent) for the web application and **Twilio** for the conversational interface.

***

## ✨ Features

### 1. Agentic Conversational Finance (via WhatsApp)

* **Natural Language Expense/Income Logging:** Users can log credits and debits simply by texting the Mikasa WhatsApp number (e.g., "Spent $50 on coffee" or "Got my $1200 salary").
* **Intelligent Intent Routing:** The AI uses a director model to categorize messages into three paths:
    * **`ACTION`:** For logging financial transactions (triggers CRUD operations).
    * **`ADVICE`:** For seeking personalized financial guidance.
    * **`CHATBOT`:** For general queries.
* **Automated CRUD Operations:** The agent extracts transaction details and securely generates/executes SQL queries against the database (via a **Query Evaluator/Optimizer** pipeline).

### 2. Personalized Web Dashboard

* **User Authentication:** Secure sign-up and login on the web platform.
* **Data Visualization:** Comprehensive dashboard displaying:
    * Investment and Savings Records.
    * Categorized Spending Breakdown.
    * Weekly, Monthly, and Annual Financial Trend Analysis.
    * Predictive modeling for future expenditure and savings.

### 3. Data-Driven AI Advisor (Personalized Guidance)

* **Delayed Activation:** The dedicated AI advisor only **activates after 500 financial entries** are logged, ensuring advice is highly personalized and data-backed.
* **Policy and Investment Guidance:** Provides customized, expert-level recommendations on financial policies, investment opportunities, and saving strategies based on the user's observed spending habits and a curated knowledge base.

***

## 🛠️ Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **AI/Orchestration** | Google Gemini (2.5 Flash), LangGraph, LangChain | Core intelligence, intent routing, and state management. |
| **Backend** | Python (Flask/FastAPI), SQLITE/PostgreSQL | Handles webhooks, API calls, and runs the AI pipeline. |
| **Frontend** | MERN Stack (React, Node.js, Express, MongoDB) | User authentication and interactive analytics dashboard. |
| **Messaging** | Twilio API | Connects the AI agent to the WhatsApp interface. |

***

## 🚀 Setup and Installation

### Prerequisites

* Python (3.9+)
* Node.js and npm (for the MERN stack frontend)
* A Twilio account (for the WhatsApp integration)
* An API key for Google Gemini (`GEMINI_API_KEY`)

### Backend (Python/Agent)

1.  **Clone the repository:**
    ```bash
    git clone [Your-Repo-Link] mikasa
    cd mikasa/backend
    ```
2.  **Set up the virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```
3.  **Configure environment variables:**
    Create a `.env` file in the `backend` directory with your keys:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    # TWILIO_ACCOUNT_SID="YOUR_TWILIO_SID"
    # TWILIO_AUTH_TOKEN="YOUR_TWILIO_TOKEN"
    ```
4.  **Run the Flask application:**
    ```bash
    python backend.py
    ```

### Frontend (MERN Dashboard)

*(Instructions for setting up the separate MERN stack frontend application go here)*

### Connecting the Chatbot (Twilio & Ngrok)

1.  **Expose your local server:** Use **Ngrok** (or a similar tool) to create a public URL for your Flask app (default port is `5000`):
    ```bash
    ngrok http 5000
    ```
2.  **Configure Twilio:** Set the Twilio Sandbox webhook to your Ngrok URL:
    * `[Ngrok-URL]/whatsapp` (e.g., `https://abcdef12345.ngrok.io/whatsapp`)
3.  **Start chatting!** Send a message to your configured Twilio WhatsApp number to begin interacting with Mikasa.

***

***