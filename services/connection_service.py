"""
Connection service module for handling Atlan connections.
"""

import streamlit as st
from pyatlan.client.atlan import AtlanClient
from pyatlan.model.assets import Connection, Asset
from pyatlan.model.fluent_search import FluentSearch, CompoundQuery
from pyatlan.model.enums import AtlanConnectorType
from services.atlan_client import execute_with_auto_reconnect
from config.settings import MAX_CONNECTIONS_TO_FETCH, MAX_SEARCH_ITERATIONS


def _get_connections_internal(client: AtlanClient):
    """Internal function to fetch connections."""
    # Simple approach: search specifically for connections with small page size
    request = (
        FluentSearch()
        .where(CompoundQuery.asset_type(Connection))
        .where(CompoundQuery.active_assets())
        .page_size(20)  # Small page size to prevent loops
        .include_on_results(Asset.NAME)
        .include_on_results(Asset.QUALIFIED_NAME)
        .include_on_results(Connection.CONNECTOR_NAME)
    ).to_request()
    
    connections = []
    search_response = client.asset.search(request)
    
    # Add loop protection - limit iterations
    iteration_count = 0
    
    for result in search_response:
        iteration_count += 1
        if iteration_count > MAX_SEARCH_ITERATIONS:
            st.warning(f"Stopped search after {MAX_SEARCH_ITERATIONS} iterations to prevent infinite loop")
            break
            
        # Check if it's a Connection
        if (hasattr(result, 'type_name') and result.type_name == 'Connection' and
            hasattr(result, 'name') and result.name):
            connections.append(result)
            
            # Stop after finding enough connections to prevent long loops
            if len(connections) >= MAX_CONNECTIONS_TO_FETCH:
                break
    
    st.info(f"Found {len(connections)} connections after {iteration_count} iterations")
    return connections


def get_connections(client: AtlanClient):
    """
    Fetches all connections from Atlan with automatic reconnection.
    """
    result = execute_with_auto_reconnect(_get_connections_internal, client)
    return result if result is not None else []


def get_api_connections(connections):
    """
    Filter connections to get only API-type connections.
    
    Args:
        connections: List of connection assets
        
    Returns:
        List of API-type connections
    """
    return [
        c for c in connections if (
            hasattr(c, 'connector_name') and 
            c.connector_name == AtlanConnectorType.API
        )
    ]


@st.cache_data(show_spinner="Fetching users and groups...")
def get_users_and_groups(_client: AtlanClient):
    """Fetches all users and groups from Atlan."""
    try:
        users = _client.user.get()
        groups = _client.group.get()
        owners = {f"User: {u.username}": u for u in users if u.username}
        owners.update({f"Group: {g.alias}": g for g in groups if g.alias})
        return owners
    except Exception as e:
        st.error(f"Error fetching users and groups: {e}")
        return {}


@st.cache_data(show_spinner="Fetching Atlan tags...")
def get_tags(_client: AtlanClient):
    """Fetches all Atlan Tags (classifications)."""
    try:
        from pyatlan.model.enums import AtlanTypeCategory
        
        # Get all type definitions for classifications (Atlan tags)
        response = _client.typedef.get(type_category=[AtlanTypeCategory.CLASSIFICATION])
        
        if response and response.atlan_tag_defs:
            # Create a dictionary mapping display names to tag definitions
            return {tag.display_name: tag for tag in response.atlan_tag_defs if tag.display_name}
        return {}
    except Exception as e:
        st.error(f"Error fetching tags: {e}")
        return {} 