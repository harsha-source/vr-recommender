import json
import os

DATA_DIR = '/Users/harsha/PycharmProjects/vr_recommender/data_collection/data'
SKILLS_PATH = os.path.join(DATA_DIR, 'skills.json')
VR_APPS_PATH = os.path.join(DATA_DIR, 'vr_apps.json')
APP_SKILLS_PATH = os.path.join(DATA_DIR, 'app_skills.json')
COURSE_SKILLS_PATH = os.path.join(DATA_DIR, 'course_skills.json')

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    print("Loading data files...")
    skills = load_json(SKILLS_PATH)
    vr_apps = load_json(VR_APPS_PATH)
    app_skills = load_json(APP_SKILLS_PATH)
    course_skills = load_json(COURSE_SKILLS_PATH)

    print("Verifying data integrity...")
    
    # Create sets for faster lookup
    skill_names = {s['name'] for s in skills}
    # Add aliases to skill names lookup
    for s in skills:
        for alias in s.get('aliases', []):
            skill_names.add(alias)
            
    app_ids = {app['app_id'] for app in vr_apps}

    errors = []

    # Check app_skills
    for entry in app_skills:
        if entry['source_type'] == 'app':
            if entry['source_id'] not in app_ids:
                errors.append(f"App ID '{entry['source_id']}' in app_skills.json not found in vr_apps.json")
            if entry['skill_name'] not in skill_names:
                # Try case-insensitive match
                found = False
                for s_name in skill_names:
                    if s_name.lower() == entry['skill_name'].lower():
                        found = True
                        break
                if not found:
                    errors.append(f"Skill '{entry['skill_name']}' in app_skills.json not found in skills.json")

    # Check course_skills
    for entry in course_skills:
        if entry['skill_name'] not in skill_names:
             # Try case-insensitive match
            found = False
            for s_name in skill_names:
                if s_name.lower() == entry['skill_name'].lower():
                    found = True
                    break
            if not found:
                errors.append(f"Skill '{entry['skill_name']}' in course_skills.json not found in skills.json")

    if errors:
        print(f"Found {len(errors)} errors:")
        for err in errors[:20]: # Show first 20 errors
            print(f"- {err}")
        if len(errors) > 20:
            print(f"... and {len(errors) - 20} more.")
    else:
        print("Data integrity check passed! No errors found.")

if __name__ == "__main__":
    main()
