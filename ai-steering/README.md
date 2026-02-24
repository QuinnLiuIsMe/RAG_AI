# AI RAG Project

A retrieval-augmented generation (RAG) demo built with:

- LangChain
- DashScope Embeddings
- Qwen (ChatTongyi)
- InMemoryVectorStore

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt


## ProjectStructure
│ backend/
│
├── app/
│   ├── agents/
│   │   └── agent.py
│   ├── tools/
│   │   ├── calculator.py
│   │   └── metrics.py
│   ├── main.py
│   └── config.py
│
├── requirements.txt
└── venv


frontend/
└── ai-ops-ui/
    ├── src/
    │   ├── App.jsx
    │   └── components/
    │       └── Chat.jsx

  


