"""
Quantum-Enhanced Communication Module for HVAC CRM/ERP System

This module provides advanced communication prioritization and routing using
quantum-inspired algorithms to optimize client interactions.
"""

import os
import logging
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from services import email_service, communication_service
from utils import db

# Configure logging
logger = logging.getLogger(__name__)

# Load quantum configuration from environment variables
QUANTUM_RETRY_ATTEMPTS = int(os.getenv("QUANTUM_RETRY_ATTEMPTS", "3"))
QUANTUM_CHANNEL_STABILITY = float(os.getenv("QUANTUM_CHANNEL_STABILITY", "0.98"))


class QuantumPrioritizer:
    """Class for prioritizing communications using quantum-inspired algorithms."""
    
    @staticmethod
    def calculate_entanglement_score(client_id: int, urgency_factor: float = 1.0) -> float:
        """
        Calculate an entanglement score for a client based on their history and importance.
        
        Higher scores indicate higher priority for communications.
        """
        try:
            # Get client data
            query = """
            SELECT c.*, 
                   COUNT(DISTINCT k.id) as communication_count,
                   COUNT(DISTINCT u.id) as device_count,
                   MAX(k.data_czas) as last_communication,
                   AVG(u.wartość) as avg_device_value
            FROM klienci c
            LEFT JOIN komunikacja k ON c.id = k.id_klienta
            LEFT JOIN urządzenia_hvac u ON u.id_klienta = c.id
            WHERE c.id = %s
            GROUP BY c.id
            """
            
            result = db.execute_query(query, [client_id])
            if not result:
                return 0.0
            
            client_data = result[0]
            
            # Base factors
            recency_factor = 1.0
            if client_data.get('last_communication'):
                days_since_last = (datetime.now() - client_data['last_communication']).days
                recency_factor = math.exp(-0.05 * days_since_last)  # Exponential decay
            
            communication_factor = min(1.0, client_data.get('communication_count', 0) / 20.0)
            device_factor = min(1.0, client_data.get('device_count', 0) / 5.0)
            value_factor = min(1.0, client_data.get('avg_device_value', 0) / 10000.0)
            wealth_factor = min(1.0, client_data.get('ocena_zamożności', 0) / 10.0)
            
            # Apply quantum uncertainty principle (small random variation)
            quantum_uncertainty = random.uniform(0.9, 1.1) * QUANTUM_CHANNEL_STABILITY
            
            # Calculate final score with weighted factors
            entanglement_score = (
                0.3 * recency_factor +
                0.2 * communication_factor +
                0.2 * device_factor +
                0.15 * value_factor +
                0.15 * wealth_factor
            ) * urgency_factor * quantum_uncertainty
            
            logger.info(f"Entanglement score for client {client_id}: {entanglement_score:.4f}")
            return entanglement_score
        
        except Exception as e:
            logger.error(f"Error calculating entanglement score: {str(e)}")
            return 0.5  # Default middle priority
    
    @staticmethod
    def prioritize_communications(communications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize a list of communications based on quantum-inspired algorithms.
        
        Returns the same communications list but sorted by priority.
        """
        if not communications:
            return []
        
        try:
            # Calculate priority scores for each communication
            for comm in communications:
                client_id = comm.get('id_klienta')
                if not client_id:
                    comm['priority_score'] = 0.0
                    continue
                
                # Base entanglement score
                entanglement_score = QuantumPrioritizer.calculate_entanglement_score(client_id)
                
                # Adjust based on communication properties
                urgency_multiplier = 1.0
                
                # Adjust by communication type
                if comm.get('typ') == 'email':
                    urgency_multiplier *= 1.0
                elif comm.get('typ') == 'telefon':
                    urgency_multiplier *= 1.5  # Phone calls are more urgent
                elif comm.get('typ') == 'SMS':
                    urgency_multiplier *= 1.2  # SMS is somewhat urgent
                
                # Adjust by sentiment if available
                sentiment = comm.get('analiza_sentymentu')
                if sentiment is not None:
                    if sentiment < -0.5:  # Very negative
                        urgency_multiplier *= 2.0
                    elif sentiment < -0.2:  # Somewhat negative
                        urgency_multiplier *= 1.5
                
                # Adjust by classification if available
                classification = comm.get('klasyfikacja')
                if classification:
                    if classification == 'reklamacja':
                        urgency_multiplier *= 2.0
                    elif classification == 'zapytanie':
                        urgency_multiplier *= 1.2
                
                # Calculate final priority score
                comm['priority_score'] = entanglement_score * urgency_multiplier
            
            # Sort by priority score (descending)
            return sorted(communications, key=lambda x: x.get('priority_score', 0), reverse=True)
        
        except Exception as e:
            logger.error(f"Error prioritizing communications: {str(e)}")
            return communications  # Return original list if error occurs


class QuantumResponseGenerator:
    """Class for generating optimized responses using quantum-inspired algorithms."""
    
    @staticmethod
    def suggest_response_time(client_id: int, comm_type: str) -> datetime:
        """
        Suggest the optimal time to respond to a client based on their history and preferences.
        """
        try:
            # Get client communication history
            query = """
            SELECT data_czas 
            FROM komunikacja 
            WHERE id_klienta = %s AND kierunek = 'przychodzący'
            ORDER BY data_czas DESC
            LIMIT 20
            """
            
            result = db.execute_query(query, [client_id])
            if not result:
                return datetime.now() + timedelta(hours=1)  # Default: respond within an hour
            
            # Analyze communication patterns
            timestamps = [row['data_czas'] for row in result]
            hours = [ts.hour for ts in timestamps]
            
            # Find most common hour for client communications
            hour_counts = {}
            for hour in hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            preferred_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
            
            # Calculate response time based on communication type and preferred hour
            now = datetime.now()
            if comm_type == 'telefon':
                # For phone calls, respond within 1 hour
                return now + timedelta(hours=1)
            elif comm_type == 'SMS':
                # For SMS, respond within 2 hours
                return now + timedelta(hours=2)
            else:  # email
                # For email, respond same day if before 3pm, otherwise next day at preferred hour
                if now.hour < 15:  # Before 3pm
                    target = now.replace(hour=preferred_hour, minute=0, second=0)
                    if target < now:  # If preferred hour has passed today
                        target = now + timedelta(hours=3)  # Respond within 3 hours
                else:
                    # Next day at preferred hour
                    target = (now + timedelta(days=1)).replace(hour=preferred_hour, minute=0, second=0)
                
                return target
        
        except Exception as e:
            logger.error(f"Error suggesting response time: {str(e)}")
            return datetime.now() + timedelta(hours=2)  # Default fallback
    
    @staticmethod
    def generate_response_suggestions(communication_id: int) -> List[str]:
        """
        Generate response suggestions for a communication based on its content and client history.
        """
        try:
            # Get communication details
            comm = communication_service.CommunicationManager.get_communication_by_id(communication_id)
            if not comm:
                return []
            
            # Basic response templates based on classification
            classification = comm.get('klasyfikacja', '').lower()
            
            if 'reklamacja' in classification:
                return [
                    "Przepraszamy za problemy. Rozumiemy Państwa frustrację i natychmiast zajmiemy się tą sprawą.",
                    "Dziękujemy za zgłoszenie problemu. Traktujemy tę sprawę priorytetowo i skontaktujemy się wkrótce z rozwiązaniem.",
                    "Przykro nam z powodu tej sytuacji. Nasz zespół techniczny już analizuje zgłoszenie i wkrótce się z Państwem skontaktuje."
                ]
            elif 'zapytanie' in classification:
                return [
                    "Dziękujemy za zainteresowanie naszymi usługami. Z przyjemnością odpowiemy na wszystkie pytania.",
                    "Doceniamy Państwa zapytanie. Przygotujemy szczegółową odpowiedź w ciągu 24 godzin.",
                    "Dziękujemy za kontakt. Chętnie udzielimy więcej informacji na temat naszych usług."
                ]
            elif 'podziękowanie' in classification:
                return [
                    "Cieszymy się, że mogliśmy pomóc. Państwa zadowolenie jest dla nas najważniejsze.",
                    "Dziękujemy za miłe słowa. Zawsze staramy się zapewnić najwyższą jakość usług.",
                    "Doceniamy Państwa opinię. To dla nas motywacja do dalszej pracy."
                ]
            else:
                return [
                    "Dziękujemy za wiadomość. Odpowiemy najszybciej jak to możliwe.",
                    "Potwierdzamy otrzymanie Państwa wiadomości. Wkrótce się skontaktujemy.",
                    "Dziękujemy za kontakt z HVAC Solutions. Odpowiemy na Państwa wiadomość w ciągu 24 godzin."
                ]
        
        except Exception as e:
            logger.error(f"Error generating response suggestions: {str(e)}")
            return [
                "Dziękujemy za wiadomość. Odpowiemy najszybciej jak to możliwe.",
                "Potwierdzamy otrzymanie Państwa wiadomości. Wkrótce się skontaktujemy."
            ]


# Main functions for using quantum-enhanced communication
def prioritize_inbox(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get and prioritize incoming communications.
    """
    try:
        # Get recent communications
        query = """
        SELECT k.*, c.nazwa as client_name, c.email as client_email
        FROM komunikacja k
        JOIN klienci c ON k.id_klienta = c.id
        WHERE k.kierunek = 'przychodzący' AND k.status = 'nowy'
        ORDER BY k.data_czas DESC
        LIMIT %s
        """
        
        communications = db.execute_query(query, [limit])
        if not communications:
            return []
        
        # Prioritize communications
        prioritized = QuantumPrioritizer.prioritize_communications(communications)
        
        # Add suggested response times
        for comm in prioritized:
            comm['suggested_response_time'] = QuantumResponseGenerator.suggest_response_time(
                comm['id_klienta'], comm['typ']
            )
            
            # Add response suggestions
            comm['response_suggestions'] = QuantumResponseGenerator.generate_response_suggestions(comm['id'])
        
        return prioritized
    
    except Exception as e:
        logger.error(f"Error prioritizing inbox: {str(e)}")
        return []


def get_client_entanglement_scores(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get entanglement scores for top clients.
    """
    try:
        # Get active clients
        query = """
        SELECT id, nazwa, email
        FROM klienci
        ORDER BY data_rejestracji DESC
        LIMIT %s
        """
        
        clients = db.execute_query(query, [limit])
        if not clients:
            return []
        
        # Calculate entanglement scores
        for client in clients:
            client['entanglement_score'] = QuantumPrioritizer.calculate_entanglement_score(client['id'])
        
        # Sort by entanglement score
        return sorted(clients, key=lambda x: x.get('entanglement_score', 0), reverse=True)
    
    except Exception as e:
        logger.error(f"Error getting client entanglement scores: {str(e)}")
        return []


# Initialize the module
def init():
    """Initialize the quantum communication module."""
    logger.info(f"Quantum communication module initialized with {QUANTUM_RETRY_ATTEMPTS} retry attempts and {QUANTUM_CHANNEL_STABILITY} channel stability")


# Initialize the module when imported
init()
