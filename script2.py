import tkinter as tk
from tkinter import ttk,messagebox,BooleanVar
from tkcalendar import DateEntry
from collections import deque
from script3 import create_manage_account
import webbrowser
from datetime import datetime, timedelta
import sqlite3
# Connect to the database
conn = sqlite3.connect("user.db")
c = conn.cursor()
c.execute("SELECT task_id, task_name, description, category_name, due_date,reminder_date, status FROM TASK")
tasks_data = c.fetchall()

# Initialize the task list
tasks = deque(task for task in tasks_data)
def create_task_manager(user_id):
    def refresh_task_list():
        task_treeview.delete(*task_treeview.get_children())
        # Fetch the data for the specific user
        query = "SELECT task_id, task_name, description, category_name, due_date, reminder_date, priority, status FROM TASK WHERE User_id=?"
        c.execute(query, (user_id,))
        results = c.fetchall()
        # Display the data in the task_treeview widget
        for row in results:
            task_id, task_name, description, category_name, due_date, reminder_date, priority, status = row

            # Define the priority highlighting colors
            if priority == "Low":
                priority_tag = "low_priority"
                priority_text = "Low"
            elif priority == "Medium":
                priority_tag = "medium_priority"
                priority_text = "Medium"
            elif priority == "High":
                priority_tag = "high_priority"
                priority_text = "High"
            else:
                priority_tag = ""  # No highlighting for "Non" priority
                priority_text = ""

            task_treeview.insert("", tk.END, text=task_id, values=(
                task_name, description, category_name, due_date, reminder_date, priority_text, status),
                                 tags=priority_tag)

    # Function to retrieve the user ID from the database
    def get_user_id():
            return user_id

    # Function to add a new task
    def add_task():
        task_name = entry_task_name.get()
        description = entry_description.get("1.0", tk.END).strip()
        category = entry_category.get() if entry_category.get() else ""
        due_date = calendar_due_date.get() if due_date_checkbox.get() else ""
        reminder_date = calendar_reminder_date.get() if reminder_date_checkbox.get() else ""
        priority = combo_priority.get()
        created_date = datetime.date.today()

        if task_name:
            user_id = get_user_id()
            if user_id is not None:
                # Insert into TASK table
                c.execute(
                    "INSERT INTO TASK (TASK_NAME, DESCRIPTION, CREATED_DATE, DUE_DATE,  CATEGORY_NAME, REMINDER_DATE, PRIORITY, STATUS, USER_ID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (task_name, description, created_date, due_date, category, reminder_date, priority, 'Incomplete',
                     user_id))
                conn.commit()
                tasks.append((task_name, description, created_date, due_date, category, reminder_date, priority, False))
                clear_fields_and_selection()
                refresh_task_list()
            else:
                messagebox.showerror("Error", "User not found.")
        else:
            messagebox.showerror("Invalid Task", "Please enter a task name.")

    # Function to delete a task
    def delete_task():
        selected_items = task_treeview.selection()
        if selected_items:
            for item in selected_items:
                task_id = task_treeview.item(item, "text")
                # Delete task data from the "TASK" table
                c.execute("DELETE FROM TASK WHERE task_id=?", (task_id,))
                remove_task_by_id(task_id)
                task_treeview.delete(item)
                conn.commit()
                refresh_task_list()
            messagebox.showinfo("Task Deleted", "Task has been deleted successfully.")
        else:
            messagebox.showerror("Invalid Selection", "Please select a task to delete.")

    def remove_task_by_id(task_id):
        index = -1
        for i, task in enumerate(tasks):
            if task[0] == task_id:
                index = i
                break
        if index != -1:
            tasks.remove(tasks[index])

    # Function to search for tasks by name for a specific user
    def search_tasks():
        search_text = entry_search.get()
        if search_text:
            user_id = get_user_id()  # Replace with the actual user ID

            # Perform a database query to search for tasks of the specific user matching the search criteria
            c.execute("SELECT task_name, description, category_name, due_date, reminder_date,priority,status FROM TASK WHERE USER_ID = ? AND lower(TASK_NAME) LIKE ?",
                      (user_id, '%' + search_text.lower() + '%',))
            matching_tasks = c.fetchall()

            if matching_tasks:
                display_search_results(matching_tasks)
            else:
                messagebox.showinfo("No Matches", "No tasks match the search criteria.")
        else:
            messagebox.showwarning("Empty Search", "Please enter a search term.")

    # Function to display the search results
    def display_search_results(results):
        task_treeview.delete(*task_treeview.get_children())
        for task in results:
            task_name, description, category, due_date, reminder_date,priority,status = task
            priority_text = priority if priority != "Non" else ""  # Get the priority text

            if priority == "Low":
                priority_tag = "low_priority"
            elif priority == "Medium":
                priority_tag = "medium_priority"
            elif priority == "High":
                priority_tag = "high_priority"
            else:
                priority_tag = ""  # No highlighting for "Non" priority

            task_treeview.insert("", tk.END,  values=(
            task_name ,description, category, due_date, reminder_date,priority, status), tags=priority_tag)

    def edit_task():
        selected_items = task_treeview.selection()
        if len(selected_items) == 1:
            item = selected_items[0]
            task_id = task_treeview.item(item, "text")
            task_index = get_task_index_by_id(task_id)

            if task_index != -1:
                task = tasks[task_index]

                entry_task_name.delete(0, tk.END)
                entry_task_name.insert(0, task[1])

                entry_description.delete("1.0", tk.END)
                entry_description.insert(tk.END, task[2])

                entry_category.delete(0, tk.END)
                entry_category.insert(0, task[3])

                due_date = task[4]
                reminder_date = task[5]
                priority = task[6]

                # Reset checkbox values
                due_date_checkbox.set(False)
                reminder_date_checkbox.set(False)
                combo_priority.set(priority)  # Set the selected priority in the combo box

                # Set checkbox and calendar values based on task data
                if due_date:
                    due_date_checkbox.set(True)
                    calendar_due_date.configure(state="normal")  # Enable the DateEntry widget
                    calendar_due_date.set_date(due_date)
                else:
                    calendar_due_date.configure(state="disabled")  # Disable the DateEntry widget
                    calendar_due_date.set_date(None)  # Clear the calendar widget

                if reminder_date:
                    reminder_date_checkbox.set(True)
                    calendar_reminder_date.configure(state="normal")  # Enable the DateEntry widget
                    calendar_reminder_date.set_date(reminder_date)
                else:
                    calendar_reminder_date.configure(state="disabled")  # Disable the DateEntry widget
                    calendar_reminder_date.set_date(None)  # Clear the calendar widget

                # Call the save_task function directly when clicking the Edit Task button
                button_edit_task.config(text="Save", command=save_task)
            else:
                messagebox.showerror("Invalid Selection", "Please select a valid task.")
        else:
            messagebox.showerror("Invalid Selection", "Please select a single task to edit.")

    def save_task():
        edited_task_name = entry_task_name.get()
        edited_description = entry_description.get("1.0", tk.END).strip()
        edited_category = entry_category.get() if entry_category.get() else ""
        edited_due_date = calendar_due_date.get() if due_date_checkbox.get() else ""
        edited_reminder_date = calendar_reminder_date.get() if reminder_date_checkbox.get() else ""
        edited_priority = combo_priority.get()

        if edited_task_name:
            selected_items = task_treeview.selection()
            if len(selected_items) == 1:
                item = selected_items[0]
                task_id = task_treeview.item(item, "text")
                task_index = get_task_index_by_id(task_id)

                if task_index != -1:
                    tasks[task_index] = (
                        task_id,
                        edited_task_name,
                        edited_description,
                        edited_category,
                        edited_due_date,
                        edited_reminder_date,
                        edited_priority,
                        tasks[task_index][6]
                    )

                    # Update the TASK table in the database
                    c.execute(
                        "UPDATE TASK SET TASK_NAME = ?, DESCRIPTION = ?, CATEGORY_NAME = ?, DUE_DATE = ?, REMINDER_DATE = ?,PRIORITY=? WHERE TASK_ID = ?",
                        (edited_task_name, edited_description, edited_category, edited_due_date,
                         edited_reminder_date, edited_priority,
                         task_treeview.item(item, "text"))
                    )
                    conn.commit()
                    clear_fields_and_selection()
                    messagebox.showinfo("Task Updated", "Task has been updated successfully.")
                    window.focus()  # Remove focus from the Save Task button
                    refresh_task_list()
                    button_edit_task.config(text="Edit", command=edit_task)
                else:
                    messagebox.showerror("Invalid Task", "Please enter a task name.")
            else:
                messagebox.showerror("Invalid Item", "Selected item does not exist in the task list.")
        else:
            messagebox.showerror("Invalid Task", "Please enter a task name.")

    # Function to get the index of a task by its id in the tasks deque
    def get_task_index_by_id(task_id):
        for i, task in enumerate(tasks):
            if task[0] == task_id:
                return i
        return -1

    # Function to toggle the completion status of selected tasks
    def complete_task():
        selected_items = task_treeview.selection()
        if selected_items:
            for item in selected_items:
                task_id = task_treeview.item(item, "text")
                task_index = get_task_index_by_id(task_id)

                if task_index != -1:
                    task = tasks[task_index]
                    completion_status = 'Complete' if task[6] == 'Incomplete' else 'Incomplete'

                    tasks[task_index] = (
                        task_id,
                        task[1],
                        task[2],
                        task[3],
                        task[4],
                        task[5],
                        completion_status
                    )

                    c.execute("UPDATE TASK SET STATUS = ? WHERE TASK_ID = ?", (completion_status, task_id))
                    conn.commit()
                    refresh_task_list()
                    messagebox.showinfo("Task Status Updated",f"Task '{task_id}' has been marked as {completion_status}.")
                else:
                    messagebox.showerror("Invalid Selection", "Please select a valid task.")
        else:
            messagebox.showerror("Invalid Selection", "Please select a task to mark as complete/incomplete.")

    # Function to clear the entry fields and selection
    def clear_fields_and_selection():
        entry_search.delete(0, tk.END)  # Clear the search field
        refresh_task_list()  # Reset the task list display
        entry_task_name.delete(0, tk.END)
        entry_description.delete("1.0", tk.END)
        entry_category.delete(0, tk.END)
        combo_priority.set('')
        calendar_due_date.configure(state="disabled")  # Disable the DateEntry widget
        calendar_due_date.set_date(None)  # Clear the calendar widget
        calendar_reminder_date.configure(state="disabled")  # Disable the DateEntry widget
        calendar_reminder_date.set_date(None)  # Clear the calendar widget
        due_date_checkbox.set(False)
        reminder_date_checkbox.set(False)
        task_treeview.selection_remove(task_treeview.focus())

    def open_google_form():
        url = "https://forms.gle/u7BmAj21Dsx6SPwL7"
        webbrowser.open_new(url)

    # Function to check for task reminders
    def check_reminders():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute(
            "SELECT task_id, task_name, description, category_name, due_date, reminder_date, status FROM TASK WHERE user_id = ?",
            (user_id,))
        tasks_data = c.fetchall()
        for task in tasks_data:
            reminder_date = task[5]
            if reminder_date and reminder_date <= current_time:
                task_name = task[1]
                messagebox.showinfo("Task Reminder", f"Reminder for task: {task_name}")

        window.after(1000, check_reminders)

    # Create the main window
    window = tk.Tk()
    window.title("Task Manager")
    window.geometry("1200x700")
    window.resizable(False, False)
    window.config(bg="#333333")  # Set a visually appealing background color

    feedback_button = tk.Button(
    window,
    text="Feedback",
    font=("Arial", 14),
    fg="#ffffff",
    bg="#333333",
    command=open_google_form
    )
    feedback_button.grid(row=0, column=0, padx=10, sticky="w")

    heading_label = tk.Label(window, text="Welcome Back to Task Manager", font=("Arial", 30, "bold"), fg="#ffffff", bg="#333333")
    heading_label.grid(row=0, column=0, columnspan=6,pady=30)
    mannage_acc_button = tk.Button(
        window,
        text="Manage Account",
        font=("Arial", 14),
        fg="#ffffff",
        bg="#333333",
        command=create_manage_account
    )
    mannage_acc_button.grid(row=0, column=5,sticky="e")

    # Create and position the entry fields
    label_task_name = tk.Label(window, text="Name:",font=("Arial", 12), fg="#ffffff", bg="#333333")
    label_task_name.grid(row=1, column=0,padx=10,pady=10, sticky="w")
    entry_task_name = tk.Entry(window, width=20,font=("Arial", 12), bg="#ffffff")
    entry_task_name.grid(row=1, column=0,padx=100 )

    label_due_date = tk.Label(window, text="Due Date:",font=("Arial", 12), fg="#ffffff", bg="#333333")
    label_due_date.grid(row=1, column=1,sticky="w")
    calendar_due_date = DateEntry(window,date_pattern="yyyy-mm-dd",font=("Arial", 14), bg="#ffffff")
    calendar_due_date.configure(state="disabled")
    calendar_due_date.grid(row=1, column=2,sticky="w")
    due_date_checkbox = tk.BooleanVar()
    checkbox_due_date = tk.Checkbutton(
        window,
        font=("Arial", 12), fg="#333333",
        variable=due_date_checkbox,
        command=lambda: calendar_due_date.configure(state="normal" if due_date_checkbox.get() else "disabled")
    )
    checkbox_due_date.grid(row=1,column=3,sticky="w")

    label_category = tk.Label(window, text="Category:",font=("Arial", 12), fg="#ffffff", bg="#333333")
    label_category.grid(row=3, column=0, padx=10,pady=10, sticky="w")
    entry_category = tk.Entry(window, width=20,font=("Arial", 12), bg="#ffffff")
    entry_category.grid(row=3, column=0, )

    label_reminder_date = tk.Label(window, text="Reminder Date:",font=("Arial", 12), fg="#ffffff", bg="#333333")
    label_reminder_date.grid(row=2, column=1,)
    calendar_reminder_date = DateEntry(window, date_pattern="yyyy-mm-dd",font=("Arial", 14), bg="#ffffff")
    calendar_reminder_date.configure(state="disabled")
    calendar_reminder_date.grid(row=2, column=2,sticky="w" )
    reminder_date_checkbox = tk.BooleanVar()
    checkbox_reminder_date = tk.Checkbutton(
        window,
        font=("Arial", 12), fg="#333333",
        variable=reminder_date_checkbox,
        command=lambda: calendar_reminder_date.configure(state="normal" if reminder_date_checkbox.get() else "disabled")
    )
    checkbox_reminder_date.grid(row=2, column=3, sticky="w")

    label_description = tk.Label(window, text="Notes:",font=("Arial", 12), fg="#ffffff", bg="#333333")
    label_description.grid(row=2, column=0,padx=10,pady=15,  sticky="w")
    entry_description = tk.Text(window, height=4, width=20,font=("Arial", 12), bg="#ffffff")
    entry_description.grid(row=2, column=0,)

    # Create and position the buttons
    button_add_task = tk.Button(window, text="Add Task",font=("Arial", 12),width=10, fg="#333333", bg="#ffffff", command=add_task)
    button_add_task.grid(row=4, column=3,sticky="w")

    button_delete_task = tk.Button(window, text="Delete Task", font=("Arial", 12),width=10, fg="#333333", bg="#ffffff",command=delete_task)
    button_delete_task.grid(row=2, column=5)

    button_edit_task = tk.Button(window, text="Edit Task",font=("Arial", 12), width=10,fg="#333333", bg="#ffffff", command=edit_task)
    button_edit_task.grid(row=1, column=5)

    button_clear = tk.Button(window, text="Clear", font=("Arial", 12),width=10, fg="#333333", bg="#ffffff",command=clear_fields_and_selection)
    button_clear.grid(row=3, column=5)

    button_complete_task = tk.Button(window, text="Complete", font=("Arial", 12),width=10, fg="#333333", bg="#ffffff",command=complete_task)
    button_complete_task.grid(row=4, column=5)

    # Create and position the search field and button
    label_search = tk.Label(window, text="Search:",font=("Arial", 12), fg="#ffffff", bg="#333333")
    label_search.grid(row=4, column=0, padx=10,pady=30, sticky="w")
    entry_search = tk.Entry(window,width=31,font=("Arial", 12), bg="#ffffff")
    entry_search.grid(row=4, column=0,sticky="e")
    button_search = tk.Button(window, text="Search",font=("Arial", 12), width=10,fg="#333333", bg="#ffffff", command=search_tasks)
    button_search.grid(row=4, column=1,)

    # Create a combobox for selecting priority
    label_priority = tk.Label(window, text="Priority:", font=("Arial", 12), fg="#ffffff", bg="#333333")
    label_priority.grid(row=3, column=1, sticky="w")
    combo_priority = ttk.Combobox(window, values=["Non", "Low", "Medium", "High"], state="readonly")
    combo_priority.grid(row=3, column=2, sticky="w")

    # Create and position the task treeview
    task_treeview = ttk.Treeview(window, columns=("Task Name", "Description", "Category", "Due Date", "Reminder Date", "Priority", "Complete"),
                                 show='headings')
    task_treeview.heading("#0", text="Task ID")
    task_treeview.heading("Task Name", text="Task Name")
    task_treeview.heading("Description", text="Description")
    task_treeview.heading("Category", text="Category")
    task_treeview.heading("Due Date", text="Due Date")
    task_treeview.heading("Reminder Date", text="Reminder Date")
    task_treeview.heading("Priority", text="Priority")
    task_treeview.heading("Complete", text="Complete")

    task_treeview.column("#0", width=10, anchor="w")
    task_treeview.heading("Task Name", width=200, anchor="w")
    task_treeview.column("Description", width=200, anchor="w")
    task_treeview.column("Category", width=100, anchor="w")
    task_treeview.column("Due Date", width=100, anchor="w")
    task_treeview.column("Reminder Date", width=100, anchor="w")
    task_treeview.column("Priority", width=70, anchor="w")
    task_treeview.column("Complete", width=70, anchor="w")

    task_treeview.grid(row=5, column=0, columnspan=6, sticky="nswe")

    # Configure priority highlighting tags and colors
    task_treeview.tag_configure("low_priority", background="green")
    task_treeview.tag_configure("medium_priority", background="yellow")
    task_treeview.tag_configure("high_priority", background="red")

    # Configure the treeview font style
    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 12))  # Set the desired font style for the Treeview widget

    # Add scrollbar to the task treeview
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=task_treeview.yview)
    scrollbar.grid(row=5, column=6,sticky="ns")
    task_treeview.configure(yscroll=scrollbar.set)

    # Configure the grid layout
    window.grid_rowconfigure(5, weight=1)
    window.grid_columnconfigure(5, weight=1)

    # Run the main window loop
    window.after(1000, check_reminders)  # Check for reminders every second (adjust the time interval as needed)

    refresh_task_list()
    conn.close

    # Run the main window loop
    window.mainloop()