import cv2
import numpy as np
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from pytube import YouTube
import os
import sys
import time
import signal
from deepface import DeepFace
import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

# Define global variables
cap = None
# Define color codes

happy_color = (0, 0, 255) #red
anger_color = (0, 255, 0) #green
sad_color = (255, 0, 0) #blue
disgust_color = (255, 0, 255) # = happy + sad = blue + red = magenta/purple
surprise_color = (0, 255, 255) # = happy + anger = green + red = yellow
fear_color = (255, 255, 0) # = sad + anger = green + blue = cyan
neutral_color = (255, 255, 255) #neutral = happy + sad + anger = white

canvas = np.ones((1024, 1024, 3), dtype=np.uint8)

def download_video():
    # Get the video URL from the entry widget
    url = url_entry.get()
    
   # Create a YouTube object
    yt = YouTube(url)

    # Select the highest resolution stream
    stream = yt.streams.get_highest_resolution()

    # Download the video
    stream.download(filename='video.mp4')

    # Update the progress status label
    status_label.config(text='Downloading: DONE')
    status_label.update()    
    
def play_video():
    global cap
    # Load the video file
    cap = cv2.VideoCapture('video.mp4')
    
    # Play the video
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img_tk = ImageTk.PhotoImage(img)
        video_canvas.img_tk = img_tk
        video_canvas.create_image(0, 0, anchor='nw', image=img_tk)
        video_canvas.update()
        video_canvas.config(width=img_tk.width(), height=img_tk.height())
    
    # Release the video file
    cap.release()
    
def preview_video():
    # Stop any video currently playing
    stop_preview()
    
    # Play the video
    play_video_button.config(state=DISABLED)
    stop_preview_button.config(state=NORMAL)
    play_video()
    play_video_button.config(state=NORMAL)
    stop_preview_button.config(state=DISABLED)
    
def stop_preview():
    global cap
    # Stop any video currently playing
    if cap is not None:
        cap.release()
        cap = None
    
    # Clear the canvas
    play_video_button.config(state=NORMAL)
    stop_preview_button.config(state=DISABLED)
    video_canvas.delete("all")

def frame_generator(cap):
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        yield frame

def extract_frames():
    folderName = 'frames'
    os.makedirs(folderName, exist_ok=True)

    # Clear any existing frames in the folder
    with os.scandir(folderName) as entries:
        for entry in entries:
            if entry.is_file():
                os.remove(entry.path)

    fileName = 'video.mp4'
    cap = cv2.VideoCapture(fileName)
    frame_count = 0
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    EVERYHOWMANYPERSECOND = int(analyse_entry.get())

    for frame in frame_generator(cap):
        frame_count += 1
        if frame_count % (fps * EVERYHOWMANYPERSECOND) == 0:
            elapsed_time = frame_count // fps
            new_filename = f"frame_{str(int(elapsed_time)).zfill(6)}.jpg"
            frame_filename = os.path.join(folderName, new_filename)
            cv2.imwrite(frame_filename, frame)

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(img)
            video_canvas.img_tk = img_tk
            video_canvas.create_image(0, 0, anchor='nw', image=img_tk)
            video_canvas.update()
            video_canvas.config(width=img_tk.width(), height=img_tk.height())

        progress = f"{frame_count}/{total_frames} ({int(frame_count/total_frames*100)}%)"
        status_label.config(text=f"{progress} frames extracted")

    cap.release()
    frame_count = len(os.listdir(folderName))
    status_label.config(text=f'{frame_count} frames extracted successfully!')
def draw_happy(canvas, happy_value, happy_color):
    if happy_value > 0:
        side_length = int(np.sqrt(10 * happy_value))
        x, y = np.random.randint(1024 - side_length), np.random.randint(1024 - side_length)
        cv2.rectangle(canvas, (x, y), (x + side_length, y + side_length), color=happy_color, thickness=-1)

def draw_sad(canvas, sad_value, sad_color):
    if sad_value > 0:
        side_length = int(np.sqrt(10 * sad_value))
        x, y = np.random.randint(1024 - side_length), np.random.randint(1024 - side_length)
        cv2.rectangle(canvas, (x, y), (x + side_length, y + side_length), color=sad_color, thickness=-1)

def draw_anger(canvas, anger_value, anger_color):
    if anger_value > 0:
        side_length = int(np.sqrt(10 * anger_value))
        x, y = np.random.randint(1024 - side_length), np.random.randint(1024 - side_length)
        cv2.rectangle(canvas, (x, y), (x + side_length, y + side_length), color=anger_color, thickness=-1)

def draw_disgust(canvas, disgust_value, disgust_color):
    if disgust_value > 0:
        side_length = int(np.sqrt(10 * disgust_value))
        x, y = np.random.randint(1024 - side_length), np.random.randint(1024 - side_length)
        cv2.rectangle(canvas, (x, y), (x + side_length, y + side_length), color=disgust_color, thickness=-1)

def draw_fear(canvas, fear_value, fear_color):
    if fear_value > 0:
        side_length = int(np.sqrt(10 * fear_value))
        x, y = np.random.randint(1024 - side_length), np.random.randint(1024 - side_length)
        cv2.rectangle(canvas, (x, y), (x + side_length, y + side_length), color=fear_color, thickness=-1)

def draw_surprise(canvas, surprise_value, surprise_color):
    if surprise_value > 0:
        side_length = int(np.sqrt(10 * surprise_value))
        x, y = np.random.randint(1024 - side_length), np.random.randint(1024 - side_length)
        cv2.rectangle(canvas, (x, y), (x + side_length, y + side_length), color=surprise_color, thickness=-1)

def draw_neutral(canvas, neutral_value, neutral_color):
    if neutral_value > 0:
        side_length = int(np.sqrt(10 * neutral_value))
        x, y = np.random.randint(1024 - side_length), np.random.randint(1024 - side_length)
        cv2.rectangle(canvas, (x, y), (x + side_length, y + side_length), color=neutral_color, thickness=-1)


def process_image(src_path, dest_path, canvas):
    analysesEmotion(src_path, canvas)
    cv2.imwrite(dest_path, canvas)
    img = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img_tk = ImageTk.PhotoImage(img)
    return img_tk

def analyse_emotion():
    canvas[:] = 0
    folder_path = "emotions"
    os.makedirs(folder_path, exist_ok=True)

    # Clear any existing files in the 'emotions' folder
    with os.scandir(folder_path) as entries:
        for entry in entries:
            if entry.is_file():
                os.remove(entry.path)

    filenames = sorted(os.listdir("frames"))
    total_files = len(filenames)
    counter = 0

    for filename in filenames:
        if filename.endswith(".jpg"):
            src_path = os.path.join("frames", filename)
            dest_filename = os.path.splitext(filename)[0] + ".png"
            dest_path = os.path.join("emotions", dest_filename)

            img_tk = process_image(src_path, dest_path, canvas)

            if counter % 5 == 0:
                video_canvas.img_tk = img_tk
                video_canvas.create_image(0, 0, anchor='nw', image=img_tk)
                video_canvas.update()
                video_canvas.config(width=img_tk.width(), height=img_tk.height())

            progress = f"{counter}/{total_files} ({int(counter/total_files*100)}%)"
            status_label.config(text=f"{progress} Emotions analysed")

            counter += 1

    status_label.config(text='Emotions analysed successfully!')

def analysesEmotion(imagePath, canvasImg):
    try:
        # Use DeepFace to analyze emotions
        result = DeepFace.analyze(imagePath, actions=['emotion'])
        
        for idx, emotion_values in enumerate(result):
            #print(f"Emotions for person {idx+1}:")
            anger_value = emotion_values['emotion']['angry']
            disgust_value = emotion_values['emotion']['disgust']
            fear_value = emotion_values['emotion']['fear']
            happy_value = emotion_values['emotion']['happy']
            sad_value = emotion_values['emotion']['sad']
            surprise_value = emotion_values['emotion']['surprise']
            neutral_value = emotion_values['emotion']['neutral']
            
            emotions = [draw_happy, draw_sad, draw_anger, draw_disgust, draw_fear, draw_surprise, draw_neutral]

            for emotion in np.random.permutation(emotions):
                emotion(canvas, happy_value, happy_color)
                emotion(canvas, sad_value, sad_color)
                emotion(canvas, anger_value, anger_color)
                emotion(canvas, disgust_value, disgust_color)
                emotion(canvas, fear_value, fear_color)
                emotion(canvas, surprise_value, surprise_color)
    
    except ValueError as e:
        print(f"No faces were found in image: {imagePath}")
        
def create_csv():
    # Set the directory path
    dir_path = 'emotions/'

    # Get the list of image files in the directory and sort them alphabetically
    image_files = sorted([f for f in os.listdir(dir_path) if f.endswith('.jpg') or f.endswith('.png')])

    # Open a CSV file for writing the emotion values
    with open('emotion.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Image', 'Emotion Value'])

        # Loop through each image file
        for i, image_file in enumerate(image_files):
            
            # Get the basename of the file
            basename = os.path.basename(image_file)

            # Strip the extension
            basename = os.path.splitext(basename)[0]

            # Keep only the numerical part of the filename
            numerical_part = ''.join(filter(str.isdigit, basename))

            # Read the image and split it into 3 channels
            image = cv2.imread(dir_path + image_file)
            b, g, r = cv2.split(image)

            # Calculate the average intensity of each channel
            avg_r = cv2.mean(r)[0]
            avg_g = cv2.mean(g)[0]
            avg_b = cv2.mean(b)[0]

            # Calculate the emotion value for the image
            emotion_value = (2*avg_r - (avg_g + avg_b)) / 2

            # Write the image filename and emotion value to the CSV file
            csvwriter.writerow([numerical_part, emotion_value])

            # Update the progress status label
            percentage_done = int((i+1) / len(image_files) * 100)
            status_label.config(text='Processing: {}%'.format(percentage_done))
            status_label.update()

    print("Emotion values have been calculated and saved to 'emotion.csv'.")


def plot():
    df = pd.read_csv('emotion.csv')

    x = df['Image'] / 60
    y = df['Emotion Value']

    avg_y = y.mean()
    if avg_y > 0:
        plot_color = 'red'
    else:
        plot_color = 'blue'

    fig = plt.figure(figsize=(6.4, 4.0), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(x, y, color=plot_color)

    ax.axhline(y=0, color='black', linestyle='-')
    ax.axvline(x=0, color='black', linestyle='-')

    ax.set_xlabel('Time (minutes)')
    ax.set_ylabel('Emotion Value')
    ax.set_title('Movie Emotion Graph')

    canvas = FigureCanvasTkAgg(fig, master=video_canvas)
    canvas.draw()

    w, h = fig.get_size_inches() * fig.get_dpi()
    img = np.fromstring(canvas.tostring_rgb(), dtype=np.uint8).reshape(int(h), int(w), 3)
    img = Image.fromarray(img)
    img_tk = ImageTk.PhotoImage(img)
    video_canvas.img_tk = img_tk
    video_canvas.create_image(0, 0, anchor='nw', image=img_tk)
    video_canvas.config(width=img_tk.width(), height=img_tk.height())


def run_all():
    download_video()
    extract_frames()
    analyse_emotion()
    create_csv()
    plot()

def select_all(event):
    # Select all text in the Entry widget
    url_entry.delete(0, 'end')

# Create the main window
window = Tk()
window.title('YouTube Downloader & emotion analyser')

# Create the URL label and entry widget in one row
url_frame = Frame(window)
url_frame.pack(pady=10)

url_label = Label(url_frame, text='Enter video URL:')
url_label.pack(side=LEFT)
url_entry = Entry(url_frame, width=90)
url_entry.pack(side=LEFT)
# Bind the Entry widget to the left mouse button click event
url_entry.bind("<Button-1>", select_all)

# Create a new frame for the Analyse label and entry widget
analyse_frame = Frame(window)
analyse_frame.pack()

analyse_label = Label(analyse_frame, text='Analyse ONE frame every X seconds: ')
analyse_label.pack(side=LEFT)
analyse_entry = Entry(analyse_frame)
analyse_entry.insert(0, '3')
analyse_entry.pack(side=LEFT)

# Create the download and preview buttons
button_frame = Frame(window)
button_frame.pack(pady=10)

download_button = ttk.Button(button_frame, text='Download', command=download_video)
download_button.pack(side=LEFT, padx=10)
play_video_button = ttk.Button(button_frame, text='Preview', command=preview_video)
play_video_button.pack(side=LEFT, padx=10)
stop_preview_button = ttk.Button(button_frame, text='Stop Preview', command=stop_preview, state=DISABLED)
stop_preview_button.pack(side=LEFT, padx=10)

extract_frames_button = ttk.Button(button_frame, text='Extract Frames', command=extract_frames)
extract_frames_button.pack(side=LEFT, padx=10)

emotion_button = ttk.Button(button_frame, text='Analyse Emotion', command=analyse_emotion)
emotion_button.pack(side=LEFT, padx=10)
csv_button = ttk.Button(button_frame, text='Create CSV', command=create_csv)
csv_button.pack(side=LEFT, padx=10)
plot_button = ttk.Button(button_frame, text='Plot', command=plot)
plot_button.pack(side=LEFT, padx=10)
run_all_button = ttk.Button(button_frame, text='Run All', command=run_all)
run_all_button.pack(side=LEFT, padx=10)

# Create the status label
status_label = Label(window, text='')
status_label.pack()

# Create the video canvas
video_canvas = Canvas(window, width=640, height=360, bg='black')
video_canvas.pack(pady=10)

# Start the main loop
window.mainloop()

