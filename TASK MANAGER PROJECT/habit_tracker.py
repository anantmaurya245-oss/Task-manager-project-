from datetime import datetime, timedelta
from database import Database


class Habit:
    def __init__(self, id=None, name="", description="", frequency="daily",
                 streak_count=0, created_date=None, last_completed=None):
        self.id = id
        self.name = name
        self.description = description
        self.frequency = frequency
        self.streak_count = streak_count
        self.created_date = created_date or datetime.now()
        self.last_completed = last_completed

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'frequency': self.frequency,
            'streak_count': self.streak_count,
            'created_date': self.created_date.isoformat(),
            'last_completed': self.last_completed.isoformat() if self.last_completed else None
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            frequency=data['frequency'],
            streak_count=data['streak_count'],
            created_date=datetime.fromisoformat(data['created_date']),
            last_completed=datetime.fromisoformat(data['last_completed']) if data['last_completed'] else None
        )


class HabitTracker:
    def __init__(self, db_path="task_manager.db"):
        self.db = Database(db_path)

    def create_habit(self, habit):
        """Create a new habit"""
        habit_data = habit.to_dict()
        del habit_data['id']

        query = '''
                INSERT INTO habits (name, description, frequency, streak_count, created_date, last_completed)
                VALUES (?, ?, ?, ?, ?, ?) \
                '''

        params = (
            habit_data['name'], habit_data['description'], habit_data['frequency'],
            habit_data['streak_count'], habit_data['created_date'], habit_data['last_completed']
        )

        return self.db.execute_query(query, params)

    def get_habit(self, habit_id):
        """Get a habit by ID"""
        query = "SELECT * FROM habits WHERE id = ?"
        results = self.db.execute_query(query, (habit_id,))
        return Habit.from_dict(results[0]) if results else None

    def get_all_habits(self):
        """Get all habits"""
        query = "SELECT * FROM habits ORDER BY created_date DESC"
        results = self.db.execute_query(query)
        return [Habit.from_dict(data) for data in results]

    def update_habit(self, habit_id, **kwargs):
        """Update habit properties"""
        allowed_fields = ['name', 'description', 'frequency', 'streak_count', 'last_completed']

        update_fields = []
        params = []

        for field, value in kwargs.items():
            if field in allowed_fields:
                if field == 'last_completed' and value:
                    value = value.isoformat()
                update_fields.append(f"{field} = ?")
                params.append(value)

        if not update_fields:
            return False

        params.append(habit_id)
        query = f"UPDATE habits SET {', '.join(update_fields)} WHERE id = ?"

        result = self.db.execute_query(query, params)
        return result is not None

    def delete_habit(self, habit_id):
        """Delete a habit and its completions"""
        # Delete completions first
        self.db.execute_query("DELETE FROM habit_completions WHERE habit_id = ?", (habit_id,))
        # Delete habit
        self.db.execute_query("DELETE FROM habits WHERE id = ?", (habit_id,))
        return True

    def mark_habit_complete(self, habit_id):
        """Mark a habit as completed for today"""
        today = datetime.now().date()
        habit = self.get_habit(habit_id)

        if not habit:
            return False

        # Check if already completed today
        query = '''
                SELECT * \
                FROM habit_completions
                WHERE habit_id = ? AND DATE (completed_date) = ? \
                '''
        results = self.db.execute_query(query, (habit_id, today.isoformat()))

        if results:
            return False  # Already completed today

        # Add completion record
        completion_query = '''
                           INSERT INTO habit_completions (habit_id, completed_date)
                           VALUES (?, ?) \
                           '''
        self.db.execute_query(completion_query, (habit_id, datetime.now().isoformat()))

        # Update streak
        last_completed = habit.last_completed.date() if habit.last_completed else None

        if last_completed == today - timedelta(days=1):
            # Consecutive day - increase streak
            new_streak = habit.streak_count + 1
        elif last_completed != today:
            # Not consecutive - reset to 1
            new_streak = 1

        # Update habit
        self.update_habit(
            habit_id,
            streak_count=new_streak,
            last_completed=datetime.now()
        )

        return True

    def get_habit_statistics(self):
        """Get habit tracking statistics"""
        habits = self.get_all_habits()
        total_habits = len(habits)

        if total_habits == 0:
            return {
                'total_habits': 0,
                'total_streaks': 0,
                'average_streak': 0,
                'completion_rate': 0,
                'longest_streak': 0
            }

        total_streaks = sum(habit.streak_count for habit in habits)
        average_streak = total_streaks / total_habits
        longest_streak = max(habit.streak_count for habit in habits) if habits else 0

        # Calculate completion rate for today
        today = datetime.now().date()
        completed_today = 0

        for habit in habits:
            query = '''
                    SELECT COUNT(*) as count \
                    FROM habit_completions
                    WHERE habit_id = ? AND DATE (completed_date) = ? \
                    '''
            results = self.db.execute_query(query, (habit.id, today.isoformat()))
            if results and results[0]['count'] > 0:
                completed_today += 1

        completion_rate = (completed_today / total_habits * 100) if total_habits > 0 else 0

        return {
            'total_habits': total_habits,
            'total_streaks': total_streaks,
            'average_streak': round(average_streak, 1),
            'completion_rate': round(completion_rate, 1),
            'longest_streak': longest_streak,
            'completed_today': completed_today
        }

    def get_habit_completions(self, habit_id, days=30):
        """Get completion history for a habit"""
        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        query = '''
                SELECT DATE (completed_date) as date, COUNT (*) as completions
                FROM habit_completions
                WHERE habit_id = ? AND completed_date >= ?
                GROUP BY DATE (completed_date)
                ORDER BY date \
                '''

        return self.db.execute_query(query, (habit_id, start_date))