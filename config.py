import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', '3306'))
    user: str = os.getenv('DB_USER', 'root')
    password: str = os.getenv('DB_PASSWORD', '')
    name: str = os.getenv('DB_NAME', 'aaitech_inventory')

@dataclass
class SlackConfig:
    webhook_url: Optional[str] = os.getenv('SLACK_WEBHOOK_URL')
    channel: str = os.getenv('SLACK_CHANNEL', '#inventory-alerts')
    username: str = os.getenv('SLACK_USERNAME', 'Inventory Bot')

@dataclass
class EmailConfig:
    smtp_server: str = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port: int = int(os.getenv('SMTP_PORT', '587'))
    username: str = os.getenv('EMAIL_USERNAME', '')
    password: str = os.getenv('EMAIL_PASSWORD', '')
    from_email: str = os.getenv('FROM_EMAIL', '')
    to_email: str = os.getenv('TO_EMAIL', '')

def get_db_config_dict():
    """Convert DatabaseConfig to dict for mysql.connector"""
    c = DatabaseConfig()
    return {
        "host": c.host,
        "port": c.port,
        "user": c.user,
        "password": c.password,
        "database": c.name
    }
