"""
VR Recommendation Analytics Demo
Demonstrates analytics capabilities with sample data
"""

import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Tuple


class VRRecommendationAnalyticsDemo:
    """Demo analytics class showing what the analytics would look like"""

    def __init__(self):
        """Initialize with sample data"""
        print("✓ Analytics Demo initialized with sample data!")
        
        # Sample data that would be stored in MongoDB
        self.sample_data = [
            {
                "timestamp": datetime.utcnow() - timedelta(days=1),
                "student_query": {
                    "query": "I want to learn about machine learning and its applications in public policy",
                    "interests": ["machine learning", "public policy", "data science"],
                    "background": "Bachelor's in Computer Science, interested in social impact"
                },
                "recommendations": [
                    {"app_name": "Neural Explorer VR", "likeliness_score": 1.0, "category": "Machine Learning"},
                    {"app_name": "AI Visualization Studio", "likeliness_score": 1.0, "category": "Machine Learning"},
                    {"app_name": "PolicyVR", "likeliness_score": 1.0, "category": "Public Policy"},
                    {"app_name": "CodeVR Workspace", "likeliness_score": 0.67, "category": "Programming"},
                    {"app_name": "DataVR", "likeliness_score": 0.33, "category": "Data Science"}
                ],
                "total_apps_recommended": 5,
                "high_score_apps": 3,
                "categories": ["Machine Learning", "Public Policy", "Programming", "Data Science"]
            },
            {
                "timestamp": datetime.utcnow() - timedelta(days=2),
                "student_query": {
                    "query": "I'm interested in cybersecurity and policy management",
                    "interests": ["cybersecurity", "policy", "management"],
                    "background": "Information Systems graduate"
                },
                "recommendations": [
                    {"app_name": "Cyber Range VR", "likeliness_score": 1.0, "category": "Cybersecurity"},
                    {"app_name": "PolicyVR", "likeliness_score": 0.8, "category": "Public Policy"},
                    {"app_name": "Horizon Workrooms", "likeliness_score": 0.6, "category": "Project Management"},
                    {"app_name": "Security Training VR", "likeliness_score": 0.9, "category": "Cybersecurity"}
                ],
                "total_apps_recommended": 4,
                "high_score_apps": 3,
                "categories": ["Cybersecurity", "Public Policy", "Project Management"]
            },
            {
                "timestamp": datetime.utcnow() - timedelta(days=3),
                "student_query": {
                    "query": "I want to learn data analytics and visualization techniques",
                    "interests": ["data analytics", "visualization", "statistics"],
                    "background": "Business Administration student"
                },
                "recommendations": [
                    {"app_name": "DataViz VR", "likeliness_score": 1.0, "category": "Data Analytics"},
                    {"app_name": "Tableau VR", "likeliness_score": 0.9, "category": "Data Analytics"},
                    {"app_name": "Virtualitics VR", "likeliness_score": 0.8, "category": "Data Science"},
                    {"app_name": "Analytics Space", "likeliness_score": 0.7, "category": "Data Analytics"},
                    {"app_name": "Spatial Analytics", "likeliness_score": 0.6, "category": "Data Science"}
                ],
                "total_apps_recommended": 5,
                "high_score_apps": 4,
                "categories": ["Data Analytics", "Data Science"]
            },
            {
                "timestamp": datetime.utcnow() - timedelta(days=4),
                "student_query": {
                    "query": "I need programming and development tools for policy analysis",
                    "interests": ["programming", "development", "policy analysis"],
                    "background": "Public Policy graduate"
                },
                "recommendations": [
                    {"app_name": "CodeVR Workspace", "likeliness_score": 1.0, "category": "Programming"},
                    {"app_name": "Immersed", "likeliness_score": 0.8, "category": "Programming"},
                    {"app_name": "PolicyVR", "likeliness_score": 0.7, "category": "Public Policy"},
                    {"app_name": "Virtual Desktop", "likeliness_score": 0.6, "category": "Programming"}
                ],
                "total_apps_recommended": 4,
                "high_score_apps": 2,
                "categories": ["Programming", "Public Policy"]
            },
            {
                "timestamp": datetime.utcnow() - timedelta(days=5),
                "student_query": {
                    "query": "I want to explore machine learning applications in finance",
                    "interests": ["machine learning", "finance", "ai"],
                    "background": "Finance and Economics student"
                },
                "recommendations": [
                    {"app_name": "Neural Explorer VR", "likeliness_score": 1.0, "category": "Machine Learning"},
                    {"app_name": "AI Visualization Studio", "likeliness_score": 0.9, "category": "Machine Learning"},
                    {"app_name": "Finance Simulator VR", "likeliness_score": 0.8, "category": "Finance"},
                    {"app_name": "Trading Floor VR", "likeliness_score": 0.7, "category": "Finance"},
                    {"app_name": "DataVR", "likeliness_score": 0.5, "category": "Data Science"}
                ],
                "total_apps_recommended": 5,
                "high_score_apps": 3,
                "categories": ["Machine Learning", "Finance", "Data Science"]
            }
        ]

    def get_total_recommendations(self) -> int:
        """Get total number of recommendations stored"""
        return len(self.sample_data)

    def get_app_recommendation_counts(self) -> Dict[str, int]:
        """Get count of how many times each app was recommended"""
        app_counts = defaultdict(int)
        for record in self.sample_data:
            for app in record["recommendations"]:
                app_counts[app["app_name"]] += 1
        return dict(sorted(app_counts.items(), key=lambda x: x[1], reverse=True))

    def get_category_recommendation_counts(self) -> Dict[str, int]:
        """Get count of how many times each category was recommended"""
        category_counts = defaultdict(int)
        for record in self.sample_data:
            for app in record["recommendations"]:
                category_counts[app["category"]] += 1
        return dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))

    def get_interest_analysis(self) -> Dict[str, int]:
        """Analyze which interests lead to most recommendations"""
        interest_counts = defaultdict(int)
        for record in self.sample_data:
            for interest in record["student_query"]["interests"]:
                interest_counts[interest] += 1
        return dict(sorted(interest_counts.items(), key=lambda x: x[1], reverse=True))

    def get_high_score_apps(self, threshold: float = 0.8) -> List[Dict]:
        """Get apps that consistently get high likeliness scores"""
        app_scores = defaultdict(list)
        for record in self.sample_data:
            for app in record["recommendations"]:
                if app["likeliness_score"] >= threshold:
                    app_scores[app["app_name"]].append({
                        "score": app["likeliness_score"],
                        "category": app["category"]
                    })
        
        high_score_apps = []
        for app_name, scores in app_scores.items():
            avg_score = sum(s["score"] for s in scores) / len(scores)
            high_score_apps.append({
                "_id": app_name,
                "count": len(scores),
                "avg_score": avg_score,
                "category": scores[0]["category"]
            })
        
        return sorted(high_score_apps, key=lambda x: (x["avg_score"], x["count"]), reverse=True)

    def get_query_pattern_analysis(self) -> List[Dict]:
        """Analyze query patterns and their associated recommendations"""
        patterns = []
        for record in self.sample_data:
            patterns.append({
                "_id": record["student_query"]["query"],
                "count": 1,
                "avg_apps_recommended": record["total_apps_recommended"],
                "avg_high_score_apps": record["high_score_apps"],
                "categories": record["categories"]
            })
        return patterns

    def print_summary_report(self):
        """Print a formatted summary report"""
        print("\n" + "="*80)
        print("VR RECOMMENDATION ANALYTICS SUMMARY (DEMO)")
        print("="*80)
        
        total_recs = self.get_total_recommendations()
        print(f"\n📊 Total Recommendations Stored: {total_recs}")
        
        if total_recs == 0:
            print("⚠ No recommendations found in database")
            return
        
        # Top recommended apps
        app_counts = self.get_app_recommendation_counts()
        print(f"\n🏆 TOP 10 MOST RECOMMENDED APPS:")
        print("-" * 50)
        for i, (app, count) in enumerate(list(app_counts.items())[:10], 1):
            print(f"  {i:2d}. {app:<25} ({count} times)")
        
        # Top categories
        category_counts = self.get_category_recommendation_counts()
        print(f"\n📂 TOP CATEGORIES BY RECOMMENDATIONS:")
        print("-" * 50)
        for i, (category, count) in enumerate(list(category_counts.items())[:5], 1):
            print(f"  {i}. {category:<20} ({count} recommendations)")
        
        # Interest analysis
        interest_counts = self.get_interest_analysis()
        print(f"\n🎯 TOP INTERESTS:")
        print("-" * 50)
        for i, (interest, count) in enumerate(list(interest_counts.items())[:5], 1):
            print(f"  {i}. {interest:<20} ({count} queries)")
        
        # High score apps
        high_score_apps = self.get_high_score_apps()
        print(f"\n⭐ HIGH-SCORING APPS (≥80% likeliness):")
        print("-" * 50)
        for i, app_data in enumerate(high_score_apps[:5], 1):
            print(f"  {i}. {app_data['_id']:<25} (avg: {app_data['avg_score']:.2f}, {app_data['count']} times)")
        
        # Query patterns
        patterns = self.get_query_pattern_analysis()
        print(f"\n🔍 RECENT QUERY PATTERNS:")
        print("-" * 50)
        for i, pattern in enumerate(patterns[:3], 1):
            print(f"  {i}. \"{pattern['_id'][:50]}{'...' if len(pattern['_id']) > 50 else ''}\"")
            print(f"     Apps recommended: {pattern['avg_apps_recommended']}, High-score apps: {pattern['avg_high_score_apps']}")
        
        print("\n" + "="*80)
        print("💡 This is a demo with sample data. With MongoDB running, you'd see real analytics!")
        print("="*80)


def main():
    """Main function to run analytics demo"""
    try:
        # Initialize analytics demo
        analytics = VRRecommendationAnalyticsDemo()
        
        # Generate and print summary report
        analytics.print_summary_report()
        
    except Exception as e:
        print(f"✗ Error running analytics demo: {e}")


if __name__ == "__main__":
    main()

