import tkinter as tk
from tkinter import messagebox
from database.auth import register_user, login_user, block_user
from database.movie_management import add_movie, delete_movie, get_user_movies, get_all_movies, get_all_users
from datetime import datetime
import pandas as pd
from googleapiclient.discovery import build


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikacja z połączeniem do YouTube API")

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

        with open("api_key.txt", "r") as file:
            API_KEY = file.read().strip()
        self.youtube = build('youtube', 'v3', developerKey=API_KEY)
        self.user_frame = tk.Frame(root)


    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = login_user(username, password)
        if user:
            self.current_user = user
            if user[3] == "admin":
                self.show_admin_view()
            else:
                self.show_user_view()
        else:
            messagebox.showerror("Błąd logowania",
                                 "Niepoprawna nazwa użytkownika lub hasło lub użytkownik zablokowany.")

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
        tk.Radiobutton(self.register_frame, text="Użytkownik", variable=self.user_role, value="user").grid(row=2,
                                                                                                           column=1)
        tk.Radiobutton(self.register_frame, text="Administrator", variable=self.user_role, value="admin").grid(
            row=3, column=1)

        tk.Button(self.register_frame, text="Zarejestruj się", command=self.register).grid(row=4, column=0,
                                                                                           columnspan=2)
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

        movies = get_all_movies()
        for movie in movies:
            tk.Label(admin_frame, text=f"{movie[1]} (id: {movie[0]})").pack()
            tk.Button(admin_frame, text="Usuń", command=lambda m=movie[0]: self.delete_movie(m)).pack()

        tk.Label(admin_frame, text="Użytkownicy:").pack()
        for user in self.get_all_users():
            tk.Label(admin_frame, text=f"{user[1]} (id: {user[0]})").pack()
            tk.Button(admin_frame, text="Zablokuj na 5 minut", command=lambda u=user[0]: self.block_user(u)).pack()


    def show_user_view(self):
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        self.user_frame.pack_forget()

        self.user_frame = tk.Frame(self.root)
        self.user_frame.pack(padx=10, pady=10)
        tk.Label(self.user_frame, text="Panel użytkownika").pack()

        tk.Button(self.user_frame, text="Dodaj film", command=self.show_add_movie).pack()

        user_movies = get_user_movies(self.current_user[0])
        for movie in user_movies:
            tk.Label(self.user_frame, text=f"{movie[1]}").pack()




    def show_add_movie(self):
        add_movie_frame = tk.Toplevel(self.root)
        tk.Label(add_movie_frame, text="Adres URL do filmu (nie playlisty!)").pack()
        video_url = tk.Entry(add_movie_frame)
        video_url.pack()
        tk.Button(add_movie_frame, text="Dodaj",
                  command=lambda: self.add_movie(video_url.get())).pack()

    def add_movie(self, video_url):
        video_id = video_url.split("v=")[1]
        request = self.youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        )
        try:
            response = request.execute()
            video_info = response["items"][0]
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Sprawdz czy podałeś bezpośredni link do filmu oraz czy film nie jest zbyt długi.")
            messagebox.showinfo("Błąd", "Sprawdz czy podałeś bezpośredni link do filmu oraz czy film nie jest zbyt długi.")
            return self.show_add_movie()
        video_data = {
            "title": video_info["snippet"]["title"],
            "published_at": video_info["snippet"]["publishedAt"],
            "views": int(video_info["statistics"]["viewCount"]),
            "likes": int(video_info["statistics"]["likeCount"]),
        }
        add_movie(video_data,  self.current_user[0])
        print("Video added successfully!")
        messagebox.showinfo("Sukces", "Film dodany")

        self.show_user_view()


    def delete_movie(self, movie_id):
        delete_movie(movie_id)
        messagebox.showinfo("Sukces", "Film usunięty")
        self.show_admin_view()

    def block_user(self, user_id):
        block_user(user_id, 5)
        messagebox.showinfo("Sukces", "Użytkownik zablokowany na 5 minut")
        self.show_admin_view()



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
