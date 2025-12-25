import sqlite3
import os
from datetime import datetime


class Database:
    def __init__(self, db_path="task_manager.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize all database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tasks table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS tasks
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           title
                           TEXT
                           NOT
                           NULL,
                           description
                           TEXT,
                           status
                           TEXT
                           NOT
                           NULL
                           DEFAULT
                           'pending',
                           priority
                           TEXT
                           NOT
                           NULL
                           DEFAULT
                           'medium',
                           created_date
                           TIMESTAMP
                           NOT
                           NULL,
                           due_date
                           TIMESTAMP,
                           completed_date
                           TIMESTAMP,
                           estimated_duration
                           INTEGER
                           DEFAULT
                           0,
                           actual_duration
                           INTEGER
                           DEFAULT
                           0,
                           category
                           TEXT,
                           tags
                           TEXT,
                           recurring
                           BOOLEAN
                           DEFAULT
                           FALSE,
                           recurrence_pattern
                           TEXT
                       )
                       ''')

        # Time tracking table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS time_sessions
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           task_id
                           INTEGER,
                           start_time
                           TIMESTAMP
                           NOT
                           NULL,
                           end_time
                           TIMESTAMP,
                           duration
                           INTEGER
                           DEFAULT
                           0,
                           session_type
                           TEXT
                           DEFAULT
                           'pomodoro',
                           FOREIGN
                           KEY
                       (
                           task_id
                       ) REFERENCES tasks
                       (
                           id
                       )
                           )
                       ''')

        conn.commit()
        conn.close()

    def execute_query(self, query, params=()):
        """Execute a query and return results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)

        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            conn.close()
            return [dict(zip(columns, row)) for row in results]
        else:
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)