from mcp.server.fastmcp import FastMCP
import mysql.connector
from typing import List, Dict

mcp = FastMCP(name="inventory_mcp")

# MySQL config
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "9446122497",
    "database": "aaitech_inventory"
}


@mcp.tool()
def add_inventory(item_id: str, product_name: str, location: str, quantity: int) -> dict:
    # Input validation
    if quantity <= 0:
        return {"error": "Quantity must be a positive integer"}
    
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
    # Input validation
    if quantity <= 0:
        return {"error": "Quantity must be a positive integer"}
    
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


@mcp.tool()
def low_stock(threshold: int = 5) -> List[Dict]:
    """
    Get items with quantity at or below threshold - foundation for automation alerts
    """
    if threshold < 0:
        return {"error": "Threshold must be >= 0"}
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT item_id, product_name, location, quantity FROM inventory WHERE quantity <= %s ORDER BY quantity ASC",
        (threshold,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


@mcp.tool()
def inventory_summary() -> Dict:
    """
    Generate daily summary for automation - total items, low stock count, top locations
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    # Get total items
    cursor.execute("SELECT COUNT(*) as total_items FROM inventory")
    total_items = cursor.fetchone()['total_items']
    
    # Get low stock count
    cursor.execute("SELECT COUNT(*) as low_stock_count FROM inventory WHERE quantity <= 5")
    low_stock_count = cursor.fetchone()['low_stock_count']
    
    # Get top locations by total quantity
    cursor.execute("""
        SELECT location, SUM(quantity) as total_quantity 
        FROM inventory 
        GROUP BY location 
        ORDER BY total_quantity DESC 
        LIMIT 3
    """)
    top_locations = cursor.fetchall()
    
    conn.close()
    
    return {
        "total_items": total_items,
        "low_stock_count": low_stock_count,
        "top_locations": top_locations,
        "summary": f"Total: {total_items} items, {low_stock_count} low stock, top location: {top_locations[0]['location'] if top_locations else 'N/A'}"
    }


if __name__ == "__main__":