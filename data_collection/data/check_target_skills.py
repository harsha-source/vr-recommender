import json

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    skills_data = load_json('/Users/harsha/PycharmProjects/vr_recommender/data_collection/data/skills.json')
    existing_skill_names = {s['name'].lower() for s in skills_data}
    
    target_skills = [
        "Machine Learning",
        "Data Science",
        "Java",
        "Public Speaking",
        "Data Visualization",
        "Cybersecurity",
        "Cyber Security" # check alias
    ]
    
    print("Checking for target skills:")
    for skill in target_skills:
        if skill.lower() in existing_skill_names:
            print(f"[FOUND] {skill}")
        else:
            print(f"[MISSING] {skill}")

if __name__ == "__main__":
    main()
