import sys
import os
import chromadb

# Add src to path
sys.path.append(os.getcwd())

try:
    print("🌈 Checking ChromaDB...")
    
    # Path inside container
    persist_dir = os.path.abspath("vector_store/data/chroma")
    print(f"   Path: {persist_dir}")
    
    client = chromadb.PersistentClient(path=persist_dir)
    
    # List collections
    collections = client.list_collections()
    print(f"   Collections found: {[c.name for c in collections]}")
    
    if not collections:
        print("   ❌ No collections found! Index build failed.")
        sys.exit(1)
        
    col = client.get_collection("skills")
    count = col.count()
    print(f"   ✅ Collection 'skills' loaded.")
    print(f"   📊 Total Vectors: {count}")
    
    if count == 0:
        print("   ⚠️  Collection is empty.")
    else:
        # Test Query
        print("\n🧪 Testing Vector Search...")
        results = col.query(
            query_texts=["machine learning"],
            n_results=3
        )
        print("   Top 3 matches for 'machine learning':")
        for i, doc in enumerate(results['documents'][0]):
            print(f"   {i+1}. {doc} (Dist: {results['distances'][0][i]:.4f})")

except Exception as e:
    print(f"\n❌ Error: {e}")
