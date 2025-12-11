from datetime import datetime
from typing import List, Optional, Dict, Any
from ..mongo_connection import mongo

class CoursesRepository:
    def __init__(self):
        self.collection = mongo.get_collection('courses')

    def find_all(self) -> List[Dict]:
        return list(self.collection.find())

    def find_by_id(self, course_id: str) -> Optional[Dict]:
        return self.collection.find_one({"_id": course_id})

    def find_by_department(self, department: str) -> List[Dict]:
        return list(self.collection.find({"department": department}))

    def insert(self, course: Dict) -> str:
        if 'course_id' in course and '_id' not in course:
            course['_id'] = course['course_id']
            
        course['created_at'] = datetime.utcnow()
        course['updated_at'] = datetime.utcnow()
        self.collection.insert_one(course)
        return course['_id']

    def bulk_upsert(self, courses: List[Dict]) -> int:
        """
        Bulk upsert courses using course_id + semester as unique key.
        This allows the same course to exist in multiple semesters.
        """
        from pymongo import UpdateOne
        if not courses:
            return 0

        operations = []
        for course in courses:
            course_id = course.get('_id') or course.get('course_id') or course.get('number')
            if not course_id:
                continue

            # Use course_id + semester as unique key to allow same course in different semesters
            semester = course.get('semester', '')
            unique_id = f"{course_id}_{semester}" if semester else course_id

            course_copy = course.copy()
            course_copy['_id'] = unique_id  # Use composite key as MongoDB _id
            course_copy['course_id'] = course_id  # Keep original course_id for queries
            course_copy['updated_at'] = datetime.utcnow()

            update_doc = course_copy.copy()
            del update_doc['_id']

            operations.append(UpdateOne(
                {"_id": unique_id},
                {"$set": update_doc, "$setOnInsert": {"created_at": datetime.utcnow()}},
                upsert=True
            ))

        if operations:
            result = self.collection.bulk_write(operations)
            return result.upserted_count + result.modified_count
        return 0

    def count(self) -> int:
        return self.collection.count_documents({})
