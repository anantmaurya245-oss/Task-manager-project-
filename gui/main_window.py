import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

from task_manager import TaskManager, TaskStatus
from time_tracker import TimeTracker
from habit_tracker import HabitTracker
from analytics import Analytics
from gui.task_dialog import TaskDialog
from gui.widgets import TaskCard, ScrollableFrame, ModernButton, ModernLabel


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Initialize managers
        self.task_manager = TaskManager()
        self.time_tracker = TimeTracker()
        self.habit_tracker = HabitTracker()
        self.analytics = Analytics()

        # Configure window
        self.title("Smart Task Manager - Productivity Insights")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # Configure theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Create UI
        self._create_ui()

        # Load initial data
        self._refresh_tasks()

    def _create_ui(self):
        # Create main grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        # Sidebar title
        title_label = ModernLabel(self.sidebar, text="Smart Task\nManager",
                                  font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, padx=20, pady=20)

        # Navigation buttons
        nav_buttons = [
            ("📋 Tasks", self._show_tasks_tab),
            ("⏱️ Timer", self._show_pomodoro_tab),
            ("📊 Analytics", self._show_analytics_tab),
        ]

        for i, (text, command) in enumerate(nav_buttons, 1):
            btn = ModernButton(self.sidebar, text=text, command=command,
                               font=("Arial", 14), height=40)
            btn.grid(row=i, column=0, padx=20, pady=10, sticky="ew")

        # Theme switcher
        self.theme_label = ModernLabel(self.sidebar, text="Appearance:", font=("Arial", 12))
        self.theme_label.grid(row=9, column=0, padx=20, pady=(10, 0))

        self.theme_option = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light"],
                                              command=self._change_theme)
        self.theme_option.set("Dark")
        self.theme_option.grid(row=10, column=0, padx=20, pady=10)

        # Main content area
        self.main_content = ctk.CTkFrame(self)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)

        # Content title
        self.content_title = ModernLabel(self.main_content, text="Task Manager",
                                         font=("Arial", 24, "bold"))
        self.content_title.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Content frame (will be replaced by different tabs)
        self.content_frame = ctk.CTkFrame(self.main_content)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Show tasks tab by default
        self._show_tasks_tab()

    def _change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme)

    def _show_tasks_tab(self):
        self._clear_content_frame()
        self.content_title.configure(text="📋 Task Management")

        # Create main container with proper grid configuration
        main_container = ctk.CTkFrame(self.content_frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)  # This makes tasks area expandable

        # TOP BAR - Fixed at top
        top_bar = ctk.CTkFrame(main_container, height=60)
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_bar.grid_columnconfigure(0, weight=1)

        # Filter section (left side)
        filter_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        filter_frame.pack(side="left", fill="x", expand=True)

        ModernLabel(filter_frame, text="Filter:", font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))

        self.filter_var = ctk.StringVar(value="all")
        filters = [("All", "all"), ("Pending", "pending"), ("In Progress", "in_progress"),
                   ("Completed", "completed")]

        for text, value in filters:
            btn = ctk.CTkRadioButton(filter_frame, text=text, variable=self.filter_var,
                                     value=value, command=self._refresh_tasks)
            btn.pack(side="left", padx=(10, 0))

        # Add task button (right side) - FIXED: This button will stay visible
        add_btn = ModernButton(top_bar, text="➕ Add New Task",
                               command=self._add_task,
                               font=("Arial", 12, "bold"),
                               height=35,
                               fg_color="#2E8B57",  # Green color
                               hover_color="#3CB371")
        add_btn.pack(side="right", padx=(10, 0))

        # TASKS SCROLLABLE AREA - This will expand
        tasks_container = ctk.CTkFrame(main_container)
        tasks_container.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        tasks_container.grid_columnconfigure(0, weight=1)
        tasks_container.grid_rowconfigure(0, weight=1)

        self.tasks_scrollable = ScrollableFrame(tasks_container)
        self.tasks_scrollable.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # STATISTICS BAR - Fixed at bottom
        stats_frame = ctk.CTkFrame(main_container, height=80)
        stats_frame.grid(row=2, column=0, sticky="ew")
        stats_frame.grid_columnconfigure(0, weight=1)

        # Load statistics and update UI
        self._refresh_tasks()
        self._update_statistics()

    def _update_statistics(self):
        """Update the statistics display"""
        stats = self.task_manager.get_task_statistics()

        # Clear existing stats
        for widget in self.content_frame.winfo_children():
            if hasattr(widget, '_is_stats_frame'):
                widget.destroy()

        # Create new stats frame at the bottom of content_frame
        stats_frame = ctk.CTkFrame(self.content_frame)
        stats_frame._is_stats_frame = True  # Mark as stats frame
        stats_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        stats_cards = [
            (f"📊 Total: {stats['total_tasks']}", "#3498db"),
            (f"✅ Done: {stats['completion_rate']}%", "#2ecc71"),
            (f"⏰ Overdue: {stats['overdue_tasks']}", "#e74c3c"),
            (f"⏱️ Avg: {stats['average_time_spent']}min", "#f39c12")
        ]

        for i, (text, color) in enumerate(stats_cards):
            card = ctk.CTkFrame(stats_frame, fg_color=color, corner_radius=8)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            stats_frame.grid_columnconfigure(i, weight=1)

            label = ModernLabel(card, text=text, font=("Arial", 11, "bold"),
                                text_color="white")
            label.pack(padx=10, pady=5)

    def _refresh_tasks(self):
        """Refresh the tasks display"""
        if not hasattr(self, 'tasks_scrollable'):
            return

        # Clear existing tasks
        for widget in self.tasks_scrollable.winfo_children():
            widget.destroy()

        # Get tasks based on filter
        filter_value = self.filter_var.get()

        if filter_value == "overdue":
            tasks = self.task_manager.get_overdue_tasks()
        elif filter_value == "all":
            tasks = self.task_manager.get_all_tasks()
        else:
            tasks = self.task_manager.get_all_tasks(status=filter_value)

        if not tasks:
            no_tasks_frame = ctk.CTkFrame(self.tasks_scrollable, fg_color="transparent")
            no_tasks_frame.pack(expand=True, fill="both", pady=50)

            ModernLabel(no_tasks_frame,
                        text="🎉 No tasks found!\nClick 'Add New Task' to create your first task.",
                        font=("Arial", 16),
                        justify="center").pack(expand=True)
            return

        # Display tasks
        for task in tasks:
            task_card = TaskCard(
                self.tasks_scrollable,
                task,
                on_edit=self._edit_task,
                on_delete=self._delete_task,
                on_start=self._start_task,
                on_complete=self._complete_task
            )
            task_card.pack(fill="x", padx=5, pady=5)

        # Update statistics
        self._update_statistics()

    def _show_pomodoro_tab(self):
        self._clear_content_frame()
        self.content_title.configure(text="⏱️ Pomodoro Timer")

        # Create pomodoro tab content
        pomodoro_frame = ctk.CTkFrame(self.content_frame)
        pomodoro_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        pomodoro_frame.grid_columnconfigure(0, weight=1)
        pomodoro_frame.grid_rowconfigure(1, weight=1)

        # Timer display - FIXED: Properly centered and visible
        timer_display_frame = ctk.CTkFrame(pomodoro_frame, fg_color="transparent")
        timer_display_frame.grid(row=0, column=0, pady=40)

        self.timer_display = ModernLabel(timer_display_frame, text="25:00",
                                         font=("Arial", 72, "bold"))
        self.timer_display.pack(pady=20)

        self.timer_type_label = ModernLabel(timer_display_frame, text="Work Session - Ready",
                                            font=("Arial", 20))
        self.timer_type_label.pack()

        # Control buttons - FIXED: Proper layout
        control_frame = ctk.CTkFrame(pomodoro_frame, fg_color="transparent")
        control_frame.grid(row=1, column=0, pady=30)

        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        self.start_btn = ModernButton(button_frame, text="🎯 Start Work Session",
                                      command=self._start_pomodoro,
                                      width=200, height=40,
                                      font=("Arial", 14, "bold"),
                                      fg_color="#2E8B57")
        self.start_btn.pack(side="left", padx=10)

        self.break_btn = ModernButton(button_frame, text="☕ Start Break",
                                      command=self._start_break,
                                      width=150, height=40,
                                      font=("Arial", 14),
                                      fg_color="#3498db")
        self.break_btn.pack(side="left", padx=10)

        self.stop_btn = ModernButton(button_frame, text="⏹️ Stop",
                                     command=self._stop_timer,
                                     width=100, height=40,
                                     font=("Arial", 14),
                                     fg_color="#e74c3c",
                                     state="disabled")
        self.stop_btn.pack(side="left", padx=10)

        # Task selection for tracking - FIXED: Better layout
        task_section = ctk.CTkFrame(pomodoro_frame)
        task_section.grid(row=2, column=0, sticky="ew", pady=20, padx=50)

        ModernLabel(task_section, text="Track time for task:",
                    font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=10)

        self.task_var = ctk.StringVar(value="none")

        # Task selection options
        tasks = self.task_manager.get_all_tasks()

        # No task option
        ctk.CTkRadioButton(task_section, text="No specific task",
                           variable=self.task_var, value="none",
                           font=("Arial", 12)).pack(anchor="w", padx=20, pady=2)

        # Available tasks
        if tasks:
            ModernLabel(task_section, text="Your tasks:",
                        font=("Arial", 12)).pack(anchor="w", padx=20, pady=(10, 5))

            for task in tasks:
                if task.status != TaskStatus.COMPLETED:
                    task_text = f"{task.title} ({task.priority})"
                    ctk.CTkRadioButton(task_section, text=task_text,
                                       variable=self.task_var, value=str(task.id),
                                       font=("Arial", 11)).pack(anchor="w", padx=30, pady=1)
        else:
            ModernLabel(task_section, text="No tasks available. Create tasks in the Tasks tab.",
                        font=("Arial", 11), text_color="gray").pack(anchor="w", padx=20, pady=5)

    def _show_analytics_tab(self):
        self._clear_content_frame()
        self.content_title.configure(text="📊 Productivity Analytics")

        # Simple analytics tab for now
        analytics_frame = ctk.CTkFrame(self.content_frame)
        analytics_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        try:
            insights = self.analytics.get_productivity_insights()
            recommendations = self.analytics.get_recommendations()

            # Productivity Score
            score_frame = ctk.CTkFrame(analytics_frame)
            score_frame.pack(fill="x", padx=20, pady=20)

            ModernLabel(score_frame, text=f"Your Productivity Score: {insights['productivity_score']}/100",
                        font=("Arial", 20, "bold")).pack(pady=10)

            progress = ctk.CTkProgressBar(score_frame, height=20)
            progress.pack(fill="x", padx=20, pady=10)
            progress.set(insights['productivity_score'] / 100)

            # Statistics
            stats_frame = ctk.CTkFrame(analytics_frame)
            stats_frame.pack(fill="x", padx=20, pady=10)

            stats_text = f"""
            Task Completion Rate: {insights['task_completion_rate']}%
            Time Tracked: {insights['total_time_tracked']} minutes
            Habit Completion: {insights['habit_completion_rate']}%
            Overdue Tasks: {insights['overdue_tasks']}
            """

            ModernLabel(stats_frame, text=stats_text, font=("Arial", 14),
                        justify="left").pack(padx=20, pady=20)

            # Recommendations
            rec_frame = ctk.CTkFrame(analytics_frame)
            rec_frame.pack(fill="x", padx=20, pady=20)

            ModernLabel(rec_frame, text="Recommendations:",
                        font=("Arial", 16, "bold")).pack(anchor="w", padx=20, pady=10)

            for rec in recommendations:
                ModernLabel(rec_frame, text=f"• {rec}",
                            font=("Arial", 12), justify="left").pack(anchor="w", padx=30, pady=2)

        except Exception as e:
            ModernLabel(analytics_frame, text=f"Analytics coming soon!\nError: {str(e)}",
                        font=("Arial", 16)).pack(expand=True)

    def _clear_content_frame(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # Task management methods
    def _add_task(self):
        dialog = TaskDialog(self, self.task_manager)
        self.wait_window(dialog)
        self._refresh_tasks()

    def _edit_task(self, task_id):
        dialog = TaskDialog(self, self.task_manager, task_id)
        self.wait_window(dialog)
        self._refresh_tasks()

    def _delete_task(self, task_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            self.task_manager.delete_task(task_id)
            self._refresh_tasks()

    def _start_task(self, task_id):
        self.task_manager.start_task(task_id)
        self._refresh_tasks()

    def _complete_task(self, task_id):
        self.task_manager.mark_task_complete(task_id)
        self._refresh_tasks()

    # Timer methods
    def _start_pomodoro(self):
        task_id = None if self.task_var.get() == "none" else int(self.task_var.get())

        def on_tick(minutes, seconds, is_break):
            self.timer_display.configure(text=f"{minutes:02d}:{seconds:02d}")
            timer_type = "Break" if is_break else "Work"
            self.timer_type_label.configure(text=f"{timer_type} Session - Running")

        def on_complete(is_break):
            self.timer_display.configure(text="25:00" if not is_break else "05:00")
            session_type = "Work" if not is_break else "Break"
            self.timer_type_label.configure(text=f"{session_type} Session - Completed!")
            self.start_btn.configure(state="normal")
            self.break_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            messagebox.showinfo("Pomodoro", f"{session_type} session completed! 🎉")

        if self.time_tracker.start_pomodoro(task_id, on_tick, on_complete):
            self.start_btn.configure(state="disabled")
            self.break_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.timer_type_label.configure(text="Work Session - Running")

    def _start_break(self):
        def on_tick(minutes, seconds, is_break):
            self.timer_display.configure(text=f"{minutes:02d}:{seconds:02d}")
            self.timer_type_label.configure(text="Break Session - Running")

        def on_complete(is_break):
            self.timer_display.configure(text="25:00")
            self.timer_type_label.configure(text="Work Session - Ready")
            self.start_btn.configure(state="normal")
            self.break_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            messagebox.showinfo("Pomodoro", "Break session completed! ☕")

        if self.time_tracker.start_break(on_tick, on_complete):
            self.start_btn.configure(state="disabled")
            self.break_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.timer_type_label.configure(text="Break Session - Running")

    def _stop_timer(self):
        self.time_tracker.stop_timer()
        self.timer_display.configure(text="25:00")
        self.timer_type_label.configure(text="Work Session - Ready")
        self.start_btn.configure(state="normal")
        self.break_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")