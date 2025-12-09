#!/usr/bin/env python3
"""Update RAG system components.

Updates and rebuilds the RAG system including data collection, skill extraction,
knowledge graph, and vector index.
"""

import argparse
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.data_collection.course_fetcher import CMUCourseFetcher
from src.data_collection.vr_app_fetcher import VRAppFetcher
from src.skill_extraction.pipeline import SkillExtractionPipeline
from src.knowledge_graph.builder import KnowledgeGraphBuilder
from src.vector_store.indexer import VectorIndexer


def main():
    """Main update function."""
    parser = argparse.ArgumentParser(description="Update RAG system")
    parser.add_argument(
        "--source",
        choices=["courses", "apps", "skills", "all"],
        default="all",
        help="Data source to update"
    )
    parser.add_argument(
        "--rebuild-graph",
        action="store_true",
        help="Rebuild Neo4j knowledge graph"
    )
    parser.add_argument(
        "--rebuild-embeddings",
        action="store_true",
        help="Rebuild ChromaDB vector index"
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Data directory path"
    )
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("RAG SYSTEM UPDATE")
    print("=" * 70)

    # 1. Update data collection
    if args.source in ["courses", "all"]:
        print("\n📚 Fetching courses...")
        try:
            fetcher = CMUCourseFetcher()
            courses = fetcher.fetch_courses()
            fetcher.save_courses(courses, f"{args.data_dir}/courses.json")
            print(f"✓ Saved {len(courses)} courses")
        except Exception as e:
            print(f"❌ Course fetch failed: {e}")

    if args.source in ["apps", "all"]:
        print("\n🥽 Fetching VR apps...")
        try:
            fetcher = VRAppFetcher()
            apps = fetcher.fetch_apps()
            fetcher.save_apps(apps, f"{args.data_dir}/vr_apps.json")
            print(f"✓ Saved {len(apps)} VR apps")
        except Exception as e:
            print(f"❌ VR app fetch failed: {e}")

    if args.source in ["skills", "all"]:
        print("\n🔧 Extracting skills...")
        try:
            pipeline = SkillExtractionPipeline()
            pipeline.run(
                f"{args.data_dir}/courses.json",
                f"{args.data_dir}/vr_apps.json",
                args.data_dir
            )
            print("✓ Skills extracted and saved")
        except Exception as e:
            print(f"❌ Skill extraction failed: {e}")

    # 2. Rebuild knowledge graph
    if args.rebuild_graph:
        print("\n🕸️ Rebuilding knowledge graph...")
        try:
            builder = KnowledgeGraphBuilder()
            builder.build(args.data_dir, clear=True)
            print("✓ Knowledge graph rebuilt")
        except Exception as e:
            print(f"❌ Graph rebuild failed: {e}")

    # 3. Rebuild vector index
    if args.rebuild_embeddings:
        print("\n📊 Rebuilding vector index...")
        try:
            indexer = VectorIndexer()
            indexer.build_index(f"{args.data_dir}/skills.json")
            print("✓ Vector index rebuilt")
        except Exception as e:
            print(f"❌ Vector index rebuild failed: {e}")

    print("\n✅ RAG system update complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
