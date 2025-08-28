"""
User profile models for the AI Representative System.
Contains data structures for storing and managing learned user information.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class UserProfile:
    """
    Represents a learned user profile with interests, traits, and facts.
    
    This class stores all the information the AI learns about a user over time,
    including their interests, personality traits, communication style, and
    specific facts they've shared.
    """
    user_id: str
    interests: Dict[str, str]  # interest_name -> description
    personality_traits: List[str]
    communication_style: str
    learned_facts: Dict[str, Dict[str, Any]]  # fact_type -> {value, learned_at, source_message}
    last_updated: str
    
    @classmethod
    def create_empty(cls, user_id: str) -> 'UserProfile':
        """
        Create an empty user profile for a new user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            UserProfile with empty data structures
        """
        return cls(
            user_id=user_id,
            interests={},
            personality_traits=[],
            communication_style="friendly",
            learned_facts={},
            last_updated=datetime.now().isoformat()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the profile to a dictionary for storage/serialization.
        
        Returns:
            Dictionary representation of the profile
        """
        return {
            "user_id": self.user_id,
            "interests": self.interests,
            "personality_traits": self.personality_traits,
            "communication_style": self.communication_style,
            "learned_facts": self.learned_facts,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """
        Create a UserProfile from a dictionary.
        
        Args:
            data: Dictionary containing profile data
            
        Returns:
            UserProfile instance
        """
        return cls(
            user_id=data.get("user_id", ""),
            interests=data.get("interests", {}),
            personality_traits=data.get("personality_traits", []),
            communication_style=data.get("communication_style", "friendly"),
            learned_facts=data.get("learned_facts", {}),
            last_updated=data.get("last_updated", datetime.now().isoformat())
        )
    
    def update_interests(self, new_interests: Dict[str, str]) -> None:
        """
        Update user interests with new information.
        
        Args:
            new_interests: Dictionary of interest_name -> description
        """
        self.interests.update(new_interests)
        self.last_updated = datetime.now().isoformat()
    
    def add_personality_traits(self, new_traits: List[str]) -> None:
        """
        Add new personality traits, avoiding duplicates.
        
        Args:
            new_traits: List of new personality traits to add
        """
        existing_traits = set(self.personality_traits)
        self.personality_traits = list(existing_traits.union(set(new_traits)))
        self.last_updated = datetime.now().isoformat()
    
    def update_communication_style(self, style: str) -> None:
        """
        Update the user's communication style.
        
        Args:
            style: New communication style description
        """
        self.communication_style = style
        self.last_updated = datetime.now().isoformat()
    
    def add_learned_fact(self, fact_type: str, fact_value: str, source_message: str) -> None:
        """
        Add a new learned fact about the user.
        
        Args:
            fact_type: Category of the fact (e.g., "job", "location", "hobby")
            fact_value: The actual fact value
            source_message: The message where this fact was learned
        """
        self.learned_facts[fact_type] = {
            "value": fact_value,
            "learned_at": datetime.now().isoformat(),
            "source_message": source_message
        }
        self.last_updated = datetime.now().isoformat()
    
    def has_meaningful_data(self) -> bool:
        """
        Check if the profile contains any meaningful learned data.
        
        Returns:
            True if profile has interests, traits, facts, or custom communication style
        """
        has_interests = bool(self.interests)
        has_traits = bool(self.personality_traits)
        has_facts = bool(self.learned_facts)
        has_custom_style = self.communication_style and self.communication_style != "friendly"
        
        return has_interests or has_traits or has_facts or has_custom_style
    
    def get_summary(self) -> Dict[str, int]:
        """
        Get a summary of the profile's data counts.
        
        Returns:
            Dictionary with counts of different data types
        """
        return {
            "interests_count": len(self.interests),
            "traits_count": len(self.personality_traits),
            "facts_count": len(self.learned_facts)
        }
    
    def __str__(self) -> str:
        """String representation of the user profile."""
        summary = self.get_summary()
        return (f"UserProfile(user_id='{self.user_id}', "
                f"interests={summary['interests_count']}, "
                f"traits={summary['traits_count']}, "
                f"facts={summary['facts_count']})")


@dataclass
class ExtractedInfo:
    """
    Represents information extracted from a user message by the AI.
    
    This class is used by the learning tool to structure the information
    extracted from user messages before updating the UserProfile.
    """
    interests: Dict[str, str]
    personality_traits: List[str]
    communication_style: Optional[str]
    factual_information: Dict[str, str]
    has_extractable_info: bool
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtractedInfo':
        """
        Create ExtractedInfo from a dictionary (typically from AI response).
        
        Args:
            data: Dictionary containing extracted information
            
        Returns:
            ExtractedInfo instance
        """
        return cls(
            interests=data.get("interests", {}),
            personality_traits=data.get("personality_traits", []),
            communication_style=data.get("communication_style"),
            factual_information=data.get("factual_information", {}),
            has_extractable_info=data.get("has_extractable_info", False)
        )
