#!/usr/bin/env python3
"""Basic RAG test without LLM dependencies.

Demonstrates the core retrieval pipeline.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.rag.retriever import RAGRetriever


def main():
    """Test the basic RAG retrieval pipeline."""
    print("="*60)
    print("BASIC RAG RETRIEVAL TEST (WITHOUT LLM)")
    print("="*60)

    retriever = RAGRetriever()

    queries = [
        "data visualization and analytics",
        "Python programming for beginners",
        "interactive learning experiences"
    ]

    for query in queries:
        print(f"\n{'-'*60}")
        print(f"Query: {query}")
        print('-'*60)

        try:
            # Get related skills
            related_skills = retriever.skill_search.find_related_skills(query, top_k=10)
            print(f"\n✓ Found {len(related_skills)} related skills")
            if related_skills:
                print(f"  Skills: {', '.join(related_skills[:5])}")

            # Retrieve apps
            apps = retriever.retrieve(query, top_k=5)
            print(f"\n✓ Found {len(apps)} VR applications")

            if apps:
                print("\nRecommended Apps:")
                for i, app in enumerate(apps, 1):
                    print(f"\n  {i}. {app['name']} ({app['category']})")
                    print(f"     Score: {app['score']:.2f}")
                    print(f"     Skills: {', '.join(app['matched_skills'])}")
            else:
                print("\n  No apps found (check skills in database)")

        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()

    retriever.close()

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
