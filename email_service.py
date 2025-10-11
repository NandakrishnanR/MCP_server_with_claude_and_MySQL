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
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.config.username, self.config.password)
                server.sendmail(self.config.from_email, to_email, message.as_string())
            
            return {"status": "success", "message": f"Email sent to {to_email}"}
            
        except Exception as e:
            return {"error": f"Failed to send email: {str(e)}"}
    
    def _company_signature(self) -> str:
        """Professional company signature block."""
        return f"""
        <table style=\"margin-top:20px;border-left:4px solid #2E86AB;padding-left:12px;font-family:Arial,sans-serif;\">
            <tr><td style=\"font-weight:bold;font-size:14px;\">AIITECH Ops</td></tr>
            <tr><td style=\"color:#555;\">Inventory & Onboarding Automation</td></tr>
            <tr><td style=\"color:#555;\">Email: {self.config.from_email}</td></tr>
        </table>
        """

    def _render_low_stock_section(self, low_stock_items: List[Dict]) -> str:
        # For intern welcome emails, do not include inventory table.
        return ""

    def send_intern_welcome_email(
        self,
        intern_name: str,
        to_email: str,
        city: str,
        pickup_location: str,
        pickup_date: str,
        role_info: Optional[str] = None,
        supervisor_name: Optional[str] = None,
        office_address: Optional[str] = None,
        map_link: Optional[str] = None,
        low_stock_items: Optional[List[Dict]] = None,
    ) -> Dict:
        """Send a professional onboarding email to the new intern with pickup details.

        Optionally includes a low-stock section if shortages exist.
        """
        links_html = """
        <ul style=\"line-height:1.6\">
            <li><a href=\"https://intranet.example.com/handbook\">Company Handbook</a></li>
            <li><a href=\"https://intranet.example.com/security\">Security & Compliance</a></li>
            <li><a href=\"https://intranet.example.com/it/vpn\">VPN & Accounts Setup</a></li>
            <li><a href=\"https://intranet.example.com/helpdesk\">IT Helpdesk</a></li>
        </ul>
        """

        low_stock_section = self._render_low_stock_section(low_stock_items or [])

        body = f"""
        <html>
        <body style=\"font-family:Arial,sans-serif\">
            <p>Dear {intern_name},</p>
            <p style=\"font-size:15px\">Welcome to <strong>AIITECH</strong>! We are excited to have you join us in {city}. Below are your first‑day essentials and useful links to get started.</p>

            {f'<p><strong>Role:</strong> {role_info}</p>' if role_info else ''}
            {f'<p><strong>Supervisor:</strong> {supervisor_name}</p>' if supervisor_name else ''}
            {f'<p><strong>Office:</strong> {office_address} (<a href="{map_link}">Map</a>)</p>' if office_address else ''}

            <h3 style=\"margin-top:24px\">🎒 Equipment Pickup</h3>
            <p>Please collect your laptop and accessories from <strong>{pickup_location}</strong> on <strong>{pickup_date}</strong>. Bring a valid ID for verification.</p>

            <h3>📚 Useful Links</h3>
            {links_html}

            {self._company_signature()}
        </body>
        </html>
        """

        return self.send_email(
            to_email=to_email,
            subject=f"Welcome to AIITECH, {intern_name}!",
            body=body,
            is_html=True,
        )

    def send_low_stock_alert(self, low_stock_items: List[Dict]) -> Dict:
        """
        Send professional Excel-style low stock alert email
        """
        if not low_stock_items:
            return {"status": "no_alert", "message": "No low stock items"}
        
        # Group by location for better analysis
        location_groups = {}
        for item in low_stock_items:
            location = item['location']
            if location not in location_groups:
                location_groups[location] = []
            location_groups[location].append(item)
        
        # Create professional Excel-style HTML email
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #2E86AB; color: white; padding: 15px; border-radius: 5px; }}
                .summary {{ background-color: #F8F9FA; padding: 15px; border-left: 4px solid #DC3545; margin: 20px 0; }}
                .location-section {{ margin: 20px 0; }}
                .location-header {{ background-color: #6C757D; color: white; padding: 10px; font-weight: bold; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th {{ background-color: #E9ECEF; padding: 12px; text-align: left; border: 1px solid #DEE2E6; }}
                td {{ padding: 10px; border: 1px solid #DEE2E6; }}
                .critical {{ background-color: #F8D7DA; color: #721C24; font-weight: bold; }}
                .warning {{ background-color: #FFF3CD; color: #856404; }}
                .recommendation {{ background-color: #D1ECF1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>📊 Inventory Stock Analysis Report</h2>
                <p>Generated: {self._get_current_time()}</p>
            </div>
            
            <div class="summary">
                <h3>🚨 Executive Summary</h3>
                <p><strong>{len(low_stock_items)} items</strong> require immediate attention across <strong>{len(location_groups)} locations</strong>.</p>
                <p><strong>Critical Action Required:</strong> Stock replenishment needed to prevent stockouts.</p>
            </div>
        """
        
        # Add location-specific analysis
        for location, items in location_groups.items():
            critical_items = [item for item in items if item['quantity'] <= 3]
            warning_items = [item for item in items if item['quantity'] > 3]
            
            html_body += f"""
            <div class="location-section">
                <div class="location-header">📍 {location} - {len(items)} Items Requiring Attention</div>
                <table>
                    <tr>
                        <th>Item ID</th>
                        <th>Product Name</th>
                        <th>Current Stock</th>
                        <th>Priority</th>
                        <th>Recommended Action</th>
                    </tr>
            """
            
            # Add critical items (red highlighting)
            for item in critical_items:
                html_body += f"""
                    <tr class="critical">
                        <td>{item['item_id']}</td>
                        <td>{item['product_name']}</td>
                        <td>{item['quantity']}</td>
                        <td>🔴 CRITICAL</td>
                        <td>Immediate restock required</td>
                    </tr>
                """
            
            # Add warning items (yellow highlighting)
            for item in warning_items:
                html_body += f"""
                    <tr class="warning">
                        <td>{item['item_id']}</td>
                        <td>{item['product_name']}</td>
                        <td>{item['quantity']}</td>
                        <td>🟡 WARNING</td>
                        <td>Plan restock within 1 week</td>
                    </tr>
                """
            
            html_body += """
                </table>
            </div>
            """
        
        # Add recommendations
        html_body += f"""
            <div class="recommendation">
                <h3>💡 Strategic Recommendations</h3>
                <ul>
                    <li><strong>Priority Locations:</strong> Focus on {', '.join(location_groups.keys())} for immediate restocking</li>
                    <li><strong>Critical Items:</strong> {len([item for item in low_stock_items if item['quantity'] <= 3])} items need immediate attention</li>
                    <li><strong>Vendor Coordination:</strong> Contact suppliers for bulk orders to reduce costs</li>
                    <li><strong>Inventory Planning:</strong> Consider increasing safety stock levels for high-demand items</li>
                </ul>
            </div>
            
            <p><em>This report was generated automatically by the Inventory Management System.</em></p>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=self.config.to_email,
            subject=f"📊 Inventory Stock Analysis - {len(low_stock_items)} Items Requiring Attention",
            body=html_body,
            is_html=True
        )
    
    def _get_current_time(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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
