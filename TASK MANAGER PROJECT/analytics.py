import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from task_manager import TaskManager
from time_tracker import TimeTracker
from habit_tracker import HabitTracker


class Analytics:
    def __init__(self, db_path="task_manager.db"):
        self.task_manager = TaskManager(db_path)
        self.time_tracker = TimeTracker(db_path)
        self.habit_tracker = HabitTracker(db_path)

    def get_productivity_insights(self, days=7):
        """Get comprehensive productivity insights"""
        task_stats = self.task_manager.get_task_statistics()
        time_stats = self.time_tracker.get_time_statistics(days)
        habit_stats = self.habit_tracker.get_habit_statistics()

        insights = {
            'task_completion_rate': task_stats['completion_rate'],
            'total_time_tracked': time_stats['total_time_minutes'],
            'habit_completion_rate': habit_stats['completion_rate'],
            'average_streak': habit_stats['average_streak'],
            'overdue_tasks': task_stats['overdue_tasks'],
            'total_habits': habit_stats['total_habits']
        }

        # Calculate productivity score (0-100)
        productivity_score = self._calculate_productivity_score(insights)
        insights['productivity_score'] = productivity_score

        return insights

    def _calculate_productivity_score(self, insights):
        """Calculate overall productivity score"""
        score = 0

        # Task completion contributes 40%
        task_score = min(insights['task_completion_rate'], 100)
        score += task_score * 0.4

        # Habit completion contributes 30%
        habit_score = insights['habit_completion_rate']
        score += habit_score * 0.3

        # Time tracking contributes 20% (normalized)
        time_score = min(insights['total_time_tracked'] / 60, 100)  # Normalize to 100
        score += time_score * 0.2

        # Overdue tasks penalty -10%
        overdue_penalty = min(insights['overdue_tasks'] * 5, 10)
        score -= overdue_penalty

        return max(0, min(100, round(score)))

    def generate_task_completion_chart(self):
        """Generate task completion chart"""
        stats = self.task_manager.get_task_statistics()

        if not stats['status_distribution']:
            return None

        labels = list(stats['status_distribution'].keys())
        sizes = list(stats['status_distribution'].values())

        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title('Task Status Distribution')
        plt.axis('equal')

        return plt

    def generate_time_tracking_chart(self, days=7):
        """Generate time tracking chart"""
        stats = self.time_tracker.get_time_statistics(days)

        if not stats['daily_breakdown']:
            return None

        dates = [item['date'] for item in stats['daily_breakdown']]
        times = [item['total_time'] / 60 for item in stats['daily_breakdown']]  # Convert to hours

        plt.figure(figsize=(10, 6))
        plt.bar(dates, times)
        plt.title('Time Tracked (Last 7 Days)')
        plt.xlabel('Date')
        plt.ylabel('Hours')
        plt.xticks(rotation=45)
        plt.tight_layout()

        return plt

    def generate_habit_streak_chart(self):
        """Generate habit streak chart"""
        habits = self.habit_tracker.get_all_habits()

        if not habits:
            return None

        habit_names = [habit.name for habit in habits]
        streaks = [habit.streak_count for habit in habits]

        plt.figure(figsize=(10, 6))
        bars = plt.bar(habit_names, streaks)
        plt.title('Current Habit Streaks')
        plt.xlabel('Habits')
        plt.ylabel('Streak (days)')
        plt.xticks(rotation=45)

        # Add value labels on bars
        for bar, streak in zip(bars, streaks):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                     str(streak), ha='center', va='bottom')

        plt.tight_layout()
        return plt

    def get_recommendations(self):
        """Get personalized productivity recommendations"""
        insights = self.get_productivity_insights()
        recommendations = []

        if insights['task_completion_rate'] < 50:
            recommendations.append("📋 Focus on completing pending tasks to improve your completion rate")

        if insights['overdue_tasks'] > 0:
            recommendations.append("⏰ You have overdue tasks. Consider rescheduling or prioritizing them")

        if insights['total_time_tracked'] < 300:  # Less than 5 hours
            recommendations.append("⏱️ Try tracking more time using the Pomodoro timer")

        if insights['habit_completion_rate'] < 60:
            recommendations.append("🔄 Consistency is key! Try to maintain your habit streaks")

        if insights['productivity_score'] > 80:
            recommendations.append("🎉 Great job! Your productivity is excellent. Keep it up!")
        elif insights['productivity_score'] > 60:
            recommendations.append("👍 Good progress! Small improvements can boost your productivity further")
        else:
            recommendations.append("💪 Let's work on building better habits and task management")

        return recommendations