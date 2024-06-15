import tkinter as tk
from tkinter import messagebox
from database.auth import register_user, login_user
from database.movie_management import add_movie, delete_movie, get_user_movies, get_all_movies

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikacja Filmowa")

        self.login_frame = tk.Frame(root)
        self.login_frame.pack(padx=10, pady=10)

        tk.Label(self.login_frame, text="Nazwa użytkownika:").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Hasło:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.login_frame, text="Zaloguj się", command=self.login).grid(row=2, column=0, columnspan=2)
        tk.Button(self.login_frame, text="Rejestracja", command=self.show_register).grid(row=3, column=0, columnspan=2)

        self.register_frame = tk.Frame(root)
        self.user_role = tk.StringVar(value="user")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = login_user(username, password)
        if user:
            if user[3] == "admin":
                self.show_admin_view()
            else:
                self.show_user_view()
        else:
            messagebox.showerror("Błąd logowania", "Niepoprawna nazwa użytkownika lub hasło")

    def show_register(self):
        self.login_frame.pack_forget()
        self.register_frame.pack(padx=10, pady=10)

        tk.Label(self.register_frame, text="Nazwa użytkownika:").grid(row=0, column=0)
        self.reg_username_entry = tk.Entry(self.register_frame)
        self.reg_username_entry.grid(row=0, column=1)

        tk.Label(self.register_frame, text="Hasło:").grid(row=1, column=0)
        self.reg_password_entry = tk.Entry(self.register_frame, show="*")
        self.reg_password_entry.grid(row=1, column=1)

        tk.Label(self.register_frame, text="Rola:").grid(row=2, column=0)
        tk.Radiobutton(self.register_frame, text="Użytkownik", variable=self.user_role, value="user").grid(row=2, column=1)
        tk.Radiobutton(self.register_frame, text="Administrator", variable=self.user_role, value="admin").grid(row=3, column=1)

        tk.Button(self.register_frame, text="Zarejestruj się", command=self.register).grid(row=4, column=0, columnspan=2)
        tk.Button(self.register_frame, text="Wróć", command=self.show_login).grid(row=5, column=0, columnspan=2)

    def register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        role = self.user_role.get()

        if register_user(username, password, role):
            messagebox.showinfo("Sukces", "Rejestracja udana")
            self.show_login()
        else:
            messagebox.showerror("Błąd rejestracji", "Nazwa użytkownika jest już zajęta")

    def show_login(self):
        self.register_frame.pack_forget()
        self.login_frame.pack(padx=10, pady=10)

    def show_admin_view(self):
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        admin_frame = tk.Frame(self.root)
        admin_frame.pack(padx=10, pady=10)
        tk.Label(admin_frame, text="Panel administratora").pack()

    def show_user_view(self):
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        user_frame = tk.Frame(self.root)
        user_frame.pack(padx=10, pady=10)
        tk.Label(user_frame, text="Panel użytkownika").pack()



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
