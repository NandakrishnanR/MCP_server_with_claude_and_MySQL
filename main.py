from mcp.server.fastmcp import FastMCP
import mysql.connector
from typing import List, Dict
from dotenv import load_dotenv
from config import get_db_config_dict
from slack_service import SlackService
from email_service import EmailService
from order_service import OrderService

# Load environment variables
load_dotenv()

mcp = FastMCP(name="inventory_mcp")

# Use centralized config
db_config = get_db_config_dict()
slack_service = SlackService()
email_service = EmailService()
order_service = OrderService()


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


@mcp.tool()
def send_slack_alert(threshold: int = 5) -> Dict:
    """
    Send low stock alert to Slack - automation foundation
    """
    # Get low stock items
    low_stock_items = low_stock(threshold)
    
    if isinstance(low_stock_items, dict) and "error" in low_stock_items:
        return low_stock_items
    
    # Send to Slack
    result = slack_service.send_low_stock_alert(low_stock_items)
    
    return {
        "slack_result": result,
        "items_checked": len(low_stock_items),
        "threshold": threshold
    }


@mcp.tool()
def send_daily_summary_to_slack() -> Dict:
    """
    Send daily inventory summary to Slack - automation foundation
    """
    # Get summary data
    summary_data = inventory_summary()
    
    # Send to Slack
    result = slack_service.send_daily_summary(summary_data)
    
    return {
        "slack_result": result,
        "summary_data": summary_data
    }


@mcp.tool()
def test_slack_connection() -> Dict:
    """
    Test Slack webhook connection - verify integration works
    """
    test_message = "🧪 Test message from Inventory MCP Server"
    result = slack_service.send_message(test_message)
    
    return {
        "test_result": result,
        "message": "Test message sent to Slack"
    }


@mcp.tool()
def send_email_alert(threshold: int = 5) -> Dict:
    """
    Send low stock alert via email - automation foundation
    """
    # Get low stock items
    low_stock_items = low_stock(threshold)
    
    if isinstance(low_stock_items, dict) and "error" in low_stock_items:
        return low_stock_items
    
    # Send email alert
    result = email_service.send_low_stock_alert(low_stock_items)
    
    return {
        "email_result": result,
        "items_checked": len(low_stock_items),
        "threshold": threshold
    }


@mcp.tool()
def send_daily_summary_email() -> Dict:
    """
    Send daily inventory summary via email - automation foundation
    """
    # Get summary data
    summary_data = inventory_summary()
    
    # Send email summary
    result = email_service.send_daily_summary(summary_data)
    
    return {
        "email_result": result,
        "summary_data": summary_data
    }


@mcp.tool()
def test_email_connection() -> Dict:
    """
    Test email SMTP connection - verify integration works
    """
    test_subject = "🧪 Test Email from Inventory MCP Server"
    test_body = """
    <html>
    <body>
        <h2>Test Email</h2>
        <p>This is a test email from your Inventory MCP Server.</p>
        <p><strong>Status:</strong> Email integration is working!</p>
    </body>
    </html>
    """
    
    result = email_service.send_email(
        to_email=email_service.config.to_email,
        subject=test_subject,
        body=test_body,
        is_html=True
    )
    
    return {
        "test_result": result,
        "message": "Test email sent"
    }


@mcp.tool()
def send_combined_alert(threshold: int = 5) -> Dict:
    """
    Send low stock alert to both Slack and Email - full automation
    """
    # Get low stock items
    low_stock_items = low_stock(threshold)
    
    if isinstance(low_stock_items, dict) and "error" in low_stock_items:
        return low_stock_items
    
    # Send to both Slack and Email
    slack_result = slack_service.send_low_stock_alert(low_stock_items)
    email_result = email_service.send_low_stock_alert(low_stock_items)
    
    return {
        "slack_result": slack_result,
        "email_result": email_result,
        "items_checked": len(low_stock_items),
        "threshold": threshold,
        "status": "Combined alert sent to Slack and Email"
    }


@mcp.tool()
def auto_reorder_low_stock(threshold: int = 5) -> Dict:
    """
    Automatically create purchase orders for low stock items - REAL BUSINESS VALUE
    """
    # Get low stock items
    low_stock_items = low_stock(threshold)
    
    if isinstance(low_stock_items, dict) and "error" in low_stock_items:
        return low_stock_items
    
    if not low_stock_items:
        return {"status": "no_action", "message": "No low stock items found"}
    
    # Create purchase order
    order = order_service.create_purchase_order(low_stock_items)
    
    # Send order to supplier
    email_result = order_service.send_order_to_supplier(order)
    
    # Send notification to manager
    notification_result = send_combined_alert(threshold)
    
    return {
        "order_created": order,
        "email_sent": email_result,
        "notifications_sent": notification_result,
        "items_ordered": len(order['items']),
        "total_amount": order['total_amount'],
        "delivery_date": order['delivery_date'][:10]
    }


@mcp.tool()
def list_purchase_orders(status: str = None) -> List[Dict]:
    """
    List all purchase orders, optionally filtered by status
    """
    orders = order_service.list_orders(status)
    return orders


@mcp.tool()
def get_order_status(order_id: str) -> Dict:
    """
    Get status of a specific purchase order
    """
    return order_service.get_order_status(order_id)


@mcp.tool()
def update_order_status(order_id: str, new_status: str) -> Dict:
    """
    Update order status (pending, confirmed, shipped, delivered)
    """
    return order_service.update_order_status(order_id, new_status)


@mcp.tool()
def full_automation_workflow(threshold: int = 5) -> Dict:
    """
    Complete automation: Check stock → Alert → Auto-order → Notify
    This is the MAIN FEATURE that provides real business value
    """
    # Step 1: Check stock levels
    low_stock_items = low_stock(threshold)
    
    if isinstance(low_stock_items, dict) and "error" in low_stock_items:
        return low_stock_items
    
    if not low_stock_items:
        return {
            "status": "all_good",
            "message": "All items are above threshold",
            "items_checked": 0
        }
    
    # Step 2: Send alerts (Slack + Email)
    alert_result = send_combined_alert(threshold)
    
    # Step 3: Auto-create purchase order
    order = order_service.create_purchase_order(low_stock_items)
    
    # Step 4: Send order to supplier
    email_result = order_service.send_order_to_supplier(order)
    
    # Step 5: Return complete workflow result
    return {
        "workflow_status": "completed",
        "alerts_sent": alert_result,
        "order_created": {
            "order_id": order['order_id'],
            "total_amount": order['total_amount'],
            "delivery_date": order['delivery_date'][:10],
            "items_count": len(order['items'])
        },
        "supplier_notified": email_result,
        "summary": f"Created order {order['order_id']} for ${order['total_amount']:.2f}, delivery on {order['delivery_date'][:10]}"
    }


if __name__ == "__main__":
    mcp.run()