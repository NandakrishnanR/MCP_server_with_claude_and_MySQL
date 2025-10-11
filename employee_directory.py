from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import json
import os

@dataclass
class Person:
    email: str
    slack_id: Optional[str] = None
    role: Optional[str] = None
    supervisor: Optional[str] = None

class EmployeeDirectory:
    def __init__(self, data: Dict[str, Any]):
        self.people = data.get("people", {})
        self.roles = data.get("roles", {})
    
    def get_person_by_name(self, name: str) -> Optional[Person]:
        """Look up person by name (case-insensitive)."""
        name_lower = name.lower().strip()
        for person_name, details in self.people.items():
            if person_name.lower() == name_lower:
                return Person(
                    email=details.get("email", ""),
                    slack_id=details.get("slack_id"),
                    role=details.get("role"),
                    supervisor=details.get("supervisor")
                )
        return None
    
    def get_default_supervisor(self, role_type: str = "ML") -> str:
        """Get default supervisor for a role type."""
        return self.roles.get(f"{role_type}_SUPERVISOR", "Anna Schmidt")
    
    def get_default_handlers(self, handler_type: str = "equipment") -> List[str]:
        """Get default handlers for a type."""
        return self.roles.get(f"{handler_type.upper()}_HANDLERS", ["@maria", "@tom"])

# Default hardcoded directory
_DEFAULT_DIRECTORY = {
    "people": {
        "anna schmidt": {"email": "anna.schmidt@example.com", "slack_id": "@anna"},
        "sarah": {"email": "sarah@example.com", "slack_id": "@sarah"},
        "tom": {"email": "tom@example.com", "slack_id": "@tom"},
        "maria": {"email": "maria@example.com", "slack_id": "@maria"},
        "john antony": {"email": "johnantonysaviour@gmail.com", "slack_id": "@john"},
        "john antony saviour": {"email": "johnantonysaviour@gmail.com", "slack_id": "@john"},
    },
    "roles": {
        "ML_SUPERVISOR": "Anna Schmidt",
        "EQUIPMENT_HANDLERS": ["@maria", "@tom"],
    },
}

def load_directory(json_path: Optional[str] = None) -> EmployeeDirectory:
    """Load employee directory from JSON file or use defaults."""
    if json_path and os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            return EmployeeDirectory(data)
        except Exception:
            pass
    
    return EmployeeDirectory(_DEFAULT_DIRECTORY)

def get_default_supervisor(role_type: str, directory: EmployeeDirectory) -> str:
    """Get default supervisor for role type."""
    return directory.get_default_supervisor(role_type)

def get_default_handlers(handler_type: str, directory: EmployeeDirectory) -> List[str]:
    """Get default handlers for type."""
    return directory.get_default_handlers(handler_type)

def get_email_for_name(name: str, directory: EmployeeDirectory) -> Optional[str]:
    """Get email for person by name."""
    person = directory.get_person_by_name(name)
    return person.email if person else None

def get_slack_for_name(name: str, directory: EmployeeDirectory) -> Optional[str]:
    """Get Slack ID for person by name."""
    person = directory.get_person_by_name(name)
    return person.slack_id if person else None
