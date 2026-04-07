## 🧠 AI Platform Evaluation (Pre-OpenClaw Decision)

Before choosing OpenClaw, we evaluated multiple AI ecosystems based on cost, automation capability, integration depth, and scalability.

---

### 🔹 Claude Agents
- ~75% nonprofit discount
- ~$8 per user/month
- Autonomous capabilities (Bash + GUI interaction)
- File system access
- Computer control (early-stage agent behavior)
- Very large context window (200K → 1M tokens)

🟢 Strong in: reasoning, long-context tasks  
🔴 Weak in: ecosystem integrations & automation pipelines

---

### 🔹 Google Gemini
- ~$5 per user/month
- Deep Google ecosystem integration (Gmail, Docs, etc.)
- Proactive features (daily summaries, reminders)
- CQV (contextual query + vision capabilities)

🟢 Strong in: personal productivity & Google-native workflows  
🔴 Weak in: external automation + agent orchestration

---

### 🔹 Microsoft Copilot Studio (+ Power Automate)
- Deep system integration (Microsoft ecosystem)
- Agents can simulate human interaction (mouse, keyboard, UI navigation)
- Native file access (SharePoint, OneDrive)
- Pricing:
  - $200/month (25,000 credits)
  - Pay-as-you-go: $0.01/credit
- Nonprofit grant:
  - ~$2,000/year Azure credits (can offset usage)

🟢 Strong in: enterprise automation, workflows, persistent agents  
🔴 Weak in: cost predictability, complexity, vendor lock-in

---

### 🔹 ChatGPT (Business – Nonprofit Plan)
- 60–70% discount
- ~$8/user/month (from ~$25)
- Minimum seats: 2 users
- Usage limitations:
  - ~160 messages / 3 hours per account
  - Shared usage across team members
- Issues observed:
  - Rate limits under concurrent usage
  - Session conflicts (multiple users)
  - Potential IP-based restrictions

🟢 Strong in: usability, flexibility, model quality  
🔴 Weak in: concurrency, automation, scalability as a backend system

---

## ⚖️ Key Comparison

| Feature        | ChatGPT                          | Microsoft Copilot |
|----------------|----------------------------------|-------------------|
| Data Access    | Isolated (manual uploads)        | Native integrations |
| Automation     | Chat-first, limited background   | Action-first, 24/7 workflows |
| Agent Identity | Stateless/session-based          | Persistent agent identity |

---

## 🎯 Why OpenClaw

OpenClaw was chosen to:
- Avoid vendor lock-in
- Combine multiple models (best tool per task)
- Handle rate limits via fallback systems
- Enable scalable agent-based workflows
- Maintain cost control using free + hybrid models

This approach provides flexibility similar to enterprise systems, without their cost and constraints.