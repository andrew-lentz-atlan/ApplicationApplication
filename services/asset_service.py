"""
Asset service module for handling Application and ApplicationField operations.
"""

import streamlit as st
from pyatlan.client.atlan import AtlanClient
from pyatlan.client.asset import Batch
from pyatlan.model.assets import Application, ApplicationField, Asset, Process
from pyatlan.model.fluent_search import FluentSearch, CompoundQuery
from pyatlan.model.enums import CertificateStatus
from services.atlan_client import execute_with_auto_reconnect
from config.settings import DEFAULT_PAGE_SIZE, MAX_SEARCH_RESULTS, FIELD_BATCH_SIZE


def _search_applications_core(client: AtlanClient, search_term: str):
    """Core search logic for applications."""
    if client is None:
        st.error("Client is not available for searching applications.")
        return {}
        
    request = (
        FluentSearch()
        .where(CompoundQuery.asset_type(Application))
        .where(CompoundQuery.active_assets())
        .page_size(50)
        .include_on_results(Asset.NAME)
        .include_on_results(Asset.QUALIFIED_NAME)
        .include_on_results(Asset.DESCRIPTION)
        .include_on_results(Application.APP_ID)
        .include_on_results(Asset.CONNECTION_QUALIFIED_NAME)
    ).to_request()
    
    applications = {}
    search_response = client.asset.search(request)
    
    # Filter results manually to match the search term
    for app in search_response:
        if (hasattr(app, 'name') and app.name and 
            search_term.lower() in app.name.lower()):
            display_name = f"{app.name}"
            if hasattr(app, 'app_id') and app.app_id:
                display_name += f" (ID: {app.app_id})"
            if hasattr(app, 'description') and app.description:
                display_name += f" - {app.description[:50]}..."
            applications[display_name] = app
            
            if len(applications) >= 20:  # Limit results
                break
    
    return applications


def search_applications(client: AtlanClient, search_term: str):
    """Search for existing Application assets with auto-reconnect."""
    result = execute_with_auto_reconnect(_search_applications_core, client, search_term)
    return result if result is not None else {}


def _load_existing_application_fields_core(client: AtlanClient, app_qualified_name: str):
    """Core logic for loading existing application fields."""
    if client is None:
        st.warning("⚠️ Client is not available. You can still update the application, but existing fields won't be loaded.")
        return []
    
    request = (
        FluentSearch()
        .where(CompoundQuery.asset_type(ApplicationField))
        .where(CompoundQuery.active_assets())
        .where(ApplicationField.APPLICATION_PARENT_QUALIFIED_NAME.eq(app_qualified_name))
        .page_size(DEFAULT_PAGE_SIZE)
        .include_on_results(Asset.NAME)
        .include_on_results(Asset.QUALIFIED_NAME)
        .include_on_results(Asset.DESCRIPTION)
    ).to_request()
    
    fields = []
    search_response = client.asset.search(request)
    
    for field in search_response:
        field_data = {
            "name": getattr(field, 'name', ''),
            "type": getattr(field, 'application_field_type', ''),
            "description": getattr(field, 'description', ''),
            "qualified_name": getattr(field, 'qualified_name', ''),
            "is_existing": True
        }
        fields.append(field_data)
    
    if fields:
        st.success(f"✅ Loaded {len(fields)} existing fields from the application")
    else:
        st.info("ℹ️ No existing fields found for this application")
    
    return fields


def load_existing_application_fields(client: AtlanClient, app_qualified_name: str):
    """Load existing ApplicationField assets with auto-reconnect."""
    result = execute_with_auto_reconnect(_load_existing_application_fields_core, client, app_qualified_name)
    if result is not None:
        return result
    else:
        st.warning("⚠️ You can still proceed to update the application, but existing fields cannot be loaded.")
        return []


def _search_assets_direct_core(client: AtlanClient, search_term: str):
    """Core asset search logic."""
    request = (
        FluentSearch()
        .where(CompoundQuery.active_assets())
        .page_size(DEFAULT_PAGE_SIZE)
        .include_on_results(Asset.NAME)
        .include_on_results(Asset.QUALIFIED_NAME)
    ).to_request()
    
    results = []
    search_response = client.asset.search(request)
    
    for asset in search_response:
        if (hasattr(asset, 'name') and asset.name and 
            search_term.lower() in asset.name.lower()):
            results.append(asset)
            if len(results) >= MAX_SEARCH_RESULTS:
                break
    
    # If no results found with partial matching, try exact name search
    if not results:
        st.info(f"No partial matches found for '{search_term}', trying exact match...")
        try:
            exact_request = (
                FluentSearch()
                .where(CompoundQuery.active_assets())
                .where(Asset.NAME.eq(search_term))
                .page_size(20)
                .include_on_results(Asset.NAME)
                .include_on_results(Asset.QUALIFIED_NAME)
            ).to_request()
            
            exact_response = client.asset.search(exact_request)
            for asset in exact_response:
                results.append(asset)
                
        except Exception as exact_e:
            st.warning(f"Exact match search also failed: {exact_e}")
    
    return {f"{a.type_name}: {a.name}": a for a in results if hasattr(a, 'name') and a.name}


def search_assets_direct(client: AtlanClient, search_term: str):
    """Search assets using FluentSearch with auto-reconnect."""
    result = execute_with_auto_reconnect(_search_assets_direct_core, client, search_term)
    return result if result is not None else {}


def _save_application_core(client: AtlanClient, application):
    """Core application save logic."""
    return client.asset.save(application)


def save_application(client: AtlanClient, application):
    """Save application with auto-reconnect."""
    return execute_with_auto_reconnect(_save_application_core, client, application)


def _add_atlan_tags_core(client: AtlanClient, asset_type, qualified_name, tag_names):
    """Core logic for adding Atlan tags."""
    return client.asset.add_atlan_tags(
        asset_type=asset_type,
        qualified_name=qualified_name,
        atlan_tag_names=tag_names,
        propagate=True,
    )


def add_atlan_tags(client: AtlanClient, asset_type, qualified_name, tag_names):
    """Add Atlan tags with auto-reconnect."""
    return execute_with_auto_reconnect(
        _add_atlan_tags_core,
        client,
        asset_type,
        qualified_name,
        tag_names
    )


def create_application_fields(client: AtlanClient, fields, app_qualified_name):
    """Create new ApplicationField assets."""
    if not fields:
        return
        
    st.write(f"🆕 **Creating {len(fields)} new ApplicationField assets...**")
    field_batch = Batch(client, max_size=FIELD_BATCH_SIZE)
    
    for field_data in fields:
        if not field_data.get("name"):
            continue
            
        field_to_create = ApplicationField.creator(
            name=field_data["name"],
            application_qualified_name=app_qualified_name,
        )
        
        if field_data.get("type"):
            field_to_create.application_field_type = field_data.get("type")
        if field_data.get("description"):
            field_to_create.description = field_data.get("description")
            
        field_batch.add(field_to_create)
    
    field_batch.flush()
    st.success(f"✅ Created {len(fields)} new fields")


def update_application_fields(client: AtlanClient, fields):
    """Update existing ApplicationField assets."""
    if not fields:
        return
        
    st.write(f"✏️ **Updating {len(fields)} existing ApplicationField assets...**")
    update_batch = Batch(client, max_size=FIELD_BATCH_SIZE)
    
    for field_data in fields:
        if not field_data.get("name") or not field_data.get("qualified_name"):
            continue
            
        field_to_update = ApplicationField.create_for_modification(
            qualified_name=field_data["qualified_name"],
            name=field_data["name"]
        )
        
        if field_data.get("type"):
            field_to_update.application_field_type = field_data.get("type")
        if field_data.get("description"):
            field_to_update.description = field_data.get("description")
            
        update_batch.add(field_to_update)
    
    update_batch.flush()
    st.success(f"✅ Updated {len(fields)} existing fields")


def _save_process_core(client: AtlanClient, process):
    """Core process save logic."""
    return client.asset.save(process)


def save_process(client: AtlanClient, process):
    """Save process with auto-reconnect."""
    return execute_with_auto_reconnect(_save_process_core, client, process) 