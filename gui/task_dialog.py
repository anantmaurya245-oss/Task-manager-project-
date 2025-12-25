import customtkinter as ctk
from datetime import datetime, timedelta
from task_manager import Task, TaskStatus, Priority


class TaskDialog(ctk.CTkToplevel):
    def __init__(self, parent, task_manager, task_id=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.task_manager = task_manager
        self.task_id = task_id
        self.result = None

        self.title("Add Task" if task_id is None else "Edit Task")
        self.geometry("500x600")
        self.resizable(False, False)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_task_data()

    def _create_widgets(self):
        # Title
        title_label = ctk.CTkLabel(self, text="Task Details", font=("Arial", 18, "bold"))
        title_label.pack(pady=20)

        # Main form frame
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Title field
        ctk.CTkLabel(form_frame, text="Title *", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        self.title_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter task title")
        self.title_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Description field
        ctk.CTkLabel(form_frame, text="Description", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        self.desc_text = ctk.CTkTextbox(form_frame, height=80)
        self.desc_text.pack(fill="x", padx=10, pady=(0, 10))

        # Priority field
        ctk.CTkLabel(form_frame, text="Priority", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        self.priority_var = ctk.StringVar(value=Priority.MEDIUM)
        priority_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        priority_frame.pack(fill="x", padx=10, pady=(0, 10))

        for priority in [Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.URGENT]:
            btn = ctk.CTkRadioButton(priority_frame, text=priority.capitalize(),
                                     variable=self.priority_var, value=priority)
            btn.pack(side="left", padx=(0, 10))

        # Status field (only for editing)
        if self.task_id is not None:
            ctk.CTkLabel(form_frame, text="Status", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
            self.status_var = ctk.StringVar(value=TaskStatus.PENDING)
            status_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            status_frame.pack(fill="x", padx=10, pady=(0, 10))

            for status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]:
                btn = ctk.CTkRadioButton(status_frame, text=status.replace('_', ' ').title(),
                                         variable=self.status_var, value=status)
                btn.pack(side="left", padx=(0, 10))

        # Due date field
        ctk.CTkLabel(form_frame, text="Due Date", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        due_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        due_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.due_date_var = ctk.StringVar(value="none")
        ctk.CTkRadioButton(due_frame, text="No due date", variable=self.due_date_var,
                           value="none", command=self._toggle_due_date).pack(anchor="w")
        ctk.CTkRadioButton(due_frame, text="Set due date", variable=self.due_date_var,
                           value="set", command=self._toggle_due_date).pack(anchor="w")

        self.due_date_frame = ctk.CTkFrame(form_frame, fg_color="transparent")

        # Date and time entries (initially hidden)
        date_time_frame = ctk.CTkFrame(self.due_date_frame, fg_color="transparent")
        date_time_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(date_time_frame, text="Date:").pack(side="left")
        self.date_entry = ctk.CTkEntry(date_time_frame, placeholder_text="YYYY-MM-DD", width=100)
        self.date_entry.pack(side="left", padx=(5, 15))

        ctk.CTkLabel(date_time_frame, text="Time:").pack(side="left")
        self.time_entry = ctk.CTkEntry(date_time_frame, placeholder_text="HH:MM", width=80)
        self.time_entry.pack(side="left", padx=(5, 0))

        # Set default date (tomorrow) and time (17:00)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.date_entry.insert(0, tomorrow)
        self.time_entry.insert(0, "17:00")

        # Category field
        ctk.CTkLabel(form_frame, text="Category", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        self.category_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., Work, Personal, Health")
        self.category_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Estimated duration
        ctk.CTkLabel(form_frame, text="Estimated Duration (minutes)", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                                                       pady=(10, 5))
        self.duration_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 30")
        self.duration_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Tags field
        ctk.CTkLabel(form_frame, text="Tags (comma separated)", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                                                 pady=(10, 5))
        self.tags_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., urgent, important, meeting")
        self.tags_entry.pack(fill="x", padx=10, pady=(0, 20))

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=20)

        self.save_btn = ctk.CTkButton(button_frame, text="Save Task", command=self._save_task)
        self.save_btn.pack(side="right", padx=(10, 0))

        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", fg_color="gray", command=self.destroy)
        cancel_btn.pack(side="right")

    def _toggle_due_date(self):
        if self.due_date_var.get() == "set":
            self.due_date_frame.pack(fill="x", padx=10, pady=(0, 10))
        else:
            self.due_date_frame.pack_forget()

    def _load_task_data(self):
        if self.task_id is not None:
            task = self.task_manager.get_task(self.task_id)
            if task:
                self.title_entry.insert(0, task.title)
                self.desc_text.insert("1.0", task.description or "")
                self.priority_var.set(task.priority)
                self.category_entry.insert(0, task.category or "")
                self.duration_entry.insert(0, str(task.estimated_duration or ""))
                self.tags_entry.insert(0, ", ".join(task.tags))

                if hasattr(self, 'status_var'):
                    self.status_var.set(task.status)

                if task.due_date:
                    self.due_date_var.set("set")
                    self._toggle_due_date()
                    self.date_entry.delete(0, "end")
                    self.date_entry.insert(0, task.due_date.strftime("%Y-%m-%d"))
                    self.time_entry.delete(0, "end")
                    self.time_entry.insert(0, task.due_date.strftime("%H:%M"))

    def _save_task(self):
        # Get form data
        title = self.title_entry.get().strip()
        if not title:
            self._show_error("Title is required")
            return

        description = self.desc_text.get("1.0", "end-1c").strip()
        priority = self.priority_var.get()
        category = self.category_entry.get().strip()

        try:
            estimated_duration = int(self.duration_entry.get() or 0)
        except ValueError:
            estimated_duration = 0

        tags = [tag.strip() for tag in self.tags_entry.get().split(",") if tag.strip()]

        # Parse due date
        due_date = None
        if self.due_date_var.get() == "set":
            date_str = self.date_entry.get().strip()
            time_str = self.time_entry.get().strip()

            if date_str and time_str:
                try:
                    due_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                except ValueError:
                    self._show_error("Invalid date or time format. Use YYYY-MM-DD and HH:MM")
                    return

        # Create or update task
        if self.task_id is None:
            # New task
            task = Task(
                title=title,
                description=description,
                priority=priority,
                category=category,
                estimated_duration=estimated_duration,
                tags=tags,
                due_date=due_date
            )
            self.task_manager.create_task(task)
        else:
            # Update existing task
            update_data = {
                'title': title,
                'description': description,
                'priority': priority,
                'category': category,
                'estimated_duration': estimated_duration,
                'tags': tags,
                'due_date': due_date
            }

            if hasattr(self, 'status_var'):
                update_data['status'] = self.status_var.get()

            self.task_manager.update_task(self.task_id, **update_data)

        self.destroy()

    def _show_error(self, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("300x100")
        error_window.transient(self)
        error_window.grab_set()

        ctk.CTkLabel(error_window, text=message, text_color="red").pack(expand=True)
        ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(pady=10)