"""
Configuration settings for the Atlan Asset Builder application.
"""

import logging

# Logging configuration
LOGGING_LEVEL = logging.DEBUG

# AtlanClient configuration
DEFAULT_CONNECT_TIMEOUT = 30.0  # Connection timeout in seconds
DEFAULT_READ_TIMEOUT = 3600.0   # Read timeout in seconds (1 hour)

# Search configuration
DEFAULT_PAGE_SIZE = 100
MAX_SEARCH_RESULTS = 50
MAX_CONNECTIONS_TO_FETCH = 20
MAX_SEARCH_ITERATIONS = 50  # Prevent infinite loops

# Application workflow configuration
FIELD_BATCH_SIZE = 20  # For ApplicationField batch operations

# Session state keys that should persist across workflow restarts
PERSISTENT_SESSION_KEYS = [
    "client", 
    "user", 
    "atlan_url", 
    "atlan_api_token"
]

# UI Configuration
APP_TITLE = "Atlan Asset Builder"
APP_ICON = "🤖" 