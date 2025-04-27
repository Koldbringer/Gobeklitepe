import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock
from integration import ServiceIntegration

class TestServiceIntegration(unittest.TestCase):
    """Test cases for the ServiceIntegration class."""
    
    def setUp(self):
        """Set up test environment."""
        # Set environment variables for testing
        os.environ['N8N_URL'] = 'http://localhost:5678'
        os.environ['N8N_API_KEY'] = 'test_api_key'
        os.environ['MASTRA_URL'] = 'http://localhost:3000'
        os.environ['MAXUN_FRONTEND_URL'] = 'http://localhost:5173'
        os.environ['MAXUN_BACKEND_URL'] = 'http://localhost:8080'
        os.environ['MINIO_URL'] = 'http://localhost:9001'
        os.environ['MINIO_ACCESS_KEY'] = 'test_access_key'
        os.environ['MINIO_SECRET_KEY'] = 'test_secret_key'
        os.environ['ENABLE_N8N'] = 'true'
        os.environ['ENABLE_MASTRA'] = 'true'
        os.environ['ENABLE_MAXUN'] = 'true'
        
        # Create integration instance
        self.integration = ServiceIntegration()
    
    @patch('integration.requests.get')
    def test_check_services(self, mock_get):
        """Test the check_services method."""
        # Mock responses for each service
        mock_responses = {
            'http://localhost:5678/healthz': MagicMock(
                status_code=200,
                json=lambda: {'status': 'ok'}
            ),
            'http://localhost:3000/api/health': MagicMock(
                status_code=200,
                json=lambda: {'status': 'ok'}
            ),
            'http://localhost:8080/api/health': MagicMock(
                status_code=200,
                json=lambda: {'status': 'ok'}
            )
        }
        
        # Configure the mock to return appropriate responses
        mock_get.side_effect = lambda url, **kwargs: mock_responses.get(url)
        
        # Call the method
        services_status = self.integration.check_services()
        
        # Verify the results
        self.assertEqual(services_status['n8n']['status'], 'up')
        self.assertEqual(services_status['mastra']['status'], 'up')
        self.assertEqual(services_status['maxun']['status'], 'up')
    
    @patch('integration.requests.post')
    def test_create_n8n_workflow(self, mock_post):
        """Test the create_n8n_workflow method."""
        # Mock response
        mock_post.return_value = MagicMock(
            status_code=201,
            json=lambda: {'id': '123', 'name': 'Test Workflow'}
        )
        
        # Call the method
        workflow_data = {
            'nodes': [],
            'connections': {}
        }
        result = self.integration.create_n8n_workflow('Test Workflow', workflow_data)
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], '123')
        self.assertEqual(result['name'], 'Test Workflow')
        
        # Verify the API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['headers']['X-N8N-API-KEY'], 'test_api_key')
        self.assertEqual(kwargs['json']['name'], 'Test Workflow')
    
    @patch('integration.requests.post')
    def test_create_mastra_agent(self, mock_post):
        """Test the create_mastra_agent method."""
        # Mock response
        mock_post.return_value = MagicMock(
            status_code=201,
            json=lambda: {'id': '456', 'name': 'Test Agent'}
        )
        
        # Call the method
        agent_config = {'model': 'gpt-4'}
        result = self.integration.create_mastra_agent('Test Agent', agent_config)
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], '456')
        self.assertEqual(result['name'], 'Test Agent')
        
        # Verify the API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['name'], 'Test Agent')
        self.assertEqual(kwargs['json']['config']['model'], 'gpt-4')
    
    @patch('integration.requests.post')
    def test_create_maxun_extraction(self, mock_post):
        """Test the create_maxun_extraction method."""
        # Mock response
        mock_post.return_value = MagicMock(
            status_code=201,
            json=lambda: {'id': '789', 'name': 'Test Extraction'}
        )
        
        # Call the method
        extraction_config = {'url': 'https://example.com'}
        result = self.integration.create_maxun_extraction('Test Extraction', extraction_config)
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], '789')
        self.assertEqual(result['name'], 'Test Extraction')
        
        # Verify the API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['name'], 'Test Extraction')
        self.assertEqual(kwargs['json']['config']['url'], 'https://example.com')

if __name__ == '__main__':
    unittest.main()
