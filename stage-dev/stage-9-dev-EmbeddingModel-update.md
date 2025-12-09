# Stage 9: Advanced Skill Extraction & Knowledge Graph Enhancement

## 1. Overview
This stage aims to transition the skill extraction and knowledge graph (KG) construction process from a brittle, rule-based system to a robust, semantic-aware architecture. By leveraging semantic embeddings, clustering algorithms, and graph representation learning, we will improve the accuracy of skill deduplication, enable hierarchical reasoning, and capture implicit structural relationships between entities.

---

## 2. Current Limitations (Diagnosed)
1.  **Greedy Matching Bug**: The current `SkillNormalizer` matches keywords in an arbitrary order. E.g., "Python Programming" is incorrectly normalized to "Programming" because it hits the "programming" keyword first, losing critical specificity.
2.  **Semantic Blindness**: "Team Collaboration" and "Working in Teams" are treated as distinct skills because they don't share exact string roots or hardcoded aliases.
3.  **Flat Topology**: The graph lacks hierarchy. There is no understanding that "Deep Learning" `IS_A` "Machine Learning", limiting the system's ability to generalize recommendations.
4.  **Lack of Structural Features**: Recommendations rely purely on explicit edge overlaps, missing implicit structural similarities (e.g., courses that serve similar roles in the curriculum but share few direct keywords).

---

## 3. Implementation Plan

### Improvement 1: Semantic Clustering for Skill Deduplication
**Goal**: Replace rule-based normalization with embedding-based clustering to automatically identify and merge synonyms.

*   **Algorithm**:
    1.  **Encode**: Use `sentence-transformers/all-MiniLM-L6-v2` to generate dense vector embeddings for all raw skill strings.
    2.  **Cluster**: Apply **HAC (Hierarchical Agglomerative Clustering)** with a cosine distance threshold (e.g., `distance < 0.2`) to group semantically identical skills.
    3.  **Canonicalize**: For each cluster, select the centroid term or the most frequent term as the "Canonical Skill Name".

*   **Code Changes**:
    *   **Modify**: `skill_extraction/src/skill_extraction/deduplicator.py`
        *   **New Dependency**: `sentence-transformers`, `scikit-learn`.
        *   **New Class**: `SemanticDeduplicator` (inherits or replaces `SkillDeduplicator`).
        *   **Method**: `deduplicate(skills: List[str]) -> Map[str, str]`.
    *   **Modify**: `skill_extraction/src/skill_extraction/pipeline.py` to use the new deduplicator.

### Improvement 2: Hierarchical Knowledge Graph (Taxonomy Construction)
**Goal**: Introduce `IS_A` relationships to support broad queries (e.g., query "Programming" matches "Python").

*   **Algorithm**:
    1.  **LLM-based Classification**: After deduplication, send the unique skill list to an LLM (Qwen/OpenRouter).
    2.  **Prompt**: "For each skill in this list, identify its immediate parent category from a standard taxonomy (e.g., ESCO or O*NET)."
    3.  **Graph Construction**: Create `ParentSkill` nodes in Neo4j.
        *   `(Skill: Python)-[:IS_A]->(ParentSkill: Programming Languages)`

*   **Code Changes**:
    *   **Modify**: `knowledge_graph/src/knowledge_graph/builder.py`.
    *   **New Logic**:
        *   Add a method `_build_taxonomy(unique_skills)`.
        *   Update Cypher queries to create `:IS_A` relationships.
    *   **Update Queries**: Modify recommendation queries in `vr_recommender.py` to traverse `IS_A` edges (e.g., `MATCH (u)-[:INTERESTED_IN]->(s:Skill)-[:IS_A*0..1]->(target)`).

### Improvement 3: Graph Embeddings (Node2Vec)
**Goal**: Capture structural similarity between courses and apps to improve recommendation "serendipity" and robustness.

*   **Algorithm**: **Node2Vec**
    *   This algorithm performs random walks on the graph to generate sequences of nodes, then trains a Skip-gram model (like Word2Vec) to learn node embeddings.
    *   Nodes that are structurally similar or close in the graph will have high cosine similarity.

*   **Implementation Strategy**:
    *   Since we are using Neo4j, we can utilize the **Graph Data Science (GDS)** library if available, or compute embeddings offline using `node2vec` python library.
    *   **Offline Approach** (Lower dependency):
        1.  Export Graph Edges to a lightweight library (e.g., `networkx`).
        2.  Run `node2vec`.
        3.  Save embeddings back to Neo4j as a node property `embedding`.
        4.  Use these embeddings in the Vector Store (ChromaDB) or for cosine similarity scoring in the Recommender.

*   **Code Changes**:
    *   **New File**: `knowledge_graph/src/knowledge_graph/embedder.py`.
    *   **Class**: `GraphEmbedder`.
    *   **Integration**: Call `GraphEmbedder.run()` after `KnowledgeGraphBuilder.build()` in `scripts/build_graph.py`.

---

## 4. Detailed Architecture

### Modified Skill Extraction Pipeline
```python
class SemanticPipeline:
    def run(self):
        # 1. Raw Extraction (LLM) -> as is
        raw_skills = self.extractor.extract_all()
        
        # 2. Semantic Deduplication (New)
        # replaces regex-based normalizer
        deduplicator = SemanticDeduplicator(model="all-MiniLM-L6-v2")
        unique_skills_map = deduplicator.cluster_and_merge(raw_skills)
        
        # 3. Taxonomy Generation (New)
        # Optional: Use LLM to find parents for unique_skills
        taxonomy_map = self.taxonomy_generator.generate(unique_skills_map.keys())
        
        return unique_skills_map, taxonomy_map
```

### Modified Knowledge Graph Schema
*   **Nodes**:
    *   `Course`, `VRApp` (Existing)
    *   `Skill` (Existing - now canonicalized)
    *   `SkillCategory` (New - e.g., "Programming Language", "Soft Skill")
*   **Relationships**:
    *   `(Course)-[:TEACHES]->(Skill)`
    *   `(VRApp)-[:DEVELOPS]->(Skill)`
    *   `(Skill)-[:IS_A]->(SkillCategory)` (New)
    *   `(Skill)-[:RELATED_TO]->(Skill)` (Implicit semantic link, optional)

---

## 5. Execution Steps (Dev Plan)

1.  **Step 1: Fix Normalizer (Quick Win)**
    *   Patch `normalizer.py` to sort aliases by length (descending) before matching. This solves the "Python Programming" -> "Programming" bug immediately.

2.  **Step 2: Implement `SemanticDeduplicator`**
    *   Create `semantic_deduplicator.py`.
    *   Implement embedding generation and HAC clustering.
    *   Write unit tests comparing it against the old regex-based approach.

3.  **Step 3: Integrate & Verify**
    *   Update the pipeline to use the new deduplicator.
    *   Re-run `extract_skills.py` on the dataset.
    *   Inspect `skills.json` to verify that "Team Collaboration" and "Working in Teams" are merged.

4.  **Step 4: Graph Embeddings (Bonus/Phase 2)**
    *   After the graph is cleaner (post-Step 3), implement `embedder.py` to generate Node2Vec embeddings and store them.

---

## 6. Required Libraries
*   `sentence-transformers`
*   `scikit-learn`
*   `networkx`
*   `node2vec` (optional, or implement simple random walk)
