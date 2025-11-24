# ai/domain_knowledge.py
import json
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DomainKnowledgeManager:
    def __init__(self, db_path: str = "domain_knowledge.db"):
        self.db_path = db_path
        self.domains = {}
        self.setup_database()
        self.load_domains()
    
    def setup_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain_id INTEGER,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                keywords TEXT,
                confidence REAL DEFAULT 1.0,
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (domain_id) REFERENCES domains (id),
                UNIQUE(domain_id, question)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain_id INTEGER,
                question TEXT,
                answer TEXT,
                user_feedback INTEGER,
                response_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (domain_id) REFERENCES domains (id)
            )
        ''')
        
        # Indexlar
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain_question ON knowledge_items(domain_id, question)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords ON knowledge_items(keywords)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_count ON knowledge_items(usage_count DESC)')
        
        conn.commit()
        conn.close()
        
        # Standart domainlarni yuklash
        self.load_default_domains()
    
    def load_default_domains(self):
        """Standart domainlarni yuklash"""
        default_domains = {
            "legal": {
                "description": "Yuridik soha - shartnomalar, qonunlar, huquqiy masalalar",
                "knowledge": [
                    {
                        "question": "What is a breach of contract?",
                        "answer": "A breach of contract occurs when one party fails to fulfill their obligations as specified in the contract without a valid legal excuse.",
                        "keywords": "breach contract obligation legal excuse"
                    },
                    {
                        "question": "What should be included in a contract?",
                        "answer": "A contract should include: parties involved, subject matter, terms and conditions, payment details, duration, termination clauses, and dispute resolution methods.",
                        "keywords": "contract parties terms payment duration termination dispute"
                    }
                ]
            },
            "education": {
                "description": "Ta'lim sohasi - o'qitish metodlari, pedagogika, o'quv dasturlari",
                "knowledge": [
                    {
                        "question": "What is differentiated instruction?",
                        "answer": "Differentiated instruction is a teaching approach that tailors instruction to meet individual student needs and learning styles.",
                        "keywords": "differentiated instruction teaching learning students"
                    },
                    {
                        "question": "What is formative assessment?",
                        "answer": "Formative assessment is ongoing evaluation during the learning process to monitor student progress and provide feedback.",
                        "keywords": "formative assessment evaluation learning progress feedback"
                    }
                ]
            },
            "medical": {
                "description": "Tibbiyot sohasi - sog'liq, kasalliklar, davolash usullari",
                "knowledge": [
                    {
                        "question": "What are vital signs?",
                        "answer": "Vital signs include body temperature, pulse rate, respiration rate, and blood pressure. These measurements indicate the state of a patient's essential body functions.",
                        "keywords": "vital signs temperature pulse respiration blood pressure"
                    }
                ]
            },
            "technology": {
                "description": "Texnologiya sohasi - dasturlash, AI, IT infratuzilmasi",
                "knowledge": [
                    {
                        "question": "What is machine learning?",
                        "answer": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.",
                        "keywords": "machine learning AI artificial intelligence data"
                    }
                ]
            }
        }
        
        for domain_name, domain_data in default_domains.items():
            self.add_domain(domain_name, domain_data["description"])
            for knowledge_item in domain_data["knowledge"]:
                self.add_knowledge(
                    domain_name,
                    knowledge_item["question"],
                    knowledge_item["answer"],
                    knowledge_item.get("keywords", "")
                )
    
    def add_domain(self, domain_name: str, description: str = "") -> bool:
        """Yangi domain qo'shish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO domains (name, description) VALUES (?, ?)",
                (domain_name, description)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error adding domain {domain_name}: {e}")
            return False
        finally:
            conn.close()
    
    def add_knowledge(self, domain_name: str, question: str, answer: str, keywords: str = "") -> bool:
        """Yangi bilim qo'shish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Domain ID ni olish
            cursor.execute("SELECT id FROM domains WHERE name = ?", (domain_name,))
            domain_result = cursor.fetchone()
            
            if not domain_result:
                logger.error(f"Domain not found: {domain_name}")
                return False
            
            domain_id = domain_result[0]
            
            # Bilim qo'shish
            cursor.execute('''
                INSERT OR REPLACE INTO knowledge_items 
                (domain_id, question, answer, keywords, last_used) 
                VALUES (?, ?, ?, ?, ?)
            ''', (domain_id, question, answer, keywords, datetime.now()))
            
            conn.commit()
            logger.info(f"Knowledge added to domain {domain_name}: {question[:50]}...")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error adding knowledge: {e}")
            return False
        finally:
            conn.close()
    
    def get_knowledge(self, domain_name: str) -> List[Dict[str, Any]]:
        """Domain bilimlarini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT k.question, k.answer, k.keywords, k.confidence, k.usage_count
                FROM knowledge_items k
                JOIN domains d ON k.domain_id = d.id
                WHERE d.name = ?
                ORDER BY k.usage_count DESC, k.confidence DESC
            ''', (domain_name,))
            
            results = cursor.fetchall()
            knowledge_list = []
            
            for question, answer, keywords, confidence, usage_count in results:
                knowledge_list.append({
                    "question": question,
                    "answer": answer,
                    "keywords": keywords,
                    "confidence": confidence,
                    "usage_count": usage_count
                })
            
            return knowledge_list
            
        except sqlite3.Error as e:
            logger.error(f"Error getting knowledge for {domain_name}: {e}")
            return []
        finally:
            conn.close()
    
    def increment_usage(self, domain_name: str, question: str):
        """Foydalanish sonini oshirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE knowledge_items 
                SET usage_count = usage_count + 1, last_used = ?
                WHERE question = ? AND domain_id IN (
                    SELECT id FROM domains WHERE name = ?
                )
            ''', (datetime.now(), question, domain_name))
            
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error incrementing usage: {e}")
        finally:
            conn.close()
    
    def search_knowledge(self, query: str, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Bilimlarni qidirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if domain:
                cursor.execute('''
                    SELECT k.question, k.answer, k.keywords, k.confidence, d.name as domain_name
                    FROM knowledge_items k
                    JOIN domains d ON k.domain_id = d.id
                    WHERE d.name = ? AND (
                        k.question LIKE ? OR k.answer LIKE ? OR k.keywords LIKE ?
                    )
                    ORDER BY k.usage_count DESC, k.confidence DESC
                    LIMIT 10
                ''', (domain, f'%{query}%', f'%{query}%', f'%{query}%'))
            else:
                cursor.execute('''
                    SELECT k.question, k.answer, k.keywords, k.confidence, d.name as domain_name
                    FROM knowledge_items k
                    JOIN domains d ON k.domain_id = d.id
                    WHERE k.question LIKE ? OR k.answer LIKE ? OR k.keywords LIKE ?
                    ORDER BY k.usage_count DESC, k.confidence DESC
                    LIMIT 10
                ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            results = cursor.fetchall()
            search_results = []
            
            for question, answer, keywords, confidence, domain_name in results:
                search_results.append({
                    "question": question,
                    "answer": answer,
                    "keywords": keywords,
                    "confidence": confidence,
                    "domain": domain_name
                })
            
            return search_results
            
        except sqlite3.Error as e:
            logger.error(f"Error searching knowledge: {e}")
            return []
        finally:
            conn.close()
    
    def get_domain_stats(self) -> Dict[str, Any]:
        """Domain statistikasini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT d.name, COUNT(k.id), SUM(k.usage_count), MAX(k.last_used)
                FROM domains d
                LEFT JOIN knowledge_items k ON d.id = k.domain_id
                GROUP BY d.name
            ''')
            
            results = cursor.fetchall()
            stats = {}
            
            for domain_name, knowledge_count, total_usage, last_used in results:
                stats[domain_name] = {
                    "knowledge_count": knowledge_count or 0,
                    "total_usage": total_usage or 0,
                    "last_used": last_used
                }
            
            return stats
            
        except sqlite3.Error as e:
            logger.error(f"Error getting domain stats: {e}")
            return {}
        finally:
            conn.close()
    
    def export_knowledge(self, file_path: str):
        """Bilimlarni eksport qilish"""
        try:
            export_data = {}
            stats = self.get_domain_stats()
            
            for domain_name in stats.keys():
                knowledge = self.get_knowledge(domain_name)
                export_data[domain_name] = knowledge
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Knowledge exported to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting knowledge: {e}")
    
    def import_knowledge(self, file_path: str):
        """Bilimlarni import qilish"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            for domain_name, knowledge_list in import_data.items():
                self.add_domain(domain_name)
                for item in knowledge_list:
                    self.add_knowledge(
                        domain_name,
                        item["question"],
                        item["answer"],
                        item.get("keywords", "")
                    )
            
            logger.info(f"Knowledge imported from {file_path}")
            
        except Exception as e:
            logger.error(f"Error importing knowledge: {e}")
    
    def load_domains(self):
        """Domainlarni memoryga yuklash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT d.name, k.question, k.answer, k.keywords
                FROM domains d
                JOIN knowledge_items k ON d.id = k.domain_id
                ORDER BY d.name, k.usage_count DESC
            ''')
            
            results = cursor.fetchall()
            
            for domain_name, question, answer, keywords in results:
                if domain_name not in self.domains:
                    self.domains[domain_name] = []
                
                self.domains[domain_name].append({
                    "question": question,
                    "answer": answer,
                    "keywords": keywords
                })
            
            logger.info(f"Loaded {len(self.domains)} domains into memory")
            
        except sqlite3.Error as e:
            logger.error(f"Error loading domains: {e}")
        finally:
            conn.close()