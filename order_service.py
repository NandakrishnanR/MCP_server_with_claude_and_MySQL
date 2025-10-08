import json
from datetime import datetime, timedelta
from typing import Dict, List
from config import EmailConfig

class OrderService:
    def __init__(self):
        self.email_config = EmailConfig()
        self.orders_file = "orders.json"
        self.suppliers_file = "suppliers.json"
    
    def load_orders(self) -> List[Dict]:
        """Load existing orders from file"""
        try:
            with open(self.orders_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_orders(self, orders: List[Dict]):
        """Save orders to file"""
        with open(self.orders_file, 'w') as f:
            json.dump(orders, f, indent=2)
    
    def load_suppliers(self) -> Dict:
        """Load supplier information"""
        try:
            with open(self.suppliers_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default suppliers - you can customize these
            default_suppliers = {
                "LAP": {
                    "name": "Tech Supplier Inc",
                    "email": "orders@techsupplier.com",
                    "min_order": 10,
                    "delivery_days": 7,
                    "unit_price": 800.00
                },
                "MOB": {
                    "name": "Mobile Distributors",
                    "email": "purchase@mobiledist.com", 
                    "min_order": 5,
                    "delivery_days": 5,
                    "unit_price": 400.00
                },
                "TAB": {
                    "name": "Tablet Solutions",
                    "email": "orders@tabletsolutions.com",
                    "min_order": 8,
                    "delivery_days": 6,
                    "unit_price": 300.00
                },
                "ACC": {
                    "name": "Accessory World",
                    "email": "buy@accessoryworld.com",
                    "min_order": 20,
                    "delivery_days": 3,
                    "unit_price": 25.00
                }
            }
            self.save_suppliers(default_suppliers)
            return default_suppliers
    
    def save_suppliers(self, suppliers: Dict):
        """Save supplier information"""
        with open(self.suppliers_file, 'w') as f:
            json.dump(suppliers, f, indent=2)
    
    def get_supplier_for_item(self, item_id: str) -> Dict:
        """Get supplier info for an item based on item ID prefix"""
        suppliers = self.load_suppliers()
        item_type = item_id.split('-')[0]  # LAP, MOB, TAB, ACC
        return suppliers.get(item_type, {
            "name": "Generic Supplier",
            "email": "orders@genericsupplier.com",
            "min_order": 10,
            "delivery_days": 7,
            "unit_price": 100.00
        })
    
    def create_purchase_order(self, low_stock_items: List[Dict]) -> Dict:
        """Create purchase order for low stock items"""
        if not low_stock_items:
            return {"error": "No items to order"}
        
        order_id = f"PO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        order_items = []
        total_amount = 0
        
        for item in low_stock_items:
            supplier = self.get_supplier_for_item(item['item_id'])
            
            # Calculate reorder quantity (minimum order or 2x current stock)
            min_order = supplier['min_order']
            reorder_qty = max(min_order, item['quantity'] * 2)
            
            unit_price = supplier['unit_price']
            item_total = reorder_qty * unit_price
            total_amount += item_total
            
            order_items.append({
                "item_id": item['item_id'],
                "product_name": item['product_name'],
                "location": item['location'],
                "current_quantity": item['quantity'],
                "reorder_quantity": reorder_qty,
                "unit_price": unit_price,
                "total_price": item_total,
                "supplier": supplier['name'],
                "delivery_days": supplier['delivery_days']
            })
        
        # Calculate delivery date
        max_delivery_days = max([item['delivery_days'] for item in order_items])
        delivery_date = datetime.now() + timedelta(days=max_delivery_days)
        
        order = {
            "order_id": order_id,
            "date": datetime.now().isoformat(),
            "delivery_date": delivery_date.isoformat(),
            "status": "pending",
            "total_amount": total_amount,
            "items": order_items,
            "supplier_email": order_items[0]['supplier'] if order_items else "orders@supplier.com"
        }
        
        # Save order
        orders = self.load_orders()
        orders.append(order)
        self.save_orders(orders)
        
        return order
    
    def send_order_to_supplier(self, order: Dict) -> Dict:
        """Send purchase order to supplier via email"""
        from email_service import EmailService
        email_service = EmailService()
        
        # Create email body
        html_body = f"""
        <html>
        <body>
            <h2>📦 Purchase Order #{order['order_id']}</h2>
            <p><strong>Date:</strong> {order['date'][:10]}</p>
            <p><strong>Delivery Date:</strong> {order['delivery_date'][:10]}</p>
            <p><strong>Total Amount:</strong> ${order['total_amount']:.2f}</p>
            
            <h3>Items Ordered:</h3>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f2f2f2;">
                    <th>Item ID</th>
                    <th>Product Name</th>
                    <th>Location</th>
                    <th>Current Stock</th>
                    <th>Reorder Qty</th>
                    <th>Unit Price</th>
                    <th>Total</th>
                </tr>
        """
        
        for item in order['items']:
            html_body += f"""
                <tr>
                    <td>{item['item_id']}</td>
                    <td>{item['product_name']}</td>
                    <td>{item['location']}</td>
                    <td>{item['current_quantity']}</td>
                    <td>{item['reorder_quantity']}</td>
                    <td>${item['unit_price']:.2f}</td>
                    <td>${item['total_price']:.2f}</td>
                </tr>
            """
        
        html_body += """
            </table>
            <p><em>Please confirm receipt and provide tracking information.</em></p>
        </body>
        </html>
        """
        
        # Send email
        result = email_service.send_email(
            to_email=order['supplier_email'],
            subject=f"📦 Purchase Order #{order['order_id']} - ${order['total_amount']:.2f}",
            body=html_body,
            is_html=True
        )
        
        return result
    
    def get_order_status(self, order_id: str) -> Dict:
        """Get status of a specific order"""
        orders = self.load_orders()
        for order in orders:
            if order['order_id'] == order_id:
                return order
        return {"error": "Order not found"}
    
    def list_orders(self, status: str = None) -> List[Dict]:
        """List all orders, optionally filtered by status"""
        orders = self.load_orders()
        if status:
            return [order for order in orders if order['status'] == status]
        return orders
    
    def update_order_status(self, order_id: str, new_status: str) -> Dict:
        """Update order status (pending, confirmed, shipped, delivered)"""
        orders = self.load_orders()
        for order in orders:
            if order['order_id'] == order_id:
                order['status'] = new_status
                order['updated_at'] = datetime.now().isoformat()
                self.save_orders(orders)
                return {"status": "success", "message": f"Order {order_id} updated to {new_status}"}
        return {"error": "Order not found"}
