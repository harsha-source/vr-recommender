import sys
import os
import logging

# Configure logging to show everything
logging.basicConfig(level=logging.DEBUG)

# Add src to path
sys.path.append(os.getcwd())

try:
    print("🔍 Starting Deep Debug of RAG Pipeline...")
    
    from src.rag.retriever import RAGRetriever
    
    print("\n1. Initializing Retriever...")
    retriever = RAGRetriever()
    
    print(f"\n   Active Skills Loaded: {len(retriever.active_skills)}")
    if len(retriever.active_skills) < 5:
        print("   ⚠️  WARNING: Very few active skills. Graph might be empty.")
        print(f"   Skills: {retriever.active_skills}")
        
    query = "machine learning for public policy"
    print(f"\n2. Testing Query: '{query}'")
    
    # Trace Strategy 1: Direct Search
    print("\n   --- Strategy 1: Direct Skill Search ---")
    related_skills = retriever.skill_search.find_related_skills(query, top_k=10)
    print(f"   Found related skills: {related_skills}")
    
    if related_skills:
        direct_apps = retriever._query_apps_by_skills(related_skills, top_k=8)
        print(f"   Direct Apps Found: {len(direct_apps)}")
        for app in direct_apps:
            print(f"     - {app['name']} (Score: {app['score']})")
    else:
        print("   ❌ No related skills found in ChromaDB.")
        
    # Trace Strategy 2: Semantic Bridge
    print("\n   --- Strategy 2: Semantic Bridge ---")
    bridged_skills_data = retriever.skill_search.find_nearest_from_candidates(
        query, 
        retriever.active_skills, 
        top_k=5, 
        min_similarity=0.1 # Lower threshold for debugging
    )
    print(f"   Bridged Skills (low threshold): {[b['name'] for b in bridged_skills_data]}")
    
    # Final Retrieve Call
    print("\n3. Running Full retrieve() method...")
    results = retriever.retrieve(query)
    print(f"   Final Results: {len(results)}")
    for app in results:
        print(f"   - {app['name']} ({app.get('retrieval_source')})")

except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
