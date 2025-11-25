"""RAG retriever component for VR app recommendations.

This module provides the retrieval pipeline that combines vector search
with knowledge graph queries to find relevant VR applications.
"""

from typing import List, Dict
import sys
import os

# Add knowledge_graph and vector_store to path for imports
kg_path = os.path.join(os.path.dirname(__file__), "../../knowledge_graph/src")
vs_path = os.path.join(os.path.dirname(__file__), "../../vector_store/src")

if kg_path not in sys.path:
    sys.path.append(kg_path)
if vs_path not in sys.path:
    sys.path.append(vs_path)

from vector_store.search_service import SkillSearchService
from knowledge_graph.connection import Neo4jConnection


class RAGRetriever:
    """Retrieves VR applications by combining vector search and graph queries."""

    def __init__(self):
        """Initialize the retriever with search and graph services."""
        self.skill_search = SkillSearchService()
        self.graph = Neo4jConnection()

    def retrieve(self, query: str, top_k: int = 8) -> List[Dict]:
        """
        Main retrieval function.
        Implements Hybrid Retrieval:
        1. Vector Search: Query -> Skill -> VRApp (via DEVELOPS)
        2. Graph Search: Query -> Course -> VRApp (via RECOMMENDS)

        Args:
            query: User query string
            top_k: Number of applications to retrieve

        Returns:
            List of dictionaries containing VR application data
        """
        candidates = {}

        # --- Strategy 1: Course-based Retrieval ---
        # Direct lookup for course codes (e.g. "15-112") or titles
        course_apps = self._query_apps_by_course(query, top_k)
        for app in course_apps:
            app["retrieval_source"] = "course_match"
            candidates[app["name"]] = app

        # --- Strategy 2: Skill-based Retrieval ---
        # Vector search for related skills -> Apps
        related_skills = self.skill_search.find_related_skills(query, top_k=15)
        if related_skills:
            skill_apps = self._query_apps_by_skills(related_skills, top_k)
            for app in skill_apps:
                if app["name"] not in candidates:
                    app["retrieval_source"] = "skill_match"
                    candidates[app["name"]] = app
                else:
                    # If already found via course, verify/boost score if needed
                    # For now, course match usually implies strong relevance
                    pass

        # Convert dict back to list and sort by score
        final_results = list(candidates.values())
        # Simple sort by score (descending)
        final_results.sort(key=lambda x: x.get("score", 0), reverse=True)

        return final_results[:top_k]

    def _query_apps_by_course(self, query_text: str, top_k: int) -> List[Dict]:
        """
        Query Neo4j for VR apps recommended for a specific course.
        Matches course_id (exact/regex) or title (fuzzy).
        """
        import re
        
        clean_query = query_text.strip()
        
        # 1. Try to find a CMU course ID (e.g., 15-112, 95-729)
        # Matches XX-XXX format
        course_id_match = re.search(r'\b(\d{2}-\d{3})\b', clean_query)
        
        if course_id_match:
            course_id = course_id_match.group(1)
            print(f"   [Course Search] Detected Course ID: {course_id}")
            
            cypher = """
            MATCH (c:Course {course_id: $course_id})
            MATCH (c)-[r:RECOMMENDS]->(a:VRApp)
            RETURN a.app_id AS app_id,
                   a.name AS name,
                   a.category AS category,
                   a.description AS description,
                   r.shared_skills AS matched_skills,
                   r.score AS score
            ORDER BY r.score DESC
            LIMIT $top_k
            """
            return self.graph.query(cypher, {"course_id": course_id, "top_k": top_k})

        # 2. Fallback: Title contains search
        # Only perform if the query is short enough to be a title, or risk false positives?
        # For now, we stick to the simple CONTAINS but maybe boost matches
        
        cypher = """
        MATCH (c:Course)
        WHERE toLower(c.title) CONTAINS toLower($query)
        MATCH (c)-[r:RECOMMENDS]->(a:VRApp)
        RETURN a.app_id AS app_id,
               a.name AS name,
               a.category AS category,
               a.description AS description,
               r.shared_skills AS matched_skills,
               r.score AS score
            ORDER BY r.score DESC
            LIMIT $top_k
        """

        results = self.graph.query(cypher, {
            "query": clean_query,
            "top_k": top_k
        })
        
        return results

    def _query_apps_by_skills(self, skills: List[str], top_k: int) -> List[Dict]:
        """
        Query Neo4j knowledge graph for VR applications based on skills.

        Args:
            skills: List of skill names
            top_k: Maximum number of results

        Returns:
            List of VR application dictionaries
        """
        cypher = """
        MATCH (s:Skill)<-[d:DEVELOPS]-(a:VRApp)
        WHERE s.name IN $skills
        WITH a, collect(s.name) AS matched_skills, sum(d.weight) AS score
        RETURN a.app_id AS app_id,
               a.name AS name,
               a.category AS category,
               a.description AS description,
               matched_skills,
               score
        ORDER BY score DESC, size(matched_skills) DESC
        LIMIT $top_k
        """

        results = self.graph.query(cypher, {
            "skills": skills,
            "top_k": top_k
        })

        return results

    def close(self):
        """Close connections to services."""
        self.graph.close()
