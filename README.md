# HVAC CRM/ERP System

A comprehensive CRM/ERP system for HVAC companies with features like OCR/DMS, invoicing, inventory management, and PWA capabilities.

## Features

- 📊 Dashboard with key metrics and visualizations
- 👥 Client management
- 🔧 Device/equipment management
- 🏢 Building/location management
- 📋 Service order management
- 📅 Calendar and scheduling
- 💰 Offers and invoices
- 📦 Inventory management
- 📈 Reports and analytics
- ✉️ Advanced communication tools (email, SMS, voice interface, phone call transcriptions)
- 🔬 Quantum-inspired prioritization algorithms for client communications
- 🎙️ Voice interface with text-to-speech capabilities
- 🖼️ Visualizations and images
- ⚙️ Automation and processes
- 🌐 Client portal

## Technology Stack

- **Frontend**: Streamlit
- **Database**: PostgreSQL, Supabase
- **Vector Database**: Qdrant
- **Automation**: 
- **AI Capabilities**: Local LLMs
- **OCR/DMS**: Document processing and management

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker (optional)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hvac-crm-erp.git
   cd hvac-crm-erp
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```

### Production Deployment

#### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t hvac-crm-erp .
   ```

2. Run the container:
   ```bash
   docker run -p 8501:8501 --env-file .env hvac-crm-erp
   ```

#### Using Fly.io

1. Install the Fly CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Deploy to Fly.io:
   ```bash
   fly launch
   ```

3. Scale as needed:
   ```bash
   fly scale memory 1024
   fly scale count 2
   ```

## Usage

1. Access the application at `http://localhost:8501` (local) or your deployed URL
2. Log in with your credentials
3. Navigate through the sidebar to access different modules

## Development

### Project Structure

```
hvac_crm_erp/
├── app.py                  # Main Streamlit application entry point
├── requirements.txt        # Dependencies
├── config.py               # Configuration (DB connections, API keys)
├── assets/                 # Static assets (images, CSS)
├── components/             # Reusable UI components
├── pages/                  # Individual pages
├── utils/                  # Utility functions
├── models/                 # Data models
├── services/               # Business logic
├── static/                 # Static files served by the application
└── .streamlit/             # Streamlit configuration
```

### Running Tests

```bash
pytest
```

### Code Style

We use Black for code formatting and flake8 for linting:

```bash
black .
flake8
```

## Advanced Features

### Quantum-Enhanced Communication

The system uses quantum-inspired algorithms to optimize client communications:

- **Client Entanglement Scoring**: Prioritizes communications based on client history, value, and interaction patterns
- **Quantum Visualization Dashboard**: Visual representation of client relationships and communication priorities
- **Optimized Response Timing**: Suggests the best time to respond to each client
- **Automated Response Suggestions**: Generates context-aware response templates

To enable quantum features, set the following in your `.env` file:

```bash
QUANTUM_RETRY_ATTEMPTS=3
QUANTUM_CHANNEL_STABILITY=0.98
```

### Voice Interface

The system includes a voice interface for hands-free operation:

- **Text-to-Speech**: Convert any text to natural-sounding speech using ElevenLabs API
- **Voice Messages**: Send voice messages to clients
- **Voice Assistant**: Interact with the system using voice commands (coming soon)
- **Voice Analytics**: Analyze sentiment and emotion in voice communications (coming soon)

To enable voice features, set the following in your `.env` file:

```bash
ENABLE_VOICE=true
ELEVENLABS_API_KEY=your_api_key
ELEVENLABS_BASE_URL=https://api.elevenlabs.io/v1
```

## Monitoring and Maintenance

### Health Checks

Access the health check endpoint at `/static/health.json` to monitor system status.

### Updates

Run the update checker periodically:

```bash
python check_updates.py
```

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Support

For support, contact support@hvacsolutions.com or call +48 123 456 789.
