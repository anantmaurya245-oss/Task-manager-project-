import json
from datetime import datetime, timedelta  # FIXED: timedelta not timedata
from typing import List, Dict, Optional  # FIXED: Dict not Blet
from database import Database


class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Priority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task:
    def __init__(self, id=None, title="", description="", status=TaskStatus.PENDING,
                 priority=Priority.MEDIUM, created_date=None, due_date=None,
                 completed_date=None, estimated_duration=0, actual_duration=0,
                 category="", tags=None, recurring=False, recurrence_pattern=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.created_date = created_date or datetime.now()
        self.due_date = due_date
        self.completed_date = completed_date
        self.estimated_duration = estimated_duration
        self.actual_duration = actual_duration
        self.category = category
        self.tags = tags or []
        self.recurring = recurring
        self.recurrence_pattern = recurrence_pattern

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_date': self.created_date.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'estimated_duration': self.estimated_duration,
            'actual_duration': self.actual_duration,
            'category': self.category,
            'tags': json.dumps(self.tags),
            'recurring': self.recurring,
            'recurrence_pattern': self.recurrence_pattern
        }

    @classmethod
    def from_dict(cls, data):
        tags = json.loads(data['tags']) if data['tags'] else []
        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            status=data['status'],
            priority=data['priority'],
            created_date=datetime.fromisoformat(data['created_date']),
            due_date=datetime.fromisoformat(data['due_date']) if data['due_date'] else None,
            completed_date=datetime.fromisoformat(data['completed_date']) if data['completed_date'] else None,
            estimated_duration=data['estimated_duration'],
            actual_duration=data['actual_duration'],
            category=data['category'],
            tags=tags,
            recurring=bool(data['recurring']),
            recurrence_pattern=data['recurrence_pattern']
        )


class TaskManager:
    def __init__(self, db_path="task_manager.db"):
        self.db = Database(db_path)

    def create_task(self, task):
        """Create a new task and return its ID"""
        task_data = task.to_dict()
        del task_data['id']  # Remove ID for insertion

        query = '''
                INSERT INTO tasks (title, description, status, priority, created_date, due_date, \
                                   completed_date, estimated_duration, actual_duration, category, \
                                   tags, recurring, recurrence_pattern) \
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) \
                '''

        params = (
            task_data['title'], task_data['description'], task_data['status'],
            task_data['priority'], task_data['created_date'], task_data['due_date'],
            task_data['completed_date'], task_data['estimated_duration'],
            task_data['actual_duration'], task_data['category'], task_data['tags'],
            task_data['recurring'], task_data['recurrence_pattern']
        )

        return self.db.execute_query(query, params)

    def get_task(self, task_id):
        """Retrieve a task by ID"""
        query = "SELECT * FROM tasks WHERE id = ?"
        results = self.db.execute_query(query, (task_id,))
        return Task.from_dict(results[0]) if results else None

    def get_all_tasks(self, status=None, category=None):
        """Retrieve all tasks with optional filtering"""
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY created_date DESC"

        results = self.db.execute_query(query, params)
        return [Task.from_dict(data) for data in results]

    def update_task(self, task_id, **kwargs):
        """Update task properties"""
        allowed_fields = ['title', 'description', 'status', 'priority', 'due_date',
                          'estimated_duration', 'actual_duration', 'category', 'tags',
                          'recurring', 'recurrence_pattern', 'completed_date']

        update_fields = []
        params = []

        for field, value in kwargs.items():
            if field in allowed_fields:
                if field == 'tags':
                    value = json.dumps(value)
                elif field in ['due_date', 'completed_date'] and value:
                    value = value.isoformat()

                update_fields.append(f"{field} = ?")
                params.append(value)

        if not update_fields:
            return False

        params.append(task_id)
        query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"

        result = self.db.execute_query(query, params)
        return result is not None

    def delete_task(self, task_id):
        """Delete a task"""
        query = "DELETE FROM tasks WHERE id = ?"
        self.db.execute_query(query, (task_id,))
        return True

    def mark_task_complete(self, task_id, actual_duration=0):
        """Mark a task as completed"""
        completed_date = datetime.now()
        return self.update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            completed_date=completed_date,
            actual_duration=actual_duration
        )

    def start_task(self, task_id):
        """Mark a task as in progress"""
        return self.update_task(task_id, status=TaskStatus.IN_PROGRESS)

    def get_overdue_tasks(self):
        """Get tasks that are overdue"""
        current_time = datetime.now().isoformat()
        query = '''
                SELECT * \
                FROM tasks
                WHERE due_date < ? \
                  AND status NOT IN (?, ?)
                ORDER BY due_date ASC \
                '''
        params = (current_time, TaskStatus.COMPLETED, TaskStatus.CANCELLED)

        results = self.db.execute_query(query, params)
        return [Task.from_dict(data) for data in results]

    def get_task_statistics(self):
        """Get comprehensive task statistics"""
        # Total tasks by status
        status_query = "SELECT status, COUNT(*) as count FROM tasks GROUP BY status"
        status_results = self.db.execute_query(status_query)
        status_counts = {result['status']: result['count'] for result in status_results}

        # Tasks by priority
        priority_query = "SELECT priority, COUNT(*) as count FROM tasks GROUP BY priority"
        priority_results = self.db.execute_query(priority_query)
        priority_counts = {result['priority']: result['count'] for result in priority_results}

        # Completion statistics
        total_tasks = sum(status_counts.values())
        completed_tasks = status_counts.get(TaskStatus.COMPLETED, 0)
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Average time spent
        time_query = '''
                     SELECT AVG(actual_duration) as avg_time
                     FROM tasks
                     WHERE status = ? \
                       AND actual_duration > 0 \
                     '''
        time_result = self.db.execute_query(time_query, (TaskStatus.COMPLETED,))
        avg_time_spent = time_result[0]['avg_time'] if time_result and time_result[0]['avg_time'] else 0

        return {
            'total_tasks': total_tasks,
            'status_distribution': status_counts,
            'priority_distribution': priority_counts,
            'completion_rate': round(completion_rate, 2),
            'average_time_spent': round(avg_time_spent, 2),
            'overdue_tasks': len(self.get_overdue_tasks())
        }