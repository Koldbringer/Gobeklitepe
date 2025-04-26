#!/bin/bash

# This script is used as a build context for Docker
# It simply copies the necessary files to the build context

# Create a temporary directory for the build context
mkdir -p build_context

# Copy the necessary files
cp -r app.py requirements.txt config.py components/ pages/ utils/ assets/ build_context/

# Copy the Dockerfile
cp Dockerfile build_context/

# Create a simple entrypoint script
cat > build_context/entrypoint.sh << EOF
#!/bin/bash
streamlit run app.py --server.port=\${PORT:-8501} --server.address=0.0.0.0
EOF

# Make the entrypoint script executable
chmod +x build_context/entrypoint.sh

echo "Build context created successfully!"
