import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox
from collections import deque
from tkinter import BooleanVar
import datetime
import sqlite3

# Connect to database
conn = sqlite3.connect('user.db')
conn.commit()
cursor = conn.cursor()

# Initialize the task list
tasks = deque()

# Function to add a new task
def add_task():
    global cursor
    task_name = entry_task_name.get()
    due_date = calendar_due_date.get() if due_date_checkbox.get() else ""
    category = entry_category.get() if entry_category.get() else ""
    reminder_date = calendar_reminder_date.get() if reminder_date_checkbox.get() else ""
    description = entry_description.get("1.0", tk.END).strip()
    is_complete = False
    created_date = datetime.date.today()  # Get the current date

    if task_name and category:
        # Check if the category already exists in the CATEGORY table
        cursor.execute("SELECT category_id FROM CATEGORY WHERE category_name=?", (category,))
        result = cursor.fetchone()

        if result:
            # If the category exists, retrieve its category_id
            category_id = result[0]
        else:
            # If the category doesn't exist, insert it into the CATEGORY table and retrieve its newly generated category_id
            cursor.execute("INSERT INTO CATEGORY (category_name) VALUES (?)", (category,))
            category_id = cursor.lastrowid

        if task_name:
            cursor.execute(
                "INSERT INTO TASK (task_name, due_date, description, status, created_date) "
                "VALUES (?, ?, ?, ?, ?)",
                (task_name, due_date, description, 'incomplete', created_date)
            )
            task_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO REMINDER (task_id, reminder_date) VALUES (?, ?)",
                (task_id, reminder_date)
            )

            conn.commit()
            tasks.append((task_name, is_complete, due_date, category, reminder_date, description))
            update_task_display(tasks)
            clear_entry_fields()
    else:
        messagebox.showerror("Invalid Task", "Please enter a task name.")

#function to retrieve the task_id from the database based on the task_name
def get_task_id_by_name(task_name):
    cursor.execute("SELECT task_id FROM TASK WHERE task_name=?", (task_name,))
    result = cursor.fetchone()
    if result:
        task_id = result[0]
        return task_id
    else:
        return None


# Function to delete a task
def delete_task():
    selected_items = task_treeview.selection()
    if selected_items:
        for item in selected_items:
            task_name = task_treeview.item(item)["text"]
            task_id = get_task_id_by_name(task_name)  # Get task_id using task_name

            task_treeview.delete(item)
            remove_task_by_name(task_name)

            # Delete task data from the "TASK" table
            cursor.execute("DELETE FROM TASK WHERE task_id=?", (task_id,))

            # Delete task data from the "reminder" table
            cursor.execute("DELETE FROM REMINDER WHERE task_id=?", (task_id,))

            # Delete task data from the "category" table
            cursor.execute("DELETE FROM CATEGORY WHERE task_id=?", (task_id,))

        conn.commit()
        messagebox.showinfo("Task Deleted", "Task has been deleted successfully.")
    else:
        messagebox.showerror("Invalid Selection", "Please select a task to delete.")



# Function to remove a task by its name from the tasks deque
def remove_task_by_name(task_name):
    index = -1
    for i, task in enumerate(tasks):
        if task[0] == task_name:
            index = i
            break
    if index != -1:
        tasks.remove(tasks[index])

# Function to edit a task
def edit_task():
    selected_item = task_treeview.selection()
    if selected_item:
        task_name = task_treeview.item(selected_item)["text"]
        task_index = get_task_index_by_name(task_name)
        selected_task = tasks[task_index]

        edit_window = tk.Toplevel(window)
        edit_window.title("Edit Task")

        label_edit_task_name = tk.Label(edit_window, text="Task Name:")
        label_edit_task_name.grid(row=0, column=0)
        entry_edit_task_name = tk.Entry(edit_window, width=30)
        entry_edit_task_name.insert(tk.END, selected_task[0])
        entry_edit_task_name.grid(row=0, column=1, columnspan=3)

        label_edit_complete = tk.Label(edit_window, text="Complete:")
        label_edit_complete.grid(row=0, column=2)
        complete_var = BooleanVar()
        complete_var.set(selected_task[1])
        checkbox_edit_complete = tk.Checkbutton(edit_window, variable=complete_var)
        checkbox_edit_complete.grid(row=0, column=3)

        label_edit_due_date = tk.Label(edit_window, text="Due Date:")
        label_edit_due_date.grid(row=1, column=0)
        calendar_edit_due_date = DateEntry(edit_window, date_pattern="yyyy-mm-dd")
        calendar_edit_due_date.set_date(selected_task[2] if selected_task[2] else None)
        calendar_edit_due_date.grid(row=1, column=1)

        label_edit_category = tk.Label(edit_window, text="Category:")
        label_edit_category.grid(row=1, column=2)
        entry_edit_category = tk.Entry(edit_window, width=15)
        entry_edit_category.insert(tk.END, selected_task[3])
        entry_edit_category.grid(row=1, column=3)

        label_edit_reminder_date = tk.Label(edit_window, text="Reminder Date:")
        label_edit_reminder_date.grid(row=2, column=0)
        calendar_edit_reminder_date = DateEntry(edit_window, date_pattern="yyyy-mm-dd")
        calendar_edit_reminder_date.set_date(selected_task[4] if selected_task[4] else None)
        calendar_edit_reminder_date.grid(row=2, column=1)

        label_edit_description = tk.Label(edit_window, text="Description:")
        label_edit_description.grid(row=3, column=0)
        entry_edit_description = tk.Text(edit_window, height=4, width=30)
        entry_edit_description.insert(tk.END, selected_task[5])
        entry_edit_description.grid(row=3, column=1, columnspan=3, padx=5, pady=5)

        def save_edited_task():
            edited_task_name = entry_edit_task_name.get()
            edited_is_complete = complete_var.get()
            edited_due_date = calendar_edit_due_date.get() if due_date_checkbox.get() else ""
            edited_category = entry_edit_category.get() if entry_edit_category.get() else ""
            edited_reminder_date = calendar_edit_reminder_date.get() if reminder_date_checkbox.get() else ""
            edited_description = entry_edit_description.get("1.0", tk.END).strip()

            if edited_task_name:
                # Update task data in the TASK table
                cursor.execute(
                    "UPDATE TASK SET task_name=?, status=?, due_date=?, description=? WHERE task_id=?",
                    (edited_task_name, edited_is_complete, edited_due_date, edited_description, selected_task[0]))

                # Update category data in the CATEGORY table
                cursor.execute("UPDATE CATEGORY SET category_name=? WHERE task_id=?",
                               (edited_category, selected_task[0]))

                # Update reminder data in the REMINDER table
                cursor.execute("UPDATE REMINDER SET reminder_date=? WHERE task_id=?",
                               (edited_reminder_date, selected_task[0]))

                conn.commit()

                if edited_task_name:
                    tasks[task_index] = (
                    edited_task_name,
                    edited_is_complete,
                    edited_due_date,
                    edited_category,
                    edited_reminder_date,
                    edited_description
                )
                update_task_display(tasks)
                edit_window.destroy()
            else:
                messagebox.showerror("Invalid Task", "Please enter a task name.")

        button_save_edited_task = tk.Button(edit_window, text="Save Task", command=save_edited_task)
        button_save_edited_task.grid(row=4, column=0, pady=5)

    else:
        messagebox.showerror("Invalid Selection", "Please select a task to edit.")

# Function to get the index of a task by its name in the tasks deque
def get_task_index_by_name(task_name):
    for i, task in enumerate(tasks):
        if task[0] == task_name:
            return i
    return -1

# Function to update the task list display
def update_task_display(task_list):
    task_treeview.delete(*task_treeview.get_children())
    for task in task_list:
        task_name = task[0]
        task_details = task[1:]
        task_treeview.insert("", tk.END, text=task_name, values=(task_details[0],) + task_details[1:])

# Function to clear the entry fields
def clear_entry_fields():
    entry_task_name.delete(0, tk.END)
    calendar_due_date.set_date(None)
    entry_category.delete(0, tk.END)
    calendar_reminder_date.set_date(None)
    entry_description.delete("1.0", tk.END)

# Function to search for tasks
def search_tasks():
    search_term = entry_search.get()
    if search_term:
        search_results = [task for task in tasks if search_term.lower() in task[0].lower()]
        update_task_display(search_results)
    else:
        update_task_display(tasks)



# Create the main window
window = tk.Tk()
window.title("Task Manager")

# Create and position the entry fields
label_task_name = tk.Label(window, text="Task Name:")
label_task_name.grid(row=0, column=0)
entry_task_name = tk.Entry(window, width=30)
entry_task_name.grid(row=0, column=1, padx=5)

label_due_date = tk.Label(window, text="Due Date:")
label_due_date.grid(row=0, column=2)
calendar_due_date = DateEntry(window, date_pattern="yyyy-mm-dd")
calendar_due_date.grid(row=0, column=3)

due_date_checkbox = tk.BooleanVar()
checkbox_due_date = tk.Checkbutton(
    window,
    variable=due_date_checkbox,
)
checkbox_due_date.grid(row=0, column=4)

label_category = tk.Label(window, text="Category:")
label_category.grid(row=1, column=0)
entry_category = tk.Entry(window, width=15)
entry_category.grid(row=1, column=1, padx=5)

label_reminder_date = tk.Label(window, text="Reminder Date:")
label_reminder_date.grid(row=1, column=2)
calendar_reminder_date = DateEntry(window, date_pattern="yyyy-mm-dd")
calendar_reminder_date.grid(row=1, column=3)

reminder_date_checkbox = tk.BooleanVar()
checkbox_reminder_date = tk.Checkbutton(
    window,
    variable=reminder_date_checkbox,
)
checkbox_reminder_date.grid(row=1, column=4)

label_description = tk.Label(window, text="Description:")
label_description.grid(row=2, column=0)
entry_description = tk.Text(window, height=4, width=30)
entry_description.grid(row=2, column=1, columnspan=3, padx=5, pady=5)

# Create and position the buttons
button_add_task = tk.Button(window, text="Add Task", command=add_task)
button_add_task.grid(row=3, column=0, pady=5)

button_delete_task = tk.Button(window, text="Delete Task", command=delete_task)
button_delete_task.grid(row=3, column=1, pady=5)

button_edit_task = tk.Button(window, text="Edit Task", command=edit_task)
button_edit_task.grid(row=3, column=2, pady=5)

# Create and position the search field and button
label_search = tk.Label(window, text="Search:")
label_search.grid(row=5, column=0)
entry_search = tk.Entry(window, width=30)
entry_search.grid(row=5, column=1, padx=5)

button_search = tk.Button(window, text="Search", command=search_tasks)
button_search.grid(row=5, column=2, padx=5)

task_treeview = ttk.Treeview(window)
# Fetch the data
query = "SELECT task_name, description, due_date, status FROM TASK"
cursor.execute(query)
results = cursor.fetchall()

# Display the data in the task_treeview widget
for row in results:
    column1_value, column2_value, column3_value, column4_value = row
    task_treeview.insert("", tk.END, text=column1_value, values=(column2_value, column3_value, column4_value))

# Function to pin/unpin a task
def update_pin_task():
    selected_item = task_treeview.selection()
    if selected_item:
        task_name = task_treeview.item(selected_item)["text"]
        task_index = get_task_index_by_name(task_name)
        selected_task = tasks[task_index]
        is_pinned = selected_task[6] if len(selected_task) >= 7 else False
        tasks[task_index] = selected_task[:6] + (not is_pinned,)
        update_task_display(tasks)

# Create and position the pin/unpin button
button_pin_task = tk.Button(window, text="Pin/Unpin Task", command=update_pin_task)
button_pin_task.grid(row=3, column=3, pady=5)

# Function to update the task list display
def update_task_display(task_list):
    task_treeview.delete(*task_treeview.get_children())
    for task in task_list:
        task_name = task[0]
        task_details = task[1:]
        is_pinned = task[6] if len(task) >= 7 else False
        pin_status = "Pinned" if is_pinned else "Unpinned"
        task_treeview.insert("", tk.END, text=task_name, values=(task_details[0],) + task_details[1:] + (pin_status,))

# Create and position the task list
task_treeview = ttk.Treeview(window)
task_treeview["columns"] = ("Complete", "Due Date", "Category", "Reminder Date", "Description", "Pin Status")

task_treeview.column("#0", width=150, minwidth=150, anchor=tk.W)
task_treeview.column("Complete", width=60, minwidth=60, anchor=tk.CENTER)
task_treeview.column("Due Date", width=100, minwidth=100, anchor=tk.CENTER)
task_treeview.column("Category", width=80, minwidth=80, anchor=tk.CENTER)
task_treeview.column("Reminder Date", width=100, minwidth=100, anchor=tk.CENTER)
task_treeview.column("Description", width=200, minwidth=200, anchor=tk.W)
task_treeview.column("Pin Status", width=80, minwidth=80, anchor=tk.CENTER)

task_treeview.heading("#0", text="Task Name", anchor=tk.W)
task_treeview.heading("Complete", text="Complete", anchor=tk.CENTER)
task_treeview.heading("Due Date", text="Due Date", anchor=tk.CENTER)
task_treeview.heading("Category", text="Category", anchor=tk.CENTER)
task_treeview.heading("Reminder Date", text="Reminder Date", anchor=tk.CENTER)
task_treeview.heading("Description", text="Description", anchor=tk.W)
task_treeview.heading("Pin Status", text="Pin Status", anchor=tk.CENTER)

task_treeview.grid(row=4, column=0, columnspan=5, padx=5, pady=5)

# Function to get the index of a task by its name in the tasks deque
def get_task_index_by_name(task_name):
    for i, task in enumerate(tasks):
        if task[0] == task_name:
            return i
    return -1

# Create and position the pin/unpin button
button_pin_task = tk.Button(window, text="Pin/Unpin Task", command=update_pin_task)
button_pin_task.grid(row=3, column=3, pady=5)

# Function to update the task list display
def update_task_display(task_list):
    task_treeview.delete(*task_treeview.get_children())
    for task in task_list:
        task_name = task[0]
        task_details = task[1:]
        task_treeview.insert("", tk.END, text=task_name, values=(task_details[0],) + task_details[1:])

# Function to clear the entry fields
def clear_entry_fields():
    entry_task_name.delete(0, tk.END)
    calendar_due_date.set_date(None)
    entry_category.delete(0, tk.END)
    calendar_reminder_date.set_date(None)
    entry_description.delete("1.0", tk.END)

# Create and position the pin/unpin button
button_pin_task = tk.Button(window, text="Pin/Unpin Task", command=update_pin_task)
button_pin_task.grid(row=3, column=3, pady=5)

# Function to save the data
def save_data():
    # Delete all existing data in the table
    cursor.execute('DELETE FROM TASK')

    # Insert the data from the Treeview into the table
    for item in task_treeview.get_children():
        values = task_treeview.item(item)['values']
        cursor.execute('INSERT INTO TASK VALUES (?, ?, ?, ?, ?, ?, ?)', values)

    # Commit the changes and close the connection
    conn.commit()


# Function to load the data
def load_data():
    # Clear the Treeview
    task_treeview.delete(*task_treeview.get_children())

    # Retrieve the data from the table with desired column order
    cursor.execute('SELECT task_name,status, due_date FROM TASK')
    data = cursor.fetchall()

    # Insert the data into the Treeview with the desired column order
    for item_data in data:
        # Extract the desired columns from the fetched data
        task_name=item_data[0]
        status = item_data[1]
        due_date = item_data[2]

        # Insert the extracted columns into the Treeview in the desired order
        task_treeview.insert("", tk.END, values=(task_name,status,due_date))


# Save the data before closing the application
window.protocol("WM_DELETE_WINDOW", save_data)

# Load the data when the application starts
load_data()

# Run the main loop
window.mainloop()

# Close the connection after the main loop
conn.close()
