import streamlit as st
import os
import json
import logging
from integration import ServiceIntegration

logger = logging.getLogger(__name__)

def render_services_status():
    """Render a UI component showing the status of integrated services."""
    st.subheader("Integrated Services Status")
    
    # Create tabs for different service categories
    tab1, tab2, tab3, tab4 = st.tabs(["Automation", "AI", "Data", "Storage"])
    
    # Get service status
    try:
        integration = ServiceIntegration()
        services_status = integration.check_services()
        
        # Automation tab (n8n)
        with tab1:
            st.markdown("### n8n Workflow Automation")
            
            if services_status['n8n']['status'] == 'up':
                st.success("✅ n8n is running")
                st.markdown(f"**URL:** {integration.n8n_url}")
                
                # Add quick actions
                st.markdown("#### Quick Actions")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Create Workflow", key="create_n8n_workflow"):
                        st.session_state.show_n8n_workflow_form = True
                with col2:
                    if st.button("View Workflows", key="view_n8n_workflows"):
                        st.markdown(f"[Open n8n Dashboard]({integration.n8n_url})")
                
                # Show workflow form if requested
                if st.session_state.get("show_n8n_workflow_form", False):
                    st.markdown("#### Create New Workflow")
                    workflow_name = st.text_input("Workflow Name")
                    workflow_description = st.text_area("Description")
                    
                    if st.button("Save Workflow"):
                        workflow_data = {
                            'nodes': [
                                {
                                    'name': 'Start',
                                    'type': 'n8n-nodes-base.start',
                                    'position': [100, 300],
                                    'parameters': {}
                                }
                            ],
                            'connections': {}
                        }
                        result = integration.create_n8n_workflow(workflow_name, workflow_data)
                        if result:
                            st.success(f"Workflow '{workflow_name}' created successfully!")
                            st.session_state.show_n8n_workflow_form = False
                        else:
                            st.error("Failed to create workflow. Check logs for details.")
            
            elif services_status['n8n']['status'] == 'disabled':
                st.info("ℹ️ n8n integration is disabled")
                st.markdown("To enable n8n integration, set `ENABLE_N8N=true` in your .env file.")
            
            else:
                st.error("❌ n8n is not running")
                st.markdown(f"**URL:** {integration.n8n_url}")
                st.markdown("Please check the logs for more information.")
        
        # AI tab (Mastra)
        with tab2:
            st.markdown("### Mastra AI Agent Framework")
            
            if services_status['mastra']['status'] == 'up':
                st.success("✅ Mastra AI is running")
                st.markdown(f"**URL:** {integration.mastra_url}")
                
                # Add quick actions
                st.markdown("#### Quick Actions")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Create Agent", key="create_mastra_agent"):
                        st.session_state.show_mastra_agent_form = True
                with col2:
                    if st.button("View Agents", key="view_mastra_agents"):
                        st.markdown(f"[Open Mastra Dashboard]({integration.mastra_url})")
                
                # Show agent form if requested
                if st.session_state.get("show_mastra_agent_form", False):
                    st.markdown("#### Create New Agent")
                    agent_name = st.text_input("Agent Name")
                    agent_description = st.text_area("Description")
                    agent_model = st.selectbox("Model", ["gpt-4", "gpt-3.5-turbo", "claude-3-opus"])
                    
                    if st.button("Save Agent"):
                        agent_config = {
                            'model': agent_model,
                            'description': agent_description,
                            'temperature': 0.7,
                            'max_tokens': 1000
                        }
                        result = integration.create_mastra_agent(agent_name, agent_config)
                        if result:
                            st.success(f"Agent '{agent_name}' created successfully!")
                            st.session_state.show_mastra_agent_form = False
                        else:
                            st.error("Failed to create agent. Check logs for details.")
            
            elif services_status['mastra']['status'] == 'disabled':
                st.info("ℹ️ Mastra AI integration is disabled")
                st.markdown("To enable Mastra AI integration, set `ENABLE_MASTRA=true` in your .env file.")
            
            else:
                st.error("❌ Mastra AI is not running")
                st.markdown(f"**URL:** {integration.mastra_url}")
                st.markdown("Please check the logs for more information.")
        
        # Data tab (Maxun)
        with tab3:
            st.markdown("### Maxun Web Data Extraction")
            
            if services_status['maxun']['status'] == 'up':
                st.success("✅ Maxun is running")
                st.markdown(f"**Frontend URL:** {integration.maxun_frontend_url}")
                st.markdown(f"**Backend URL:** {integration.maxun_backend_url}")
                
                # Add quick actions
                st.markdown("#### Quick Actions")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Create Extraction", key="create_maxun_extraction"):
                        st.session_state.show_maxun_extraction_form = True
                with col2:
                    if st.button("View Extractions", key="view_maxun_extractions"):
                        st.markdown(f"[Open Maxun Dashboard]({integration.maxun_frontend_url})")
                
                # Show extraction form if requested
                if st.session_state.get("show_maxun_extraction_form", False):
                    st.markdown("#### Create New Extraction")
                    extraction_name = st.text_input("Extraction Name")
                    extraction_url = st.text_input("URL to Extract")
                    
                    if st.button("Save Extraction"):
                        extraction_config = {
                            'url': extraction_url,
                            'selectors': [
                                {
                                    'name': 'title',
                                    'selector': 'h1',
                                    'type': 'text'
                                }
                            ]
                        }
                        result = integration.create_maxun_extraction(extraction_name, extraction_config)
                        if result:
                            st.success(f"Extraction '{extraction_name}' created successfully!")
                            st.session_state.show_maxun_extraction_form = False
                        else:
                            st.error("Failed to create extraction. Check logs for details.")
            
            elif services_status['maxun']['status'] == 'disabled':
                st.info("ℹ️ Maxun integration is disabled")
                st.markdown("To enable Maxun integration, set `ENABLE_MAXUN=true` in your .env file.")
            
            else:
                st.error("❌ Maxun is not running")
                st.markdown(f"**Frontend URL:** {integration.maxun_frontend_url}")
                st.markdown(f"**Backend URL:** {integration.maxun_backend_url}")
                st.markdown("Please check the logs for more information.")
        
        # Storage tab (MinIO)
        with tab4:
            st.markdown("### MinIO Object Storage")
            
            # MinIO doesn't have a health check endpoint in our integration
            # So we'll just show the URL
            st.info("ℹ️ MinIO status check not implemented")
            st.markdown(f"**URL:** {integration.minio_url}")
            st.markdown("Access MinIO console to manage your files and buckets.")
            
            if st.button("Open MinIO Console"):
                st.markdown(f"[Open MinIO Console]({integration.minio_url})")
    
    except Exception as e:
        logger.error(f"Error rendering services status: {str(e)}")
        st.error(f"Error loading services status: {str(e)}")
        st.markdown("Please check the logs for more information.")

if __name__ == "__main__":
    # For testing the component directly
    st.set_page_config(page_title="Services Status", page_icon="🔌", layout="wide")
    render_services_status()
