# api/routes.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import uuid

from ai.nlp_processor import NLPProcessor
from ai.domain_knowledge import DomainKnowledgeManager
from database.models import DatabaseManager
from config.settings import settings

# Router yaratish
router = APIRouter()

# Pydantic modellari
class KnowledgeItem(BaseModel):
    question: str
    answer: str
    keywords: Optional[str] = ""
    confidence: Optional[float] = 1.0

class DomainInfo(BaseModel):
    name: str
    description: str
    knowledge_count: int
    total_usage: int

class SearchRequest(BaseModel):
    query: str
    domain: Optional[str] = None
    limit: Optional[int] = 10

class VoiceRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    domain: Optional[str] = "general"

class VoiceResponse(BaseModel):
    text: str
    answer: str
    response_time: float
    session_id: str

# Global instances
db_manager = DatabaseManager(settings.DATABASE_URL)
domain_manager = DomainKnowledgeManager()
ai_processor = NLPProcessor()

# Domain bilimlarini yuklash
@router.on_event("startup")
async def startup_event():
    """Startup da domain bilimlarini yuklash"""
    domains_data = {}
    for domain_name in settings.DOMAIN_KNOWLEDGE.keys():
        knowledge = domain_manager.get_knowledge(domain_name)
        domains_data[domain_name] = knowledge
    
    ai_processor.load_domain_knowledge(domains_data)
    print("Domain knowledge loaded successfully")

# Domain boshqaruvi
@router.get("/domains", response_model=List[DomainInfo])
async def get_all_domains():
    """Barcha domainlarni olish"""
    stats = domain_manager.get_domain_stats()
    domains_info = []
    
    for domain_name, domain_stats in stats.items():
        # Domain description ni olish
        conn = db_manager.get_session()
        try:
            result = conn.execute(
                "SELECT description FROM domains WHERE name = ?",
                (domain_name,)
            )
            description_row = result.fetchone()
            description = description_row[0] if description_row else ""
        finally:
            conn.close()
        
        domains_info.append(DomainInfo(
            name=domain_name,
            description=description,
            knowledge_count=domain_stats["knowledge_count"],
            total_usage=domain_stats["total_usage"]
        ))
    
    return domains_info

@router.post("/domains/{domain_name}")
async def create_domain(domain_name: str, description: str = ""):
    """Yangi domain yaratish"""
    success = domain_manager.add_domain(domain_name, description)
    if not success:
        raise HTTPException(status_code=400, detail="Domain already exists or invalid")
    return {"message": f"Domain '{domain_name}' created successfully"}

# Bilimlar boshqaruvi
@router.get("/domains/{domain_name}/knowledge", response_model=List[KnowledgeItem])
async def get_domain_knowledge(domain_name: str, limit: int = Query(50, ge=1, le=1000)):
    """Domain bilimlarini olish"""
    knowledge = domain_manager.get_knowledge(domain_name)
    if not knowledge:
        raise HTTPException(status_code=404, detail="Domain not found or no knowledge")
    
    return knowledge[:limit]

@router.post("/domains/{domain_name}/knowledge")
async def add_knowledge_item(domain_name: str, item: KnowledgeItem):
    """Domainga yangi bilim qo'shish"""
    success = domain_manager.add_knowledge(
        domain_name, 
        item.question, 
        item.answer, 
        item.keywords
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add knowledge item")
    
    # AI processorni yangilash
    knowledge = domain_manager.get_knowledge(domain_name)
    ai_processor.load_domain_knowledge({domain_name: knowledge})
    
    return {"message": "Knowledge item added successfully"}

@router.delete("/domains/{domain_name}/knowledge")
async def delete_knowledge_item(domain_name: str, question: str):
    """Bilim elementini o'chirish"""
    # Bu funksiya domain_knowledge.py ga qo'shilishi kerak
    # Soddalik uchun faqat struktura ko'rsatilgan
    return {"message": "Delete functionality to be implemented"}

# Qidiruv
@router.post("/search", response_model=List[KnowledgeItem])
async def search_knowledge(request: SearchRequest):
    """Bilimlarni qidirish"""
    results = domain_manager.search_knowledge(request.query, request.domain)
    return results

# Statistikalar
@router.get("/stats/domains")
async def get_domain_statistics():
    """Domain statistikasi"""
    stats = domain_manager.get_domain_stats()
    return stats

@router.get("/stats/usage")
async def get_usage_statistics(days: int = Query(7, ge=1, le=365)):
    """Foydalanish statistikasi"""
    conn = db_manager.get_session()
    try:
        # Oxirgi kunlar uchun chat statistikasi
        result = conn.execute('''
            SELECT domain, COUNT(*) as count, AVG(response_time) as avg_time
            FROM conversations 
            WHERE created_at >= datetime('now', ?)
            GROUP BY domain
        ''', (f'-{days} days',))
        
        stats = []
        for domain, count, avg_time in result:
            stats.append({
                "domain": domain,
                "request_count": count,
                "average_response_time": avg_time or 0.0
            })
        
        return stats
    finally:
        conn.close()

# Ovozli API
@router.post("/voice/chat", response_model=VoiceResponse)
async def voice_chat_endpoint(request: VoiceRequest):
    """Ovozli chat endpoint"""
    start_time = time.time()
    session_id = str(uuid.uuid4())
    
    try:
        # Base64 audio ni matnga aylantirish
        # Haqiqiy loyihada speech-to-text ishlatiladi
        import base64
        # audio_text = speech_to_text(request.audio_data)  # Haqiqiy implementatsiya
        
        # Hozircha demo uchun
        audio_text = "Hello, this is a voice message"
        
        # AI dan javob olish
        answer, confidence = ai_processor.find_best_answer(audio_text, request.domain)
        
        response_time = time.time() - start_time
        
        # Database ga saqlash
        db_manager.add_conversation(
            user_id=1,  # Default user
            session_id=session_id,
            question=audio_text,
            answer=answer,
            domain=request.domain,
            response_time=response_time
        )
        
        return VoiceResponse(
            text=audio_text,
            answer=answer,
            response_time=response_time,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")

# Eksport/Import
@router.post("/export")
async def export_knowledge(file_path: str = "knowledge_export.json"):
    """Bilimlarni eksport qilish"""
    try:
        domain_manager.export_knowledge(file_path)
        return {"message": f"Knowledge exported to {file_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/import")
async def import_knowledge(file_path: str):
    """Bilimlarni import qilish"""
    try:
        domain_manager.import_knowledge(file_path)
        
        # AI processorni yangilash
        domains_data = {}
        for domain_name in domain_manager.domains.keys():
            knowledge = domain_manager.get_knowledge(domain_name)
            domains_data[domain_name] = knowledge
        
        ai_processor.load_domain_knowledge(domains_data)
        
        return {"message": f"Knowledge imported from {file_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

# Health check va system info
@router.get("/health")
async def health_check():
    """Tizim holatini tekshirish"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "domains_loaded": len(ai_processor.knowledge_base),
        "total_knowledge_items": sum(len(items) for items in ai_processor.knowledge_base.values())
    }

@router.get("/system/info")
async def system_info():
    """Tizim ma'lumotlari"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "debug_mode": settings.DEBUG,
        "api_docs_url": settings.API_DOCS_URL,
        "domains_available": list(settings.DOMAIN_KNOWLEDGE.keys())
    }