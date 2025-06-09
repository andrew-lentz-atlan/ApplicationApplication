"""
Step 3/4: Relationships and Submission Page

Allows users to define relationships, lineage, and submit assets to Atlan.
"""

import streamlit as st
from pyatlan.client.asset import Batch
from pyatlan.errors import AtlanError
from pyatlan.model.assets import Application, ApplicationField, Asset, Process, Connection
from pyatlan.model.enums import AtlanConnectorType
from services.asset_service import (
    search_assets_direct, save_application, add_atlan_tags, 
    create_application_fields, update_application_fields, save_process
)
from utils.session_state import (
    is_update_mode, get_selected_application, get_asset_details, 
    get_enrichment_details, get_search_results, set_search_results,
    initialize_search_results, clear_workflow_state
)


def step3_relationships_and_submit(client):
    """Render the UI for step 3: Defining relationships and submitting."""
    is_update = is_update_mode()
    
    st.markdown("---")
    if is_update:
        st.header("Step 4: Update Relationships & Submit")
        st.write(
            "Finally, update relationships and submit your changes to the application."
        )
        selected_app = get_selected_application()
        if selected_app:
            st.info(f"Updating relationships for: **{selected_app.name}**")
    else:
        st.header("Step 3: Define Relationships & Submit")
        st.write(
            "Finally, search for and select any assets to link to your new application."
        )

    # Initialize search results
    initialize_search_results()

    # Asset Search UI
    st.subheader("Asset Search")
    search_query = st.text_input(
        "Search for assets to link",
        help="Enter a search term (e.g., 'orders') and click Search.",
    )
    if st.button("Search Assets"):
        with st.spinner("Searching..."):
            results = search_assets_direct(client, search_query)
            set_search_results(results)
            st.success(f"Found {len(results)} assets.")

    # Main Form
    with st.form("relationships_form"):
        st.subheader("Link Related Assets")

        search_results = get_search_results()
        available_assets = list(search_results.keys())

        owned_assets_selection = st.multiselect(
            "Owned Assets",
            options=available_assets,
            help="Assets that are owned by this application.",
        )

        st.subheader("Define Lineage")
        lineage_inputs = st.multiselect(
            "Upstream Assets (Inputs)",
            options=available_assets,
            help="Assets that are inputs to this application.",
        )
        lineage_outputs = st.multiselect(
            "Downstream Assets (Outputs)",
            options=available_assets,
            help="Assets that this application produces as output.",
        )

        # Navigation and Submission
        st.markdown("---")
        cols = st.columns(2)
        go_back = cols[0].form_submit_button("Go Back", use_container_width=True)
        
        submit_text = "Create Asset in Atlan" if not is_update else "Update Asset in Atlan"
        submit = cols[1].form_submit_button(
            submit_text, use_container_width=True, type="primary"
        )

        if go_back:
            del st.session_state["enrichment_details"]
            st.rerun()

        elif submit:
            spinner_text = "Creating assets in Atlan... This may take a moment." if not is_update else "Updating assets in Atlan... This may take a moment."
            with st.spinner(spinner_text):
                try:
                    _handle_asset_submission(
                        client, is_update, owned_assets_selection, 
                        lineage_inputs, lineage_outputs, search_results
                    )
                except AtlanError as e:
                    action = "updating" if is_update else "creating"
                    st.error(f"An error occurred while {action} the asset: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")


def _handle_asset_submission(client, is_update, owned_assets_selection, lineage_inputs, lineage_outputs, search_results):
    """Handle the main asset submission logic."""
    asset_details = get_asset_details()
    enrichment_details = get_enrichment_details()
    
    connection_qn = asset_details.get("connection_qualified_name")
    
    # Step 0: Create new connection if requested (only for create mode)
    if not is_update and asset_details.get("create_new_connection"):
        connection_qn = _create_new_connection(client, asset_details)
        if not connection_qn:
            return  # Connection creation failed

    # Step 1: Create or Update the Application
    app_qn = _handle_application_asset(
        client, is_update, asset_details, enrichment_details, 
        owned_assets_selection, search_results, connection_qn
    )
    if not app_qn:
        return  # Application creation/update failed

    # Step 2: Handle ApplicationField assets
    _handle_application_fields(client, asset_details, app_qn)

    # Step 3: Add Atlan Tags
    if enrichment_details.get("tag_names"):
        add_atlan_tags(client, Application, app_qn, enrichment_details["tag_names"])

    # Step 4: Create Lineage
    _create_lineage_processes(client, lineage_inputs, lineage_outputs, asset_details, connection_qn, app_qn, search_results)

    # Step 5: Show success and clean up
    _show_success_and_cleanup(is_update, asset_details, app_qn)


def _create_new_connection(client, asset_details):
    """Create a new API connection."""
    new_conn_name = asset_details.get("new_connection_name")
    current_user = st.session_state["user"]
    st.write(f"Creating a new API connection named '{new_conn_name}'...")

    try:
        # Try to get admin role - this might be needed for connection creation
        admin_role_guid = None
        try:
            admin_role_guid = client.role_cache.get_id_for_name("$admin")
        except:
            pass  # If admin role doesn't exist, proceed without it
        
        connection_to_create = Connection.create(
            name=new_conn_name,
            connector_type=AtlanConnectorType.API,
            admin_users=[current_user.username],
            admin_roles=[admin_role_guid] if admin_role_guid else [],
        )
    except Exception as conn_create_error:
        st.error(f"Error creating connection object: {conn_create_error}")
        return None

    created_conn_response = save_application(client, connection_to_create)
    if not created_conn_response:
        return None
        
    try:
        created_connection = created_conn_response.assets_created(asset_type=Connection)[0]
        connection_qn = created_connection.qualified_name
        st.success(f"✅ Connection '{new_conn_name}' created successfully with qualified_name: {connection_qn}")
        return connection_qn
    except Exception as e:
        st.error(f"Could not extract connection from response: {e}")
        return None


def _handle_application_asset(client, is_update, asset_details, enrichment_details, owned_assets_selection, search_results, connection_qn):
    """Handle creating or updating the main Application asset."""
    if is_update:
        return _update_application_asset(client, asset_details, enrichment_details, owned_assets_selection, search_results)
    else:
        return _create_application_asset(client, asset_details, enrichment_details, owned_assets_selection, search_results, connection_qn)


def _update_application_asset(client, asset_details, enrichment_details, owned_assets_selection, search_results):
    """Update an existing Application asset."""
    st.write("✏️ **Updating Application Asset:**")
    app_qn = asset_details["qualified_name"]
    st.write(f"Application qualified_name: {app_qn}")
    
    # Create an updater for the existing application
    application_to_update = Application.create_for_modification(
        qualified_name=app_qn,
        name=asset_details["name"]
    )
    
    # Set properties for update
    if asset_details.get("app_id"):
        application_to_update.app_id = asset_details.get("app_id")
        st.write(f"Updated app_id: {asset_details.get('app_id')}")
    
    if enrichment_details.get("description"):
        application_to_update.description = enrichment_details.get("description")
        st.write(f"Updated description: {enrichment_details.get('description')[:50]}...")
    
    if enrichment_details.get("owner_users"):
        application_to_update.owner_users = set(enrichment_details.get("owner_users", []))
        st.write(f"Updated owner_users: {enrichment_details.get('owner_users')}")
    
    if enrichment_details.get("owner_groups"):
        application_to_update.owner_groups = set(enrichment_details.get("owner_groups", []))
        st.write(f"Updated owner_groups: {enrichment_details.get('owner_groups')}")
    
    # Save the main update first (without owned assets to avoid conflicts)
    st.write("💾 **Saving Application Updates to Atlan...**")
    app_response = save_application(client, application_to_update)
    if app_response is None:
        st.error("❌ Failed to save application update")
        return None
    
    # Extract the updated application
    try:
        updated_app_response = app_response.assets_updated(asset_type=Application)[0]
        st.success(f"✅ Application updated successfully: {updated_app_response.qualified_name}")
    except Exception as e:
        st.warning(f"Could not extract updated application from response: {e}")
        # For updates, we already have the qualified_name, so continue
    
    # Now handle owned assets with a separate, focused update
    if owned_assets_selection or owned_assets_selection == []:  # Handle both setting and clearing
        _update_owned_assets_relationship(client, app_qn, asset_details["name"], owned_assets_selection, search_results)
    
    return app_qn


def _create_application_asset(client, asset_details, enrichment_details, owned_assets_selection, search_results, connection_qn):
    """Create a new Application asset."""
    st.write("🔨 **Creating Application Asset:**")
    st.write(f"Application name: {asset_details['name']}")
    st.write(f"Connection qualified_name: {connection_qn}")
    
    application_to_create = Application.create(
        name=asset_details["name"],
        connection_qualified_name=connection_qn,
    )
    
    # Set additional properties after creation
    if asset_details.get("app_id"):
        application_to_create.app_id = asset_details.get("app_id")
        st.write(f"Set app_id: {asset_details.get('app_id')}")
    
    if enrichment_details.get("description"):
        application_to_create.description = enrichment_details.get("description")
        st.write(f"Set description: {enrichment_details.get('description')[:50]}...")
    
    if enrichment_details.get("owner_users"):
        application_to_create.owner_users = set(enrichment_details.get("owner_users", []))
        st.write(f"Set owner_users: {enrichment_details.get('owner_users')}")
    
    if enrichment_details.get("owner_groups"):
        application_to_create.owner_groups = set(enrichment_details.get("owner_groups", []))
        st.write(f"Set owner_groups: {enrichment_details.get('owner_groups')}")
    
    # Note: We'll set owned assets after creation for better reliability

    # Save the application
    st.write("💾 **Saving Application to Atlan...**")
    app_response = save_application(client, application_to_create)
    if app_response is None:
        st.error("❌ Failed to save application")
        return None

    # Extract the created application
    try:
        created_app_response = app_response.assets_created(asset_type=Application)[0]
        app_qn = created_app_response.qualified_name
        st.success(f"✅ Application created successfully with qualified_name: {app_qn}")
        
        # Now set owned assets with a separate update for better reliability
        if owned_assets_selection or owned_assets_selection == []:
            _update_owned_assets_relationship(client, app_qn, asset_details["name"], owned_assets_selection, search_results)
        
        return app_qn
    except Exception as e:
        st.error(f"Could not extract application from response: {e}")
        return None


def _handle_application_fields(client, asset_details, app_qn):
    """Handle ApplicationField assets (create new, update existing)."""
    if not asset_details["fields"]:
        return
        
    new_fields = [f for f in asset_details["fields"] if not f.get("is_existing")]
    existing_fields = [f for f in asset_details["fields"] if f.get("is_existing")]
    
    # Create new fields
    if new_fields:
        create_application_fields(client, new_fields, app_qn)
    
    # Update existing fields
    if existing_fields:
        update_application_fields(client, existing_fields)


def _create_lineage_processes(client, lineage_inputs, lineage_outputs, asset_details, connection_qn, app_qn, search_results):
    """Create lineage Process assets."""
    if not lineage_inputs and not lineage_outputs:
        return
        
    # The app itself is an output of its inputs
    if lineage_inputs:
        process_inputs = Process.create(
            name=f"{asset_details['name']} Upstream Lineage",
            connection_qualified_name=connection_qn,
            inputs=[
                Asset.ref_by_qualified_name(search_results[i].qualified_name)
                for i in lineage_inputs
            ],
            outputs=[Asset.ref_by_qualified_name(app_qn)],
        )
        save_process(client, process_inputs)

    # If the app produces outputs
    if lineage_outputs:
        process_outputs = Process.create(
            name=f"{asset_details['name']} Downstream Lineage",
            connection_qualified_name=connection_qn,
            inputs=[Asset.ref_by_qualified_name(app_qn)],
            outputs=[
                Asset.ref_by_qualified_name(search_results[o].qualified_name)
                for o in lineage_outputs
            ],
        )
        save_process(client, process_outputs)


def _update_owned_assets_relationship(client, app_qn, app_name, owned_assets_selection, search_results):
    """Update the bidirectional owned assets relationship for proper UI display."""
    if owned_assets_selection:
        st.write(f"🔗 **Setting {len(owned_assets_selection)} owned assets with bidirectional relationship...**")
    else:
        st.write("🔗 **Clearing owned assets (none selected)...**")
    
    success_count = 0
    
    # Step 1: Update the Application to reference the owned assets
    try:
        relationship_updater = Application.create_for_modification(
            qualified_name=app_qn,
            name=app_name
        )
        
        if owned_assets_selection:
            owned_asset_refs = [
                Asset.ref_by_qualified_name(search_results[a].qualified_name)
                for a in owned_assets_selection
            ]
            relationship_updater.application_owned_assets = owned_asset_refs
            st.write(f"✅ Will set owned assets on Application:")
            for ref in owned_asset_refs:
                st.write(f"   - {ref.qualified_name}")
        else:
            # Explicitly clear owned assets if none selected
            relationship_updater.application_owned_assets = []
            st.write("✅ Will clear all owned assets from Application")
        
        # Save the Application-side relationship update
        relationship_response = save_application(client, relationship_updater)
        if relationship_response:
            st.success(f"✅ Step 1: Successfully updated Application-side relationship")
            success_count += 1
        else:
            st.warning("⚠️ Step 1: Failed to update Application-side relationship")
            
    except Exception as app_e:
        st.warning(f"⚠️ Step 1: Application update failed: {app_e}")
    
    # Step 2: Update each owned asset to set applicationQualifiedName
    if owned_assets_selection:
        st.write(f"🔄 **Step 2: Updating {len(owned_assets_selection)} individual assets with applicationQualifiedName...**")
        
        # Use batch processing for efficiency
        try:
            batch = Batch(client, max_size=20)  # Process in batches
            
            for asset_name in owned_assets_selection:
                try:
                    owned_asset = search_results[asset_name]
                    asset_qn = owned_asset.qualified_name
                    asset_type_name = owned_asset.type_name
                    
                    # Use trimToRequired() pattern from Atlan documentation for updates
                    # This gives us a builder with only the minimum required attributes
                    asset_updater = owned_asset.trim_to_required()
                    
                    # Set the applicationQualifiedName to create the reverse relationship
                    asset_updater.application_qualified_name = app_qn
                    
                    batch.add(asset_updater)
                    st.write(f"   - Queued: {asset_qn} -> applicationQualifiedName = {app_qn}")
                    
                except Exception as asset_prep_e:
                    st.warning(f"   - Failed to prepare asset {asset_name}: {asset_prep_e}")
            
            # Flush the batch to update all owned assets
            if batch.size > 0:
                batch_response = batch.flush()
                st.success(f"✅ Step 2: Successfully updated {len(owned_assets_selection)} assets with applicationQualifiedName")
                success_count += 1
            else:
                st.warning("⚠️ Step 2: No assets were queued for update")
                
        except Exception as batch_e:
            st.warning(f"⚠️ Step 2: Batch update of owned assets failed: {batch_e}")
            
            # Fallback: Try updating assets individually
            st.write("🔄 Trying individual asset updates as fallback...")
            individual_success = 0
            for asset_name in owned_assets_selection:
                try:
                    owned_asset = search_results[asset_name]
                    asset_qn = owned_asset.qualified_name
                    
                    # Use trimToRequired() for individual updates
                    asset_updater = owned_asset.trim_to_required()
                    asset_updater.application_qualified_name = app_qn
                    
                    # Save individual asset
                    asset_response = save_application(client, asset_updater)
                    if asset_response:
                        individual_success += 1
                        st.write(f"   ✅ Updated: {asset_qn}")
                    else:
                        st.write(f"   ❌ Failed: {asset_qn}")
                        
                except Exception as individual_e:
                    st.write(f"   ❌ Failed: {asset_name} - {individual_e}")
            
            if individual_success > 0:
                st.success(f"✅ Step 2 (Fallback): Updated {individual_success}/{len(owned_assets_selection)} assets individually")
                success_count += 1
    
    # Summary
    if success_count >= 2:
        st.success(f"🎉 **Owned assets relationship fully established!** Both sides of the bidirectional relationship have been set.")
    elif success_count == 1:
        st.warning(f"⚠️ **Partial success:** Only one side of the relationship was set. Owned assets may not display properly in the UI.")
    else:
        st.error(f"❌ **Failed to establish owned assets relationship.** This may be due to API limitations or permissions.")
        st.info("💡 **Note:** Application was updated successfully, but the owned assets relationship could not be established. The assets may need to be linked manually in the Atlan UI.")


def _show_success_and_cleanup(is_update, asset_details, app_qn):
    """Show success message and clean up session state."""
    atlan_url = st.session_state["atlan_url"]
    
    if is_update:
        # For updates, we might not have created_app_response, use the selected app
        selected_app = get_selected_application()
        if selected_app and hasattr(selected_app, 'guid'):
            asset_url = f"{atlan_url}/assets/{selected_app.guid}/overview"
        else:
            asset_url = f"{atlan_url}/assets"  # Fallback
        st.success(
            f"🎉 Successfully updated Application: [{asset_details['name']}]({asset_url})"
        )
    else:
        # For create mode, we'd need the created asset GUID for the URL
        # For now, use a generic success message
        st.success(f"🎉 Successfully created Application: {asset_details['name']}")

    # Clean up session state for next operation
    clear_workflow_state()
    st.rerun() 