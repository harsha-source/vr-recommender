import json
import os

DATA_DIR = '/Users/harsha/PycharmProjects/vr_recommender/data_collection/data'
VR_APPS_PATH = os.path.join(DATA_DIR, 'vr_apps.json')
APP_SKILLS_PATH = os.path.join(DATA_DIR, 'app_skills.json')

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    vr_apps = load_json(VR_APPS_PATH)
    app_skills = load_json(APP_SKILLS_PATH)

    new_apps = [
        # Machine Learning
        {
            "app_id": "NeuralNet_VR",
            "name": "NeuralNet VR",
            "category": "education",
            "description": "Visualize and interact with neural networks in 3D. Understand backpropagation and activation functions intuitively.",
            "features": ["3D Neural Network Visualization", "Interactive Activation Functions", "Real-time Training Visualization"],
            "skills_developed": ["Machine Learning", "Deep Learning", "Neural Networks", "Artificial Intelligence"],
            "rating": 4.5,
            "price": "$14.99"
        },
        {
            "app_id": "ML_Lab_VR",
            "name": "ML Lab VR",
            "category": "education",
            "description": "Build and train machine learning models in a virtual laboratory environment. Experiment with different algorithms and datasets.",
            "features": ["Virtual ML Workbench", "Algorithm Selection", "Dataset Exploration"],
            "skills_developed": ["Machine Learning", "Data Science", "Model Training", "Python"],
            "rating": 4.3,
            "price": "$19.99"
        },
        # Data Science
        {
            "app_id": "DataVerse",
            "name": "DataVerse",
            "category": "productivity",
            "description": "Explore complex datasets in immersive 3D. Identify patterns and outliers that are hard to see on 2D screens.",
            "features": ["Immersive Data Exploration", "Pattern Recognition Tools", "Collaborative Analysis"],
            "skills_developed": ["Data Science", "Data Analysis", "Pattern Recognition", "Big Data"],
            "rating": 4.6,
            "price": "$29.99"
        },
        {
            "app_id": "StatSim_VR",
            "name": "StatSim VR",
            "category": "education",
            "description": "Interactive statistical simulations. Experience probability distributions and statistical concepts firsthand.",
            "features": ["Interactive Simulations", "Probability Experiments", "Statistical Modeling"],
            "skills_developed": ["Data Science", "Statistics", "Probability", "Mathematics"],
            "rating": 4.2,
            "price": "$9.99"
        },
        # Java
        {
            "app_id": "JavaWorld",
            "name": "JavaWorld",
            "category": "education",
            "description": "Learn Java concepts through gamified challenges. Solve coding puzzles to progress through the world.",
            "features": ["Gamified Coding Challenges", "Java Syntax Practice", "Object-Oriented Concepts"],
            "skills_developed": ["Java", "Programming", "Object-Oriented Programming", "Problem Solving"],
            "rating": 4.4,
            "price": "$12.99"
        },
        {
            "app_id": "CodeCity_Java",
            "name": "CodeCity: Java Edition",
            "category": "productivity",
            "description": "Visualize Java codebases as cities. Classes are buildings, methods are rooms. Navigate code structure spatially.",
            "features": ["Codebase Visualization", "Dependency Mapping", "Refactoring Tools"],
            "skills_developed": ["Java", "Software Architecture", "Code Analysis", "Refactoring"],
            "rating": 4.7,
            "price": "$24.99"
        },
        # Public Speaking
        {
            "app_id": "Virtual_Podium",
            "name": "Virtual Podium",
            "category": "training",
            "description": "Practice speeches in front of a realistic virtual audience. Adjust audience size and behavior to test your nerves.",
            "features": ["Realistic Audience Simulation", "Distraction Settings", "Timer and Notes"],
            "skills_developed": ["Public Speaking", "Communication", "Confidence", "Presentation"],
            "rating": 4.8,
            "price": "$19.99"
        },
        {
            "app_id": "SpeechMaster_VR",
            "name": "SpeechMaster VR",
            "category": "training",
            "description": "AI-driven feedback on your speaking skills. Analyze your pace, tone, and eye contact in real-time.",
            "features": ["AI Speech Analysis", "Real-time Feedback", "Eye Contact Tracking"],
            "skills_developed": ["Public Speaking", "Communication", "Speech Analysis", "Soft Skills"],
            "rating": 4.6,
            "price": "$29.99"
        },
        # Data Visualization
        {
            "app_id": "ImmersiveCharts",
            "name": "ImmersiveCharts",
            "category": "productivity",
            "description": "Create and walk through 3D charts. Present data in a compelling and memorable way.",
            "features": ["3D Chart Creation", "Walk-through Presentations", "Data Storytelling"],
            "skills_developed": ["Data Visualization", "Presentation", "Data Storytelling", "Communication"],
            "rating": 4.5,
            "price": "$14.99"
        },
        {
            "app_id": "GraphWalk",
            "name": "GraphWalk",
            "category": "productivity",
            "description": "Explore large network graphs in VR. Understand connections and relationships in complex systems.",
            "features": ["Large Graph Rendering", "Node Interaction", "Pathfinding Visualization"],
            "skills_developed": ["Data Visualization", "Network Analysis", "Graph Theory", "Systems Thinking"],
            "rating": 4.4,
            "price": "$19.99"
        },
        # Cybersecurity
        {
            "app_id": "CyberDefend_VR",
            "name": "CyberDefend VR",
            "category": "training",
            "description": "Defend a virtual network from cyber attacks. Monitor traffic, identify threats, and deploy countermeasures.",
            "features": ["Network Defense Simulation", "Threat Detection", "Incident Response"],
            "skills_developed": ["Cybersecurity", "Network Security", "Incident Response", "Threat Analysis"],
            "rating": 4.7,
            "price": "$39.99"
        },
        {
            "app_id": "EthicalHacker_VR",
            "name": "EthicalHacker VR",
            "category": "education",
            "description": "Learn penetration testing in a safe environment. Find vulnerabilities and exploit them to understand security flaws.",
            "features": ["Penetration Testing Labs", "Vulnerability Scanning", "Exploit Simulation"],
            "skills_developed": ["Cybersecurity", "Ethical Hacking", "Penetration Testing", "Vulnerability Assessment"],
            "rating": 4.6,
            "price": "$34.99"
        }
    ]

    # Generate app_skills entries
    new_app_skills = []
    for app in new_apps:
        for skill in app['skills_developed']:
            new_app_skills.append({
                "source_id": app['app_id'],
                "source_type": "app",
                "skill_name": skill,
                "weight": 0.9  # Default high weight for primary skills
            })

    # Append new data
    vr_apps.extend(new_apps)
    app_skills.extend(new_app_skills)

    # Save files
    save_json(VR_APPS_PATH, vr_apps)
    save_json(APP_SKILLS_PATH, app_skills)

    print(f"Added {len(new_apps)} new VR apps and {len(new_app_skills)} new app_skills entries.")

if __name__ == "__main__":
    main()
