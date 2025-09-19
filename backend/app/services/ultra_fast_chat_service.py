"""
Ultra-fast local chatbot service - no model loading, instant responses
"""
import logging
import random

logger = logging.getLogger(__name__)

class UltraFastChatService:
    def __init__(self):
        logger.info("Ultra-fast chat service initialized")
        
        # Comprehensive college Q&A database
        self.responses = {
            # Admission related
            "admission": [
                "College admissions typically open in April-June. Required documents: 12th marksheet, entrance exam scores, ID proof. Contact admissions office for specific requirements.",
                "Admission process includes application form, document verification, entrance test (if applicable), and merit list. Apply early for better chances!"
            ],
            "eligibility": [
                "Eligibility varies by course: Engineering needs 12th with PCM, Arts/Commerce need 12th any stream. Minimum 50% marks generally required.",
                "For UG courses: 12th pass, for PG: Bachelor's degree required. Check specific course requirements on college website."
            ],
            
            # Fees related
            "fees": [
                "Annual fee structure: Tuition ₹40,000-80,000, Hostel ₹25,000-50,000, Other fees ₹5,000-15,000. Exact amounts vary by course.",
                "Fees payment can be done semester-wise or annually. Scholarships available for meritorious students. Contact accounts office for details."
            ],
            "scholarship": [
                "Merit-based and need-based scholarships available. Government scholarships through e-kalyan portal. Apply through college scholarship cell.",
                "Scholarships cover 25-100% tuition fees based on merit/family income. Apply before deadline for consideration."
            ],
            
            # Hostel related  
            "hostel": [
                "Hostel facilities include furnished rooms, mess, Wi-Fi, 24/7 security, recreation room. Fees around ₹30,000-50,000 per year.",
                "Both AC and non-AC rooms available. Mess provides 3 meals daily. Separate hostels for boys and girls. Apply early as seats limited."
            ],
            "mess": [
                "Mess provides nutritious vegetarian meals 3 times daily. Monthly mess charges around ₹3,000-4,000. Special food on festivals.",
                "Mess menu changes weekly with variety of North and South Indian dishes. Hygiene standards maintained strictly."
            ],
            
            # Exam related
            "exam": [
                "Semester exams held in November-December and April-May. Internal assessments throughout semester. Schedules published 1 month advance.",
                "Exam pattern: Theory papers 70%, Internal assessment 30%. Minimum 40% required to pass. Supplementary exams for failed subjects."
            ],
            "result": [
                "Results declared within 45 days of exam completion. Available on college website and notice board. Mark sheets issued after fee clearance.",
                "Grade system followed: A+ (90+), A (80-89), B+ (70-79), B (60-69), C (50-59), F (below 50)."
            ],
            
            # College timing and events
            "opening": [
                "College opening day for 1st years usually in mid-July after admission completion. Orientation programs start 1 week before regular classes.",
                "Academic year starts in July, ends in May. Two semesters: July-December and January-May. Summer break in May-June."
            ],
            "timing": [
                "College timing: 9:00 AM to 4:00 PM on weekdays. Saturday till 1:00 PM. Sunday holiday. Library open till 8:00 PM.",
                "Class duration: 50 minutes each. 15-minute break between periods. Lunch break: 12:30-1:30 PM daily."
            ],
            
            # Courses
            "course": [
                "Available courses: Engineering (CSE, ECE, Mechanical, Civil), Arts (English, History, Political Science), Science (Physics, Chemistry, Maths), Commerce (B.Com, BBA).",
                "Professional courses: MBA, MCA, B.Tech, M.Tech available. Duration: UG 3-4 years, PG 2 years. Check website for complete list."
            ],
            
            # Facilities
            "library": [
                "Central library with 50,000+ books, digital resources, reading hall capacity 300 students. Open 9 AM to 8 PM on weekdays.",
                "Library facilities: Book issue/return, digital library, internet access, photocopy services, group study rooms available."
            ],
            "sports": [
                "Sports facilities: Cricket ground, basketball court, badminton hall, gym, swimming pool. Inter-college tournaments organized regularly.",
                "Sports activities: Morning PT, yoga classes, sports meet, cultural events. Coaching available for various sports."
            ]
        }
        
        # Personal/Identity questions
        self.identity_responses = {
            "name": [
                "I'm SIH Bot, your friendly college assistant! I'm here to help with all your college-related questions.",
                "You can call me SIH Bot! I'm designed to help students with college information and queries.",
                "I'm SIH Bot - think of me as your personal college guide. What would you like to know?"
            ],
            "who": [
                "I'm an AI assistant specifically created to help students with college information. I know about admissions, fees, facilities, and more!",
                "I'm SIH Bot, your college information assistant. I can help you with everything from admission requirements to hostel facilities."
            ],
            "what": [
                "I'm an AI chatbot designed to assist students with college-related questions. Ask me about admissions, fees, courses, or campus life!",
                "I'm here to make your college journey easier by providing instant answers to your questions about academics, facilities, and campus life."
            ],
            "hello": [
                "Hello there! I'm SIH Bot, ready to help with your college questions. What would you like to know?",
                "Hi! Great to meet you. I'm here to assist with any college-related queries you might have.",
                "Hey! Welcome to our college chat assistant. How can I help you today?"
            ],
            "hi": [
                "Hi there! I'm SIH Bot, your college information assistant. What can I help you with?",
                "Hello! Ready to help you with any college questions. What's on your mind?",
                "Hi! I'm here to make your college experience smoother. What would you like to know?"
            ],
            "help": [
                "I can help you with college admissions, fee structures, hostel information, exam schedules, course details, library facilities, sports activities, and much more! What specific information do you need?",
                "I'm equipped to answer questions about: Admissions & eligibility, Fee structure & scholarships, Hostel & mess facilities, Exam schedules & results, Available courses, Library & sports facilities. What interests you?"
            ]
        }
        
        # Hindi mixed responses
        self.hindi_responses = {
            "fees": "Fees ka structure: Annual tuition ₹40,000-80,000, Hostel ₹25,000-50,000 hai. Exact amount ke liye office se contact kariye.",
            "admission": "Admission April-June me hota hai. 12th ke marks, entrance exam, documents chahiye. Office me jaake form bhariye.",
            "hostel": "Hostel facilities achhi hai - furnished rooms, mess, Wi-Fi, security. Fees ₹30,000-50,000 per year. Jaldi apply kariye seats limited hai.",
            "exam": "Exams November-December aur April-May me hote hai. Time table 1 mahine pehle aata hai. Regular study karte rahiye.",
            "opening": "College opening July me hota hai 1st year ke liye. Orientation program 1 week pehle start hota hai.",
            "course": "Courses available hai: Engineering, Arts, Science, Commerce. Website pe complete list check kar sakte hai.",
            "name": "Main SIH Bot hun, aapka college assistant! College ke baare me koi bhi sawal puchiye.",
            "hello": "Namaste! Main SIH Bot hun. College ke admission, fees, hostel ke baare me kuch puchna hai?",
            "hi": "Hello! Main aapki college queries me help kar sakta hun. Kya jaanna chahte hai?",
            "help": "Main college admission, fees, hostel, exam, courses ke baare me batata hun. Kya specific information chahiye?"
        }

    def generate_response(self, question: str, context: str = "") -> dict:
        logger.info(f"Processing question: {question}")
        
        question_lower = question.lower()
        
        # Check for Hindi/mixed language indicators
        hindi_indicators = ["kya", "hai", "kab", "kaise", "kitna", "kahan", "kyun", "kaun"]
        is_hindi_mixed = any(word in question_lower for word in hindi_indicators)
        
        # Find matching keywords and responses
        for keyword in self.responses.keys():
            if keyword in question_lower:
                if is_hindi_mixed and keyword in self.hindi_responses:
                    response = self.hindi_responses[keyword]
                else:
                    response = random.choice(self.responses[keyword])
                
                return {
                    "answer": response,
                    "confidence": 0.9,
                    "source": "ultra-fast-local"
                }
        
        # Fallback responses
        if is_hindi_mixed:
            fallback = "Main college ke admission, fees, hostel, exam aur courses ke baare me help kar sakta hun. Kya puchna chahte hai?"
        else:
            fallback = "I can help with college admissions, fees, hostel info, exam schedules, and course details. What would you like to know?"
        
        return {
            "answer": fallback,
            "confidence": 0.7,
            "source": "ultra-fast-local"
        }

# Global instance
ultra_fast_chat_service = UltraFastChatService()