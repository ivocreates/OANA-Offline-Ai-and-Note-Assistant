"""
Database module for OANA - Offline AI and Note Assistant
Handles SQLite database operations for chat history and document storage
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class OANADatabase:
    """SQLite database handler for OANA application"""
    
    def __init__(self, db_path: str = "oana.db"):
        """Initialize database connection and create tables"""
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create chat_sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    title TEXT,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Create chat_history table (updated with session reference)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
                )
            ''')
            
            # Create documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    content TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    upload_time TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Create sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat_history(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_active ON documents(is_active)')
            
            conn.commit()
            
    def add_chat_message(self, role: str, message: str, session_id: str = "default") -> int:
        """Add a chat message to the database and ensure session exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Ensure session exists
            cursor.execute('SELECT session_id FROM chat_sessions WHERE session_id = ?', (session_id,))
            if not cursor.fetchone():
                self.create_chat_session(session_id)
            
            # Add message
            cursor.execute('''
                INSERT INTO chat_history (session_id, role, message, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (session_id, role, message, datetime.now().isoformat()))
            
            # Update session timestamp
            cursor.execute('''
                UPDATE chat_sessions 
                SET updated_at = ? 
                WHERE session_id = ?
            ''', (datetime.now().isoformat(), session_id))
            
            conn.commit()
            return cursor.lastrowid
            
    def get_chat_history(self, session_id: str = "default", limit: int = 100) -> List[Dict]:
        """Get chat history for a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, role, message FROM chat_history
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (session_id, limit))
            
            results = cursor.fetchall()
            return [
                {"timestamp": row[0], "role": row[1], "message": row[2]}
                for row in reversed(results)  # Reverse to get chronological order
            ]
            
    def clear_chat_history(self, session_id: str = "default") -> int:
        """Clear chat history for a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM chat_history WHERE session_id = ?', (session_id,))
            conn.commit()
            return cursor.rowcount
            
    # Chat Session Management
    def create_chat_session(self, session_id: str, title: str = None) -> str:
        """Create a new chat session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if not title:
                title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
            cursor.execute('''
                INSERT OR REPLACE INTO chat_sessions (session_id, title, updated_at)
                VALUES (?, ?, ?)
            ''', (session_id, title, datetime.now().isoformat()))
            
            conn.commit()
            return session_id
            
    def update_chat_session(self, session_id: str, title: str = None, summary: str = None):
        """Update chat session metadata"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if title:
                updates.append("title = ?")
                params.append(title)
                
            if summary:
                updates.append("summary = ?")
                params.append(summary)
                
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(session_id)
            
            cursor.execute(f'''
                UPDATE chat_sessions 
                SET {', '.join(updates)}
                WHERE session_id = ?
            ''', params)
            
            conn.commit()
            
    def get_chat_sessions(self, limit: int = 50) -> List[Dict]:
        """Get all chat sessions ordered by most recent"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_id, title, summary, created_at, updated_at,
                       (SELECT COUNT(*) FROM chat_history WHERE session_id = cs.session_id) as message_count
                FROM chat_sessions cs
                WHERE is_active = 1
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            return [
                {
                    "session_id": row[0],
                    "title": row[1],
                    "summary": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                    "message_count": row[5]
                }
                for row in results
            ]
            
    def delete_chat_session(self, session_id: str):
        """Delete a chat session and its messages"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete chat history first
            cursor.execute('DELETE FROM chat_history WHERE session_id = ?', (session_id,))
            
            # Then delete session
            cursor.execute('DELETE FROM chat_sessions WHERE session_id = ?', (session_id,))
            
            conn.commit()
            
    def generate_chat_summary(self, session_id: str) -> str:
        """Generate a summary for a chat session based on first few messages"""
        messages = self.get_chat_history(session_id, limit=5)
        
        if not messages:
            return "Empty chat"
            
        # Create summary from first user message or first few words
        first_user_msg = next((msg for msg in messages if msg['role'] == 'user'), None)
        if first_user_msg:
            text = first_user_msg['message']
            # Take first 50 characters and add ellipsis if longer
            summary = text[:50] + "..." if len(text) > 50 else text
            return summary
        
        return f"Chat from {messages[0]['timestamp'][:10]}"
            
    def add_document(self, name: str, path: str, content: str, file_type: str, file_size: int) -> int:
        """Add a document to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT INTO documents (name, path, content, file_type, file_size, upload_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, path, content, file_type, file_size, upload_time))
            
            conn.commit()
            return cursor.lastrowid
            
    def get_documents(self, active_only: bool = True) -> List[Dict]:
        """Get all documents from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT id, name, path, content, file_type, file_size, upload_time
                FROM documents
            '''
            params = []
            
            if active_only:
                query += ' WHERE is_active = ?'
                params.append(1)
                
            query += ' ORDER BY upload_time DESC'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "path": row[2],
                    "content": row[3],
                    "type": row[4],
                    "size": row[5],
                    "upload_time": row[6]
                }
                for row in results
            ]
            
    def remove_document(self, document_id: int) -> bool:
        """Remove a document (soft delete)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE documents SET is_active = 0 WHERE id = ?
            ''', (document_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
    def delete_document_permanently(self, document_id: int) -> bool:
        """Permanently delete a document"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
            conn.commit()
            return cursor.rowcount > 0
            
    def get_document_by_name(self, name: str) -> Optional[Dict]:
        """Get a document by name"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, path, content, file_type, file_size, upload_time
                FROM documents
                WHERE name = ? AND is_active = 1
            ''', (name,))
            
            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "name": result[1],
                    "path": result[2],
                    "content": result[3],
                    "type": result[4],
                    "size": result[5],
                    "upload_time": result[6]
                }
            return None
            
    def save_setting(self, key: str, value: str) -> None:
        """Save a setting to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            
            conn.commit()
            
    def get_setting(self, key: str, default_value: str = None) -> Optional[str]:
        """Get a setting from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            
            return result[0] if result else default_value
            
    def get_all_settings(self) -> Dict[str, str]:
        """Get all settings from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT key, value FROM settings')
            results = cursor.fetchall()
            
            return {row[0]: row[1] for row in results}
            
    def create_session(self, session_id: str, title: str = None) -> int:
        """Create a new chat session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sessions (session_id, title)
                VALUES (?, ?)
            ''', (session_id, title))
            
            conn.commit()
            return cursor.lastrowid
            
    def get_sessions(self) -> List[Dict]:
        """Get all chat sessions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_id, title, created_at, last_accessed
                FROM sessions
                ORDER BY last_accessed DESC
            ''')
            
            results = cursor.fetchall()
            return [
                {
                    "session_id": row[0],
                    "title": row[1],
                    "created_at": row[2],
                    "last_accessed": row[3]
                }
                for row in results
            ]
            
    def update_session_access(self, session_id: str) -> None:
        """Update last accessed time for a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions 
                SET last_accessed = CURRENT_TIMESTAMP
                WHERE session_id = ?
            ''', (session_id,))
            
            conn.commit()
            
    def get_stats(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get message count
            cursor.execute('SELECT COUNT(*) FROM chat_history')
            message_count = cursor.fetchone()[0]
            
            # Get document count
            cursor.execute('SELECT COUNT(*) FROM documents WHERE is_active = 1')
            document_count = cursor.fetchone()[0]
            
            # Get session count
            cursor.execute('SELECT COUNT(*) FROM sessions')
            session_count = cursor.fetchone()[0]
            
            # Get total file size
            cursor.execute('SELECT SUM(file_size) FROM documents WHERE is_active = 1')
            total_size = cursor.fetchone()[0] or 0
            
            return {
                "messages": message_count,
                "documents": document_count,
                "sessions": session_count,
                "total_file_size": total_size
            }
            
    def backup_to_json(self, backup_path: str) -> bool:
        """Backup database to JSON file"""
        try:
            backup_data = {
                "chat_history": [],
                "documents": [],
                "settings": self.get_all_settings(),
                "sessions": self.get_sessions(),
                "backup_timestamp": datetime.now().isoformat()
            }
            
            # Get all chat history
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT timestamp, role, message, session_id FROM chat_history ORDER BY timestamp')
                for row in cursor.fetchall():
                    backup_data["chat_history"].append({
                        "timestamp": row[0],
                        "role": row[1],
                        "message": row[2],
                        "session_id": row[3]
                    })
                    
                # Get all documents (excluding content for size reasons)
                cursor.execute('''
                    SELECT name, path, file_type, file_size, upload_time 
                    FROM documents WHERE is_active = 1
                ''')
                for row in cursor.fetchall():
                    backup_data["documents"].append({
                        "name": row[0],
                        "path": row[1],
                        "file_type": row[2],
                        "file_size": row[3],
                        "upload_time": row[4]
                    })
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
            
    def close(self):
        """Close database connection (not needed with context manager, but good practice)"""
        pass