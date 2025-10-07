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
            "username": self.config.username
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
        Send formatted low stock alert to Slack
        """
        if not low_stock_items:
            return {"status": "no_alert", "message": "No low stock items"}
        
        # Create Slack blocks for rich formatting
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 Low Stock Alert"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{len(low_stock_items)} items* are running low on stock:"
                }
            }
        ]
        
        # Add each low stock item
        for item in low_stock_items[:10]:  # Limit to 10 items
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Item:* {item['item_id']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Product:* {item['product_name']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Location:* {item['location']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Quantity:* {item['quantity']}"
                    }
                ]
            })
        
        if len(low_stock_items) > 10:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"... and {len(low_stock_items) - 10} more items"
                }
            })
        
        return self.send_message("Low Stock Alert", blocks)
    
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
