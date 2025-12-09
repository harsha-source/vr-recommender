"""Data models for RAG retrieval and recommendation system."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class VRAppMatch:
    """Represents a matched VR application with metadata."""
    app_id: str
    name: str
    category: str
    score: float
    matched_skills: List[str]
    reasoning: str
    retrieval_source: str = "direct"
    bridge_explanation: str = ""


@dataclass
class RecommendationResult:
    """Complete recommendation result with query understanding."""
    apps: List[VRAppMatch]
    query_understanding: str
    matched_skills: List[str]
    total_matches: int
