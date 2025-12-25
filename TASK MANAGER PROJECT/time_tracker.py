import time
import threading
from datetime import datetime, timedelta
from database import Database


class TimeTracker:
    def __init__(self, db_path="task_manager.db"):
        self.db = Database(db_path)
        self.is_running = False
        self.current_session = None
        self.start_time = None
        self.duration = 0
        self.on_tick = None
        self.on_complete = None

        # Pomodoro settings
        self.work_duration = 25 * 60  # 25 minutes
        self.break_duration = 5 * 60  # 5 minutes
        self.is_break = False

    def start_pomodoro(self, task_id=None, on_tick=None, on_complete=None):
        """Start a Pomodoro session"""
        if self.is_running:
            return False

        self.is_running = True
        self.is_break = False
        self.duration = self.work_duration
        self.start_time = datetime.now()
        self.on_tick = on_tick
        self.on_complete = on_complete

        # Create time session record
        query = '''
                INSERT INTO time_sessions (task_id, start_time, session_type)
                VALUES (?, ?, ?) \
                '''
        self.current_session = self.db.execute_query(
            query, (task_id, self.start_time.isoformat(), 'pomodoro_work')
        )

        # Start the timer thread
        self.timer_thread = threading.Thread(target=self._run_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

        return True

    def start_break(self):
        """Start a break session"""
        if self.is_running:
            return False

        self.is_running = True
        self.is_break = True
        self.duration = self.break_duration
        self.start_time = datetime.now()

        query = '''
                INSERT INTO time_sessions (start_time, session_type)
                VALUES (?, ?) \
                '''
        self.current_session = self.db.execute_query(
            query, (self.start_time.isoformat(), 'pomodoro_break')
        )

        self.timer_thread = threading.Thread(target=self._run_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

        return True

    def stop_timer(self):
        """Stop the current timer"""
        if not self.is_running:
            return

        self.is_running = False
        end_time = datetime.now()

        # Calculate total duration
        total_seconds = (end_time - self.start_time).total_seconds()

        # Update the time session
        if self.current_session:
            query = '''
                    UPDATE time_sessions
                    SET end_time = ?, \
                        duration = ?
                    WHERE id = ? \
                    '''
            self.db.execute_query(
                query, (end_time.isoformat(), int(total_seconds), self.current_session)
            )

    def _run_timer(self):
        """Internal timer loop"""
        while self.is_running and self.duration > 0:
            time.sleep(1)
            self.duration -= 1

            if self.on_tick:
                minutes = self.duration // 60
                seconds = self.duration % 60
                self.on_tick(minutes, seconds, self.is_break)

        if self.is_running:  # Timer completed naturally
            self.is_running = False
            if self.on_complete:
                self.on_complete(self.is_break)

    def get_time_statistics(self, days=7):
        """Get time tracking statistics"""
        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Total time spent
        query = '''
                SELECT SUM(duration) as total_time
                FROM time_sessions
                WHERE start_time >= ? \
                  AND duration > 0 \
                '''
        result = self.db.execute_query(query, (start_date,))
        total_time = result[0]['total_time'] if result and result[0]['total_time'] else 0

        # Time by session type
        type_query = '''
                     SELECT session_type, SUM(duration) as total_time
                     FROM time_sessions
                     WHERE start_time >= ? \
                       AND duration > 0
                     GROUP BY session_type \
                     '''
        type_results = self.db.execute_query(type_query, (start_date,))
        time_by_type = {result['session_type']: result['total_time'] for result in type_results}

        # Daily time spent
        daily_query = '''
                      SELECT DATE (start_time) as date, SUM (duration) as total_time
                      FROM time_sessions
                      WHERE start_time >= ? AND duration > 0
                      GROUP BY DATE (start_time)
                      ORDER BY date DESC
                          LIMIT 7 \
                      '''
        daily_results = self.db.execute_query(daily_query, (start_date,))

        return {
            'total_time_minutes': total_time // 60 if total_time else 0,
            'time_by_type': time_by_type,
            'daily_breakdown': daily_results
        }

    def set_pomodoro_durations(self, work_minutes=25, break_minutes=5):
        """Set custom Pomodoro durations"""
        self.work_duration = work_minutes * 60
        self.break_duration = break_minutes * 60

    def get_remaining_time(self):
        """Get remaining time in minutes and seconds"""
        if not self.is_running:
            return 0, 0
        return self.duration // 60, self.duration % 60