import os
import sys
import json
import logging
import requests
from dotenv import load_dotenv
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ServiceIntegration:
    """Class to handle integration between services."""
    
    def __init__(self):
        """Initialize the integration with service URLs from environment variables."""
        self.n8n_url = os.getenv('N8N_URL', 'http://localhost:5678')
        self.n8n_api_key = os.getenv('N8N_API_KEY', '')
        
        self.mastra_url = os.getenv('MASTRA_URL', 'http://localhost:3000')
        
        self.maxun_frontend_url = os.getenv('MAXUN_FRONTEND_URL', 'http://localhost:5173')
        self.maxun_backend_url = os.getenv('MAXUN_BACKEND_URL', 'http://localhost:8080')
        
        self.minio_url = os.getenv('MINIO_URL', 'http://localhost:9001')
        self.minio_access_key = os.getenv('MINIO_ACCESS_KEY', '')
        self.minio_secret_key = os.getenv('MINIO_SECRET_KEY', '')
        
        # Feature flags
        self.enable_n8n = os.getenv('ENABLE_N8N', 'true').lower() == 'true'
        self.enable_mastra = os.getenv('ENABLE_MASTRA', 'true').lower() == 'true'
        self.enable_maxun = os.getenv('ENABLE_MAXUN', 'true').lower() == 'true'
    
    def check_services(self):
        """Check if all services are running and accessible."""
        services_status = {}
        
        # Check n8n
        if self.enable_n8n:
            try:
                response = requests.get(f"{self.n8n_url}/healthz", timeout=5)
                services_status['n8n'] = {
                    'status': 'up' if response.status_code == 200 else 'down',
                    'details': response.json() if response.status_code == 200 else {'error': response.text}
                }
            except Exception as e:
                services_status['n8n'] = {
                    'status': 'error',
                    'details': {'error': str(e)}
                }
        else:
            services_status['n8n'] = {'status': 'disabled'}
        
        # Check Mastra
        if self.enable_mastra:
            try:
                response = requests.get(f"{self.mastra_url}/api/health", timeout=5)
                services_status['mastra'] = {
                    'status': 'up' if response.status_code == 200 else 'down',
                    'details': response.json() if response.status_code == 200 else {'error': response.text}
                }
            except Exception as e:
                services_status['mastra'] = {
                    'status': 'error',
                    'details': {'error': str(e)}
                }
        else:
            services_status['mastra'] = {'status': 'disabled'}
        
        # Check Maxun
        if self.enable_maxun:
            try:
                response = requests.get(f"{self.maxun_backend_url}/api/health", timeout=5)
                services_status['maxun'] = {
                    'status': 'up' if response.status_code == 200 else 'down',
                    'details': response.json() if response.status_code == 200 else {'error': response.text}
                }
            except Exception as e:
                services_status['maxun'] = {
                    'status': 'error',
                    'details': {'error': str(e)}
                }
        else:
            services_status['maxun'] = {'status': 'disabled'}
        
        return services_status
    
    def create_n8n_workflow(self, workflow_name, workflow_data):
        """Create a new workflow in n8n."""
        if not self.enable_n8n:
            logger.warning("n8n integration is disabled")
            return None
        
        try:
            headers = {
                'X-N8N-API-KEY': self.n8n_api_key,
                'Content-Type': 'application/json'
            }
            
            # Create workflow
            payload = {
                'name': workflow_name,
                'nodes': workflow_data.get('nodes', []),
                'connections': workflow_data.get('connections', {})
            }
            
            response = requests.post(
                f"{self.n8n_url}/api/v1/workflows",
                headers=headers,
                json=payload
            )
            
            if response.status_code in (200, 201):
                logger.info(f"Successfully created n8n workflow: {workflow_name}")
                return response.json()
            else:
                logger.error(f"Failed to create n8n workflow: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating n8n workflow: {str(e)}")
            return None
    
    def create_mastra_agent(self, agent_name, agent_config):
        """Create a new agent in Mastra AI."""
        if not self.enable_mastra:
            logger.warning("Mastra integration is disabled")
            return None
        
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            # Create agent
            payload = {
                'name': agent_name,
                'config': agent_config
            }
            
            response = requests.post(
                f"{self.mastra_url}/api/agents",
                headers=headers,
                json=payload
            )
            
            if response.status_code in (200, 201):
                logger.info(f"Successfully created Mastra agent: {agent_name}")
                return response.json()
            else:
                logger.error(f"Failed to create Mastra agent: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating Mastra agent: {str(e)}")
            return None
    
    def create_maxun_extraction(self, extraction_name, extraction_config):
        """Create a new extraction in Maxun."""
        if not self.enable_maxun:
            logger.warning("Maxun integration is disabled")
            return None
        
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            # Create extraction
            payload = {
                'name': extraction_name,
                'config': extraction_config
            }
            
            response = requests.post(
                f"{self.maxun_backend_url}/api/extractions",
                headers=headers,
                json=payload
            )
            
            if response.status_code in (200, 201):
                logger.info(f"Successfully created Maxun extraction: {extraction_name}")
                return response.json()
            else:
                logger.error(f"Failed to create Maxun extraction: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating Maxun extraction: {str(e)}")
            return None

def main():
    """Main function to test the integration."""
    integration = ServiceIntegration()
    
    # Check services
    logger.info("Checking services...")
    services_status = integration.check_services()
    logger.info(f"Services status: {json.dumps(services_status, indent=2)}")
    
    # Example: Create n8n workflow
    if integration.enable_n8n and services_status['n8n']['status'] == 'up':
        logger.info("Creating example n8n workflow...")
        workflow_data = {
            'nodes': [
                {
                    'name': 'Start',
                    'type': 'n8n-nodes-base.start',
                    'position': [100, 300],
                    'parameters': {}
                },
                {
                    'name': 'HTTP Request',
                    'type': 'n8n-nodes-base.httpRequest',
                    'position': [300, 300],
                    'parameters': {
                        'url': 'https://example.com',
                        'method': 'GET'
                    }
                }
            ],
            'connections': {
                'Start': {
                    'main': [
                        [
                            {
                                'node': 'HTTP Request',
                                'type': 'main',
                                'index': 0
                            }
                        ]
                    ]
                }
            }
        }
        integration.create_n8n_workflow('Example Workflow', workflow_data)
    
    # Example: Create Mastra agent
    if integration.enable_mastra and services_status['mastra']['status'] == 'up':
        logger.info("Creating example Mastra agent...")
        agent_config = {
            'model': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 1000,
            'tools': [
                {
                    'name': 'search',
                    'description': 'Search for information'
                },
                {
                    'name': 'calculate',
                    'description': 'Perform calculations'
                }
            ]
        }
        integration.create_mastra_agent('Example Agent', agent_config)
    
    # Example: Create Maxun extraction
    if integration.enable_maxun and services_status['maxun']['status'] == 'up':
        logger.info("Creating example Maxun extraction...")
        extraction_config = {
            'url': 'https://example.com',
            'selectors': [
                {
                    'name': 'title',
                    'selector': 'h1',
                    'type': 'text'
                },
                {
                    'name': 'description',
                    'selector': 'meta[name="description"]',
                    'type': 'attribute',
                    'attribute': 'content'
                }
            ]
        }
        integration.create_maxun_extraction('Example Extraction', extraction_config)

if __name__ == "__main__":
    main()
