Hello 👋

I have created a Python Program Where you either write or copy text. Then that text is converted into Speech.

I have Created to 2 version 
1. Windows
2. Mac

🛑 Features 🛑
1. Multiple Voices: Choose from different voice options for speech synthesis.
2. Speed & Pitch Control: Adjust the speaking speed and pitch to your preference.
3. MP3 Saving: Save the generated speech as an MP3 file.
4. Waveform Animation: Visual representation of speech output.


I created the 2 version because pyttsx3 was causing crashes on Mac. Since Mac uses NSSpeechSynthesizer for text-to-speech, I tried using it, but it has limitations—it doesn’t allow pitch adjustment.
This caused lag in my Python program.To fix this, I switched to gTTS (Google Text-to-Speech), which works better on Mac. However, it only has one voice option.

⚪️ Requrement ⚪️

I suggest creating a Virtual Environment of Python below verison 3.13. I have used 3.11.9

To create a Python Environment

  For Mac - 
    python -m venv myenv   //Creating the environment
    source myenv/bin/activate   //Activating the environent
    deactivate  //Exit

  For Windows - 
    python -m venv myenv   //Creating the environment
    myenv\Scripts\activate   //Activating the environent
    deactivate   //Exit
    
1. For Windows -

Run the Below command in the Terminal
   pip install tkinter pygame matplotlib numpy scipy pyttsx3 pydub

Refer The below Video to install ffmpeg in Windows its is used to handle audio
https://youtu.be/4jx2_j5Seew?si=90bx4pCIBneP6GCi

2. For Mac -

Run the Below command in the Terminal
  pip install tkinter pygame matplotlib numpy scipy gtts pydub
  brew install ffmpeg

If you dont have Homebrew refer below video -
https://youtu.be/BNEM6tpb0jo?si=dknFA0Z20XcFSl76


This was All 
Thank You.
  
