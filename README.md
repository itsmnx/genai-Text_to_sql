# GenialQuery - AI-Powered Text-to-SQL

**Convert natural language to optimized SQL queries using NLP + Machine Learning + Groq AI**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.2-green.svg)](https://flask.palletsprojects.com/)
[![Groq](https://img.shields.io/badge/Groq-API-orange.svg)](https://console.groq.com/)


---

##  Features

-  **Text-to-SQL**: Convert natural language to SQL queries
-  **ML Model**: Trained on 1,205 examples with Random Forest
-  **Groq AI**: Advanced LLM for complex queries (Mixtral/LLaMA)
-  **Dynamic Schema**: Auto-discovers tables from CSV files
-  **Guest Mode**: Use without registration
  
---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask 2.3.2 |
| **ML Model** | scikit-learn (Random Forest) |
| **AI/LLM** | Groq API (Llama 3.3) |
| **NLP** | Custom regex + keyword matching |
| **Data Processing** | pandas |
| **Authentication** | Flask-JWT-Extended |
| **Frontend** | HTML5, CSS3, Vanilla JS |

---
## 🔄 Query Processing Pipeline

```mermaid
flowchart TD
    A[User Query] --> B[NLP Processing]
    B --> C{ML Model Check}
    C -->|High Confidence| D[SQL Generation]
    C -->|Low Confidence| E[Groq AI]
    E --> D
    D --> F[Query Optimization]
    F --> G[Security Check]
    G --> H[Explanation Generation]
    H --> I[Response]
    
    style A fill:#6C63FF,color:#fff
    style B fill:#4A90D9,color:#fff
    style C fill:#F5A623,color:#fff
    style E fill:#FF6B6B,color:#fff
    style D fill:#4CAF50,color:#fff
    style F fill:#4CAF50,color:#fff
    style G fill:#4CAF50,color:#fff
    style H fill:#4CAF50,color:#fff
    style I fill:#6C63FF,color:#fff
```
---
