#!/usr/bin/env python3
"""
Script to check for updates to the application and its dependencies.
Run this script periodically to ensure your application is up to date.
"""

import os
import sys
import subprocess
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("update_check.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("update_checker")

def check_pip_updates():
    """Check for updates to pip packages."""
    logger.info("Checking for package updates...")
    
    try:
        # Get list of outdated packages
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        outdated_packages = json.loads(result.stdout)
        
        if outdated_packages:
            logger.info(f"Found {len(outdated_packages)} outdated packages:")
            for package in outdated_packages:
                logger.info(f"  {package['name']}: {package['version']} -> {package['latest_version']}")
            
            return outdated_packages
        else:
            logger.info("All packages are up to date.")
            return []
    except Exception as e:
        logger.error(f"Error checking for package updates: {e}")
        return None

def check_security_vulnerabilities():
    """Check for security vulnerabilities in dependencies."""
    logger.info("Checking for security vulnerabilities...")
    
    try:
        # Use safety to check for vulnerabilities
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "safety"],
            capture_output=True,
            text=True
        )
        
        result = subprocess.run(
            [sys.executable, "-m", "safety", "check", "--json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("No security vulnerabilities found.")
            return []
        else:
            vulnerabilities = json.loads(result.stdout)
            logger.warning(f"Found {len(vulnerabilities)} security vulnerabilities!")
            for vuln in vulnerabilities:
                logger.warning(f"  {vuln['package_name']}: {vuln['vulnerability_id']}")
            
            return vulnerabilities
    except Exception as e:
        logger.error(f"Error checking for security vulnerabilities: {e}")
        return None

def generate_report():
    """Generate a report of updates and vulnerabilities."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "outdated_packages": check_pip_updates() or [],
        "security_vulnerabilities": check_security_vulnerabilities() or []
    }
    
    # Save report to file
    with open("update_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Report saved to update_report.json")
    
    return report

if __name__ == "__main__":
    logger.info("Starting update check...")
    report = generate_report()
    
    if report["outdated_packages"] or report["security_vulnerabilities"]:
        logger.warning("Updates or security vulnerabilities found. Please review update_report.json")
        sys.exit(1)
    else:
        logger.info("No updates or security vulnerabilities found.")
        sys.exit(0)
