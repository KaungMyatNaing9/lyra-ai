import google.generativeai as genai
import streamlit as st
from datetime import datetime

# Configure Gemini API
genai.configure(api_key=st.secrets["API_KEY"])

def generate_practice_questions(context, topic, num_questions=5):
    """Generate practice questions based on course material"""
    
    prompt = f"""
Based on the following course material, generate {num_questions} multiple-choice questions for exam preparation.

Course Material:
{context}

Topic Focus: {topic}

Format each question exactly as:
QUESTION: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
CORRECT: [A/B/C/D]
EXPLANATION: [brief explanation]
---

Generate {num_questions} questions now.
"""
    
    try:
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
        questions = parse_quiz_questions(response.text)
        return questions
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return []

def parse_quiz_questions(text):
    """Parse generated questions into structured format"""
    questions = []
    current_q = {}
    
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('QUESTION:'):
            if current_q:
                questions.append(current_q)
            current_q = {'question': line.replace('QUESTION:', '').strip(), 'options': []}
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            current_q['options'].append(line)
        elif line.startswith('CORRECT:'):
            current_q['correct'] = line.replace('CORRECT:', '').strip()
        elif line.startswith('EXPLANATION:'):
            current_q['explanation'] = line.replace('EXPLANATION:', '').strip()
        elif line == '---' and current_q:
            questions.append(current_q)
            current_q = {}
    
    if current_q and 'question' in current_q:
        questions.append(current_q)
    
    return questions

def generate_flashcards(context, topic, num_cards=6):
    """Generate front/back flashcards from course material"""
    prompt = f"""
You are an experienced study coach. Create {num_cards} high-yield flashcards to help a student review the topic "{topic}".

Use only the following course material:
{context}

Follow this exact format for every card:
FLASHCARD:
FRONT: [short prompt or question]
BACK: [clear answer or explanation]
TIP: [memory tip or real-world hook]
---

Generate {num_cards} cards now.
"""
    try:
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
        return parse_flashcards(response.text)
    except Exception as e:
        st.error(f"Error generating flashcards: {e}")
        return []

def parse_flashcards(text):
    """Parse flashcards from Gemini response"""
    cards = []
    current_card = {}
    
    for raw_line in text.split('\n'):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("FLASHCARD"):
            if current_card:
                cards.append(current_card)
            current_card = {}
        elif line.startswith("FRONT:"):
            current_card['front'] = line.replace("FRONT:", "").strip()
        elif line.startswith("BACK:"):
            current_card['back'] = line.replace("BACK:", "").strip()
        elif line.startswith("TIP:"):
            current_card['tip'] = line.replace("TIP:", "").strip()
        elif line == "---" and current_card:
            cards.append(current_card)
            current_card = {}
    
    if current_card:
        cards.append(current_card)
    
    return cards

def provide_exam_feedback(score, total):
    """Provide personalized feedback based on exam performance"""
    percentage = (score / total) * 100
    
    if percentage >= 90:
        feedback = "Excellent work! You have a strong grasp of this material. 🌟"
        level = "Advanced"
    elif percentage >= 75:
        feedback = "Good job! You understand most concepts well. Keep practicing! 👍"
        level = "Proficient"
    elif percentage >= 60:
        feedback = "You're making progress. Review the topics you missed and try again. 📚"
        level = "Developing"
    else:
        feedback = "You may need more study time on this topic. Don't worry - learning takes time! 💪"
        level = "Needs Review"
    
    return feedback, level

def update_progress_tracking(topic, score):
    """Update student's progress on specific topics"""
    if topic not in st.session_state.student_profile['exam_scores']:
        st.session_state.student_profile['exam_scores'][topic] = []
    
    st.session_state.student_profile['exam_scores'][topic].append({
        'score': score,
        'date': datetime.now().isoformat()
    })
