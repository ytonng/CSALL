import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import re

class LoginPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.signup_page = None  # Initialize signup_page as None

        # Set window title
        self.master.title("Login Page")

        # Set window size
        self.master.geometry("1200x700")
        self.master.resizable(False, False)

        # Set window background color
        self.master.config(bg="#333333")

        # Create header label
        header_label = tk.Label(self.master, text="Welcome Back!", font=("Arial", 40), fg="#ffffff", bg="#333333")
        header_label.pack(pady=100)

        # Create form frame
        form_frame = tk.Frame(self.master, bg="#333333")
        form_frame.pack()

        # Create username label and entry
        username_label = tk.Label(form_frame, text="Username", font=("Arial", 16), fg="#ffffff", bg="#333333")
        username_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        username_entry = tk.Entry(form_frame, font=("Arial", 16), bg="#ffffff")
        username_entry.grid(row=0, column=1, padx=10, pady=10)

        # Create password label, entry and show password checkbutton
        password_label = tk.Label(form_frame, text="Password", font=("Arial", 16), fg="#ffffff", bg="#333333")
        password_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        password_entry = tk.Entry(form_frame, show="*", font=("Arial", 16), bg="#ffffff")
        password_entry.grid(row=1, column=1, padx=10, pady=10)
        show_password_var = tk.BooleanVar()
        show_password_checkbox = tk.Checkbutton(
            form_frame, font=("Arial", 16), fg="#333333",
            text="Show Password",
            variable=show_password_var,
            command=lambda: self.show_password(show_password_var.get(), password_entry)
        )

        show_password_checkbox.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.username_entry = username_entry
        self.password_entry = password_entry

        # Create login button
        login_button = tk.Button(self.master, text="Login", font=("Arial", 16), fg="#333333", bg="#ffffff",
                                 command=self.login)
        login_button.pack(pady=7)

        # Create forgot password label
        forgot_password_label = tk.Label(self.master, text="Forgot Password?", font=("Arial", 14), fg="#ffffff",
                                         bg="#333333")
        forgot_password_label.pack(pady=10)
        forgot_password_label.bind("<Button-1>", lambda event: self.forgot_password())

        # Create create account label
        create_account_label = tk.Label(self.master, text="Don't have an account? Sign up now!", font=("Arial", 14),
                                        fg="#ffffff", bg="#333333")
        create_account_label.pack(pady=10)
        create_account_label.bind("<Button-1>", lambda event: self.open_signup_page())


        # Create response message label
        self.response_label = tk.Label(self.master, text="", font=("Arial", 14), fg="#ffffff", bg="#333333")
        self.response_label.pack(pady=20)

    def show_password(self, true, entry):
        if true:
            entry.config(show="")
        else:
            entry.config(show="*")

    def execute_query(self, query, *params):
        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def login(self):
        # Get the username and password from the entry fields
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check if the username and password are correct
        query = "SELECT * FROM User WHERE Username = ? AND Password = ?"
        user = self.execute_query(query, username, password)

        if user:
            self.response_label.config(text="Welcome back, {}".format(username), fg="#00ff00")
        else:
            self.response_label.config(text="Incorrect username or password. Please try again.", fg="#ff0000")

    def forgot_password(self):
        email = simpledialog.askstring("Forgot Password", "Enter your email:", parent=self.master)

        if email:
            # Check if the email exists in the database
            query = "SELECT * FROM User WHERE Email = ?"
            user = self.execute_query(query, email)

            if user:
                # Reset the password to the default password
                new_password = '123456'  # Default password

                # Update the password in the database
                query = "UPDATE User SET Password = ? WHERE Email = ?"
                self.execute_query(query, new_password, email)

                messagebox.showinfo("Password Reset", "The password is reset to the default password '123456'.")
            else:
                messagebox.showerror("Error", "Email not found.")
        else:
            messagebox.showerror("Error", "Email not found.")



    def open_signup_page(self):
            # Destroy the current window
        self.master.destroy()

        # Create a new Tkinter window
        root = tk.Tk()

         # Create an instance of the SignupPage
        signup_page = SignupPage(root, self)

        # Run the main loop for the signup page
        signup_page.mainloop()

def execute_query(query, *params):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

class SignupPage(tk.Frame):
    def __init__(self, master, login_page):
        super().__init__(master)
        self.master = master
        self.login_page = login_page

        # Set window title
        self.master.title("Sign up Page")

        # Set window size
        self.master.geometry("1200x700")
        self.master.resizable(False, False)

        # Set window background color
        self.master.config(bg="#333333")

        # Create header label
        header_label = tk.Label(
            self.master,
            text="Create an Account",
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

        # Create password label, entry, and show password checkbutton
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

        # Create show password checkbox and variable
        self.show_password_var = tk.BooleanVar()
        show_password_checkbox = tk.Checkbutton(
            form_frame,
            text="Show Password",
            font=("Arial", 14),
            fg="#333333",
            variable=self.show_password_var,
            command=self.toggle_show_password,
        )
        show_password_checkbox.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        # Create sign-up button
        signup_button = tk.Button(
            self.master,
            text="Sign up",
            font=("Arial", 16),
            fg="#333333",
            bg="#ffffff",
            command=self.signup,
        )
        signup_button.pack(pady=30)

        # Create response message label
        self.response_label = tk.Label(
            self.master,
            text="",
            font=("Arial", 14),
            fg="#ffffff",
            bg="#333333",
        )
        self.response_label.pack(pady=0)

        # Create back to login label
        back_to_login_label = tk.Label(
            self.master,
            text="Back to Login",
            font=("Arial", 14),
            fg="#ffffff",
            bg="#333333",
        )
        back_to_login_label.pack(anchor="nw", padx=10, pady=0)
        back_to_login_label.bind("<Button-1>", lambda event: self.open_login_page())

    def toggle_show_password(self):
        if self.show_password_var.get():
            self.password_entry.config(show="")
            self.password_confirm_entry.config(show="")
        else:
            self.password_entry.config(show="*")
            self.password_confirm_entry.config(show="*")

    def open_login_page(self):
        # Destroy the current window
        self.master.destroy()

        # Create a new Tkinter window
        root = tk.Tk()

        # Create an instance of the LoginPage
        login_page = LoginPage(root)

        # Run the main loop for the login page
        login_page.mainloop()

    def username_exists_in_database(self, username):
        query = "SELECT Username FROM User WHERE Username = ?"
        result = execute_query(query, username)
        return result is not None

    def email_exists_in_database(self, email):
        query = "SELECT Email FROM User WHERE Email = ?"
        result = execute_query(query, email)
        return result is not None

    def signup(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        email = self.email_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        password_confirm = self.password_confirm_entry.get()

        # Validate input fields
        if not first_name or not last_name or not email or not username or not password or not password_confirm:
            messagebox.showerror("Error", "All fields are required")
            return

        if self.username_exists_in_database(username):
            messagebox.showerror("Error", "Username already exists")
            return

        if self.email_exists_in_database(email):
            messagebox.showerror("Error", "Email already exists")
            return

        if password != password_confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if not re.match(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email):
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return

        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long")
            return

        if not re.search("[a-z]", password) or not re.search("[A-Z]", password) or not re.search("[0-9]", password):
            messagebox.showerror("Error", "Password must contain at least one lowercase letter, one uppercase letter, and one digit")
            return

        # Save user details to the database
        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        query = "INSERT INTO User (FirstName, LastName, Email, Username, Password) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(query, (first_name, last_name, email, username, password))
        conn.commit()
        cursor.close()
        conn.close()

        # Show success message
        messagebox.showinfo("Success", "Account created successfully!")

        # Clear input fields
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.password_confirm_entry.delete(0, tk.END)

        # Return focus to the first name entry field
        self.first_name_entry.focus_set()


if __name__ == "__main__":
    # Create a Tkinter window
    root = tk.Tk()

    # Create an instance of the LoginPage
    login_page = LoginPage(root)

    # Run the main loop for the login page
    login_page.mainloop()
