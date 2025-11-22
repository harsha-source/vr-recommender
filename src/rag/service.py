"""RAG Service - Main entry point for VR app recommendations.

Orchestrates the complete retrieval and ranking pipeline.
"""

from typing import List
from .retriever import RAGRetriever
from .ranker import LLMRanker
from .models import RecommendationResult, VRAppMatch


class RAGService:
    """RAG recommendation service main entry point."""

    def __init__(self):
        """Initialize the RAG service with retriever and ranker."""
        self.retriever = RAGRetriever()
        self.ranker = LLMRanker()

    def recommend(self, query: str, top_k: int = 8) -> RecommendationResult:
        """
        Generate VR app recommendations for a user query.

        Args:
            query: User query string
            top_k: Number of recommendations to return

        Returns:
            RecommendationResult with apps and metadata
        """
        # 1. Understand the query
        query_understanding = self.ranker.understand_query(query)

        # 2. Retrieve candidate applications
        candidates = self.retriever.retrieve(query, top_k=top_k * 2)

        if not candidates:
            return RecommendationResult(
                apps=[],
                query_understanding=query_understanding,
                matched_skills=[],
                total_matches=0
            )

        # 3. Rank and explain using LLM
        ranked_apps = self.ranker.rank_and_explain(query, candidates)

        # 4. Build final result
        all_skills = set()
        app_matches = []

        for app in ranked_apps[:top_k]:
            all_skills.update(app["matched_skills"])
            app_matches.append(VRAppMatch(
                app_id=app["app_id"],
                name=app["name"],
                category=app["category"],
                score=app["score"],
                matched_skills=app["matched_skills"],
                reasoning=app["reasoning"]
            ))

        return RecommendationResult(
            apps=app_matches,
            query_understanding=query_understanding,
            matched_skills=list(all_skills),
            total_matches=len(candidates)
        )

    def close(self):
        """Close service connections."""
        self.retriever.close()
