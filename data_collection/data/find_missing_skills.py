import json

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    skills_data = load_json('/Users/harsha/PycharmProjects/vr_recommender/data_collection/data/skills.json')
    course_skills_data = load_json('/Users/harsha/PycharmProjects/vr_recommender/data_collection/data/course_skills.json')

    existing_skill_names = {s['name'] for s in skills_data}
    # Also check aliases just in case, though usually we want the canonical name
    for s in skills_data:
        for alias in s.get('aliases', []):
            existing_skill_names.add(alias)

    missing_skills = set()
    for cs in course_skills_data:
        skill_name = cs['skill_name']
        if skill_name not in existing_skill_names:
            missing_skills.add(skill_name)

    print(f"Found {len(missing_skills)} missing skills.")
    for skill in sorted(missing_skills):
        print(skill)

if __name__ == "__main__":
    main()
