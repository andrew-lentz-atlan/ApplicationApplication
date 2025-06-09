# Atlan Asset Builder

A Streamlit application for creating and updating Application assets in Atlan with their ApplicationField sub-assets.

## Features

- ✅ **Dual Mode Operation**: Create new Application assets or update existing ones
- 🔍 **Smart Search**: Search and select existing applications for updates
- 📝 **Field Management**: Add, edit, and remove ApplicationField assets
- 🏷️ **Enrichment**: Add descriptions, owners, and Atlan tags
- 🔗 **Relationships**: Define owned assets and lineage (upstream/downstream)
- 🔄 **Auto-Reconnection**: Automatic client session recovery on timeouts
- 🎛️ **Modern UI**: Clean, intuitive interface with step-by-step workflow

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

## Architecture Highlights

### Service Layer
- **`atlan_client.py`**: Centralized client management with automatic reconnection
- **`asset_service.py`**: All asset operations (search, create, update) with error handling
- **`connection_service.py`**: Connection management and metadata retrieval

### UI Layer
- **Modular Pages**: Each workflow step in its own module
- **Reusable Components**: Sidebar and field editor as standalone components
- **Clean Separation**: UI logic separated from business logic

### Configuration
- **Centralized Settings**: All configuration in `config/settings.py`
- **Environment-Aware**: Easy to adjust timeouts, limits, and behavior

### Error Handling
- **Auto-Reconnection**: Transparent handling of client session timeouts
- **Graceful Degradation**: Continues workflow even if some operations fail
- **User-Friendly Messages**: Clear error messages and recovery suggestions

## Key Design Patterns

1. **Service-Oriented Architecture**: Business logic separated into service modules
2. **Component-Based UI**: Reusable UI components with clear interfaces
3. **Session State Management**: Centralized state handling with utility functions
4. **Error Recovery**: Automatic reconnection with fallback strategies
5. **Configuration-Driven**: Easy customization through settings file

## Comparison with Single-File Version

| Aspect | Single File | Refactored |
|--------|-------------|------------|
| **Maintainability** | Hard to navigate 1349+ lines | Clear module boundaries |
| **Testing** | Difficult to test individual functions | Easy to unit test services |
| **Reusability** | Monolithic functions | Reusable components |
| **Configuration** | Hardcoded values | Centralized settings |
| **Error Handling** | Scattered throughout | Centralized in services |
| **Code Organization** | All mixed together | Clear separation of concerns |

## Development

### Adding New Features
1. **Services**: Add business logic to appropriate service module
2. **UI**: Create new page or component in `ui/` directory
3. **Configuration**: Add settings to `config/settings.py`
4. **State**: Use utilities in `utils/session_state.py`

### Testing
- Services can be unit tested independently
- UI components can be tested with mock services
- Configuration changes are isolated and controllable

### Deployment
- Single entry point (`main.py`) for easy deployment
- All dependencies listed in `requirements.txt`
- Environment variables can be added to `config/settings.py`

## Migration from Single File

The refactored version maintains 100% feature parity with the original single-file application while providing:
- Better code organization
- Easier maintenance and debugging
- More robust error handling
- Clearer testing strategies
- Improved scalability for future features

All existing functionality (create/update modes, auto-reconnection, field management, etc.) works exactly the same but is now properly organized into logical modules. 