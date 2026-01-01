<img width="1911" height="949" alt="image" src="https://github.com/user-attachments/assets/ad40bd94-db2e-468d-9291-da48473a89c4" />



```streamlit run app.py```

# 🍗 Los Pollos Hermanos – Agentic AI Delivery System

An **agent-based food delivery simulation** built using **Streamlit**, demonstrating how multiple AI-inspired agents collaborate to process natural language food orders, manage inventory, and intelligently assign delivery drivers.

This project focuses on **agent orchestration and intelligent system design**, making it ideal for **AI, Intelligent Systems, and Multi-Agent coursework or demos**.

---

## 🚀 Features

### 🤖 Agentic Architecture

The system is composed of multiple cooperating agents:

1. **Order Parsing Agent**
   - Extracts food items, quantities, and delivery address from natural language.
   - Uses rule-based NLP and regex (mock LLM behavior).

2. **RAG (Retrieval-Augmented Generation) Agent**
   - Suggests menu items when user input is vague or ambiguous.
   - Uses semantic keyword mappings (e.g., *spicy*, *veg*, *healthy*).

3. **Inventory Management Agent**
   - Tracks live stock using Streamlit session state.
   - Prevents orders if items are out of stock.

4. **Dispatch Agent**
   - Assigns the best delivery driver based on:
     - Order size
     - Driver vehicle capacity
     - Distance from restaurant
   - Calculates estimated delivery time (ETA).

---

## 🖥️ User Interface

- Chat-based conversational ordering
- Live cart preview
- Manual address entry fallback
- **Manager Dashboard (Sidebar)**:
  - Real-time inventory view
  - Driver fleet status

---

## 📦 Menu Highlights

- Fried Chicken (Regular & Spicy)
- Pizza (Pepperoni, Margherita)
- Curly Fries
- Chicken Wings
- Family Combos
- Drinks & “Blue Candy”

---

## 🚚 Driver Fleet Simulation

Each driver includes:
- Vehicle type
- Capacity (`small`, `medium`, `large`, `huge`)
- Simulated location
- Intelligent assignment logic

---

## 🛠️ Tech Stack

- **Python 3**
- **Streamlit**
- Built-in libraries:
  - `json`
  - `re`
  - `math`
  - `random`

No external ML libraries are required.

---


---
### 1️⃣ Install Dependencies

```bash
pip install streamlit
```
### ▶️ How to Run

```bash
streamlit run app.py
```

### Example Prompt
```bash
I want a bucket of spicy fried chicken and 2 cokes
```
```bash
My address is 221B Baker Street
```

```confirm order```

## 🔮 Future Improvements

- Integrate a real Large Language Model (LLM) for advanced intent extraction
- Add delivery route visualization using maps
- Persist inventory and orders using a database (PostgreSQL / MongoDB)
- Implement user authentication and order history
- Add payment workflow simulation
- Improve driver dispatch using optimization algorithms
- Add analytics dashboard for order insights

## 👤 Author

**Mohammed Abdul Razzack**  
📍 London, United Kingdom  

- GitHub: https://github.com/Abdulrazzack  
- LinkedIn: https://www.linkedin.com/in/abdulrazzack  

AI & Software Engineering enthusiast with interests in  
**Intelligent Systems, Multi-Agent Architectures, and Applied Machine Learning**.

## ⚠️ Disclaimer

This project is created **strictly for educational and demonstration purposes**.

All characters, brand names, and references to **Los Pollos Hermanos** are fictional
and inspired by popular media. No affiliation or endorsement is intended.

The system does not represent a real delivery service.

