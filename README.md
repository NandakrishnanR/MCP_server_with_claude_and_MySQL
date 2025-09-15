# Inventory Management MCP Server

## What This Project Does

This is a **Model Context Protocol (MCP) server** that connects **Claude Desktop** to your **MySQL database**. It allows you to manage inventory through natural language conversations with Claude.

### Key Components

1. **MCP Server** (`main.py`): Python server that exposes database operations as tools
2. **MySQL Database** (`database.sql`): Stores inventory data with products, locations, and quantities
3. **Claude Desktop Integration**: Tools appear in Claude's interface for natural language queries

## Architecture Deep Dive

### 1. MCP (Model Context Protocol)
- **Purpose**: Standardized way for AI assistants to interact with external systems
- **How it works**: Your server exposes "tools" that Claude can call
- **Transport**: Uses stdio (standard input/output) to communicate with Claude

### 2. FastMCP Framework
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP(name="inventory_mcp")
```
- **FastMCP**: Python library that simplifies MCP server creation
- **Decorators**: `@mcp.tool()` converts functions into callable tools
- **Auto-serialization**: Handles JSON conversion between Claude and your functions

### 3. Database Integration
```python
db_config = {
    "host": "localhost",
    "user": "root", 
    "password": "9446122497",
    "database": "aaitech_inventory"
}
```
- **Connection Management**: Each tool opens/closes its own connection
- **SQL Operations**: Direct MySQL queries for CRUD operations
- **Error Handling**: Basic connection management (can be improved)

### 4. Tool Design Pattern
Each tool follows this pattern:
1. **Connect** to database
2. **Execute** SQL query
3. **Process** results
4. **Close** connection
5. **Return** structured data

## Available Tools

### 1. `add_inventory(item_id, product_name, location, quantity)`
- **Purpose**: Add new inventory or update existing stock
- **SQL**: Uses `INSERT ... ON DUPLICATE KEY UPDATE`
- **Returns**: Confirmation message with details

### 2. `remove_inventory(item_id, location, quantity)`
- **Purpose**: Reduce stock levels
- **Safety**: Only removes if sufficient quantity exists
- **SQL**: `UPDATE` with quantity check

### 3. `check_stock(item_id, location)`
- **Purpose**: Get current stock for specific item/location
- **Returns**: Item details or zero if not found
- **Use Case**: Quick stock checks

### 4. `list_inventory()`
- **Purpose**: Get all inventory across all locations
- **Returns**: Complete inventory list as JSON
- **Use Case**: Full inventory reports

## How to Use

### 1. Setup MySQL
```bash
# Create database and table
mysql -u root -p < database.sql
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Run in Development Mode
```bash
uv run mcp dev main.py
```

### 4. Install in Claude Desktop
```bash
uv run mcp install main.py -n InventoryMCP
```

### 5. Use in Claude
- Open Claude Desktop
- Enable "InventoryMCP" in Tools
- Ask: "Show me all inventory" or "Add 5 laptops to Mumbai"

## Learning Path for MCP Development

### Phase 1: Understanding Current Project
1. **Study the code structure** - How FastMCP works
2. **Test each tool** - Use MCP Inspector to call tools directly
3. **Modify existing tools** - Add error handling, logging
4. **Add new tools** - Create search, analytics functions

### Phase 2: Advanced MCP Concepts
1. **Resources** - Expose data as queryable resources
2. **Prompts** - Create reusable prompt templates
3. **Authentication** - Add security layers
4. **Configuration** - Environment-based config management

### Phase 3: Integration Patterns
1. **Multiple Databases** - Connect to different data sources
2. **External APIs** - Integrate with third-party services
3. **Real-time Updates** - WebSocket connections
4. **Caching** - Redis for performance

## Next Steps: Intern Onboarding System

Based on this inventory system, you can build an intern onboarding MCP server with:

### Core Features
1. **Intern Database** - Store intern profiles, skills, assignments
2. **Calendar Integration** - Schedule meetings, training sessions
3. **Email Automation** - Send welcome emails, reminders
4. **Task Management** - Assign and track onboarding tasks
5. **Progress Tracking** - Monitor completion status

### Technical Stack
- **MCP Server**: Python with FastMCP
- **Database**: MySQL (extend current schema)
- **Calendar**: Google Calendar API or Outlook API
- **Email**: SMTP or SendGrid API
- **Authentication**: OAuth2 for external services

### Database Schema Extension
```sql
-- Interns table
CREATE TABLE interns (
    intern_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    start_date DATE,
    department VARCHAR(50),
    manager_id VARCHAR(50),
    status ENUM('pending', 'active', 'completed')
);

-- Onboarding tasks
CREATE TABLE onboarding_tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    intern_id VARCHAR(50),
    task_name VARCHAR(200),
    due_date DATE,
    status ENUM('pending', 'in_progress', 'completed'),
    assigned_by VARCHAR(50)
);

-- Calendar events
CREATE TABLE calendar_events (
    event_id VARCHAR(50) PRIMARY KEY,
    intern_id VARCHAR(50),
    title VARCHAR(200),
    start_time DATETIME,
    end_time DATETIME,
    location VARCHAR(100),
    description TEXT
);
```

This project demonstrates the power of MCP for creating AI-powered business applications that can interact with multiple systems through natural language.
