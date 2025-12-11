import json
import os

DATA_DIR = '/Users/harsha/PycharmProjects/vr_recommender/data_collection/data'
SKILLS_PATH = os.path.join(DATA_DIR, 'skills.json')

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    skills = load_json(SKILLS_PATH)
    
    new_skills = [
        {
            "name": "Model Training",
            "aliases": ["Training ML Models", "Model Fitting"],
            "category": "technical",
            "source_count": 1,
            "weight": 0.9
        },
        {
            "name": "Software Architecture",
            "aliases": ["System Architecture", "Software Design"],
            "category": "technical",
            "source_count": 1,
            "weight": 0.95
        },
        {
            "name": "Code Analysis",
            "aliases": ["Static Analysis", "Code Review"],
            "category": "technical",
            "source_count": 1,
            "weight": 0.85
        },
        {
            "name": "Refactoring",
            "aliases": ["Code Refactoring", "Code Improvement"],
            "category": "technical",
            "source_count": 1,
            "weight": 0.9
        },
        {
            "name": "Confidence",
            "aliases": ["Self-Confidence", "Self-Assurance"],
            "category": "soft",
            "source_count": 1,
            "weight": 0.8
        },
        {
            "name": "Speech Analysis",
            "aliases": ["Voice Analysis", "Speech Pattern Analysis"],
            "category": "technical",
            "source_count": 1,
            "weight": 0.85
        },
        {
            "name": "Soft Skills",
            "aliases": ["Interpersonal Skills", "People Skills"],
            "category": "soft",
            "source_count": 1,
            "weight": 1.0
        },
        {
            "name": "Threat Analysis",
            "aliases": ["Threat Modeling", "Security Threat Analysis"],
            "category": "technical",
            "source_count": 1,
            "weight": 0.9
        },
        {
            "name": "Vulnerability Assessment",
            "aliases": ["Vulnerability Scanning", "Security Assessment"],
            "category": "technical",
            "source_count": 1,
            "weight": 0.9
        }
    ]

    # Check if they already exist (just in case)
    existing_names = {s['name'] for s in skills}
    
    added_count = 0
    for new_skill in new_skills:
        if new_skill['name'] not in existing_names:
            skills.append(new_skill)
            added_count += 1
            print(f"Added skill: {new_skill['name']}")
        else:
            print(f"Skill already exists: {new_skill['name']}")

    save_json(SKILLS_PATH, skills)
    print(f"Successfully added {added_count} new skills to skills.json")

if __name__ == "__main__":
    main()
