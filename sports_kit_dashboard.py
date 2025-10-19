import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to SQLite database
conn = sqlite3.connect("kits.db")
cur = conn.cursor()

# Create tables if not exist
cur.execute('''CREATE TABLE IF NOT EXISTS kits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    total INT,
    available INT,
    lost INT DEFAULT 0,
    wornout INT DEFAULT 0
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    kit_name TEXT,
    action TEXT,
    fine INT DEFAULT 0,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')
conn.commit()

# Streamlit UI
st.set_page_config(page_title="Sports Kits Dashboard", page_icon="🏏", layout="wide")
st.title("🏏 Sports Kits Management Dashboard")

menu = ["Add Kit", "Issue Kit", "Return Kit", "Inventory", "Transactions", "Visualization"]
choice = st.sidebar.radio("Select an Option", menu)

# ---------------------- 1. Add Kit ----------------------
if choice == "Add Kit":
    st.subheader("➕ Add New Kit")
    name = st.text_input("Kit Name")
    total = st.number_input("Total Quantity", min_value=1, step=1)
    if st.button("Add Kit"):
        try:
            cur.execute("INSERT INTO kits (name, total, available) VALUES (?, ?, ?)", (name, total, total))
            conn.commit()
            st.success(f"✅ {name} added successfully!")
        except sqlite3.IntegrityError:
            st.error("⚠️ Kit already exists!")

# ---------------------- 2. Issue Kit ----------------------
elif choice == "Issue Kit":
    st.subheader("🏃 Issue a Kit")
    user = st.text_input("User Name")
    kit_name = st.text_input("Kit Name")
    if st.button("Issue Kit"):
        cur.execute("SELECT available FROM kits WHERE name=?", (kit_name,))
        row = cur.fetchone()
        if row and row[0] > 0:
            cur.execute("UPDATE kits SET available = available - 1 WHERE name=?", (kit_name,))
            cur.execute("INSERT INTO transactions (user, kit_name, action) VALUES (?, ?, ?)",
                        (user, kit_name, "issued"))
            conn.commit()
            st.success(f"✅ {kit_name} issued to {user}")
        else:
            st.error("❌ Kit not available or doesn't exist!")

# ---------------------- 3. Return Kit ----------------------
elif choice == "Return Kit":
    st.subheader("🔙 Return a Kit")
    user = st.text_input("User Name")
    kit_name = st.text_input("Kit Name")
    condition = st.selectbox("Condition", ["good", "wornout", "lost"])

    if st.button("Return Kit"):
        fine = 0
        if condition == "lost":
            fine = 200
            cur.execute("UPDATE kits SET lost = lost + 1 WHERE name=?", (kit_name,))
        elif condition == "wornout":
            fine = 100
            cur.execute("UPDATE kits SET wornout = wornout + 1 WHERE name=?", (kit_name,))
        else:
            cur.execute("UPDATE kits SET available = available + 1 WHERE name=?", (kit_name,))

        cur.execute("INSERT INTO transactions (user, kit_name, action, fine) VALUES (?, ?, ?, ?)",
                    (user, kit_name, "returned", fine))
        conn.commit()
        st.success(f"✅ {kit_name} returned by {user} | Fine ₹{fine}")

# ---------------------- 4. Inventory ----------------------
elif choice == "Inventory":
    st.subheader("📦 Current Inventory")
    df = pd.read_sql("SELECT * FROM kits", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No kits found. Add some kits first!")

# ---------------------- 5. Transactions ----------------------
elif choice == "Transactions":
    st.subheader("🧾 All Transactions")
    df = pd.read_sql("SELECT * FROM transactions ORDER BY date DESC", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No transactions yet!")

# ---------------------- 6. Visualization ----------------------
elif choice == "Visualization":
    st.subheader("📊 Kits Overview")
    df = pd.read_sql("SELECT name, available, lost, wornout FROM kits", conn)
    if not df.empty:
        df.set_index("name")[["available", "lost", "wornout"]].plot(kind="bar")
        plt.title("Kits Summary")
        st.pyplot(plt)
    else:
        st.warning("No data available for visualization.")

# Footer
st.markdown("---")
st.caption("© 2025 Sports Kit Management Dashboard | Built with ❤️ using Streamlit & SQLite")
