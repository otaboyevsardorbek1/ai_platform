# ai/nlp_processor.py
import re
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self):
        self.vectorizers = {}
        self.knowledge_base = {}
        self.setup_nltk()
    
    def setup_nltk(self):
        """NLTK ni sozlash"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
    
    def preprocess_text(self, text: str) -> str:
        """Matnni qayta ishlash"""
        if not text:
            return ""
        
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        tokens = nltk.word_tokenize(text)
        tokens = [token for token in tokens if token not in self.stop_words]
        return ' '.join(tokens)
    
    def load_domain_knowledge(self, domain_knowledge: Dict):
        """Domain bilimlarini yuklash"""
        self.knowledge_base = domain_knowledge
        
        # Har bir domain uchun vectorizer yaratish
        for domain, knowledge_list in domain_knowledge.items():
            questions = [item["question"] for item in knowledge_list]
            processed_questions = [self.preprocess_text(q) for q in questions]
            
            vectorizer = TfidfVectorizer(max_features=1000)
            vectorizer.fit(processed_questions)
            self.vectorizers[domain] = vectorizer
    
    def find_best_answer(self, question: str, domain: str = "general") -> Tuple[str, float]:
        """Eng yaxshi javobni topish"""
        if domain not in self.knowledge_base:
            return "I don't have knowledge about this domain yet.", 0.0
        
        processed_question = self.preprocess_text(question)
        knowledge_list = self.knowledge_base[domain]
        
        if not knowledge_list:
            return "No knowledge available for this domain.", 0.0
        
        # TF-IDF vektorlari
        questions = [item["question"] for item in knowledge_list]
        processed_questions = [self.preprocess_text(q) for q in questions]
        
        vectorizer = self.vectorizers.get(domain)
        if vectorizer is None:
            return "Domain model not trained yet.", 0.0
        
        try:
            # Similarity hisoblash
            question_vec = vectorizer.transform([processed_question])
            knowledge_vecs = vectorizer.transform(processed_questions)
            
            similarities = cosine_similarity(question_vec, knowledge_vecs)
            best_match_idx = np.argmax(similarities)
            best_similarity = similarities[0][best_match_idx]
            
            if best_similarity > 0.3:  # Threshold
                best_answer = knowledge_list[best_match_idx]["answer"]
                return best_answer, float(best_similarity)
            else:
                return self.get_fallback_response(question), 0.0
                
        except Exception as e:
            logger.error(f"Error in similarity calculation: {e}")
            return "I encountered an error processing your question.", 0.0
    
    def get_fallback_response(self, question: str) -> str:
        """Standart javoblar"""
        fallback_responses = [
            "I'm still learning about this topic. Could you provide more context?",
            "That's an interesting question. Let me research this further.",
            "I understand your question, but I need more specific information.",
            "Could you rephrase your question or ask about another topic?",
            "I'm continuously learning. Please try another question."
        ]
        
        import random
        return random.choice(fallback_responses)
    
    def add_knowledge(self, domain: str, question: str, answer: str, keywords: str = ""):
        """Yangi bilim qo'shish"""
        if domain not in self.knowledge_base:
            self.knowledge_base[domain] = []
        
        self.knowledge_base[domain].append({
            "question": question,
            "answer": answer,
            "keywords": keywords
        })
        
        # Vectorizer ni qayta train qilish
        questions = [item["question"] for item in self.knowledge_base[domain]]
        processed_questions = [self.preprocess_text(q) for q in questions]
        
        vectorizer = TfidfVectorizer(max_features=1000)
        vectorizer.fit(processed_questions)
        self.vectorizers[domain] = vectorizer