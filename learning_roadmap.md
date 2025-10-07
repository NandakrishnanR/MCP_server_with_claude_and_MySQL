# MCP Development Learning Roadmap

## Phase 1: Understanding Your Current Project (Week 1-2)

### 1.1 Study the Codebase
- [ ] **Read `main.py`** - Understand FastMCP structure and tool decorators
- [ ] **Analyze `database.sql`** - Learn the data model and relationships
- [ ] **Test each tool** - Use MCP Inspector to call tools directly
- [ ] **Modify existing tools** - Add error handling, input validation

### 1.2 Hands-on Exercises
```bash
# Exercise 1: Test current tools
uv run mcp dev main.py
# In Inspector: Call list_inventory, add_inventory, check_stock

# Exercise 2: Add logging
import logging
logging.basicConfig(level=logging.INFO)

# Exercise 3: Add input validation
def add_inventory(item_id: str, product_name: str, location: str, quantity: int) -> dict:
    if quantity <= 0:
        return {"error": "Quantity must be positive"}
    # ... rest of function
```

### 1.3 Key Concepts to Master
- **MCP Protocol**: How Claude communicates with your server
- **FastMCP Decorators**: `@mcp.tool()` pattern
- **Database Connections**: Connection management and SQL operations
- **Error Handling**: Graceful failure and user feedback

## Phase 2: Advanced MCP Features (Week 3-4)

### 2.1 Resources (Data Exposure)
```python
@mcp.resource("inventory://{location}")
def get_inventory_by_location(location: str) -> str:
    """Get inventory data for specific location as JSON"""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventory WHERE location = %s", (location,))
    rows = cursor.fetchall()
    conn.close()
    return json.dumps(rows, indent=2)
```

### 2.2 Prompts (Reusable Templates)
```python
@mcp.prompt()
def inventory_report(location: str = None, format: str = "summary") -> str:
    """Generate inventory report with optional location filter"""
    if location:
        data = get_inventory_by_location(location)
        return f"Inventory Report for {location}:\n{data}"
    else:
        data = list_inventory()
        return f"Complete Inventory Report:\n{json.dumps(data, indent=2)}"
```

### 2.3 Configuration Management
```python
import os
from typing import Optional

class Config:
    def __init__(self):
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_user = os.getenv('DB_USER', 'root')
        self.db_password = os.getenv('DB_PASSWORD', '')
        self.db_name = os.getenv('DB_NAME', 'aaitech_inventory')
        
    def get_db_config(self):
        return {
            "host": self.db_host,
            "user": self.db_user,
            "password": self.db_password,
            "database": self.db_name
        }
```

### 2.4 Authentication and Security
```python
import hashlib
import secrets

def verify_api_key(api_key: str) -> bool:
    """Verify API key for secure access"""
    # Implement your authentication logic
    return api_key == os.getenv('MCP_API_KEY')

@mcp.tool()
def secure_add_inventory(api_key: str, item_id: str, product_name: str, 
                        location: str, quantity: int) -> dict:
    """Secure version of add_inventory with API key"""
    if not verify_api_key(api_key):
        return {"error": "Invalid API key"}
    # ... rest of function
```

## Phase 3: External Integrations (Week 5-6)

### 3.1 Calendar Integration (Google Calendar)
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

class CalendarService:
    def __init__(self, credentials_path: str):
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        self.service = build('calendar', 'v3', credentials=self.credentials)
    
    def create_event(self, title: str, start_time: str, end_time: str, 
                    attendees: list = None) -> dict:
        event = {
            'summary': title,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
        }
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        return self.service.events().insert(
            calendarId='primary', body=event
        ).execute()
```

### 3.2 Email Integration (SendGrid)
```python
import sendgrid
from sendgrid.helpers.mail import Mail
import os

class EmailService:
    def __init__(self):
        self.sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
    
    def send_email(self, to_email: str, subject: str, content: str) -> dict:
        message = Mail(
            from_email='noreply@yourcompany.com',
            to_emails=to_email,
            subject=subject,
            html_content=content
        )
        try:
            response = self.sg.send(message)
            return {"status": "sent", "response_code": response.status_code}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
```

### 3.3 Webhook Integration
```python
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

@app.route('/webhook/inventory-update', methods=['POST'])
def inventory_webhook():
    """Handle external inventory updates"""
    data = request.json
    # Process webhook data
    # Update database
    # Send notifications
    return jsonify({"status": "success"})

def run_webhook_server():
    app.run(host='0.0.0.0', port=5000, debug=False)

# Start webhook server in background
webhook_thread = threading.Thread(target=run_webhook_server)
webhook_thread.daemon = True
webhook_thread.start()
```

## Phase 4: Advanced Patterns (Week 7-8)

### 4.1 Caching and Performance
```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiry_seconds=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiry_seconds, json.dumps(result))
            return result
        return wrapper
    return decorator

@mcp.tool()
@cache_result(expiry_seconds=600)  # Cache for 10 minutes
def list_inventory_cached() -> list:
    """Cached version of list_inventory"""
    return list_inventory()
```

### 4.2 Async Operations
```python
import asyncio
import aiohttp
import asyncpg

async def async_database_operation():
    """Example of async database operations"""
    conn = await asyncpg.connect(
        user='user', password='password', database='db', host='localhost'
    )
    rows = await conn.fetch('SELECT * FROM inventory')
    await conn.close()
    return rows

@mcp.tool()
async def async_list_inventory() -> list:
    """Async version of list_inventory"""
    rows = await async_database_operation()
    return [dict(row) for row in rows]
```

### 4.3 Error Handling and Logging
```python
import logging
import traceback
from typing import Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except mysql.connector.Error as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            return {"error": "Database operation failed", "details": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            logger.error(traceback.format_exc())
            return {"error": "An unexpected error occurred", "details": str(e)}
    return wrapper

@mcp.tool()
@handle_errors
def safe_add_inventory(item_id: str, product_name: str, location: str, quantity: int) -> dict:
    """Add inventory with comprehensive error handling"""
    # ... implementation
```

## Phase 5: Production Deployment (Week 9-10)

### 5.1 Environment Configuration
```python
# config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    host: str
    user: str
    password: str
    database: str
    port: int = 3306
    
    @classmethod
    def from_env(cls):
        return cls(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'aaitech_inventory'),
            port=int(os.getenv('DB_PORT', '3306'))
        )

@dataclass
class EmailConfig:
    api_key: str
    from_email: str
    
    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv('SENDGRID_API_KEY', ''),
            from_email=os.getenv('FROM_EMAIL', 'noreply@yourcompany.com')
        )
```

### 5.2 Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "mcp", "run", "main.py"]
```

### 5.3 Monitoring and Health Checks
```python
@mcp.tool()
def health_check() -> dict:
    """Check system health and dependencies"""
    checks = {
        "database": False,
        "redis": False,
        "email_service": False,
        "calendar_service": False
    }
    
    # Check database
    try:
        conn = mysql.connector.connect(**db_config)
        conn.close()
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis
    try:
        redis_client.ping()
        checks["redis"] = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
    
    # Check email service
    try:
        email_service = EmailService()
        # Test email service
        checks["email_service"] = True
    except Exception as e:
        logger.error(f"Email service health check failed: {e}")
    
    return {
        "status": "healthy" if all(checks.values()) else "unhealthy",
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }
```

## Phase 6: Building Your Intern Onboarding System (Week 11-12)

### 6.1 Project Structure
```
intern_onboarding_mcp/
├── main.py                 # Main MCP server
├── config.py              # Configuration management
├── database/
│   ├── schema.sql         # Database schema
│   └── migrations/        # Database migrations
├── services/
│   ├── calendar_service.py
│   ├── email_service.py
│   └── database_service.py
├── tools/
│   ├── intern_tools.py
│   ├── task_tools.py
│   ├── calendar_tools.py
│   └── email_tools.py
├── templates/
│   └── email_templates/
├── tests/
│   └── test_tools.py
├── docker-compose.yml
└── README.md
```

### 6.2 Implementation Steps
1. **Set up project structure** - Create folders and files
2. **Implement database schema** - Create all tables
3. **Build core tools** - Start with intern management
4. **Add external integrations** - Calendar and email
5. **Test thoroughly** - Use MCP Inspector
6. **Deploy to production** - Docker or cloud deployment

### 6.3 Testing Strategy
```python
# tests/test_tools.py
import pytest
from unittest.mock import Mock, patch
from main import add_intern, get_intern

class TestInternTools:
    @patch('main.mysql.connector.connect')
    def test_add_intern_success(self, mock_connect):
        # Mock database connection
        mock_cursor = Mock()
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Test the function
        result = add_intern("INT-001", "John Doe", "john@example.com", 
                          "2024-01-15", "Engineering", "MGR-001")
        
        # Assertions
        assert result["status"] == "success"
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
```

## Resources and Next Steps

### Learning Resources
1. **MCP Documentation**: https://modelcontextprotocol.io/docs
2. **FastMCP Examples**: https://github.com/modelcontextprotocol/python-sdk
3. **Google Calendar API**: https://developers.google.com/calendar
4. **SendGrid API**: https://docs.sendgrid.com/
5. **MySQL Python Connector**: https://dev.mysql.com/doc/connector-python/

### Practice Projects
1. **Extend current inventory system** - Add search, analytics, reporting
2. **Build a simple CRM** - Customer management with MCP
3. **Create a task manager** - Personal productivity tool
4. **Build a notification system** - Multi-channel notifications

### Community and Support
1. **MCP Discord**: Join the community for help and discussions
2. **GitHub Issues**: Report bugs and request features
3. **Stack Overflow**: Tag questions with 'model-context-protocol'

This roadmap will take you from understanding your current project to building sophisticated AI-powered business applications with MCP!
