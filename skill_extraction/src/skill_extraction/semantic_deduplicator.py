"""
Semantic Skill Deduplication using Embeddings and Clustering
"""

import sys
import os
from typing import List, Dict, Tuple
import numpy as np
from collections import Counter

# Add stage2/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.models import Skill
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering

class SemanticDeduplicator:
    """
    Deduplicates skills using semantic embeddings and clustering.
    Replaces strict string matching with "Fuzzy Semantic" matching.
    """

    def __init__(self, normalizer, model_name='all-MiniLM-L6-v2', distance_threshold=0.25):
        """
        Args:
            normalizer: Existing SkillNormalizer for basic cleaning
            model_name: HuggingFace model for embeddings
            distance_threshold: Cosine distance threshold for clustering (0.0 - 1.0).
                                Lower = stricter matching. 0.25 is a good starting point.
        """
        self.normalizer = normalizer
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.distance_threshold = distance_threshold

    def deduplicate(self, skills: List[Dict]) -> List[Skill]:
        """
        Merge semantically similar skills.
        
        Process:
        1. Normalize strings (basic cleaning).
        2. Group by normalized string to get raw counts.
        3. Compute embeddings for unique strings.
        4. Cluster embeddings.
        5. Pick canonical name for each cluster.
        6. Merge stats (counts, weights).
        """
        if not skills:
            return []

        # --- Step 1: Pre-processing ---
        # Map: Normalized Name -> List of original skill dicts
        # This groups exact string matches first (to save embedding compute)
        grouped_skills = {}
        
        for s in skills:
            if not isinstance(s, dict) or "name" not in s:
                continue
                
            # Use existing normalizer for basic cleanup (trimming, casing, explicit aliases)
            # This handles "Python" vs "python" vs "PYTHON"
            norm_name = self.normalizer.normalize(s["name"])
            
            if norm_name not in grouped_skills:
                grouped_skills[norm_name] = []
            grouped_skills[norm_name].append(s)
            
        unique_names = list(grouped_skills.keys())
        if not unique_names:
            return []

        print(f"Semantic Dedup: {len(skills)} raw skills -> {len(unique_names)} unique strings (pre-clustering)")

        # --- Step 2: Embedding & Clustering ---
        # Only encode if we have enough items to cluster
        if len(unique_names) > 1:
            embeddings = self.model.encode(unique_names, batch_size=32, show_progress_bar=True)
            
            # Normalize embeddings to unit length for cosine distance
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

            # Agglomerative Clustering with Cosine Distance
            # distance_threshold determines cut-off. Linkage='average' works well for "clouds" of synonyms.
            clustering = AgglomerativeClustering(
                n_clusters=None,
                metric='cosine',
                linkage='average',
                distance_threshold=self.distance_threshold
            )
            cluster_labels = clustering.fit_predict(embeddings)
        else:
            cluster_labels = [0]

        # --- Step 3: Merging by Cluster ---
        # Map: Cluster ID -> List of unique_names belonging to it
        clusters = {}
        for idx, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(unique_names[idx])

        final_skills = []

        for label, names_in_cluster in clusters.items():
            # Gather all raw skill instances for this cluster
            cluster_raw_instances = []
            for name in names_in_cluster:
                cluster_raw_instances.extend(grouped_skills[name])

            # --- Step 4: Canonicalization ---
            # Heuristic: Pick the most frequent name in this cluster as the Canonical Name
            # If tie, pick the shortest one (usually "Python" is better than "Python Programming" as a label)
            name_counts = Counter()
            for instance in cluster_raw_instances:
                # Use the normalized name from Step 1
                n_name = self.normalizer.normalize(instance["name"])
                name_counts[n_name] += 1
                
            # Sort by frequency (desc), then length (asc)
            sorted_candidates = sorted(
                name_counts.items(), 
                key=lambda x: (-x[1], len(x[0]))
            )
            canonical_name = sorted_candidates[0][0]

            # Aggregate Metadata
            aliases = set()
            max_weight = 0.0
            total_count = 0
            categories = []

            for instance in cluster_raw_instances:
                total_count += 1
                max_weight = max(max_weight, float(instance.get("weight", 0.5)))
                
                # Collect aliases (original raw names)
                raw_original = instance["name"].strip()
                if raw_original.lower() != canonical_name.lower():
                    aliases.add(raw_original)
                
                # Collect normalized variants in this cluster as aliases too if different
                norm_variant = self.normalizer.normalize(raw_original)
                if norm_variant != canonical_name:
                    aliases.add(norm_variant)

                # Vote on Category
                cat = instance.get("category", "technical")
                if cat in ["technical", "soft", "domain"]:
                    categories.append(cat)
                else:
                    # Try auto-classify
                    categories.append(self.normalizer.get_category(canonical_name))

            # Determine majority category
            if categories:
                final_category = Counter(categories).most_common(1)[0][0]
            else:
                final_category = "technical"

            final_skills.append(Skill(
                name=canonical_name,
                aliases=list(aliases),
                category=final_category,
                source_count=total_count,
                weight=max_weight
            ))
            
        return final_skills

    def merge_skill_lists(self, skill_lists: List[List[Dict]]) -> List[Skill]:
        """Wrapper to merge list of lists"""
        all_skills = []
        for sl in skill_lists:
            all_skills.extend(sl)
        return self.deduplicate(all_skills)
