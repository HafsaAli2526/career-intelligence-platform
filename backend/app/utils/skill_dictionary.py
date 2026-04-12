
from typing import Set, List, Dict
import json
from pathlib import Path

class SkillDictionary:
    """
    Manages comprehensive skills dictionary
    Categorizes skills into different domains
    """
    
    def __init__(self, custom_dict_path: str = None):
        """
        Initialize with built-in skills or load from JSON
        Args:
            custom_dict_path: Path to custom skills JSON file
        """
        if custom_dict_path and Path(custom_dict_path).exists():
            self.load_from_json(custom_dict_path)
        else:
            self.skills = self._load_default_skills()
            self.categories = self._load_default_categories()
    
    def _load_default_skills(self) -> Set[str]:
        """Load comprehensive default skills dictionary"""
        return {
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php',
            'ruby', 'go', 'rust', 'kotlin', 'swift', 'r', 'matlab', 'scala',
            'perl', 'dart', 'objective-c', 'c', 'assembly', 'vba',
            
            # Web Frontend
            'html', 'css', 'react', 'angular', 'vue', 'nextjs', 'nuxtjs',
            'svelte', 'jquery', 'bootstrap', 'tailwind', 'sass', 'less',
            'webpack', 'babel', 'vite', 'parcel',
            
            # Web Backend
            'nodejs', 'express', 'django', 'flask', 'fastapi', 'spring boot',
            'asp.net', 'laravel', 'ruby on rails', 'gin', 'fiber', 'nestjs',
            
            # Mobile Development
            'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic',
            'kotlin', 'swift', 'objective-c',
            
            # Databases
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'oracle', 'sql server', 'dynamodb', 'cassandra', 'neo4j',
            'sqlite', 'mariadb', 'couchdb', 'firebase',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'github actions', 'gitlab ci', 'terraform', 'ansible', 'ci/cd',
            'aws lambda', 'ec2', 's3', 'cloudformation', 'helm', 'istio',
            
            # Data Science & ML
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'keras', 'opencv', 'spacy', 'transformers', 'langchain',
            'matplotlib', 'seaborn', 'jupyter', 'data analysis',
            
            # Big Data
            'hadoop', 'spark', 'kafka', 'airflow', 'hive', 'pig',
            
            # Version Control
            'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial',
            
            # Testing
            'pytest', 'jest', 'selenium', 'cypress', 'junit', 'mocha',
            'unittest', 'testing', 'tdd', 'bdd', 'postman',
            
            # Project Management Tools
            'jira', 'confluence', 'trello', 'asana', 'monday',
            
            # Other Tools
            'linux', 'agile', 'scrum', 'restful api', 'graphql',
            'microservices', 'websockets', 'blockchain', 'rabbitmq',
            'nginx', 'apache', 'redis', 'memcached',
            
            # Soft Skills
            'communication', 'leadership', 'teamwork', 'problem solving',
            'analytical thinking', 'creativity', 'time management',
            'adaptability', 'critical thinking', 'collaboration',
            'project management', 'attention to detail', 'presentation',
            'negotiation', 'conflict resolution', 'mentoring'
        }
    
    def _load_default_categories(self) -> Dict[str, List[str]]:
        """Load skill categories"""
        return {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#',
                'go', 'rust', 'kotlin', 'swift', 'php', 'ruby', 'r'
            ],
            'web_frontend': [
                'html', 'css', 'react', 'angular', 'vue', 'nextjs',
                'typescript', 'javascript', 'tailwind', 'bootstrap', 'sass'
            ],
            'web_backend': [
                'nodejs', 'django', 'flask', 'fastapi', 'express',
                'spring boot', 'laravel', 'asp.net', 'nestjs'
            ],
            'mobile': [
                'android', 'ios', 'react native', 'flutter', 'swift',
                'kotlin', 'xamarin', 'ionic'
            ],
            'databases': [
                'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
                'sql', 'oracle', 'dynamodb', 'cassandra', 'firebase'
            ],
            'cloud_devops': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
                'terraform', 'ci/cd', 'ansible', 'github actions'
            ],
            'data_ml': [
                'machine learning', 'deep learning', 'tensorflow', 'pytorch',
                'pandas', 'numpy', 'scikit-learn', 'nlp', 'data analysis'
            ],
            'soft_skills': [
                'communication', 'leadership', 'teamwork', 'problem solving',
                'analytical thinking', 'project management', 'collaboration'
            ]
        }
    
    def get_all_skills(self) -> Set[str]:
        """Get all skills"""
        return self.skills
    
    def get_skills_by_category(self, category: str) -> List[str]:
        """Get skills for a specific category"""
        return self.categories.get(category, [])
    
    def is_skill(self, text: str) -> bool:
        """Check if text is a known skill"""
        return text.lower().strip() in self.skills
    
    def categorize_skill(self, skill: str) -> str:
        """Determine category of a skill"""
        skill_lower = skill.lower().strip()
        
        for category, skills in self.categories.items():
            if skill_lower in [s.lower() for s in skills]:
                return category
        
        return 'other'
    
    def save_to_json(self, filepath: str):
        """Save skills dictionary to JSON file"""
        data = {
            'skills': sorted(list(self.skills)),
            'categories': self.categories
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_json(self, filepath: str):
        """Load skills dictionary from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.skills = set(data.get('skills', []))
        self.categories = data.get('categories', {})