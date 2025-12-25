import customtkinter as ctk


class ModernButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


class ModernEntry(ctk.CTkEntry):
    def __init__(self, master, placeholder="", **kwargs):
        super().__init__(master, placeholder_text=placeholder, **kwargs)


class ModernLabel(ctk.CTkLabel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


class TaskCard(ctk.CTkFrame):
    def __init__(self, master, task, on_edit=None, on_delete=None, on_start=None, on_complete=None, **kwargs):
        super().__init__(master, **kwargs)
        self.task = task
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_start = on_start
        self.on_complete = on_complete

        self._create_widgets()

    def _create_widgets(self):
        # Main grid for task card
        self.grid_columnconfigure(0, weight=1)

        # Task title and priority - TOP ROW
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ModernLabel(header_frame, text=self.task.title,
                                  font=("Arial", 16, "bold"), justify="left")
        title_label.grid(row=0, column=0, sticky="w")

        # Priority badge
        priority_color = {
            "low": "#27ae60",  # Green
            "medium": "#f39c12",  # Orange
            "high": "#e74c3c",  # Red
            "urgent": "#c0392b"  # Dark Red
        }.get(self.task.priority, "gray")

        priority_label = ModernLabel(header_frame, text=self.task.priority.upper(),
                                     font=("Arial", 10, "bold"),
                                     text_color="white",
                                     fg_color=priority_color,
                                     corner_radius=8,
                                     width=60)
        priority_label.grid(row=0, column=1, sticky="e", padx=(10, 0))

        # Description - SECOND ROW
        if self.task.description:
            desc_frame = ctk.CTkFrame(self, fg_color="transparent")
            desc_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))

            desc_label = ModernLabel(desc_frame, text=self.task.description,
                                     font=("Arial", 12),
                                     justify="left",
                                     wraplength=600)  # Allow text wrapping
            desc_label.pack(anchor="w", fill="x")

        # Task details - THIRD ROW (IMPROVED LAYOUT)
        details_frame = ctk.CTkFrame(self, fg_color="transparent")
        details_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 8))
        details_frame.grid_columnconfigure(0, weight=1)  # Make first column expandable

        # Left side: Status and Duration
        left_details = ctk.CTkFrame(details_frame, fg_color="transparent")
        left_details.grid(row=0, column=0, sticky="w")

        # Status with color coding
        status_color = {
            "pending": "#95a5a6",  # Gray
            "in_progress": "#3498db",  # Blue
            "completed": "#2ecc71"  # Green
        }.get(self.task.status, "gray")

        status_label = ModernLabel(left_details,
                                   text=f"● {self.task.status.replace('_', ' ').title()}",
                                   text_color=status_color,
                                   font=("Arial", 11, "bold"))
        status_label.pack(side="left", padx=(0, 15))

        # ESTIMATED TIME - MORE PROMINENT DISPLAY
        if self.task.estimated_duration > 0:
            time_color = "#9b59b6"  # Purple for time
            time_bg = "#f4ecf7"  # Light purple background
            time_frame = ctk.CTkFrame(left_details,
                                      fg_color=time_bg,
                                      corner_radius=6,
                                      height=24)
            time_frame.pack(side="left", padx=(0, 15))
            time_frame.pack_propagate(False)  # Prevent frame from shrinking

            time_icon = ModernLabel(time_frame, text="⏱", font=("Arial", 12))
            time_icon.pack(side="left", padx=(8, 2))

            time_text = ModernLabel(time_frame,
                                    text=f"{self.task.estimated_duration} min",
                                    text_color=time_color,
                                    font=("Arial", 11, "bold"))
            time_text.pack(side="left", padx=(2, 8))

        # Right side: Due date and category
        right_details = ctk.CTkFrame(details_frame, fg_color="transparent")
        right_details.grid(row=0, column=1, sticky="e")

        # Due date (if exists)
        if self.task.due_date:
            due_date = self.task.due_date.strftime("%b %d, %Y %H:%M")
            # Color code based on how close the due date is
            now = datetime.now()
            time_left = self.task.due_date - now
            due_color = "#e74c3c" if time_left.days < 1 else "#f39c12"  # Red if less than 1 day, orange otherwise

            due_frame = ctk.CTkFrame(right_details, fg_color="transparent")
            due_frame.pack(side="left", padx=(10, 0))

            due_icon = ModernLabel(due_frame, text="📅", font=("Arial", 12))
            due_icon.pack(side="left", padx=(0, 5))

            due_label = ModernLabel(due_frame, text=due_date,
                                    text_color=due_color,
                                    font=("Arial", 11))
            due_label.pack(side="left")

        # Category (if exists)
        if self.task.category:
            category_frame = ctk.CTkFrame(right_details, fg_color="transparent")
            category_frame.pack(side="left", padx=(10, 0))

            category_icon = ModernLabel(category_frame, text="📁", font=("Arial", 12))
            category_icon.pack(side="left", padx=(0, 5))

            category_label = ModernLabel(category_frame, text=self.task.category,
                                         font=("Arial", 11),
                                         text_color="#7f8c8d")
            category_label.pack(side="left")

        # Tags (if exist) - FOURTH ROW
        if self.task.tags:
            tags_frame = ctk.CTkFrame(self, fg_color="transparent")
            tags_frame.grid(row=3, column=0, sticky="w", padx=10, pady=(0, 8))

            ModernLabel(tags_frame, text="Tags:",
                        font=("Arial", 10, "bold"),
                        text_color="#7f8c8d").pack(side="left", padx=(0, 5))

            for tag in self.task.tags[:3]:  # Show max 3 tags
                tag_label = ModernLabel(tags_frame, text=f"#{tag}",
                                        font=("Arial", 10),
                                        text_color="#3498db",
                                        fg_color="#ebf5fb",
                                        corner_radius=10,
                                        padx=8, pady=2)
                tag_label.pack(side="left", padx=(0, 5))

            if len(self.task.tags) > 3:
                more_label = ModernLabel(tags_frame, text=f"+{len(self.task.tags) - 3} more",
                                         font=("Arial", 10),
                                         text_color="#95a5a6")
                more_label.pack(side="left", padx=(5, 0))

        # Action buttons - FIFTH ROW
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Left side: Status action buttons
        left_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        left_buttons.pack(side="left")

        # Right side: Edit/Delete buttons
        right_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        right_buttons.pack(side="right")

        # Action buttons based on status
        if self.task.status == "pending":
            start_btn = ModernButton(left_buttons, text="🚀 Start Task",
                                     width=110, height=32,
                                     font=("Arial", 11, "bold"),
                                     fg_color="#3498db",
                                     hover_color="#2980b9",
                                     command=lambda: self.on_start(self.task.id))
            start_btn.pack(side="left", padx=(0, 8))

        elif self.task.status == "in_progress":
            complete_btn = ModernButton(left_buttons, text="✅ Complete",
                                        width=110, height=32,
                                        font=("Arial", 11, "bold"),
                                        fg_color="#2ecc71",
                                        hover_color="#27ae60",
                                        command=lambda: self.on_complete(self.task.id))
            complete_btn.pack(side="left", padx=(0, 8))

        # Always show edit and delete buttons
        edit_btn = ModernButton(right_buttons, text="✏️ Edit",
                                width=80, height=32,
                                font=("Arial", 11),
                                fg_color="#f39c12",
                                hover_color="#e67e22",
                                command=lambda: self.on_edit(self.task.id))
        edit_btn.pack(side="left", padx=(0, 8))

        delete_btn = ModernButton(right_buttons, text="🗑️ Delete",
                                  width=80, height=32,
                                  font=("Arial", 11),
                                  fg_color="#e74c3c",
                                  hover_color="#c0392b",
                                  command=lambda: self.on_delete(self.task.id))
        delete_btn.pack(side="left")

        # Add a subtle separator at the bottom
        separator = ctk.CTkFrame(self, height=1, fg_color="#ecf0f1")
        separator.grid(row=5, column=0, sticky="ew", padx=10, pady=(5, 0))