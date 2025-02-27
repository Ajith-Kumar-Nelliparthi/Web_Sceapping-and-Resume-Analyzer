from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import requests
import re                              # Import the regular expression module for text processing
from bs4 import BeautifulSoup          # Import the BeautifulSoup module for web scraping
import PyPDF2                          # Import the PyPDF2 module for PDF processing

app = Flask(__name__)

# Function to clean extracted text
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)           # Replace multiple newlines with a single newline
    text = re.sub(r'\s+', ' ', text)            # Replace multiple spaces with a single space
    text = re.sub(r'[^\x00-\x7F]+', '', text)   # Remove non-ASCII characters
    return text.strip()

# Function to scrape website with content filtering
def scrape_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove unwanted elements
        for tag in soup(["script", "style", "nav", "aside", "footer"]):
            tag.decompose()

        # Extract meaningful content
        main_content = soup.find("article") or soup.find("main") or soup.body
        text = main_content.get_text(separator=" ", strip=True) if main_content else "No meaningful content found."
        cleaned_text = clean_text(text)

        data = {
            'title': soup.title.string if soup.title else 'No Title',
            'text': cleaned_text
        }

        json_filename = "scraped_data.json"
        with open(json_filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        return json_filename
    except Exception as e:
        return str(e)

# Function to extract text from resume
def extract_text_from_resume(resume_file):
    pdf_reader = PyPDF2.PdfReader(resume_file)
    text = "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return clean_text(text)

# Function to analyze missing skills
def analyze_missing_skills(resume_text, job_role):
    job_skills = {
        "Data Scientist": ["Python", "Machine Learning", "Deep Learning", "SQL", "NLP"],
        "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Flask"],
        "AI Engineer": ["TensorFlow", "PyTorch", "Deep Learning", "AI Ethics"],
        "Software Engineer": ["Java", "C++", "Python", "System Design", "Algorithms"],
        "DevOps Engineer": ["Docker", "Kubernetes", "CI/CD", "Terraform", "AWS"],
        "Cybersecurity Analyst": ["Network Security", "Penetration Testing", "SIEM", "Cryptography"],
        "Cloud Engineer": ["AWS", "Azure", "Google Cloud", "Infrastructure as Code"],
        "Database Administrator": ["SQL", "NoSQL", "Database Tuning", "Backup & Recovery"],
        "QA Engineer": ["Selenium", "JUnit", "Test Automation", "Bug Tracking"],
        "Mobile Developer": ["Swift", "Kotlin", "Flutter", "React Native"],
        "UI/UX Designer": ["Figma", "Sketch", "User Research", "Wireframing"],
        "Game Developer": ["Unity", "Unreal Engine", "C#", "Game Physics"],
        "Embedded Systems Engineer": ["C", "C++", "Microcontrollers", "RTOS"],
        "Blockchain Developer": ["Solidity", "Ethereum", "Smart Contracts", "Cryptography"],
        "ML Engineer": ["TensorFlow", "PyTorch", "Scikit-learn", "MLOps"]
    }
    required_skills = job_skills.get(job_role, [])
    missing_skills = [skill for skill in required_skills if skill.lower() not in resume_text.lower()]
    return missing_skills

# Predefined skill descriptions
def fill_missing_skills(missing_skills):
    skill_descriptions = {
        "Python": "Python is a versatile programming language used for data analysis, web development, and automation.",
        "Machine Learning": "Machine learning involves training algorithms to recognize patterns and make predictions.",
        "Deep Learning": "Deep learning is a subset of ML focused on neural networks and large-scale data modeling.",
        "SQL": "SQL is a language for managing and querying relational databases.",
        "NLP": "Natural Language Processing enables machines to understand and process human language.",
        "HTML": "HTML is the standard language for creating web pages.",
        "CSS": "CSS is used to style web pages and enhance their visual presentation.",
        "JavaScript": "JavaScript is a programming language for adding interactivity to web pages.",
        "React": "React is a JavaScript library for building user interfaces.",
        "Flask": "Flask is a lightweight Python web framework for building web applications.",
        "TensorFlow": "TensorFlow is an open-source machine learning framework for numerical computations.",
        "PyTorch": "PyTorch is a deep learning framework known for dynamic computation graphs.",
        "AI Ethics": "AI Ethics involves understanding the ethical implications of AI technologies.",
        "Java": "Java is a widely-used programming language for building cross-platform applications.",
        "C++": "C++ is a high-performance language often used for systems programming.",
        "System Design": "System design is the process of defining architecture and components of a system.",
        "Algorithms": "Algorithms are step-by-step procedures for solving problems efficiently.",
        "Docker": "Docker is a containerization platform for deploying applications consistently.",
        "Kubernetes": "Kubernetes is an orchestration tool for managing containerized applications.",
        "CI/CD": "Continuous Integration and Continuous Deployment automate software delivery.",
        "Terraform": "Terraform is an infrastructure as code tool for managing cloud resources.",
        "AWS": "Amazon Web Services provides cloud computing solutions.",
        "Network Security": "Network Security involves protecting data from cyber threats.",
        "Penetration Testing": "Penetration Testing simulates cyberattacks to identify vulnerabilities.",
        "SIEM": "Security Information and Event Management (SIEM) helps monitor security threats.",
        "Cryptography": "Cryptography ensures data security through encryption and decryption.",
        "Swift": "Swift is a programming language for developing iOS applications.",
        "Kotlin": "Kotlin is a modern programming language used for Android development.",
        "Flutter": "Flutter is a UI toolkit for building cross-platform mobile apps.",
        "React Native": "React Native allows developers to build mobile apps using JavaScript.",
        "Figma": "Figma is a collaborative tool for UI/UX design.",
        "Sketch": "Sketch is a vector graphics editor for designing user interfaces.",
        "User Research": "User Research involves studying user behavior to improve product design.",
        "Wireframing": "Wireframing is the process of creating basic design layouts for apps and websites."
    }
    return {skill: skill_descriptions.get(skill, "Description not available.") for skill in missing_skills}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    option = request.form['option']
    if option == 'website':
        url = request.form['url']
        json_file = scrape_website(url)
        return send_file(json_file, as_attachment=True)
    elif option == 'resume':
        resume = request.files['resume']
        job_role = request.form['job_role']
        resume_text = extract_text_from_resume(resume)
        missing_skills = analyze_missing_skills(resume_text, job_role)
        filled_skills = fill_missing_skills(missing_skills)
        return render_template('result.html', missing_skills=missing_skills, filled_skills=filled_skills)

if __name__ == '__main__':
    app.run(debug=True)
