# ShopBot AI — MCP-powered E-commerce Support Agent

ShopBot AI is an e-commerce support chatbot I built to explore how far you can push LLMs when they’re connected to real systems like databases and retrieval pipelines.

Instead of relying only on prompt-based answers, the bot can actually:
- check real orders stored in MySQL
- search a knowledge base using embeddings (FAISS)
- decide when it should use tools vs when it should just answer normally

The idea was simple:  
**a chatbot that doesn’t hallucinate when it matters (like order status).**

🔗 Live demo: https://shopbot-ai-os4z.onrender.com

---

## Why I built this

Most chatbot demos feel impressive at first, but break down quickly when you ask:

- “Where is my order?”
- “What exactly is your refund policy?”
- “Is this product in stock?”

They usually respond confidently… even when they shouldn’t.

I wanted to build something closer to how a real support system should behave:
- if it’s factual → query a database
- if it’s semantic → search knowledge base
- otherwise → let the model respond normally

This pushed me into combining RAG, tool calling, and routing logic in one system.

---

## How it works
User message
↓
Flask API
↓
Gemini decides intent (route query)
↓
MCP tool layer
├── MySQL tool → order / customer data
└── FAISS tool → FAQ / policy retrieval
↓
↓
Final response to user

---

## Key design choices (and why I made them)

### MCP instead of direct function calls
I used MCP because I didn’t want tool logic mixed directly into the LLM layer. It keeps things modular, so adding a new tool later doesn’t require rewriting the whole routing logic.

---

### FAISS instead of a hosted vector DB
I went with FAISS mainly because I wanted everything to run locally without extra infrastructure costs. It keeps the project self-contained and easier to demonstrate.

---

### Gemini for routing
Gemini is only used to decide what kind of question this is, not to store any “truth.” That separation was intentional to reduce hallucination risk.

---

### Flask instead of FastAPI
This started as a prototype, so Flask was simply faster to iterate with. I prioritized building the system over framework perfection.

---

## What I learned from building this

- Tool use matters more than prompt engineering for real-world reliability
- RAG alone isn’t enough unless retrieval is well scoped
- A simple routing layer improves accuracy more than expected
- Most “AI chatbot problems” are actually system design problems
