import mysql.connector
import re

# MySQL database connection parameters
conn = mysql.connector.connect(
        user='root',
        password="your_password",
        host='localhost',
        database='your_dbname'
)

def get_order_status(order_id: int):
    try:
        cursor = conn.cursor()
        query = ("SELECT status FROM order_tracking WHERE order_id = %s")
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result[0]
        else:
            return "Order ID not found"
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def get_str_from_food_dict(new_food_dict: dict):
    return ", ".join([f"{int(value)} {key}" for key, value in new_food_dict.items()])

def extract_session_id(session_str: str):
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        return match.group(1)
    return None

def insert_order_item(food_items, quantity, order_id):
    try:
        cursor = conn.cursor()
        cursor.callproc("insert_order_item", (food_items, quantity, order_id))
        conn.commit()
        cursor.close()
        return 1
    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")
        conn.rollback()
        return -1

def get_order_total(order_id):
    cursor = conn.cursor()
    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    cursor.close()
    return result

def insert_order_tracking(order_id, status):
    cursor = conn.cursor()
    query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(query, (order_id, status))
    conn.commit()
    cursor.close()

def get_next_order_id():
    cursor = conn.cursor()
    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    cursor.close()
    return 1 if result is None else result + 1

