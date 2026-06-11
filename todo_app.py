#!/usr/bin/env python3
"""
Simple To-Do List Application using Tkinter
A clean and modern GUI application for managing tasks
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 To-Do List Manager")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure('Title.TLabel', 
                            font=('Helvetica', 24, 'bold'),
                            background='#f0f0f0',
                            foreground='#333333')
        
        self.style.configure('Add.TButton',
                            font=('Helvetica', 12, 'bold'),
                            background='#4CAF50',
                            foreground='white')
        
        self.style.configure('Delete.TButton',
                            font=('Helvetica', 10),
                            background='#f44336',
                            foreground='white')
        
        self.style.configure('Complete.TButton',
                            font=('Helvetica', 10),
                            background='#2196F3',
                            foreground='white')
        
        self.tasks = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Title Label
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(pady=(20, 10))
        
        title_label = ttk.Label(title_frame, 
                               text="📋 My To-Do List",
                               style='Title.TLabel')
        title_label.pack()
        
        # Date label
        date_label = tk.Label(title_frame,
                             text=datetime.now().strftime("%B %d, %Y"),
                             font=('Helvetica', 10),
                             bg='#f0f0f0',
                             fg='#666666')
        date_label.pack()
        
        # Input Frame
        input_frame = tk.Frame(self.root, bg='#f0f0f0')
        input_frame.pack(pady=10, padx=20, fill='x')
        
        self.task_entry = tk.Entry(input_frame,
                                  font=('Helvetica', 12),
                                  bg='white',
                                  relief='flat',
                                  highlightthickness=2,
                                  highlightbackground='#cccccc',
                                  highlightcolor='#4CAF50')
        self.task_entry.pack(side='left', fill='x', expand=True, ipady=8)
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        add_button = ttk.Button(input_frame,
                               text="➕ Add",
                               command=self.add_task,
                               style='Add.TButton',
                               width=10)
        add_button.pack(side='left', padx=(10, 0))
        
        # Task List Frame with Scrollbar
        list_frame = tk.Frame(self.root, bg='#f0f0f0')
        list_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Create canvas with scrollbar
        self.canvas = tk.Canvas(list_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.canvas.yview)
        
        self.task_container = tk.Frame(self.canvas, bg='white')
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.task_container, anchor='nw')
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Bind resize event
        self.task_container.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Mouse wheel binding
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)
        
        # Stats Frame
        stats_frame = tk.Frame(self.root, bg='#f0f0f0')
        stats_frame.pack(pady=10, padx=20, fill='x')
        
        self.stats_label = tk.Label(stats_frame,
                                   text="Total Tasks: 0 | Completed: 0",
                                   font=('Helvetica', 10),
                                   bg='#f0f0f0',
                                   fg='#666666')
        self.stats_label.pack()
        
        # Button Frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        clear_btn = ttk.Button(button_frame,
                              text="🗑️ Clear All",
                              command=self.clear_all,
                              width=15)
        clear_btn.pack(side='left', padx=5)
        
    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def on_canvas_configure(self, event):
        """Resize the inner frame to match canvas width"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def add_task(self):
        """Add a new task to the list"""
        task_text = self.task_entry.get().strip()
        
        if not task_text:
            messagebox.showwarning("Warning", "Please enter a task!")
            return
        
        task = {
            'id': len(self.tasks),
            'text': task_text,
            'completed': False,
            'created_at': datetime.now()
        }
        
        self.tasks.append(task)
        self.task_entry.delete(0, 'end')
        self.refresh_task_list()
        self.update_stats()
    
    def refresh_task_list(self):
        """Refresh the task list display"""
        # Clear existing widgets
        for widget in self.task_container.winfo_children():
            widget.destroy()
        
        if not self.tasks:
            empty_label = tk.Label(self.task_container,
                                  text="No tasks yet! Add your first task above.",
                                  font=('Helvetica', 11, 'italic'),
                                  bg='white',
                                  fg='#999999',
                                  pady=20)
            empty_label.pack(fill='x', padx=20)
            return
        
        for i, task in enumerate(self.tasks):
            self.create_task_widget(task, i)
    
    def create_task_widget(self, task, index):
        """Create a widget for a single task"""
        task_frame = tk.Frame(self.task_container, bg='white', pady=8)
        task_frame.pack(fill='x', padx=15, pady=2)
        
        # Task number
        num_label = tk.Label(task_frame,
                            text=f"{index + 1}.",
                            font=('Helvetica', 11, 'bold'),
                            bg='white',
                            fg='#4CAF50',
                            width=3,
                            anchor='w')
        num_label.pack(side='left')
        
        # Task text
        text_color = '#999999' if task['completed'] else '#333333'
        font_style = ('Helvetica', 11, 'overstrike') if task['completed'] else ('Helvetica', 11)
        
        task_label = tk.Label(task_frame,
                             text=task['text'],
                             font=font_style,
                             bg='white',
                             fg=text_color,
                             anchor='w')
        task_label.pack(side='left', fill='x', expand=True, padx=(5, 10))
        
        # Buttons frame
        btn_frame = tk.Frame(task_frame, bg='white')
        btn_frame.pack(side='right', padx=5)
        
        # Complete button
        complete_btn = tk.Button(btn_frame,
                                text="✓" if not task['completed'] else "↩",
                                font=('Helvetica', 10, 'bold'),
                                bg='#2196F3' if not task['completed'] else '#FFC107',
                                fg='white',
                                relief='flat',
                                width=3,
                                command=lambda t=task: self.toggle_complete(t))
        complete_btn.pack(side='left', padx=2)
        
        # Delete button
        delete_btn = tk.Button(btn_frame,
                              text="✕",
                              font=('Helvetica', 10, 'bold'),
                              bg='#f44336',
                              fg='white',
                              relief='flat',
                              width=3,
                              command=lambda t=task: self.delete_task(t))
        delete_btn.pack(side='left', padx=2)
    
    def toggle_complete(self, task):
        """Toggle task completion status"""
        task['completed'] = not task['completed']
        self.refresh_task_list()
        self.update_stats()
    
    def delete_task(self, task):
        """Delete a task from the list"""
        if messagebox.askyesno("Confirm", f"Delete task: '{task['text']}'?"):
            self.tasks.remove(task)
            self.refresh_task_list()
            self.update_stats()
    
    def clear_all(self):
        """Clear all tasks"""
        if self.tasks:
            if messagebox.askyesno("Confirm", "Delete ALL tasks?"):
                self.tasks.clear()
                self.refresh_task_list()
                self.update_stats()
    
    def update_stats(self):
        """Update statistics display"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t['completed'])
        self.stats_label.config(text=f"Total Tasks: {total} | Completed: {completed}")


def main():
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
