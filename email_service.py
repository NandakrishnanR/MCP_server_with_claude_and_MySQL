import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from config import EmailConfig

class EmailService:
    def __init__(self):
        self.config = EmailConfig()
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> Dict:
        """
        Send email via SMTP - basic email sending
        """
        if not self.config.username or not self.config.password:
            return {"error": "Email credentials not configured"}
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.config.from_email
            message["To"] = to_email
            
            # Add body
            if is_html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.config.username, self.config.password)
                server.sendmail(self.config.from_email, to_email, message.as_string())
            
            return {"status": "success", "message": f"Email sent to {to_email}"}
            
        except Exception as e:
            return {"error": f"Failed to send email: {str(e)}"}
    
    def send_low_stock_alert(self, low_stock_items: List[Dict]) -> Dict:
        """
        Send formatted low stock alert email
        """
        if not low_stock_items:
            return {"status": "no_alert", "message": "No low stock items"}
        
        # Create HTML email body
        html_body = f"""
        <html>
        <body>
            <h2>🚨 Low Stock Alert</h2>
            <p><strong>{len(low_stock_items)} items</strong> are running low on stock:</p>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f2f2f2;">
                    <th>Item ID</th>
                    <th>Product Name</th>
                    <th>Location</th>
                    <th>Current Quantity</th>
                </tr>
        """
        
        for item in low_stock_items:
            html_body += f"""
                <tr>
                    <td>{item['item_id']}</td>
                    <td>{item['product_name']}</td>
                    <td>{item['location']}</td>
                    <td style="color: red; font-weight: bold;">{item['quantity']}</td>
                </tr>
            """
        
        html_body += """
            </table>
            <p><em>Please check inventory and consider reordering.</em></p>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=self.config.to_email,
            subject="🚨 Low Stock Alert - Immediate Action Required",
            body=html_body,
            is_html=True
        )
    
    def send_daily_summary(self, summary_data: Dict) -> Dict:
        """
        Send daily inventory summary email
        """
        html_body = f"""
        <html>
        <body>
            <h2>📊 Daily Inventory Summary</h2>
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
                <h3>Key Metrics</h3>
                <ul>
                    <li><strong>Total Items:</strong> {summary_data.get('total_items', 0)}</li>
                    <li><strong>Low Stock Items:</strong> {summary_data.get('low_stock_count', 0)}</li>
                </ul>
            </div>
        """
        
        if summary_data.get('top_locations'):
            html_body += """
                <h3>Top Locations by Quantity</h3>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #f2f2f2;">
                        <th>Location</th>
                        <th>Total Quantity</th>
                    </tr>
            """
            
            for loc in summary_data['top_locations']:
                html_body += f"""
                    <tr>
                        <td>{loc['location']}</td>
                        <td>{loc['total_quantity']}</td>
                    </tr>
                """
            
            html_body += "</table>"
        
        html_body += """
            <p><em>Generated automatically by Inventory MCP Server</em></p>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=self.config.to_email,
            subject="📊 Daily Inventory Summary",
            body=html_body,
            is_html=True
        )
    
    def send_order_confirmation(self, order_details: Dict) -> Dict:
        """
        Send order confirmation email to supplier
        """
        html_body = f"""
        <html>
        <body>
            <h2>📦 Purchase Order Confirmation</h2>
            <p><strong>Order ID:</strong> {order_details.get('order_id', 'N/A')}</p>
            <p><strong>Date:</strong> {order_details.get('date', 'N/A')}</p>
            <p><strong>Delivery Address:</strong> {order_details.get('delivery_address', 'N/A')}</p>
            
            <h3>Items Ordered:</h3>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f2f2f2;">
                    <th>Item ID</th>
                    <th>Product Name</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Total</th>
                </tr>
        """
        
        total_amount = 0
        for item in order_details.get('items', []):
            item_total = item['quantity'] * item.get('unit_price', 0)
            total_amount += item_total
            html_body += f"""
                <tr>
                    <td>{item['item_id']}</td>
                    <td>{item['product_name']}</td>
                    <td>{item['quantity']}</td>
                    <td>${item.get('unit_price', 0):.2f}</td>
                    <td>${item_total:.2f}</td>
                </tr>
            """
        
        html_body += f"""
            </table>
            <h3>Total Amount: ${total_amount:.2f}</h3>
            <p><em>Please confirm delivery date and send tracking information.</em></p>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=order_details.get('supplier_email', self.config.to_email),
            subject=f"📦 Purchase Order #{order_details.get('order_id', 'N/A')}",
            body=html_body,
            is_html=True
        )
