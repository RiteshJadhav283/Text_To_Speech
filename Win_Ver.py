import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import pygame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os
import tempfile
import time
import threading
from scipy.io import wavfile
import platform
import pyttsx3
from pydub import AudioSegment  # For MP3 conversion


class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Speech Converter")
        self.root.geometry("800x650")

        # Initialize pygame for audio playback
        pygame.mixer.init()

        # Initialize pyttsx3 engine
        self.engine = pyttsx3.init()

        # Track if audio is currently playing
        self.is_playing = False
        self.temp_files = []

        # Check if running on macOS
        self.is_mac = platform.system() == "Darwin"

        self.create_widgets()

    def create_widgets(self):
        # Text input area
        input_frame = ttk.LabelFrame(self.root, text="Enter Text")
        input_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.text_input = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, width=70, height=10)
        self.text_input.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Controls frame
        controls_frame = ttk.LabelFrame(self.root, text="Voice Controls")
        controls_frame.pack(padx=10, pady=10, fill=tk.X)

        # Voice selection
        ttk.Label(controls_frame, text="Voice Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.voice_type = ttk.Combobox(controls_frame, values=["Male", "Female", "Robotic"],
                                       state="readonly")
        self.voice_type.current(1)
        self.voice_type.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Speed control
        ttk.Label(controls_frame, text="Speech Speed:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.speed_scale = ttk.Scale(controls_frame, from_=50, to=200, length=200, orient=tk.HORIZONTAL, value=100)
        self.speed_scale.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.speed_label = ttk.Label(controls_frame, text="100%")
        self.speed_label.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.speed_scale.bind("<Motion>",
                              lambda e: self.speed_label.configure(text=f"{int(self.speed_scale.get())}%"))

        # Pitch control (disabled on macOS)
        ttk.Label(controls_frame, text="Pitch:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.pitch_scale = ttk.Scale(controls_frame, from_=50, to=200, length=200, orient=tk.HORIZONTAL, value=100)
        self.pitch_scale.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.pitch_label = ttk.Label(controls_frame, text="100%")
        self.pitch_label.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        self.pitch_scale.bind("<Motion>",
                              lambda e: self.pitch_label.configure(text=f"{int(self.pitch_scale.get())}%"))

        if self.is_mac:
            self.pitch_scale.config(state=tk.DISABLED)
            self.pitch_label.config(text="Not supported on macOS")

        # Buttons frame
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(padx=10, pady=10, fill=tk.X)

        self.play_button = ttk.Button(buttons_frame, text="Play", command=self.play_text)
        self.play_button.grid(row=0, column=0, padx=5, pady=5)

        self.save_button = ttk.Button(buttons_frame, text="Save as MP3", command=self.save_as_mp3)  # Updated to MP3
        self.save_button.grid(row=0, column=1, padx=5, pady=5)

        self.stop_button = ttk.Button(buttons_frame, text="Stop", command=self.stop_playback, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=5, pady=5)

        # Waveform display
        self.fig, self.ax = plt.subplots(figsize=(7, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(padx=10, pady=10, fill=tk.BOTH)
        self.ax.set_title("Audio Waveform")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.canvas.draw()

        # Status label
        self.status_label = ttk.Label(self.root, text="Ready")
        self.status_label.pack(pady=5)

        # Clean up temp files on exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def set_voice_params(self):
        """Set voice parameters for pyttsx3"""
        # Set voice type
        voices = self.engine.getProperty('voices')
        if "Male" in self.voice_type.get():
            self.engine.setProperty('voice', voices[0].id)  # Male voice
        elif "Female" in self.voice_type.get():
            self.engine.setProperty('voice', voices[1].id)  # Female voice
        elif "Robotic" in self.voice_type.get():
            self.engine.setProperty('voice', voices[0].id)  # Default to male for robotic

        # Set speed
        self.engine.setProperty('rate', int(self.speed_scale.get()))

        # Set pitch (disabled on macOS)
        if not self.is_mac:
            self.engine.setProperty('pitch', int(self.pitch_scale.get()))

    def text_to_audio(self, text, output_file=None):
        """Convert text to speech using pyttsx3"""
        if not text:
            return None

        # Create a temporary file if no output file is specified
        if output_file is None:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            output_file = temp_file.name
            temp_file.close()
            self.temp_files.append(output_file)

        # Set voice parameters
        self.set_voice_params()

        # Save speech to a file
        self.engine.save_to_file(text, output_file)
        self.engine.runAndWait()

        return output_file

    def play_text(self):
        """Process text and play the resulting audio"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            self.status_label.config(text="Please enter some text first")
            return

        # Disable buttons during processing
        self.play_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.status_label.config(text="Processing...")
        self.root.update()

        # Create a thread for text-to-speech processing
        def process_and_play():
            try:
                # Convert text to speech
                audio_file = self.text_to_audio(text)
                if audio_file is None:
                    self.status_label.config(text="Failed to generate speech")
                    self.play_button.config(state=tk.NORMAL)
                    self.save_button.config(state=tk.NORMAL)
                    return

                # Display waveform
                self.display_waveform(audio_file)

                # Play the audio
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()

                # Update UI state
                self.is_playing = True
                self.root.after(0, lambda: self.stop_button.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.status_label.config(text="Playing..."))

                # Wait for playback to finish
                while pygame.mixer.music.get_busy() and self.is_playing:
                    time.sleep(0.1)

                # Reset UI when done
                self.root.after(0, lambda: self.play_button.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.save_button.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))

                if self.is_playing:  # Only update if not manually stopped
                    self.root.after(0, lambda: self.status_label.config(text="Ready"))
                    self.is_playing = False

            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}"))
                self.root.after(0, lambda: self.play_button.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.save_button.config(state=tk.NORMAL))

        # Start processing thread
        threading.Thread(target=process_and_play, daemon=True).start()

    def stop_playback(self):
        """Stop audio playback"""
        self.is_playing = False
        pygame.mixer.music.stop()
        self.play_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped")

    def display_waveform(self, wav_file):
        """Display the waveform of the audio file"""
        try:
            # Read the WAV file
            sample_rate, data = wavfile.read(wav_file)

            # If stereo, convert to mono by taking the average
            if len(data.shape) > 1 and data.shape[1] > 1:
                data = np.mean(data, axis=1)

            # Normalize data for display
            normalized_data = data / (np.max(np.abs(data)) + 1e-10)

            # Calculate time axis
            time = np.linspace(0, len(data) / sample_rate, num=len(data))

            # Clear previous plot
            self.ax.clear()

            # Plot the waveform
            self.ax.plot(time, normalized_data, linewidth=0.5)
            self.ax.set_title("Audio Waveform")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Amplitude")
            self.ax.set_ylim(-1, 1)
            self.ax.grid(True)

            # Update the canvas
            self.canvas.draw()

        except Exception as e:
            print(f"Error displaying waveform: {str(e)}")

    def save_as_mp3(self):
        """Save speech as an MP3 file"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            self.status_label.config(text="Please enter some text first")
            return

        # Get the file save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )

        if not file_path:
            self.status_label.config(text="Save cancelled")
            return

        # Disable buttons during processing
        self.play_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.status_label.config(text="Processing and saving...")
        self.root.update()

        # Create a thread for saving
        def process_and_save():
            try:
                # Generate the WAV file
                wav_file = self.text_to_audio(text)

                # Verify the WAV file
                try:
                    sample_rate, data = wavfile.read(wav_file)
                    print(f"WAV file is valid. Sample rate: {sample_rate}, Data shape: {data.shape}")
                except Exception as e:
                    self.root.after(0, lambda: self.status_label.config(text=f"Invalid WAV file: {str(e)}"))
                    return

                # Convert WAV to MP3 using pydub
                audio = AudioSegment.from_wav(wav_file)
                audio.export(file_path, format="mp3", bitrate="192k")  # Set bitrate for better quality

                # Display the waveform
                self.display_waveform(wav_file)

                # Update UI
                self.root.after(0, lambda: self.status_label.config(text=f"Saved to {file_path}"))

            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"Error saving file: {str(e)}"))

            # Re-enable buttons
            self.root.after(0, lambda: self.play_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.save_button.config(state=tk.NORMAL))

        # Start processing thread
        threading.Thread(target=process_and_save, daemon=True).start()

    def on_closing(self):
        """Clean up temporary files when closing the application"""
        # Stop any playback
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        # Delete all temporary files
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass

        # Close the window
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()