# ShoppingAssitant
An AI-powered shopping assistant that compares products, analyzes reviews, finds trending items, and gives budget-optimized recommendations using ChatGroq and Firecrawl, all inside a modern Streamlit UI.



# 🛍️ AI Shopping Assistant

### Smart Product Comparison • Review Analysis • Budget Optimization

An AI-powered shopping assistant built with **Streamlit + Agno Agents + Groq + Firecrawl**, designed to help users:

* 💼 Optimize shopping within a budget
* 📊 Analyze product reviews with sentiment breakdown
* 🧑‍🎓 Learn what to check before buying
* 🔍 Compare products across platforms
* 🌟 Discover trending deals

---

## 🚀 Features

### 1️⃣ Budget Optimizer

* Enter shopping list
* Set total budget
* Choose optimization priority
* AI suggests best combinations
* Provides structured product breakdown

---

### 2️⃣ Review Sentiment Analysis

* Paste product URL
* Extracts real user reviews
* Classifies:

  * Positive
  * Negative
  * Neutral
* Shows pros, cons & verdict (Buy / Consider / Avoid)

---

### 3️⃣ Smart Buying Guide

* Enter product type
* Get expert-style checklist:

  * Key specs
  * Budget tiers
  * Mistakes to avoid
  * Quick decision checklist

---

### 4️⃣ Product Comparison

* Compare variants across:

  * Amazon
  * Flipkart
  * Reliance Digital
* Returns:

  * Price comparison
  * Key differentiators
  * Best pick recommendation

---

### 5️⃣ Trending Products

* Finds trending products under ₹1000
* Real-time scraping
* Compact, structured results

---

## 🧠 Tech Stack

| Component       | Technology                    |
| --------------- | ----------------------------- |
| Framework       | Streamlit                     |
| Agent Framework | Agno                          |
| LLM             | ChatGroq (openai/gpt-oss-20b) |
| Web Scraping    | Firecrawl                     |
| Search          | DuckDuckGoTools               |
| UI Styling      | Custom CSS                    |
| Environment     | dotenv                        |

---

## 🏗 Architecture Overview

```
User Input
    ↓
Agno Agent
    ↓
ChatGroq Model (gpt-oss-20b)
    ↓
Tools Layer
   ├── DuckDuckGo (URL Discovery)
   └── Firecrawl (Scraping)
    ↓
Structured AI Response
    ↓
Streamlit UI
```

---

## 📂 Project Structure

```
ai-shopping-assistant/
│
├── app.py
├── .env
├── requirements.txt
└── README.md
```

---

## 🔑 Environment Variables

Create a `.env` file:

```
GROQ_API_KEY=your_groq_key
FIRECRAWL_API_KEY=your_firecrawl_key
```

If needed:

```
AGNO_API_KEY=your_agno_key
```

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/ai-shopping-assistant.git
cd ai-shopping-assistant
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Add Environment Variables

Create `.env` and add API keys.

### 4️⃣ Run Application

```bash
streamlit run app.py
```

---

## 📊 Core Agent Configuration

All agents are globally forced to use:

```python
Agent.default_model = ChatGroq(model="openai/gpt-oss-20b")
```

This ensures:

* Consistent model usage
* No hidden model overrides
* Predictable cost & behavior

---

## 🛡 Safety & Optimization

* URL pre-filtering via DuckDuckGo
* Limited Firecrawl pages
* Response length clamped to prevent overflow
* Max product limit per request
* Compact structured output only

---

## 🎯 Use Cases

* Students shopping on a budget
* Tech enthusiasts comparing gadgets
* Smart buyers researching before purchase
* Deal hunters tracking trends
* E-commerce assistants & AI demos

---

## 🌟 Future Improvements

* Price history tracking
* Auto deal alerts
* Wishlist memory
* Multi-region price comparison
* Payment gateway integration
* Affiliate link integration
* Deployment on Streamlit Cloud

---

## 👨‍💻 Author

Built with ❤️ by **Satyajit**
Powered by **Agno Agents + Groq + Firecrawl**

---

## 📜 License

MIT License

---

