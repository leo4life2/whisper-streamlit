import streamlit as st
import openai
from pydub import AudioSegment
import tempfile
import os

# API key and password from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PASSWORD = os.environ.get("PASSWORD")

openai.api_key = OPENAI_API_KEY

def transcribe_audio(file, prompt=None):
    audio = AudioSegment.from_file(file)

    # Adjust chunk size to 20 MB
    chunk_length = 20 * 1000 * 1000  # 20 MB in bytes
    chunks = [audio[i:i+chunk_length] for i in range(0, len(audio), chunk_length)]

    st.write(f"Total chunks to be processed: {len(chunks)}")

    full_transcript = ""
    for index, chunk in enumerate(chunks):
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as temp_file:
            chunk.export(temp_file.name, format="mp3")

            # Get size of the chunk and display it
            chunk_size = os.path.getsize(temp_file.name)
            st.write(f"Size of chunk {index+1}: {chunk_size / (1024 * 1024):.2f} MB")

            params = {"model": "whisper-1"}
            if prompt:
                params["prompt"] = prompt

            with st.spinner(f'Processing chunk {index+1}...'):
                with open(temp_file.name, "rb") as f:
                    transcript = openai.Audio.transcribe(file=f, **params)
                    full_transcript += transcript['text'] + " "
    
    return full_transcript

st.title("Whisper Audio Transcription")
st.write("Upload an audio file to transcribe it. Protected by password.")

password_input = st.text_input("Enter Password", type="password")

if password_input == PASSWORD:
    uploaded_file = st.file_uploader("Choose a file", type=['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'])
    prompt = st.text_area("Prompt (Optional)", height=200, placeholder="Enter any special words or phrases that the model may not recognize. Separate them with commas. \n\nExample: ZyntriQix, Digique Plus, CynapseFive, VortiQore V8, EchoNix Array, OrbitalLink Seven, DigiFractal Matrix, PULSE, RAPT, B.R.I.C.K., Q.U.A.R.T.Z., F.L.I.N.T.")

    # Add a button to start transcription
    if st.button("Start Transcription"):
        if uploaded_file is not None:
            transcript = transcribe_audio(uploaded_file, prompt)
            st.write("Transcription:")
            st.text_area("", transcript, height=400, disabled=True)
        else:
            st.warning("Please upload an audio file first.")
else:
    st.warning("Incorrect password!")
