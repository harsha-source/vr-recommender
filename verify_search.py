import sys
import os

# Add src to path
sys.path.append(os.getcwd())

try:
    from src.rag.retriever import RAGRetriever
    
    print("🔄 Initializing RAG Retriever...")
    retriever = RAGRetriever()
    
    query = "data visualization"
    print(f"\n🔍 Searching for: '{query}'")
    
    results = retriever.retrieve(query)
    
    print(f"\n📊 Found {len(results)} results:")
    for app in results:
        print(f"   - {app['name']} (Score: {app.get('score', 0):.2f})")
        print(f"     Source: {app.get('retrieval_source', 'unknown')}")
        
    if not results:
        print("\n❌ No results found. Possible causes:")
        print("   1. ChromaDB vector index is empty.")
        print("   2. Neo4j graph is empty.")
        print("   3. 'Data Visualization' skill is not connected to any apps.")

except Exception as e:
    print(f"\n❌ Error: {e}")
