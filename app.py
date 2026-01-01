import streamlit as st
import time
import json
import re
import math
import random
from typing import List, Dict

# --- CONFIGURATION & DATABASES ---

# 1. MENU CATALOG
MENU_CATALOG = {
    "fried chicken":              {"id": "LPH-001", "price": 15.00, "desc": "Signature spiced fried chicken (Bucket)."},
    "curly fries":                {"id": "LPH-002", "price": 4.50,  "desc": "Twisted potato fries seasoned with paprika."},
    "pizza (pepperoni, small)":   {"id": "LPH-003A", "price": 8.00,  "desc": "Small 8 inch pizza with pepperoni."},
    "pizza (pepperoni, medium)":  {"id": "LPH-003B", "price": 12.00, "desc": "Medium Pepperoni pizza."},
    "pizza (margherita, small)":  {"id": "LPH-003D", "price": 7.50,  "desc": "Small vegetarian pizza."},
    "coffee":                     {"id": "LPH-004", "price": 3.00,  "desc": "Hot, black brewed coffee."},
    "blue candy":                 {"id": "LPH-005", "price": 50.00, "desc": "Crystal blue rock candy. 99.1% pure."},
    "coke":                       {"id": "LPH-006", "price": 2.50,  "desc": "Carbonated sweet cola soda."},
    "chicken wings (6 pcs)":      {"id": "LPH-007", "price": 8.00,  "desc": "Crispy fried wings."},
    "spicy fried chicken":        {"id": "LPH-010", "price": 16.00, "desc": "Extra-hot crispy fried chicken bucket."},
    "grilled chicken":            {"id": "LPH-011", "price": 13.00, "desc": "Healthy charcoal grilled chicken."},
    "family chicken combo":       {"id": "LPH-022", "price": 28.00, "desc": "8 pieces of chicken, sides and drinks."}
}

# 2. INVENTORY (Initialize in Session State to persist across reruns)
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        "LPH-001": 50, "LPH-002": 100, "LPH-003A": 10, "LPH-003B": 10,
        "LPH-003D": 10, "LPH-004": 20, "LPH-005": 5, "LPH-006": 2, "LPH-007": 40,
        "LPH-010": 15, "LPH-011": 25, "LPH-022": 10
    }

# 3. DRIVER FLEET
DRIVER_FLEET = [
    {"id": "D1", "name": "Gustavo", "vehicle": "Station Wagon", "capacity": "large", "status": "idle", "loc": (5, 5)},
    {"id": "D2", "name": "Jesse",   "vehicle": "Scooter",       "capacity": "small", "status": "idle", "loc": (2, 2)},
    {"id": "D3", "name": "Mike",    "vehicle": "Armored Truck", "capacity": "huge",  "status": "idle", "loc": (10, 10)},
    {"id": "D4", "name": "Walter",  "vehicle": "Sedan",         "capacity": "medium","status": "idle", "loc": (20, 20)}
]

# --- CLASSES (RAG & AGENTS) ---

class VectorDatabase:
    def __init__(self, menu_catalog):
        self.semantic_map = {
            "spicy": ["spicy fried chicken", "buffalo sauce"],
            "hot":   ["spicy fried chicken", "coffee"],
            "crunchy": ["fried chicken", "curly fries"],
            "veg":     ["pizza (margherita, small)"],
            "sweet":   ["blue candy", "coke"],
            "healthy": ["grilled chicken"],
            "group": ["family chicken combo"]
        }
        self.catalog = menu_catalog

    def search(self, user_query: str) -> List[Dict]:
        query_words = user_query.lower().split()
        scores = {name: 0.0 for name in self.catalog.keys()}
        for name, details in self.catalog.items():
            doc_text = (name + " " + details['desc']).lower()
            for word in query_words:
                if word in doc_text: scores[name] += 1.0
            for word in query_words:
                for concept, related_items in self.semantic_map.items():
                    if word in concept and name in related_items: scores[name] += 3.0
        sorted_names = sorted(scores, key=scores.get, reverse=True)
        results = []
        if scores[sorted_names[0]] > 0:
            top_name = sorted_names[0]
            results.append({"name": top_name, "desc": self.catalog[top_name]['desc'], "score": scores[top_name]})
        return results

class AIModel:
    def generate(self, prompt: str) -> str:
        # Mock Logic 
        prompt_lower = prompt.lower()
        items = []
        def check(keywords, cat_name):
            for k in keywords:
                if k in prompt_lower:
                    qty = 1
                    match = re.search(rf'(\d+)\s.*{k}', prompt_lower)
                    if match: qty = int(match.group(1))
                    items.append({"item": cat_name, "qty": qty})
                    return

        check(["fried chicken", "bucket"], "fried chicken")
        check(["curly fries"], "curly fries")
        check(["pepperoni"], "pizza (pepperoni, small)")
        check(["margherita"], "pizza (margherita, small)")
        check(["coffee"], "coffee")
        check(["candy", "blue"], "blue candy")
        check(["coke", "cola"], "coke")
        check(["wings"], "chicken wings (6 pcs)")
        check(["spicy"], "spicy fried chicken")
        check(["grilled"], "grilled chicken")
        check(["family"], "family chicken combo")

        addr = None
        # Simple address extraction
        if "address is" in prompt_lower:
             addr = prompt_lower.split("address is")[1].strip()
        elif "lane" in prompt_lower or "street" in prompt_lower:
             addr = "308 Negra Arroyo Lane" # Mock fallback

        return json.dumps({"intent": "order", "items": items, "address": addr})

class DispatchAgent:
    def __init__(self):
        self.restaurant_loc = (0, 0)

    def _get_delivery_coords(self, address):
        seed = sum(ord(c) for c in address)
        random.seed(seed)
        x = random.randint(1, 30)
        y = random.randint(1, 30)
        random.seed()
        return (x, y)

    def _calculate_distance(self, loc1, loc2):
        return math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)

    def _estimate_order_size(self, items):
        total_items = sum(i['qty'] for i in items)
        if total_items > 20: return "huge"
        if total_items > 5: return "large"
        if total_items > 2: return "medium"
        return "small"

    def assign(self, address, items):
        target_loc = self._get_delivery_coords(address)
        order_size = self._estimate_order_size(items)
        best_driver = None
        min_dist = float('inf')
        size_rank = {"small": 1, "medium": 2, "large": 3, "huge": 4}

        for driver in DRIVER_FLEET:
            driver_cap = size_rank.get(driver['capacity'], 1)
            order_cap = size_rank.get(order_size, 1)
            if driver_cap < order_cap: continue 
            
            dist = self._calculate_distance(driver['loc'], self.restaurant_loc)
            if dist < min_dist:
                min_dist = dist
                best_driver = driver

        if best_driver:
            travel_dist = self._calculate_distance(self.restaurant_loc, target_loc)
            total_time = (min_dist + travel_dist) * 2
            return {"driver": best_driver, "eta": int(total_time), "status": "success", "dest": target_loc}
        return {"status": "failed"}

# --- STREAMLIT UI LAYOUT ---

st.set_page_config(page_title="Los Pollos Hermanos AI", page_icon="🍗", layout="wide")

# Initialize Session State Variables
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'cart' not in st.session_state: st.session_state.cart = {"items": [], "address": None}
if 'order_status' not in st.session_state: st.session_state.order_status = "taking_order" 

# Instances
ai = AIModel()
rag = VectorDatabase(MENU_CATALOG)
dispatch = DispatchAgent()

# --- SIDEBAR (Inventory & Debug) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/a/ae/Los_Pollos_Hermanos_logo.png", width=150)
    st.title("Manager Dashboard")
    st.markdown("### 📦 Warehouse Live Stock")
    
    # Display Inventory
    stock_data = []
    for item_name, details in MENU_CATALOG.items():
        stock_count = st.session_state.inventory.get(details['id'], 0)
        stock_data.append({"Item": item_name, "Stock": stock_count})
    st.dataframe(stock_data, height=300)

    st.markdown("### 🚚 Fleet Status")
    for d in DRIVER_FLEET:
        st.caption(f"**{d['name']}** ({d['vehicle']}) - {d['status'].upper()}")

# --- MAIN CHAT INTERFACE ---

st.title("🍗 Agentic Delivery System")
st.caption("Powered by Multi-Agent Logic: Parsing -> Inventory -> Dispatch")

# Display Chat History
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- PROCESSING LOGIC ---

def process_order(user_input):
    # 1. Parse Input
    raw_json = ai.generate(user_input)
    data = json.loads(raw_json)
    
    response_text = ""
    
    # 2. Add items to Cart
    if data['items']:
        added_items = []
        for item in data['items']:
            # Check if item exists in menu
            if item['item'] in MENU_CATALOG:
                found = False
                for cart_item in st.session_state.cart['items']:
                    if cart_item['item'] == item['item']:
                        cart_item['qty'] += item['qty']
                        found = True
                        break
                if not found:
                    st.session_state.cart['items'].append(item)
                added_items.append(f"{item['qty']}x {item['item']}")
        if added_items:
            response_text += f"Added to cart: {', '.join(added_items)}. "
    
    # 3. RAG Search (Fallback)
    elif not data['items'] and "yes" not in user_input.lower():
        results = rag.search(user_input)
        if results:
            top = results[0]
            response_text += f"I didn't find that exactly, but we have **{top['name']}** ({top['desc']}). Should I add that? "
        else:
            response_text += "I didn't catch that. You can ask for fried chicken, pizza, or sides. "

    # 4. Address (Auto-detect)
    if data['address']:
        st.session_state.cart['address'] = data['address']
        response_text += f"Updated address to: {data['address']}. "

    # 5. Check for Finish
    if "confirm" in user_input.lower() or "place order" in user_input.lower():
        if not st.session_state.cart['items']:
            response_text = "Your cart is empty!"
        elif not st.session_state.cart['address']:
            response_text = "I still need a delivery address! You can type it in the box below."
        else:
            finalize_order()
            return # Stop processing
            
    if not response_text:
        response_text = "Anything else?"

    # Append to chat
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": response_text})

def finalize_order():
    st.session_state.order_status = "processing"
    cart = st.session_state.cart
    
    # A. Inventory Check
    receipt_lines = []
    total = 0
    missing = []
    
    for item in cart['items']:
        key = item['item']
        qty = item['qty']
        meta = MENU_CATALOG[key]
        stock_id = meta['id']
        
        if st.session_state.inventory[stock_id] >= qty:
            st.session_state.inventory[stock_id] -= qty
            cost = meta['price'] * qty
            total += cost
            receipt_lines.append(f"{qty}x {key} (${cost:.2f})")
        else:
            missing.append(key)

    if missing:
        msg = f"⚠️ Order Failed! Out of stock for: {', '.join(missing)}"
        st.session_state.chat_history.append({"role": "assistant", "content": msg})
        st.session_state.order_status = "taking_order"
        return

    # B. Dispatch
    delivery = dispatch.assign(cart['address'], cart['items'])
    
    if delivery['status'] == "success":
        msg = f"""
        **✅ ORDER CONFIRMED!**
        
        **Receipt:**
        {chr(10).join(['- ' + l for l in receipt_lines])}
        
        **Total:** ${total:.2f}
        
        **Dispatch Details:**
        - Driver: {delivery['driver']['name']} 
        - Vehicle: {delivery['driver']['vehicle']}
        - ETA: {delivery['eta']} minutes
        """
        st.session_state.chat_history.append({"role": "assistant", "content": msg})
        st.balloons()
        # Reset
        st.session_state.cart = {"items": [], "address": None}
    else:
        st.session_state.chat_history.append({"role": "assistant", "content": "⚠️ No drivers available for this order size!"})

# --- INPUT AREA ---

user_input = st.chat_input("Ex: I want a bucket of fried chicken and a coke...")

if user_input:
    process_order(user_input)
    st.rerun()

# --- CURRENT CART DISPLAY (Bottom) ---
if st.session_state.cart['items']:
    with st.expander("🛒 Current Cart", expanded=True):
        # 1. Show Items
        st.markdown("### Your Items")
        for i in st.session_state.cart['items']:
            st.write(f"- {i['qty']}x {i['item']}")
        
        st.divider()

        # 2. Manual Address Entry (The Fix)
        st.markdown("### Delivery Details")
        
        # This input box acts as a fallback. If AI missed the address, you can type it here.
        manual_address = st.text_input(
            "📍 Delivery Address", 
            value=st.session_state.cart['address'] if st.session_state.cart['address'] else "",
            placeholder="Type address here if AI didn't catch it..."
        )
        
        # Update session state immediately if user types in box
        if manual_address:
            st.session_state.cart['address'] = manual_address

        st.divider()

        # 3. Confirm Button
        # Only show the button if an address is present
        if st.session_state.cart['address']:
            if st.button("✅ Confirm & Place Order", type="primary"):
                process_order("confirm order")
                st.rerun()
        else:
            st.warning("⚠️ Please enter an address above to checkout.")
