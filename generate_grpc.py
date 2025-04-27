#!/usr/bin/env python
"""
Generate gRPC Code

This script generates Python code from Protocol Buffer definitions.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_protoc():
    """Check if protoc is installed."""
    try:
        result = subprocess.run(["protoc", "--version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        if result.returncode == 0:
            logger.info(f"Found protoc: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"Error checking protoc: {result.stderr}")
            return False
    except FileNotFoundError:
        logger.error("protoc not found. Please install Protocol Buffers compiler.")
        return False

def check_grpc_tools():
    """Check if grpcio-tools is installed."""
    try:
        import grpc_tools.protoc
        logger.info("Found grpcio-tools")
        return True
    except ImportError:
        logger.error("grpcio-tools not found. Please install it with: pip install grpcio-tools")
        return False

def generate_code():
    """Generate Python code from Protocol Buffer definitions."""
    # Create output directories if they don't exist
    os.makedirs("generated", exist_ok=True)
    
    # Find all .proto files
    proto_files = list(Path("protos").glob("*.proto"))
    if not proto_files:
        logger.error("No .proto files found in the 'protos' directory.")
        return False
    
    logger.info(f"Found {len(proto_files)} .proto files: {[p.name for p in proto_files]}")
    
    # Generate code for each .proto file
    for proto_file in proto_files:
        logger.info(f"Generating code for {proto_file}")
        
        # Create an __init__.py file in the generated directory
        with open(os.path.join("generated", "__init__.py"), "w") as f:
            f.write("# Generated gRPC code\n")
        
        # Use grpcio-tools to generate code
        try:
            from grpc_tools import protoc
            
            protoc_args = [
                "grpc_tools.protoc",
                f"--proto_path=protos",
                f"--python_out=generated",
                f"--grpc_python_out=generated",
                f"protos/{proto_file.name}"
            ]
            
            result = protoc.main(protoc_args)
            
            if result != 0:
                logger.error(f"Error generating code for {proto_file}")
                return False
            
            logger.info(f"Successfully generated code for {proto_file}")
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return False
    
    logger.info("Code generation completed successfully.")
    return True

def main():
    """Main function."""
    logger.info("Checking dependencies...")
    
    if not check_grpc_tools():
        logger.error("Missing dependencies. Please install them and try again.")
        sys.exit(1)
    
    logger.info("Generating gRPC code...")
    
    if generate_code():
        logger.info("gRPC code generation completed successfully.")
        sys.exit(0)
    else:
        logger.error("gRPC code generation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
