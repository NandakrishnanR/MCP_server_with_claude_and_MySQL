from mcp.server.fastmcp import FastMCP
import mysql.connector

mcp = FastMCP(name="inventory_mcp")

# MySQL config
db_config = {
    "host": "localhost",
    "user": "root",  # change to your MySQL username
    "password": "9446122497",  # change to your MySQL password
    "database": "aaitech_inventory"
}


@mcp.tool()
def add_inventory(item_id: str, product_name: str, location: str, quantity: int) -> dict:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inventory (item_id, product_name, location, quantity) VALUES (%s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE quantity = quantity + %s, product_name = VALUES(product_name)",
        (item_id, product_name, location, quantity, quantity)
    )
    conn.commit()
    conn.close()
    return {"message": f"Added {quantity} units of {product_name} ({item_id}) at {location}"}


@mcp.tool()
def remove_inventory(item_id: str, location: str, quantity: int) -> dict:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE inventory SET quantity = quantity - %s WHERE item_id=%s AND location=%s AND quantity >= %s",
        (quantity, item_id, location, quantity)
    )
    conn.commit()
    conn.close()
    return {"message": f"Removed {quantity} units of {item_id} from {location}"}


@mcp.tool()
def check_stock(item_id: str, location: str) -> dict:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT product_name, quantity FROM inventory WHERE item_id=%s AND location=%s",
        (item_id, location)
    )
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "item_id": item_id,
            "location": location,
            "product_name": result[0],
            "quantity": result[1]
        }
    else:
        return {
            "item_id": item_id,
            "location": location,
            "product_name": None,
            "quantity": 0
        }


@mcp.tool()
def list_inventory() -> list:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT item_id, product_name, location, quantity FROM inventory")
    rows = cursor.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    mcp.run()