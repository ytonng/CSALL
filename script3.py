import tkinter as tk
from tkinter import messagebox
import sqlite3
class ManageAccountPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Set window title
        self.master.title("Manage Account")

        # Set window size
        self.master.geometry("1200x700")
        self.master.resizable(False, False)

        # Set window background color
        self.master.config(bg="#333333")

        # Create header label
        header_label = tk.Label(
            self.master,
            text="Manage Account",
            font=("Arial", 40),
            fg="#ffffff",
            bg="#333333",
        )
        header_label.pack(pady=50)

        # Create form frame
        form_frame = tk.Frame(self.master, bg="#333333")
        form_frame.pack()

        # Create first name label and entry
        first_name_label = tk.Label(
            form_frame, text="First Name", font=("Arial", 16), fg="#ffffff", bg="#333333"
        )
        first_name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.first_name_entry = tk.Entry(form_frame, font=("Arial", 16), bg="#ffffff")
        self.first_name_entry.grid(row=0, column=1, padx=10, pady=10)

        # Create last name label and entry
        last_name_label = tk.Label(
            form_frame, text="Last Name", font=("Arial", 16), fg="#ffffff", bg="#333333"
        )
        last_name_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.last_name_entry = tk.Entry(form_frame, font=("Arial", 16), bg="#ffffff")
        self.last_name_entry.grid(row=1, column=1, padx=10, pady=10)

        # Create email label and entry
        email_label = tk.Label(
            form_frame, text="Email", font=("Arial", 16), fg="#ffffff", bg="#333333"
        )
        email_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.email_entry = tk.Entry(form_frame, font=("Arial", 16), bg="#ffffff")
        self.email_entry.grid(row=2, column=1, padx=10, pady=10)

        # Create username label and entry
        username_label = tk.Label(
            form_frame, text="Username", font=("Arial", 16), fg="#ffffff", bg="#333333"
        )
        username_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.username_entry = tk.Entry(form_frame, font=("Arial", 16), bg="#ffffff")
        self.username_entry.grid(row=3, column=1, padx=10, pady=10)

        self.password_label = tk.Label(
            form_frame, text="Password", font=("Arial", 16), fg="#ffffff", bg="#333333"
        )
        self.password_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = tk.Entry(
            form_frame, font=("Arial", 16), bg="#ffffff", show="*"
        )
        self.password_entry.grid(row=4, column=1, padx=10, pady=10)

        # Create password confirmation label and entry
        self.password_confirm_label = tk.Label(
            form_frame,
            text="Confirm Password",
            font=("Arial", 16),
            fg="#ffffff",
            bg="#333333",
        )
        self.password_confirm_label.grid(
            row=5, column=0, padx=10, pady=10, sticky="w"
        )
        self.password_confirm_entry = tk.Entry(
            form_frame, font=("Arial", 16), bg="#ffffff", show="*"
        )
        self.password_confirm_entry.grid(
            row=5, column=1, padx=10, pady=10
        )
        # Create save button
        save_button = tk.Button(
            self.master,
            text="Save",
            font=("Arial", 16),
            fg="#333333",
            bg="#ffffff",
            command=self.save_changes,
        )
        save_button.pack(pady=30)

    def save_changes(self):
        # Retrieve the entered values
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        username=self.username_entry.get()

        # Connect to the database
        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()

        # Get the user_id from the database
        query = "SELECT UserID FROM User WHERE Username=?"
        cursor.execute(query,(username,))
        user = cursor.fetchone()
        if user:
            user_id = user[0]  # Extract the user_id from the result

            # Execute the SQL UPDATE statement
            query = "UPDATE User SET FirstName = ?, LastName = ?, Email = ?, Password = ? WHERE UserID = ?"
            cursor.execute(query, (first_name, last_name, email, password, user_id))

            # Commit the changes and close the cursor and connection
            conn.commit()
            cursor.close()
            conn.close()

            # Show success message
            messagebox.showinfo("Success", "Changes saved successfully.")
        else:
            # Close the cursor and connection
            cursor.close()
            conn.close()

            # Show error message
            messagebox.showerror("Error", "User not found.")

        # Add any additional logic or display a success message if needed

        # Create back label
        back_label = tk.Button(
            self.master,
            text="Back to Task Manager",
            font=("Arial", 16),
            fg="#ffffff",
            bg="#333333",
            cursor="hand2",
            command=self.back_to_task_manager  # Add cursor style for hover effect
        )
        back_label.pack(side="top", pady=10)
        back_label.bind("<Button-1>", self.back_to_task_manager)  # Bind the label to the method

    def back_to_task_manager(self, event):
        self.master.destroy()

def create_manage_account():
    # Create the main tkinter window
    root = tk.Tk()

    # Create an instance of the ManageAccountPage class
    manage_account_page = ManageAccountPage(root)

    # Create back label
    back_label = tk.Label(
        root,
        text="Back to Task Manager",
        font=("Arial", 16),
        fg="#ffffff",
        bg="#333333",
        cursor="hand2"  # Add cursor style for hover effect
    )
    back_label.pack(side="top", pady=10)
    back_label.bind("<Button-1>", manage_account_page.back_to_task_manager)  # Bind the label to the method

    # Run the tkinter event loop
    root.mainloop()