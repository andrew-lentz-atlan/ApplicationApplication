"""
Sidebar component for Atlan connection management.
"""

import streamlit as st
from services.atlan_client import connect_to_atlan


def render_sidebar():
    """
    Render the sidebar for Atlan connection configuration.
    
    Returns:
        AtlanClient instance if connected, None otherwise
    """
    st.sidebar.title("Atlan Configuration")
    st.sidebar.info("Enter your Atlan URL and API Token to connect.")

    atlan_url_input = st.sidebar.text_input(
        "Atlan URL", 
        help="Your Atlan instance URL (e.g., tenant.atlan.com)."
    )
    atlan_api_token = st.sidebar.text_input(
        "API Token", 
        type="password", 
        help="Your Atlan API token."
    )

    if st.sidebar.button("Connect to Atlan"):
        if atlan_url_input and atlan_api_token:
            client, user = connect_to_atlan(atlan_url_input, atlan_api_token)
            
            if client and user:
                # Store connection details in session state
                st.session_state["atlan_url"] = atlan_url_input.strip()
                if not st.session_state["atlan_url"].startswith(("http://", "https://")):
                    st.session_state["atlan_url"] = f"https://{st.session_state['atlan_url']}"
                    
                st.session_state["atlan_api_token"] = atlan_api_token
                st.session_state["client"] = client
                st.session_state["user"] = user
                st.sidebar.success(f"Connected as {user.username}")
            # Error handling is done in the connect_to_atlan function
        else:
            st.sidebar.warning("Please enter both Atlan URL and API Token.")

    # Return the current client if available
    return st.session_state.get("client") 