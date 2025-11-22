#!/usr/bin/env python3
"""Test script for the RAG retrieval system.

Demonstrates VR app recommendations using RAG pipeline.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from rag.service import RAGService


def main():
    """Run test queries against the RAG system."""
    service = RAGService()

    queries = [
        "I want to learn machine learning for public policy",
        "cybersecurity and risk management",
        "data visualization and analytics",
        "Python programming for beginners"
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)

        try:
            result = service.recommend(query)

            print(f"\n📝 Understanding: {result.query_understanding}")
            print(f"🔗 Matched Skills: {', '.join(result.matched_skills[:5])}")
            print(f"\n🥽 Recommended VR Apps ({len(result.apps)}/{result.total_matches}):")

            for i, app in enumerate(result.apps, 1):
                print(f"\n{i}. {app.name} ({app.category})")
                print(f"   Score: {app.score:.2f}")
                print(f"   Skills: {', '.join(app.matched_skills)}")
                print(f"   Why: {app.reasoning}")

        except Exception as e:
            print(f"Error processing query: {e}")
            import traceback
            traceback.print_exc()

    service.close()
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)


if __name__ == "__main__":
    main()
