"""
Entity Resolution Layer for Individual-Centric Surveillance

This module implements the Identity Graph functionality to resolve PersonIDs
across fragmented data streams including trading accounts, email IDs, desk 
affiliation, HR data, and communication handles.

Features:
- Probabilistic record linkage with confidence weighting
- Dynamic identity graph maintenance
- Fuzzy matching for name/email variations
- HR data override capabilities
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

import numpy as np
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


@dataclass
class IdentityLink:
    """Represents a link between two identity attributes with confidence scoring"""
    
    source_type: str  # 'account', 'email', 'desk', 'hr_record', 'comm_handle'
    source_value: str
    target_type: str
    target_value: str
    confidence: float  # 0.0 to 1.0
    evidence: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(init=False)
    updated_at: datetime = field(init=False)
    
    def __post_init__(self):
        """Set timestamps to avoid timestamp drift"""
        now = datetime.now(timezone.utc)
        self.created_at = now
        self.updated_at = now
    
    def __hash__(self):
        return hash((self.source_type, self.source_value, self.target_type, self.target_value))


@dataclass
class PersonIdentity:
    """Represents a resolved person identity with all linked attributes"""
    
    person_id: str
    confidence_score: float  # Overall confidence in this identity resolution
    linked_accounts: Set[str] = field(default_factory=set)
    linked_emails: Set[str] = field(default_factory=set)
    linked_desks: Set[str] = field(default_factory=set)
    linked_comm_handles: Set[str] = field(default_factory=set)
    hr_records: List[Dict[str, Any]] = field(default_factory=list)
    primary_name: Optional[str] = None
    primary_role: Optional[str] = None
    created_at: datetime = field(init=False)
    updated_at: datetime = field(init=False)
    
    def __post_init__(self):
        """Set timestamps to avoid timestamp drift"""
        now = datetime.now(timezone.utc)
        self.created_at = now
        self.updated_at = now
    
    def get_all_identifiers(self) -> Set[str]:
        """Get all identifiers associated with this person"""
        identifiers = set()
        identifiers.update(self.linked_accounts)
        identifiers.update(self.linked_emails)
        identifiers.update(self.linked_desks)
        identifiers.update(self.linked_comm_handles)
        return identifiers


class IdentityMatcher:
    """Handles probabilistic matching between identity attributes"""
    
    def __init__(self):
        self.name_similarity_threshold = 0.8
        self.email_similarity_threshold = 0.9
        self.fuzzy_match_threshold = 0.85
        
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names using fuzzy matching"""
        if not name1 or not name2:
            return 0.0
            
        # Normalize names (lowercase, remove extra spaces)
        name1_norm = re.sub(r'\s+', ' ', name1.lower().strip())
        name2_norm = re.sub(r'\s+', ' ', name2.lower().strip())
        
        # Exact match
        if name1_norm == name2_norm:
            return 1.0
            
        # Fuzzy matching
        similarity = SequenceMatcher(None, name1_norm, name2_norm).ratio()
        
        # Check for common name variations (e.g., "John Smith" vs "J. Smith")
        if self._check_name_variations(name1_norm, name2_norm):
            similarity = max(similarity, 0.9)
            
        return similarity
    
    def calculate_email_similarity(self, email1: str, email2: str) -> float:
        """Calculate similarity between email addresses"""
        if not email1 or not email2:
            return 0.0
            
        email1_norm = email1.lower().strip()
        email2_norm = email2.lower().strip()
        
        if email1_norm == email2_norm:
            return 1.0
            
        # Check if same domain and similar username
        try:
            user1, domain1 = email1_norm.split('@')
            user2, domain2 = email2_norm.split('@')
            
            if domain1 == domain2:
                user_similarity = SequenceMatcher(None, user1, user2).ratio()
                return user_similarity * 0.9  # Slight penalty for different usernames
        except ValueError:
            pass
            
        return SequenceMatcher(None, email1_norm, email2_norm).ratio()
    
    def _check_name_variations(self, name1: str, name2: str) -> bool:
        """Check for common name variations like initials"""
        # Split names into parts
        parts1 = name1.split()
        parts2 = name2.split()
        
        if len(parts1) != len(parts2):
            return False
            
        for p1, p2 in zip(parts1, parts2):
            # Check if one is initial of the other
            if len(p1) == 1 and p1 == p2[0]:
                continue
            elif len(p2) == 1 and p2 == p1[0]:
                continue
            elif p1 != p2:
                return False
                
        return True
    
    def match_attributes(self, attr1: Dict[str, Any], attr2: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Match two attribute sets and return confidence score with evidence
        
        Args:
            attr1, attr2: Attribute dictionaries containing name, email, desk, etc.
            
        Returns:
            Tuple of (confidence_score, evidence_dict)
        """
        evidence = {}
        total_score = 0.0
        weight_sum = 0.0
        
        # Name matching
        if 'name' in attr1 and 'name' in attr2:
            name_sim = self.calculate_name_similarity(attr1['name'], attr2['name'])
            evidence['name_similarity'] = name_sim
            total_score += name_sim * 0.4  # 40% weight
            weight_sum += 0.4
            
        # Email matching
        if 'email' in attr1 and 'email' in attr2:
            email_sim = self.calculate_email_similarity(attr1['email'], attr2['email'])
            evidence['email_similarity'] = email_sim
            total_score += email_sim * 0.3  # 30% weight
            weight_sum += 0.3
            
        # Desk matching (exact match for now)
        if 'desk' in attr1 and 'desk' in attr2:
            desk_match = 1.0 if attr1['desk'] == attr2['desk'] else 0.0
            evidence['desk_match'] = desk_match
            total_score += desk_match * 0.2  # 20% weight
            weight_sum += 0.2
            
        # Role matching
        if 'role' in attr1 and 'role' in attr2:
            role_match = 1.0 if attr1['role'] == attr2['role'] else 0.0
            evidence['role_match'] = role_match
            total_score += role_match * 0.1  # 10% weight
            weight_sum += 0.1
            
        # Calculate final confidence
        confidence = total_score / weight_sum if weight_sum > 0 else 0.0
        
        return confidence, evidence


class IdentityGraph:
    """Maintains the dynamic identity graph for person resolution"""
    
    def __init__(self):
        self.persons: Dict[str, PersonIdentity] = {}
        self.identity_links: List[IdentityLink] = []
        self.attribute_to_person: Dict[str, str] = {}  # Maps attribute values to person_ids
        self.matcher = IdentityMatcher()
        
    def resolve_person_id(self, attributes: Dict[str, Any], hr_override: bool = False) -> Tuple[str, float]:
        """
        Resolve a PersonID from given attributes
        
        Args:
            attributes: Dict containing name, email, desk, account_id, etc.
            hr_override: Whether HR data should override fuzzy matching
            
        Returns:
            Tuple of (person_id, confidence_score)
        """
        logger.info(f"Resolving PersonID for attributes: {attributes}")
        
        # Check for existing exact matches first
        person_id = self._find_exact_match(attributes)
        if person_id:
            confidence = self.persons[person_id].confidence_score
            logger.info(f"Found exact match: {person_id} with confidence {confidence}")
            return person_id, confidence
            
        # HR override logic
        if hr_override and 'hr_employee_id' in attributes:
            person_id = self._handle_hr_override(attributes)
            if person_id:
                return person_id, 1.0
                
        # Fuzzy matching against existing persons
        best_match = self._find_fuzzy_match(attributes)
        if best_match:
            person_id, confidence = best_match
            self._update_person_identity(person_id, attributes)
            logger.info(f"Found fuzzy match: {person_id} with confidence {confidence}")
            return person_id, confidence
            
        # Create new person identity
        person_id = self._create_new_person(attributes)
        logger.info(f"Created new person: {person_id}")
        return person_id, 0.8  # Default confidence for new persons
    
    def _find_exact_match(self, attributes: Dict[str, Any]) -> Optional[str]:
        """Find exact match based on known identifiers"""
        for attr_type in ['account_id', 'email', 'comm_handle']:
            if attr_type in attributes:
                attr_key = f"{attr_type}:{attributes[attr_type]}"
                if attr_key in self.attribute_to_person:
                    return self.attribute_to_person[attr_key]
        return None
    
    def _find_fuzzy_match(self, attributes: Dict[str, Any]) -> Optional[Tuple[str, float]]:
        """Find best fuzzy match among existing persons"""
        best_person_id = None
        best_confidence = 0.0
        
        for person_id, person in self.persons.items():
            # Create comparison attributes from person data
            person_attrs = {
                'name': person.primary_name,
                'role': person.primary_role,
            }
            
            # Add first email and desk if available
            if person.linked_emails:
                person_attrs['email'] = list(person.linked_emails)[0]
            if person.linked_desks:
                person_attrs['desk'] = list(person.linked_desks)[0]
                
            confidence, evidence = self.matcher.match_attributes(attributes, person_attrs)
            
            if confidence > best_confidence and confidence > 0.7:  # Minimum threshold
                best_confidence = confidence
                best_person_id = person_id
                
        return (best_person_id, best_confidence) if best_person_id else None
    
    def _handle_hr_override(self, attributes: Dict[str, Any]) -> Optional[str]:
        """Handle HR data override for authoritative identity resolution"""
        hr_id = attributes['hr_employee_id']
        
        # Look for existing person with this HR ID
        for person in self.persons.values():
            for hr_record in person.hr_records:
                if hr_record.get('employee_id') == hr_id:
                    self._update_person_identity(person.person_id, attributes)
                    return person.person_id
                    
        return None
    
    def _create_new_person(self, attributes: Dict[str, Any]) -> str:
        """Create a new person identity"""
        person_id = f"person_{uuid4().hex[:8]}"
        
        person = PersonIdentity(
            person_id=person_id,
            confidence_score=0.8,
            primary_name=attributes.get('name'),
            primary_role=attributes.get('role')
        )
        
        self._update_person_identity(person_id, attributes)
        self.persons[person_id] = person
        
        return person_id
    
    def _update_person_identity(self, person_id: str, attributes: Dict[str, Any]):
        """Update person identity with new attributes"""
        if person_id not in self.persons:
            return
            
        person = self.persons[person_id]
        person.updated_at = datetime.now(timezone.utc)
        
        # Update linked attributes
        if 'account_id' in attributes:
            person.linked_accounts.add(attributes['account_id'])
            self.attribute_to_person[f"account_id:{attributes['account_id']}"] = person_id
            
        if 'email' in attributes:
            person.linked_emails.add(attributes['email'])
            self.attribute_to_person[f"email:{attributes['email']}"] = person_id
            
        if 'desk' in attributes:
            person.linked_desks.add(attributes['desk'])
            
        if 'comm_handle' in attributes:
            person.linked_comm_handles.add(attributes['comm_handle'])
            self.attribute_to_person[f"comm_handle:{attributes['comm_handle']}"] = person_id
            
        # Update HR records
        if 'hr_employee_id' in attributes:
            hr_record = {
                'employee_id': attributes['hr_employee_id'],
                'name': attributes.get('name'),
                'role': attributes.get('role'),
                'department': attributes.get('department'),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            person.hr_records.append(hr_record)
            
        # Update primary fields if not set
        if not person.primary_name and 'name' in attributes:
            person.primary_name = attributes['name']
        if not person.primary_role and 'role' in attributes:
            person.primary_role = attributes['role']
    
    def get_person_accounts(self, person_id: str) -> Set[str]:
        """Get all account IDs linked to a person"""
        if person_id in self.persons:
            return self.persons[person_id].linked_accounts
        return set()
    
    def get_person_by_account(self, account_id: str) -> Optional[PersonIdentity]:
        """Get person identity by account ID"""
        attr_key = f"account_id:{account_id}"
        if attr_key in self.attribute_to_person:
            person_id = self.attribute_to_person[attr_key]
            return self.persons.get(person_id)
        return None
    
    def get_cross_account_evidence(self, person_id: str) -> Dict[str, Any]:
        """Get aggregated evidence across all accounts for a person"""
        if person_id not in self.persons:
            return {}
            
        person = self.persons[person_id]
        return {
            'person_id': person_id,
            'linked_accounts': list(person.linked_accounts),
            'linked_desks': list(person.linked_desks),
            'account_count': len(person.linked_accounts),
            'desk_count': len(person.linked_desks),
            'primary_name': person.primary_name,
            'primary_role': person.primary_role,
            'confidence_score': person.confidence_score,
            'hr_records': person.hr_records
        }


class EntityResolutionService:
    """Main service for entity resolution functionality"""
    
    def __init__(self):
        self.identity_graph = IdentityGraph()
        
    def resolve_trading_data_person_id(self, trade_data: Dict[str, Any]) -> Tuple[str, float]:
        """
        Resolve PersonID from trading data
        
        Args:
            trade_data: Trading data containing trader_id, desk, etc.
            
        Returns:
            Tuple of (person_id, confidence_score)
        """
        attributes = {
            'account_id': trade_data.get('trader_id'),
            'name': trade_data.get('trader_name'),
            'role': trade_data.get('trader_role'),
            'desk': trade_data.get('desk'),
            'book': trade_data.get('book')
        }
        
        # Remove None values
        attributes = {k: v for k, v in attributes.items() if v is not None}
        
        return self.identity_graph.resolve_person_id(attributes)
    
    def resolve_communication_person_id(self, comm_data: Dict[str, Any]) -> Tuple[str, float]:
        """Resolve PersonID from communication data"""
        attributes = {
            'email': comm_data.get('sender_email'),
            'comm_handle': comm_data.get('sender_handle'),
            'name': comm_data.get('sender_name')
        }
        
        attributes = {k: v for k, v in attributes.items() if v is not None}
        
        return self.identity_graph.resolve_person_id(attributes)
    
    def add_hr_data(self, hr_records: List[Dict[str, Any]]):
        """Add HR data with override authority"""
        for record in hr_records:
            attributes = {
                'hr_employee_id': record.get('employee_id'),
                'name': record.get('full_name'),
                'email': record.get('email'),
                'role': record.get('job_title'),
                'department': record.get('department'),
                'desk': record.get('desk_assignment')
            }
            
            attributes = {k: v for k, v in attributes.items() if v is not None}
            
            if attributes:
                self.identity_graph.resolve_person_id(attributes, hr_override=True)
    
    def get_person_cross_account_summary(self, person_id: str) -> Dict[str, Any]:
        """Get comprehensive person summary across all linked accounts"""
        return self.identity_graph.get_cross_account_evidence(person_id)
    
    def get_all_persons(self) -> Dict[str, PersonIdentity]:
        """Get all resolved person identities"""
        return self.identity_graph.persons.copy()