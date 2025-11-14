"""
VR Recommendation Analytics System
Analyzes stored recommendation data from MongoDB
"""

import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from pymongo import MongoClient
from typing import Dict, List, Tuple
import json


class VRRecommendationAnalytics:
    """Analytics class for VR recommendation data"""

    def __init__(self, mongodb_uri: str = None):
        """Initialize MongoDB connection for analytics"""
        self.mongodb_uri = mongodb_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        
        try:
            self.mongo_client = MongoClient(self.mongodb_uri)
            self.db = self.mongo_client["vr_recommendations"]
            self.collection = self.db["recommendations"]
            # Test connection
            self.mongo_client.admin.command('ping')
            print("✓ MongoDB analytics connection successful!")
        except Exception as e:
            print(f"✗ MongoDB analytics connection failed: {e}")
            raise

    def get_total_recommendations(self) -> int:
        """Get total number of recommendations stored"""
        return self.collection.count_documents({})

    def get_app_recommendation_counts(self) -> Dict[str, int]:
        """Get count of how many times each app was recommended"""
        pipeline = [
            {"$unwind": "$recommendations"},
            {"$group": {
                "_id": "$recommendations.app_name",
                "count": {"$sum": 1},
                "avg_score": {"$avg": "$recommendations.likeliness_score"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return {result["_id"]: result["count"] for result in results}

    def get_category_recommendation_counts(self) -> Dict[str, int]:
        """Get count of how many times each category was recommended"""
        pipeline = [
            {"$unwind": "$recommendations"},
            {"$group": {
                "_id": "$recommendations.category",
                "count": {"$sum": 1},
                "avg_score": {"$avg": "$recommendations.likeliness_score"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return {result["_id"]: result["count"] for result in results}

    def get_query_pattern_analysis(self) -> Dict[str, any]:
        """Analyze query patterns and their associated recommendations"""
        pipeline = [
            {"$group": {
                "_id": "$student_query.query",
                "count": {"$sum": 1},
                "avg_apps_recommended": {"$avg": "$total_apps_recommended"},
                "avg_high_score_apps": {"$avg": "$high_score_apps"},
                "categories": {"$addToSet": "$categories"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return results

    def get_interest_analysis(self) -> Dict[str, int]:
        """Analyze which interests lead to most recommendations"""
        pipeline = [
            {"$unwind": "$student_query.interests"},
            {"$group": {
                "_id": "$student_query.interests",
                "count": {"$sum": 1},
                "avg_apps": {"$avg": "$total_apps_recommended"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return {result["_id"]: result["count"] for result in results}

    def get_time_based_analysis(self, days: int = 30) -> Dict[str, any]:
        """Get recommendations over time"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {"$group": {
                "_id": {
                    "year": {"$year": "$timestamp"},
                    "month": {"$month": "$timestamp"},
                    "day": {"$dayOfMonth": "$timestamp"}
                },
                "count": {"$sum": 1},
                "avg_apps": {"$avg": "$total_apps_recommended"}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return results

    def get_high_score_apps(self, threshold: float = 0.8) -> List[Dict]:
        """Get apps that consistently get high likeliness scores"""
        pipeline = [
            {"$unwind": "$recommendations"},
            {"$match": {"recommendations.likeliness_score": {"$gte": threshold}}},
            {"$group": {
                "_id": "$recommendations.app_name",
                "count": {"$sum": 1},
                "avg_score": {"$avg": "$recommendations.likeliness_score"},
                "category": {"$first": "$recommendations.category"}
            }},
            {"$sort": {"avg_score": -1, "count": -1}}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return results

    def get_query_to_app_mapping(self) -> Dict[str, List[str]]:
        """Map queries to their most recommended apps"""
        pipeline = [
            {"$unwind": "$recommendations"},
            {"$group": {
                "_id": "$student_query.query",
                "apps": {"$addToSet": "$recommendations.app_name"},
                "top_apps": {
                    "$push": {
                        "app": "$recommendations.app_name",
                        "score": "$recommendations.likeliness_score"
                    }
                }
            }},
            {"$project": {
                "query": "$_id",
                "apps": 1,
                "top_apps": {
                    "$slice": [
                        {
                            "$sortArray": {
                                "input": "$top_apps",
                                "sortBy": {"score": -1}
                            }
                        },
                        5
                    ]
                }
            }}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return {result["query"]: [app["app"] for app in result["top_apps"]] for result in results}

    def generate_comprehensive_report(self) -> Dict[str, any]:
        """Generate a comprehensive analytics report"""
        print("🔍 Generating comprehensive analytics report...")
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_recommendations": self.get_total_recommendations(),
                "total_unique_apps": len(self.get_app_recommendation_counts()),
                "total_categories": len(self.get_category_recommendation_counts())
            },
            "app_statistics": self.get_app_recommendation_counts(),
            "category_statistics": self.get_category_recommendation_counts(),
            "interest_analysis": self.get_interest_analysis(),
            "query_patterns": self.get_query_pattern_analysis(),
            "high_score_apps": self.get_high_score_apps(),
            "query_to_app_mapping": self.get_query_to_app_mapping(),
            "time_analysis": self.get_time_based_analysis()
        }
        
        return report

    def print_summary_report(self):
        """Print a formatted summary report"""
        print("\n" + "="*80)
        print("VR RECOMMENDATION ANALYTICS SUMMARY")
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
        
        print("\n" + "="*80)


def main():
    """Main function to run analytics"""
    try:
        # Initialize analytics
        analytics = VRRecommendationAnalytics()
        
        # Generate and print summary report
        analytics.print_summary_report()
        
        # Generate comprehensive report (optional)
        # report = analytics.generate_comprehensive_report()
        # with open('analytics_report.json', 'w') as f:
        #     json.dump(report, f, indent=2, default=str)
        # print("\n✓ Comprehensive report saved to analytics_report.json")
        
    except Exception as e:
        print(f"✗ Error running analytics: {e}")
        print("\nMake sure MongoDB is running and accessible")


if __name__ == "__main__":
    main()

