import requests
import json
from typing import Dict, List, Optional
from config import SlackConfig

class SlackService:
    def __init__(self):
        self.config = SlackConfig()
    
    def send_message(self, text: str, blocks: Optional[List[Dict]] = None) -> Dict:
        """
        Send a message to Slack via webhook
        """
        if not self.config.webhook_url:
            return {"error": "Slack webhook URL not configured"}
        
        payload = {
            "text": text,
            "channel": self.config.channel,
            "username": self.config.username,
            # Ensure @user and <!channel> mentions are linked
            "link_names": 1
        }
        
        if blocks:
            payload["blocks"] = blocks
        
        try:
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return {"status": "success", "message": "Slack message sent"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to send Slack message: {str(e)}"}
    
    def send_low_stock_alert(self, low_stock_items: List[Dict]) -> Dict:
        """
        Send colleague-friendly low stock alert to Slack with specific assignments
        """
        if not low_stock_items:
            return {"status": "no_alert", "message": "No low stock items"}
        
        # Group by location for better organization
        location_groups = {}
        for item in low_stock_items:
            location = item['location']
            if location not in location_groups:
                location_groups[location] = []
            location_groups[location].append(item)
        
        # Create colleague-friendly message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Stock Alert - Immediate Action Required"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hey team! 👋 We have *{len(low_stock_items)} items* running low across *{len(location_groups)} locations*. Need your help to prevent stockouts!"
                }
            }
        ]
        
        # Add location-specific assignments
        team_members = ["@sarah", "@mike", "@priya", "@alex", "@jenny"]
        vendor_contacts = ["@tom", "@lisa", "@david", "@maria", "@kevin"]
        
        for i, (location, items) in enumerate(location_groups.items()):
            critical_items = [item for item in items if item['quantity'] <= 3]
            warning_items = [item for item in items if item['quantity'] > 3]
            
            # Assign team member for stock management
            stock_manager = team_members[i % len(team_members)]
            vendor_manager = vendor_contacts[i % len(vendor_contacts)]
            
            # Create location text
            location_text = f"📍 *{location} Location* - {len(items)} items need attention\n"
            
            if critical_items:
                location_text += f"🔴 *CRITICAL ({len(critical_items)} items):*\n"
                for item in critical_items[:3]:  # Show max 3 critical items
                    location_text += f"• {item['product_name']} ({item['item_id']}) - *{item['quantity']} left*\n"
                if len(critical_items) > 3:
                    location_text += f"• ... and {len(critical_items) - 3} more critical items\n"
            
            if warning_items:
                location_text += f"🟡 *WARNING ({len(warning_items)} items):*\n"
                for item in warning_items[:2]:  # Show max 2 warning items
                    location_text += f"• {item['product_name']} ({item['item_id']}) - {item['quantity']} left\n"
                if len(warning_items) > 2:
                    location_text += f"• ... and {len(warning_items) - 2} more warning items\n"
            
            # Add assignments
            location_text += f"\n👤 *{stock_manager}* - Please check stock levels and update inventory\n"
            location_text += f"📞 *{vendor_manager}* - Contact vendors for: "
            
            # List specific products for vendor contact
            vendor_products = []
            for item in critical_items[:2]:  # Max 2 products for vendor contact
                vendor_products.append(f"{item['product_name']} ({item['item_id']})")
            if len(critical_items) > 2:
                vendor_products.append(f"and {len(critical_items) - 2} more models")
            
            location_text += ", ".join(vendor_products)
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": location_text
                }
            })
        
        # Add summary and next steps
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "📋 *Next Steps:*\n• Check physical inventory\n• Contact suppliers\n• Update stock levels\n• Plan restocking schedule"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Report generated at {self._get_current_time()} | Inventory Management System"
                    }
                ]
            }
        ])
        
        return self.send_message("🚨 URGENT: Stock Alert - Action Required!", blocks)
    
    def _get_current_time(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def send_daily_summary(self, summary_data: Dict) -> Dict:
        """
        Send daily inventory summary to Slack
        """
        text = f"📊 Daily Inventory Summary\n\n{summary_data.get('summary', 'No summary available')}"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Daily Inventory Summary"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Items:* {summary_data.get('total_items', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Low Stock Items:* {summary_data.get('low_stock_count', 0)}"
                    }
                ]
            }
        ]
        
        if summary_data.get('top_locations'):
            location_text = "\n".join([
                f"• {loc['location']}: {loc['total_quantity']} items"
                for loc in summary_data['top_locations']
            ])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Top Locations:*\n{location_text}"
                }
            })
        
        return self.send_message(text, blocks)

    def send_welcome_message(self, intern_name: str, city: str, pickup_location: str, pickup_date: str, intern_slack_mention: str | None = None, notify_channel: bool = True, role_info: str | None = None, supervisor_name: str | None = None, office_address: str | None = None, map_link: str | None = None) -> Dict:
        """Send a professional corporate welcome message to Slack."""
        
        # Professional welcome message
        text = f"Welcome {intern_name} to AIITECH! 🎉"
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"👋 Welcome {intern_name}!"}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Dear Team,\n\nPlease join me in welcoming *{intern_name}* to our {city} office!\n\n{f'**Role:** {role_info}\n' if role_info else ''}{f'**Supervisor:** {supervisor_name}\n' if supervisor_name else ''}**Equipment Pickup:** {pickup_location} on {pickup_date}\n{f'**Office:** {office_address}\n' if office_address else ''}\nWe're excited to have you join our team!"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📧 **Microsoft Account Setup:** Please contact @maria for Microsoft account configuration and VPN access.\n\n📞 **IT Support:** helpdesk@aiitech.com | +49 30 1234 5678"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Best regards,\n**AIITECH Operations Team**\nManaging Director: Dr. Anna Schmidt\nEmail: operations@aiitech.com"
                    }
                ]
            }
        ]
        
        return self.send_message(text, blocks)

    def send_inventory_update_message(self, low_stock_items: List[Dict], assignees: Optional[List[str]] = None, notify_channel: bool = False) -> Dict:
        """Send a professional inventory update message."""
        if not low_stock_items:
            return {"status": "no_updates"}

        # Group by location
        location_groups: Dict[str, List[Dict]] = {}
        for item in low_stock_items:
            location_groups.setdefault(item["location"], []).append(item)

        text = f"📊 Inventory Alert: {len(low_stock_items)} items require attention"
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📊 Inventory Stock Alert"}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"**Executive Summary:**\n• {len(low_stock_items)} items require immediate attention\n• {len(location_groups)} locations affected\n• Critical action required to prevent stockouts"
                }
            }
        ]

        # Add location-specific details
        for location, items in location_groups.items():
            critical_items = [item for item in items if int(item.get("quantity", 0)) <= 3]
            warning_items = [item for item in items if int(item.get("quantity", 0)) > 3]
            
            location_text = f"**📍 {location} Location**\n"
            
            if critical_items:
                location_text += f"🔴 **Critical ({len(critical_items)} items):**\n"
                for item in critical_items[:3]:
                    location_text += f"• {item['product_name']} ({item['item_id']}) - {item['quantity']} units\n"
                if len(critical_items) > 3:
                    location_text += f"• ... and {len(critical_items) - 3} more critical items\n"
            
            if warning_items:
                location_text += f"🟡 **Warning ({len(warning_items)} items):**\n"
                for item in warning_items[:2]:
                    location_text += f"• {item['product_name']} ({item['item_id']}) - {item['quantity']} units\n"
                if len(warning_items) > 2:
                    location_text += f"• ... and {len(warning_items) - 2} more warning items\n"

            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": location_text}
            })

        # Add action items
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "**📋 Action Required:**\n• Contact suppliers for immediate restocking\n• Update inventory levels\n• Plan bulk orders for cost reduction\n• Review safety stock levels"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Report generated: {self._get_current_time()} | AIITECH Inventory Management System"
                    }
                ]
            }
        ])

        return self.send_message(text, blocks)
