from typing import Dict, List
from datetime import datetime, timedelta
import uuid

class OrderService:
    def __init__(self):
        self.orders = {}  # In-memory storage for demo
    
    def create_purchase_order(self, low_stock_items: List[Dict]) -> Dict:
        """
        Create a purchase order for low stock items
        """
        order_id = f"PO-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Calculate quantities needed (restock to 20 units)
        items = []
        total_amount = 0
        
        for item in low_stock_items:
            current_qty = item['quantity']
            needed_qty = max(20 - current_qty, 10)  # At least 10 units
            
            # Mock pricing based on item type
            unit_price = self._get_unit_price(item['product_name'])
            item_total = needed_qty * unit_price
            total_amount += item_total
            
            items.append({
                'item_id': item['item_id'],
                'product_name': item['product_name'],
                'current_quantity': current_qty,
                'order_quantity': needed_qty,
                'unit_price': unit_price,
                'total': item_total,
                'location': item['location']
            })
        
        # Calculate delivery date (7-14 days)
        delivery_date = datetime.now() + timedelta(days=10)
        
        order = {
            'order_id': order_id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'delivery_date': delivery_date.strftime('%Y-%m-%d'),
            'status': 'pending',
            'items': items,
            'total_amount': total_amount,
            'supplier_email': 'supplier@techcorp.com',
            'delivery_address': 'AIITECH Warehouse, Berlin, Germany'
        }
        
        # Store order
        self.orders[order_id] = order
        
        return order
    
    def _get_unit_price(self, product_name: str) -> float:
        """Mock pricing based on product type."""
        name_lower = product_name.lower()
        
        if 'laptop' in name_lower or 'macbook' in name_lower:
            return 1200.0
        elif 'iphone' in name_lower or 'samsung' in name_lower:
            return 800.0
        elif 'ipad' in name_lower or 'tablet' in name_lower:
            return 500.0
        elif 'mouse' in name_lower or 'keyboard' in name_lower:
            return 50.0
        elif 'charger' in name_lower:
            return 30.0
        elif 'headphone' in name_lower or 'airpod' in name_lower:
            return 150.0
        else:
            return 100.0  # Default price
    
    def send_order_to_supplier(self, order: Dict) -> Dict:
        """
        Send order confirmation to supplier
        """
        # In a real implementation, this would send an email to the supplier
        # For now, we'll just return success
        
        return {
            "status": "success",
            "message": f"Order {order['order_id']} sent to supplier",
            "supplier_email": order['supplier_email'],
            "total_amount": order['total_amount']
        }
    
    def list_orders(self, status: str = None) -> List[Dict]:
        """
        List all orders, optionally filtered by status
        """
        if status:
            return [order for order in self.orders.values() if order['status'] == status]
        return list(self.orders.values())
    
    def get_order_status(self, order_id: str) -> Dict:
        """
        Get status of a specific order
        """
        if order_id in self.orders:
            return {
                "order_id": order_id,
                "status": self.orders[order_id]['status'],
                "delivery_date": self.orders[order_id]['delivery_date'],
                "total_amount": self.orders[order_id]['total_amount']
            }
        return {"error": f"Order {order_id} not found"}
    
    def update_order_status(self, order_id: str, new_status: str) -> Dict:
        """
        Update order status
        """
        if order_id in self.orders:
            self.orders[order_id]['status'] = new_status
            return {
                "status": "success",
                "message": f"Order {order_id} status updated to {new_status}"
            }
        return {"error": f"Order {order_id} not found"}