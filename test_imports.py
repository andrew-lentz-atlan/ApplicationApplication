#!/usr/bin/env python3
"""
Simple test script to verify all imports are working correctly.
"""

def test_imports():
    """Test that all modules can be imported without errors."""
    try:
        print("Testing config imports...")
        from config import settings
        print("✅ Config imports successful")
        
        print("Testing service imports...")
        from services import atlan_client, asset_service, connection_service
        print("✅ Service imports successful")
        
        print("Testing UI component imports...")
        from ui.components import sidebar, field_editor
        print("✅ UI component imports successful")
        
        print("Testing UI page imports...")
        from ui.pages import operation_selection, application_selection, asset_definition, enrichment, relationships
        print("✅ UI page imports successful")
        
        print("Testing utility imports...")
        from utils import session_state
        print("✅ Utility imports successful")
        
        print("\n🎉 All imports successful! The refactored application structure is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    test_imports() 