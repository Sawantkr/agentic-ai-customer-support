<div align="center">

# 🤖 Agentic AI Customer Support

### Intelligent Customer Support System with AI Routing & Human Escalation

<p>
  <a href="https://github.com/Sawantkr/agentic-ai-customer-support">
    <img src="https://img.shields.io/badge/💻%20Source%20Code-GitHub-181717?style=for-the-badge&logo=github" />
  </a>
  <img src="https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Groq-F54A00?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
</p>

<p>
  An AI-powered customer support platform that classifies customer requests,
  routes them to specialized workflows, maintains conversation state,
  and escalates complex cases to human support.
</p>

</div>

---

## ✨ Overview

**Agentic AI Customer Support** is an AI-powered customer support system built around **LangGraph workflows**.

Instead of treating every customer message as a simple chatbot query, the system first determines the customer's intent and then routes the request to a specialized workflow.

The system supports:

- Account-related requests
- Billing-related requests
- Technical support
- General queries
- Human-in-the-loop escalation
- Conversation persistence
- Workflow checkpointing
- REST APIs
- Streamlit-based customer interface
- Automated testing

The project is also designed to integrate with the **Sawantflix** application as its customer-support backend.

---

# 🎯 Key Features

| Feature | Description |
|---|---|
| 🧠 Intent Classification | Identifies the type of customer request |
| 🔀 Intelligent Routing | Sends requests to the appropriate workflow |
| 💳 Billing Workflow | Handles payment and billing-related requests |
| 👤 Account Workflow | Handles account-related requests |
| 🛠️ Technical Workflow | Handles technical support requests |
| 💬 General Workflow | Handles general customer queries |
| 👨‍💻 Human Escalation | Transfers complex cases to human support |
| 🔄 Workflow Resume | Continues the conversation after human intervention |
| 💾 Conversation Persistence | Maintains conversation state |
| 🗄️ SQLite Checkpointing | Stores LangGraph workflow state |
| ⚡ FastAPI | Provides REST API endpoints |
| 🖥️ Streamlit | Provides interactive customer chat UI |
| 🧪 Automated Tests | API, classifier and workflow tests |
| 🐳 Docker | Containerization support |

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │        USER          │
                         │   Customer Message   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      Streamlit       │
                         │     Chat Interface   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │     REST Backend     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      LangGraph       │
                         │   Agentic Workflow   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Intent Classification│
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
                Account          Billing         Technical
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                              General Workflow
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Resolution / Agent   │
                         │      Response        │
                         └──────────┬───────────┘
                                    │
                           ┌────────┴────────┐
                           │                 │
                           ▼                 ▼
                       Resolved       Human Escalation
                                             │
                                             ▼
                                      Human Review
                                             │
                                             ▼
                                      Workflow Resume
