import sqlite3
import json
import time
import logging

class CallDatabase:
    def __init__(self, db_path='calls.db'):
        self.db_path = db_path
        self._initialize_db()
        
    def _initialize_db(self):
        """Create database and tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create calls table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_id TEXT UNIQUE,
            lead_id TEXT,
            phone_number TEXT,
            campaign_id TEXT,
            status TEXT,
            start_time REAL,
            end_time REAL,
            metadata TEXT,
            transcript TEXT,
            analytics TEXT
        )
        ''')
        
        conn.commit()
        conn.close()

    def create_call(self, call_data):
        """Create a new call record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata = json.dumps(call_data.get('metadata', {}))
        
        cursor.execute('''
        INSERT INTO calls (
            call_id, lead_id, phone_number, campaign_id, 
            status, start_time, metadata
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            call_data['call_id'],
            call_data['lead_id'],
            call_data['phone_number'],
            call_data['campaign_id'],
            call_data['status'],
            call_data['start_time'],
            metadata
        ))
        
        conn.commit()
        conn.close()

    def get_call(self, call_id):
        """Get call details by call_id"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM calls WHERE call_id = ?', (call_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            result = dict(row)
            result['metadata'] = json.loads(result['metadata'])
            if result['analytics']:
                result['analytics'] = json.loads(result['analytics'])
            return result
        return None

    def update_call(self, call_id, update_data):
        """Update call details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Handle JSON fields
        if 'metadata' in update_data:
            update_data['metadata'] = json.dumps(update_data['metadata'])
        if 'analytics' in update_data:
            update_data['analytics'] = json.dumps(update_data['analytics'])
            
        # Construct SET clause dynamically
        set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(call_id)
        
        cursor.execute(
            f"UPDATE calls SET {set_clause} WHERE call_id = ?",
            values
        )
        
        conn.commit()
        conn.close()

    def get_active_calls_count(self):
        """Get count of active calls"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM calls WHERE status IN ('initiated', 'in-progress')"
        )
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

    def get_campaign_stats(self, campaign_id, start_time=None, end_time=None):
        """Get statistics for a campaign"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT 
            COUNT(*) as total_calls,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_calls,
            AVG(CASE WHEN end_time IS NOT NULL THEN end_time - start_time ELSE NULL END) as avg_duration
        FROM calls 
        WHERE campaign_id = ?
        """
        params = [campaign_id]
        
        if start_time:
            query += " AND start_time >= ?"
            params.append(start_time)
        if end_time:
            query += " AND start_time <= ?"
            params.append(end_time)
            
        cursor.execute(query, params)
        stats = dict(zip(['total_calls', 'completed_calls', 'avg_duration'], cursor.fetchone()))
        
        conn.close()
        return stats