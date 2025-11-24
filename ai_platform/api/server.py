# api/server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import time
import uuid

from ai.nlp_processor import NLPProcessor
from database.models import DatabaseManager
from config.settings import settings

class ChatRequest(BaseModel):
    question: str
    domain: str = "general"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    response_time: float
    confidence: float
    domain: str

class AIPlatformAPI:
    def __init__(self):
        self.app = FastAPI(
            title=settings.APP_NAME,
            version=settings.VERSION,
            docs_url=settings.API_DOCS_URL
        )
        
        # Komponentlarni yuklash
        self.db = DatabaseManager(settings.DATABASE_URL)
        self.ai_processor = NLPProcessor()
        self.ai_processor.load_domain_knowledge(settings.DOMAIN_KNOWLEDGE)
        
        # Middleware sozlash
        self.setup_middleware()
        # Route'larni sozlash
        self.setup_routes()
    
    def setup_middleware(self):
        """Middleware sozlash"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Route'larni sozlash"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": f"Welcome to {settings.APP_NAME}",
                "version": settings.VERSION,
                "status": "running"
            }
        
        @self.app.post("/api/chat", response_model=ChatResponse)
        async def chat_endpoint(request: ChatRequest):
            start_time = time.time()
            
            # Session ID yaratish
            session_id = request.session_id or str(uuid.uuid4())
            
            # AI dan javob olish
            answer, confidence = self.ai_processor.find_best_answer(
                request.question, 
                request.domain
            )
            
            response_time = time.time() - start_time
            
            # Database ga saqlash
            self.db.add_conversation(
                user_id=1,  # Default user
                session_id=session_id,
                question=request.question,
                answer=answer,
                domain=request.domain,
                response_time=response_time
            )
            
            return ChatResponse(
                answer=answer,
                session_id=session_id,
                response_time=response_time,
                confidence=confidence,
                domain=request.domain
            )
        
        @self.app.get("/api/domains")
        async def get_domains():
            return {
                "domains": list(settings.DOMAIN_KNOWLEDGE.keys()),
                "total_domains": len(settings.DOMAIN_KNOWLEDGE)
            }
        
        @self.app.post("/api/knowledge/{domain}")
        async def add_knowledge(domain: str, question: str, answer: str, keywords: str = ""):
            self.ai_processor.add_knowledge(domain, question, answer, keywords)
            return {"message": "Knowledge added successfully", "domain": domain}
    
    def run(self, host: str = None, port: int = None):
        """Serverni ishga tushirish"""
        host = host or settings.API_HOST
        port = port or settings.API_PORT
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info" if settings.DEBUG else "warning"
        )

# Global instance
api_server = AIPlatformAPI()
app = api_server.app