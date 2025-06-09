"""
AtlanClient service module with automatic reconnection functionality.
"""

import streamlit as st
from pyatlan.client.atlan import AtlanClient
from pyatlan.errors import AtlanError
from config.settings import DEFAULT_CONNECT_TIMEOUT, DEFAULT_READ_TIMEOUT


def create_client(base_url: str, api_key: str) -> AtlanClient:
    """
    Create a new AtlanClient instance.
    
    Args:
        base_url: The Atlan instance URL
        api_key: The API token for authentication
        
    Returns:
        AtlanClient instance
        
    Raises:
        AtlanError: If client creation fails
    """
    return AtlanClient(
        base_url=base_url,
        api_key=api_key,
        connect_timeout=DEFAULT_CONNECT_TIMEOUT,
        read_timeout=DEFAULT_READ_TIMEOUT
    )


def execute_with_auto_reconnect(operation_func, client, *args, **kwargs):
    """
    Execute any operation with automatic client reconnection.
    
    Args:
        operation_func: Function to execute that uses AtlanClient
        client: The AtlanClient instance
        *args, **kwargs: Arguments to pass to the operation
    
    Returns:
        Result of the operation, or None if failed
    """
    try:
        return operation_func(client, *args, **kwargs)
    except Exception as e:
        error_msg = str(e)
        if "No instance of AtlanClient has been created" in error_msg:
            # Attempt automatic reconnection
            st.warning("🔄 Client session expired. Attempting to reconnect...")
            
            atlan_url = st.session_state.get("atlan_url")
            atlan_api_token = st.session_state.get("atlan_api_token")
            
            if atlan_url and atlan_api_token:
                try:
                    # Create a new client
                    new_client = create_client(atlan_url, atlan_api_token)
                    # Update session state
                    st.session_state["client"] = new_client
                    st.success("✅ Reconnected! Retrying operation...")
                    
                    # Retry the operation with the new client
                    return operation_func(new_client, *args, **kwargs)
                    
                except Exception as reconnect_e:
                    st.error(f"❌ Failed to reconnect: {reconnect_e}")
                    st.info("💡 Please try reconnecting manually using the sidebar.")
                    return None
            else:
                st.error("❌ Cannot reconnect - missing credentials. Please use the sidebar to reconnect.")
                return None
        else:
            # Re-raise the original error if it's not an AtlanClient issue
            raise e


def connect_to_atlan(atlan_url: str, atlan_api_token: str) -> tuple[AtlanClient, dict]:
    """
    Connect to Atlan and validate the connection.
    
    Args:
        atlan_url: The Atlan instance URL
        atlan_api_token: The API token
        
    Returns:
        Tuple of (client, user_info) if successful, (None, None) if failed
    """
    try:
        processed_url = atlan_url.strip()
        # Prepend https:// if no scheme is provided
        if not processed_url.startswith(("http://", "https://")):
            processed_url = f"https://{processed_url}"

        # Create client
        client = create_client(processed_url, atlan_api_token)
        
        # Validate connection by getting current user
        user = client.user.get_current()
        
        return client, user
        
    except AtlanError as e:
        st.sidebar.error(f"Connection failed: {e}")
        return None, None 