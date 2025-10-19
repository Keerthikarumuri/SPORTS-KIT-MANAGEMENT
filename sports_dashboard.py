import sqlite3
from datetime import datetime

# Connect to database (it will be created if not exists)
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

# ---------------- FUNCTIONS ---------------- #
def add_kit():
    name = input("Enter kit name: ").strip()
    total = int(input("Enter total quantity: "))
    try:
        cur.execute("INSERT INTO kits (name, total, available) VALUES (?, ?, ?)", (name, total, total))
        conn.commit()
        print(f"✅ {name} added successfully!\n")
    except sqlite3.IntegrityError:
        print("⚠️ Kit already exists!\n")

def issue_kit():
    user = input("Enter user name: ").strip()
    kit_name = input("Enter kit name: ").strip()

    cur.execute("SELECT available FROM kits WHERE name=?", (kit_name,))
    row = cur.fetchone()

    if row and row[0] > 0:
        cur.execute("UPDATE kits SET available = available - 1 WHERE name=?", (kit_name,))
        cur.execute("INSERT INTO transactions (user, kit_name, action) VALUES (?, ?, ?)",
                    (user, kit_name, "issued"))
        conn.commit()
        print(f"✅ {kit_name} issued to {user}\n")
    else:
        print("❌ Kit not available or does not exist!\n")

def return_kit():
    user = input("Enter user name: ").strip()
    kit_name = input("Enter kit name: ").strip()
    condition = input("Enter condition (good/wornout/lost): ").strip().lower()

    fine = 0
    if condition == "lost":
        fine = 200
        cur.execute("UPDATE kits SET lost = lost + 1 WHERE name=?", (kit_name,))
    elif condition == "wornout":
        fine = 100
        cur.execute("UPDATE kits SET wornout = wornout + 1 WHERE name=?", (kit_name,))
    elif condition == "good":
        cur.execute("UPDATE kits SET available = available + 1 WHERE name=?", (kit_name,))
    else:
        print("⚠️ Invalid condition. Enter good/wornout/lost.")
        return

    cur.execute("INSERT INTO transactions (user, kit_name, action, fine) VALUES (?, ?, ?, ?)",
                (user, kit_name, "returned", fine))
    conn.commit()
    print(f"✅ {kit_name} returned by {user} | Fine ₹{fine}\n")

def show_inventory():
    print("\n📦 INVENTORY:")
    cur.execute("SELECT * FROM kits")
    rows = cur.fetchall()
    if rows:
        print("{:<5} {:<15} {:<10} {:<10} {:<10} {:<10}".format("ID", "Name", "Total", "Avail", "Lost", "Wornout"))
        for r in rows:
            print("{:<5} {:<15} {:<10} {:<10} {:<10} {:<10}".format(r[0], r[1], r[2], r[3], r[4], r[5]))
    else:
        print("No kits available.\n")

def show_transactions():
    print("\n🧾 TRANSACTIONS:")
    cur.execute("SELECT * FROM transactions ORDER BY date DESC")
    rows = cur.fetchall()
    if rows:
        print("{:<5} {:<10} {:<15} {:<10} {:<10} {:<20}".format("ID", "User", "Kit", "Action", "Fine", "Date"))
        for r in rows:
            print("{:<5} {:<10} {:<15} {:<10} {:<10} {:<20}".format(r[0], r[1], r[2], r[3], r[4], r[5]))
    else:
        print("No transactions yet.\n")

# ---------------- MAIN MENU ---------------- #
def main():
    while True:
        print("\n🎯 SPORTS KIT MANAGEMENT SYSTEM")
        print("1. Add Kit")
        print("2. Issue Kit")
        print("3. Return Kit")
        print("4. View Inventory")
        print("5. View Transactions")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            add_kit()
        elif choice == "2":
            issue_kit()
        elif choice == "3":
            return_kit()
        elif choice == "4":
            show_inventory()
        elif choice == "5":
            show_transactions()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("⚠️ Invalid choice! Try again.")

if __name__ == "__main__":
    main()
