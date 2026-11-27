PERMISSIONS = {
    "organizations:create": "Create organizations",
    "organizations:read_all": "View every organization on the platform",
    "organizations:read_own": "View own organization",
    "organizations:update_own": "Edit own organization",
    "users:create": "Create users in own organization",
    "users:read": "View users in own organization",
    "users:update": "Edit users in own organization",
    "roles:assign": "Assign roles to users in own organization",
    "projects:create": "Create projects",
    "projects:read": "View projects",
    "projects:update": "Edit projects",
    "projects:delete": "Delete projects",
}

_ALL = list(PERMISSIONS)

ROLES = {
    "platform_admin": {
        "description": "Manages the whole platform",
        "permissions": _ALL,
    },
    "org_admin": {
        "description": "Manages one organization and its users",
        "permissions": [
            "organizations:read_own", "organizations:update_own",
            "users:create", "users:read", "users:update", "roles:assign",
            "projects:create", "projects:read", "projects:update", "projects:delete",
        ],
    },
    "programme_manager": {
        "description": "Manages programmes and projects",
        "permissions": [
            "organizations:read_own", "users:read",
            "projects:create", "projects:read", "projects:update",
        ],
    },
    "project_manager": {
        "description": "Manages assigned projects",
        "permissions": ["organizations:read_own", "projects:read", "projects:update"],
    },
    "field_officer": {
        "description": "Submits field data",
        "permissions": ["organizations:read_own", "projects:read"],
    },
    "me_officer": {
        "description": "Manages indicators and verifies results",
        "permissions": ["organizations:read_own", "projects:read", "projects:update"],
    },
    "data_analyst": {
        "description": "Accesses analytics and reports",
        "permissions": ["organizations:read_own", "projects:read"],
    },
    "viewer": {
        "description": "Read-only access",
        "permissions": ["organizations:read_own", "projects:read"],
    },
}
