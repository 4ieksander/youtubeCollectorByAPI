import tkinter as tk
from tkinter import messagebox, ttk
from database.auth import register_user, login_user, block_user, get_all_users
from database.movie_management import add_movie, delete_movie, get_user_movies, get_all_movies
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
        self.admin_frame = tk.Frame(root)
        self.movies_tree = None


    # Authentication methods
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



    # Admin views and methods
    def show_admin_view(self):
        self.clear_frame(self.user_frame)
        self.clear_frame(self.register_frame)
        self.clear_frame(self.login_frame)
        self.clear_frame(self.admin_frame)

        self.admin_frame = tk.Frame(self.root)
        self.admin_frame.pack(padx=10, pady=10)

        tk.Label(self.admin_frame, text="Panel administratora").pack()

        all_users = get_all_users()
        all_movies = get_all_movies()

        for user in all_users:
            if user[3] == 'admin':
                continue

            user_movies = [movie for movie in all_movies if movie[5] == user[0]]

            if user[4]:
                blocked_until = f" (Zablokowany do: {user[4]})"
            else:
                blocked_until = ""

            user_info = f"{user[1]} (id: {user[0]}) - Filmy: {len(user_movies)}{blocked_until}"
            tk.Label(self.admin_frame, text=user_info).pack()

            tk.Button(self.admin_frame, text="Zablokuj na 5 minut",
                      command=lambda u=user[0]: self.block_user(u)).pack()

            movies_tree = ttk.Treeview(self.admin_frame,
                                       columns=("id", "title", "published_at", "views", "likes"),
                                       show='headings')
            movies_tree.heading("id", text="ID")
            movies_tree.column("id", width=30)
            movies_tree.heading("title", text="Tytuł")
            movies_tree.heading("published_at", text="Data publikacji")
            movies_tree.heading("views", text="Wyświetlenia")
            movies_tree.heading("likes", text="Polubienia")
            movies_tree.pack()

            for movie in user_movies:
                movies_tree.insert("", "end", values=(movie[0], movie[1], movie[2], movie[3], movie[4]))

            movies_tree.bind("<Double-1>", lambda event, tree=movies_tree: self.handle_admin_delete_click(event, tree))

    def clear_frame(self, frame):
        if frame:
            for widget in frame.winfo_children():
                widget.destroy()

    def handle_admin_delete_click(self, event, tree):
        item_id = tree.identify_row(event.y)
        column = tree.identify_column(event.x)

        if column == "#6":  # Column 6 is for delete button
            movie_id = tree.item(item_id)["values"][0]
            self.delete_movie_admin(movie_id)

    def delete_movie_admin(self, movie_id):
        delete_movie(movie_id)
        messagebox.showinfo("Sukces", "Film usunięty")
        self.show_admin_view()

    def block_user(self, user_id):
        block_user(user_id, 5)
        messagebox.showinfo("Sukces", "Użytkownik zablokowany na 5 minut")
        self.show_admin_view()



    # User views and methods
    def show_user_view(self):
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        self.user_frame.pack_forget()

        self.user_frame = tk.Frame(self.root)
        self.user_frame.pack(padx=10, pady=10)
        tk.Label(self.user_frame, text="Panel użytkownika").pack()

        tk.Button(self.user_frame, text="Dodaj film", command=self.show_add_movie).pack()

        self.movies_tree = ttk.Treeview(self.user_frame,
                                        columns=("id", "title", "published_at", "views", "likes", "delete"),
                                        show='headings')
        self.movies_tree.heading("id", text="ID", anchor=tk.W)  # Ukryta kolumna
        self.movies_tree.column("id", width=0, stretch=tk.NO)
        self.movies_tree.heading("title", text="Tytuł")
        self.movies_tree.heading("published_at", text="Data publikacji")
        self.movies_tree.heading("views", text="Wyświetlenia")
        self.movies_tree.heading("likes", text="Polubienia")
        self.movies_tree.heading("delete", text="Usuń")
        self.movies_tree.column("delete", width=50)
        self.movies_tree.pack()

        self.populate_movies_tree()

        tk.Button(self.user_frame, text="Sortuj filmy", command=self.sort_movies).pack()
        tk.Button(self.user_frame, text="Filtruj filmy", command=self.filter_movies).pack()

    def populate_movies_tree(self):
        for i in self.movies_tree.get_children():
            self.movies_tree.delete(i)

        user_movies = get_user_movies(self.current_user[0])
        for movie in user_movies:
            self.movies_tree.insert("", "end", values=(movie[0], movie[1], movie[2], movie[3], movie[4], "Usuń"))

        self.movies_tree.bind("<Button-1>", self.handle_delete_click)

    def handle_delete_click(self, event):
        region = self.movies_tree.identify_region(event.x, event.y)
        if region == "cell":
            row_id = self.movies_tree.identify_row(event.y)
            column = self.movies_tree.identify_column(event.x)
            if column == "#6":
                movie_id = self.movies_tree.item(row_id)["values"][0]
                self.delete_movie_user(movie_id)

    def delete_movie_user(self, movie_id):
        delete_movie(movie_id)
        messagebox.showinfo("Sukces", "Film usunięty")
        self.show_user_view()


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



    # Sorting and filtering methods
    def sort_movies(self):
        sort_window = tk.Toplevel(self.root)
        sort_window.title("Sortowanie filmów")

        tk.Label(sort_window, text="Sortuj według:").pack()
        sort_by = tk.StringVar()
        options = ["title", "published_at", "views", "likes"]
        ttk.Combobox(sort_window, textvariable=sort_by, values=options).pack()

        tk.Label(sort_window, text="Kolejność:").pack()
        ascending = tk.BooleanVar()
        tk.Radiobutton(sort_window, text="Rosnąco", variable=ascending, value=True).pack()
        tk.Radiobutton(sort_window, text="Malejąco", variable=ascending, value=False).pack()

        tk.Button(sort_window, text="Sortuj", command=lambda: self.perform_sort(sort_by.get(), ascending.get(), sort_window)).pack()

    def perform_sort(self, sort_by, ascending, window):
        user_movies = get_user_movies(self.current_user[0])
        df = pd.DataFrame(user_movies, columns=["id", "title", "published_at", "views", "likes", "user_id"])
        df = df.sort_values(by=sort_by, ascending=ascending)

        for i in self.movies_tree.get_children():
            self.movies_tree.delete(i)

        for _, movie in df.iterrows():
            self.movies_tree.insert("", "end", values=(
            movie["id"], movie["title"], movie["published_at"], movie["views"], movie["likes"], "Usuń"))

        window.destroy()
        self.movies_tree.bind("<Button-1>", self.handle_delete_click)


    def filter_movies(self):
        filter_window = tk.Toplevel(self.root)
        filter_window.title("Filtracja filmów")

        tk.Label(filter_window, text="Filtruj według:").pack()
        filter_by = tk.StringVar()
        options = ["title", "published_at", "views", "likes"]
        ttk.Combobox(filter_window, textvariable=filter_by, values=options).pack()

        tk.Label(filter_window, text="Operator:").pack()
        operator = tk.StringVar()
        options = ["==", "!=", ">", "<", ">=", "<="]
        ttk.Combobox(filter_window, textvariable=operator, values=options).pack()

        tk.Label(filter_window, text="Wartość:").pack()
        value_entry = tk.Entry(filter_window)
        value_entry.pack()

        tk.Button(filter_window, text="Filtruj", command=lambda: self.perform_filter(filter_by.get(), operator.get(), value_entry.get(), filter_window)).pack()

    def perform_filter(self, filter_by, operator, value, window):
        user_movies = get_user_movies(self.current_user[0])
        df = pd.DataFrame(user_movies, columns=["id", "title", "published_at", "views", "likes", "user_id"])

        try:
            if filter_by in ["views", "likes"]:
                value = int(value)
            df = df.query(f"{filter_by} {operator} @value")

            for i in self.movies_tree.get_children():
                self.movies_tree.delete(i)

            for _, movie in df.iterrows():
                self.movies_tree.insert("", "end", values=(
                movie["id"], movie["title"], movie["published_at"], movie["views"], movie["likes"], "Usuń"))
        except Exception as e:
            messagebox.showerror("Błąd filtrowania", f"Wystąpił błąd: {e}")

        window.destroy()
        self.movies_tree.bind("<Button-1>", self.handle_delete_click)





if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = App(root)
        root.mainloop()
    except KeyboardInterrupt:
        messagebox.showinfo("Koniec dzialania aplikacji", "Program zostal przerwany przez uzytkownika")
        exit(0)