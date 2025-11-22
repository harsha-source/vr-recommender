"""Data models for Stage 2 Skill Extraction"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Skill:
    """Represents a standardized skill with metadata"""
    name: str                      # Standardized name, e.g., "Machine Learning"
    aliases: List[str]             # Alternative names, e.g., ["ML", "机器学习"]
    category: str                  # "technical" | "soft" | "domain"
    source_count: int              # Number of times this skill appeared
    weight: Optional[float] = None # Average importance weight (0.0-1.0)


@dataclass
class SkillMapping:
    """Maps a source (course or app) to a skill with weight"""
    source_id: str          # course_id or app_id
    source_type: str        # "course" | "app"
    skill_name: str         # Standardized skill name
    weight: float           # Importance score 0.0-1.0
