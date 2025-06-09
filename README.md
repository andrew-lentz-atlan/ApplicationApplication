# ApplicationApplication

Poorly put together streamlit slop to build/update applications. Do not know what I am doing.

## Project Structure

```
atlan_asset_builder/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration settings
├── services/
│   ├── __init__.py
│   ├── atlan_client.py       # AtlanClient management & auto-reconnect
│   ├── asset_service.py      # Asset operations (CRUD, search)
│   └── connection_service.py # Connection & metadata operations
├── ui/
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── sidebar.py        # Connection sidebar
│   │   └── field_editor.py   # ApplicationField editor
│   └── pages/
│       ├── __init__.py
│       ├── operation_selection.py    # Step 0: Create vs Update
│       ├── application_selection.py  # Step 1: Select existing app
│       ├── asset_definition.py       # Asset definition & fields
│       ├── enrichment.py             # Descriptions, owners, tags
│       └── relationships.py          # Relationships & submission
└── utils/
    ├── __init__.py
    └── session_state.py      # Session state management
```

## Installation

1. **Clone or download** this project directory
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application**:
   ```bash
   streamlit run main.py
   ```

2. **Connect to Atlan**:
   - Enter your Atlan URL and API Token in the sidebar
   - Click "Connect to Atlan"

3. **Choose your workflow**:
   - **Create Mode**: Build a new Application asset from scratch
   - **Update Mode**: Search for and modify existing applications

4. **Follow the guided steps**:
   - Define or update application details
   - Add or modify ApplicationField assets
   - Set enrichment details (descriptions, owners, tags)
   - Define relationships and lineage
   - Submit to Atlan

## Architecture "Highlights"

### Service Layer
- **`atlan_client.py`**: Centralized client management with automatic reconnection because i dont know why it constantly disconnects
- **`asset_service.py`**: All asset operations (search, create, update) with error handling. dont know what im doing
- **`connection_service.py`**: Connection management and metadata retrieval

### Configuration
- **Centralized Settings**: All configuration in `config/settings.py`
