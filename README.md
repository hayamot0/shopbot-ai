# ShopBot AI — MCP-Powered Customer Support Agent

A domain-specific AI customer support agent for e-commerce, built with Python and Flask. ShopBot connects a large language model directly to a live MySQL database and a RAG knowledge base via a custom MCP server — giving it real-time access to order data and product information without hallucinating.

🟢 **Live Demo:** [https://shopbot-ai-os4z.onrender.com](https://shopbot-ai-os4z.onrender.com)

> ⚠️ **Note:** The app is hosted on Render's free tier and may take **30–60 seconds to load on first visit** (cold start). Please be patient.
> If the bot does not reply to your message, the Gemini API free quota (20 requests/day) has been reached and will reset the following day.

---

## What It Does

ShopBot handles two types of customer queries intelligently:

- **Order tracking** — looks up real order status, tracking numbers, and shipping dates from a live MySQL database
- **Product & policy questions** — searches a RAG knowledge base covering FAQs, return policy, shipping info, and product catalog

The LLM classifies each incoming message and routes it to the right tool automatically. If neither tool is needed, it answers directly.

---

## Architecture

```
Browser → Flask API → Gemini 2.5 Flash (classifier)
                    ↓
              MCP Server
              ├── Tool 1: check_order_status   → MySQL Database
              └── Tool 2: search_knowledge_base → FAISS Vector Store (RAG)
```

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `check_order_status` | Queries MySQL for order status, tracking number, and shipping date by order ID or customer email |
| `search_knowledge_base` | Performs semantic search over the FAISS vector store to answer product, policy, and FAQ questions |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| LLM | Gemini 2.5 Flash (google-genai SDK) |
| MCP Server | FastMCP (stdio transport) |
| RAG Pipeline | LangChain + FAISS + gemini-embedding-001 |
| Backend | Flask (async orchestration) |
| Database | MySQL |
| Frontend | HTML / CSS / JavaScript |
| Deployment | Render.com |

---

## Project Structure

```
shopbot-ai/
├── rag.py                        ← RAG pipeline (FAISS index loader)
├── mcp/shopbot_server.py         ← MCP server with 2 tools
├── flask_app/
│   ├── app.py                    ← Flask API + MCP client + Gemini calls
│   └── templates/index.html      ← Chat UI
├── knowledge_base/               ← faq.txt, return_policy.txt, shipping_info.txt, products.txt
├── faiss_db/                     ← FAISS vector index
└── Procfile                      ← Render deployment config
```

---

## Local Setup

### Prerequisites
- Python 3.10+
- MySQL running locally
- Google API key (Gemini)

### Installation

```bash
git clone https://github.com/hayamot0/shopbot-ai.git
cd shopbot-ai
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```
GOOGLE_API_KEY=your_google_api_key_here
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=shopbot
```

### Database Setup

```sql
CREATE DATABASE shopbot;

CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    product VARCHAR(100),
    status VARCHAR(50),
    order_date DATE,
    tracking_number VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

### Run

```bash
python flask_app/app.py
```

Visit `http://localhost:5000`

---

## Key Design Decisions

- **stdio transport over SSE** — chosen for simplicity and portfolio demonstration; SSE would be used for production multi-client deployments
- **Gemini over OpenAI** — used due to regional payment gateway limitations; the architecture is LLM-agnostic and can be swapped to any provider
- **FAISS over hosted vector DB** — local vector store keeps the project self-contained with zero additional infrastructure cost
- **Async event loop isolation** — each Flask request spawns its own event loop to avoid conflicts between Flask's sync context and the async MCP client

---

## Use Cases This Architecture Covers

This project serves as a reference implementation for:

- AI customer support agents for e-commerce businesses
- Domain-specific MCP servers with database tool integration
- RAG pipelines for product and policy knowledge bases
- Flask + async MCP client orchestration patterns

---

## License

MIT License — see [LICENSE](./LICENSE) file for details.
