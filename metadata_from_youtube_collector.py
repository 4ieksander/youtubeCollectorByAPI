import os
import pandas as pd
from googleapiclient.discovery import build

# Set up API credentials
with open("api_key.txt", "r") as f:
    API_KEY = f.read().strip()
youtube = build('youtube', 'v3', developerKey=API_KEY)

database = []


def add_video():
    video_url = input("Enter the URL of the video: ")
    video_id = video_url.split("v=")[1]
    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )
    response = request.execute()
    video_info = response["items"][0]
    video_data = {
        "title": video_info["snippet"]["title"],
        "published_at": video_info["snippet"]["publishedAt"],
        "views": int(video_info["statistics"]["viewCount"]),
        "likes": int(video_info["statistics"]["likeCount"]),
    }
    print(type(video_info["snippet"]["publishedAt"]))
    database.append(video_data)
    print("Video added successfully!")


def display_videos():
    if not database:
        print("No videos in the database.")
        return
    df = pd.DataFrame(database)
    print(df)


def sort_videos():
    if not database:
        print("No videos in the database.")
        return
    sort_by = input("Enter the column to sort by (title, published_at, views, likes): ")
    order = input("Sort in ascending order? (yes/no): ").lower() == 'yes'
    df = pd.DataFrame(database)
    df = df.sort_values(by=sort_by, ascending=order)
    print(df)


def filter_videos():
    if not database:
        print("No videos in the database.")
        return
    filter_by = input("Enter the column to filter by (title, published_at, views, likes): ")
    char = input("Enter operator (>, <, >=, <=, ==, !=): ")
    value = input("Enter value to filter by: ")

    try:
        value = int(value) if filter_by in ['views', 'likes'] else value
        df = pd.DataFrame(database)
        df = df[eval(f"df[filter_by] {char} value")]
        print(df)
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    while True:
        try:
            print("Menu:")
            print("1. Wyświetl filmy")
            print("2. Dodaj nowy film")
            print("3. Sortuj filmy")
            print("4. Filtruj filmy")
            print("5. Wyjdź")

            choice = input("Choose an option: ")

            if choice == "1":
                display_videos()
            elif choice == "2":
                add_video()
            elif choice == "3":
                sort_videos()
            elif choice == "4":
                filter_videos()
            elif choice == "5":
                break
            else:
                print("Invalid option. Please try again.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
