# 🧠 Conversational AI Analytics Engine!
### Conversational Analytics on Microsoft SQL Server  
*Built with love by Pratik &mdash; README authored by a Senior AI Engineer at Google.*

---

## 🚀 Why this project matters
Modern teams drown in data yet starve for insights.  **SQL‑GPT Chatbot** turns natural‑language questions into *production‑grade* T‑SQL, validates every statement with an additional AI safety net, and streams results back in a beautiful, tabulated format.  
No more context‑switching between BI tools, no more brittle saved queries—just ask, and get answers.

---

## ✨ Key capabilities
| Capability | What it means for you |
|------------|-----------------------|
| **Natural‑language → T‑SQL** | GPT‑4‑class model translates any business question into optimized SQL Server syntax (`TOP`, bracketed identifiers, etc.). |
| **Dual‑layer safety** | 1️⃣ Static heuristics (balanced parentheses, keyword checks)  +  2️⃣ *AI‑powered* validator that rejects UPDATE/DELETE/DDL. |
| **Autonomous fallback** | If validation fails, the bot automatically substitutes a harmless `SELECT TOP 5 *` so you’re never blocked. |
| **Resilient DB connector** | Connection tested up‑front; granular error handling for time‑outs, missing tables, syntax errors. |
| **Rich CLI UX** | Results printed with `tabulate`, numeric summaries auto‑generated, and actionable suggestions offered on failure. |
| **Zero‑trust ready** | All credentials injected via environment variables / `.env`; no secrets hard‑coded. |

---

## 🏗️ Architecture at a glance
```
┌──────────────┐      user query       ┌───────────────┐
│  CLI Prompt  │ ────────────────────► │  GPT (3.5/4)  │
└──────────────┘                       └─────┬─────────┘
        ▲                                   │ SQL draft
        │                       AI syntax   ▼
┌───────┴────────┐  fallback    checker ┌──────────────┐
│  Heuristic     │◄─────────────GPT────►│  Validator   │
│  Guardrails    │                     └─────┬─────────┘
└───────┬────────┘                           │ validated SQL
        │                                    ▼
        │                           ┌────────────────┐
        │     pyodbc                │  SQL Server    │
        └──────────────────────────►│   (T‑SQL)      │
                                    └────────────────┘
```

---

## 🔧 Quick‑start

1. **Clone & cd**
   ```bash
   git clone https://github.com/<your‑handle>/sql-gpt-chatbot.git
   cd sql-gpt-chatbot
   ```

2. **Install deps**
   ```bash
   pip install -r requirements.txt
   # plus the Microsoft ODBC Driver 17 for SQL Server
   ```

3. **Configure environment**
   ```
   OPENAI_API_KEY=sk‑...
   DB_SERVER=localhost,1433
   DB_NAME=SampleDB
   DB_USER=sa
   DB_PASSWORD=dockerStrongPwd123
   ```

4. **Run**
   ```bash
   python main.py
   ```

---

## 🕹️ Usage demo

```text
=== SQL Chatbot with AI-Based SQL Validation ===
What do you want to know about the brands? (type 'exit' to quit): 
> Top 3 brands by market share in California last year
```

The bot prints the generated query, validates it, executes, and shows:

```
+-----------+----------+-------------+
| brand     | state    | percentage  |
+===========+==========+=============+
| Brand A   | CA       | 27.4        |
| Brand B   | CA       | 22.1        |
| Brand C   | CA       | 18.9        |
+-----------+----------+-------------+

Total rows: 3 | Execution time: 0.17 s
```

---

## 🏅 Design highlights (what makes this *Google‑grade*)
* **Idempotent by design** – read‑only guarantees unless explicitly overridden.  
* **Latency‑aware** – network and DB operations are timed; future PRs will add async concurrency.  
* **Extensible schema introspection** – swap in `INFORMATION_SCHEMA` calls to build prompts dynamically.  
* **Cloud‑native friendly** – drop into Docker or Cloud Run with zero code changes.

---

## 📂 Project layout
```
.
├── main.py              # CLI entry‑point
├── sql_utils.py         # Guardrails & validation helpers (future split)
├── requirements.txt
└── README.md
```

---

## 🤝 Contributing
1. **Fork** the repo & create a feature branch.  
2. Ensure `pre‑commit run --all-files` passes (Black, Ruff, isort).  
3. Open a PR describing *why* your change matters—benchmarks > opinions.

---

## 🗺️ Roadmap
- [ ] Dynamic schema discovery & embedding
- [ ] Streaming result sets for large tables
- [ ] Web UI (Next.js + FastAPI) with JWT auth
- [ ] Vector‑based query refinement for follow‑ups

---

## 📜 License
[MIT](LICENSE) – free to use, fork, and improve. If this bot saves you hours, a ⭐️ is appreciated!

---

> *“The best interface is conversation.”*  
> **SQL‑GPT Chatbot** makes that real for your data warehouse.
