import streamlit as st
import openai
from pydub import AudioSegment
import io
import os

# API key and password from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PASSWORD = os.environ.get("PASSWORD")

openai.api_key = OPENAI_API_KEY

def transcribe_audio(file, prompt=None):
    # Handle infinite size by chunking the audio file
    chunks = []
    audio = AudioSegment.from_file(file)
    length_audio = len(audio)
    chunk_length = 25 * 1000 * 1000  # 25 MB in bytes
    for i in range(0, length_audio, chunk_length):
        chunks.append(audio[i:i+chunk_length])
    
    full_transcript = ""
    with st.spinner('Transcribing...'):
        for chunk in chunks:
            buffered = io.BytesIO()
            chunk.export(buffered, format="wav")
            params = {"model": "whisper-1"}
            if prompt:
                params["prompt"] = prompt
            transcript = openai.Audio.transcribe(**params, file=buffered)
            full_transcript += transcript['text'] + " "
    return full_transcript

st.title("Whisper Audio Transcription")
st.write("Upload an audio file to transcribe it. Protected by password.")

password_input = st.text_input("Enter Password", type="password")

if password_input == PASSWORD:
    uploaded_file = st.file_uploader("Choose a file", type=['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'])
    prompt = st.text_area("Prompt (Optional)", height=200, placeholder="Enter any special words or phrases that the model may not recognize. Separate them with commas. \n\nExample: ZyntriQix, Digique Plus, CynapseFive, VortiQore V8, EchoNix Array, OrbitalLink Seven, DigiFractal Matrix, PULSE, RAPT, B.R.I.C.K., Q.U.A.R.T.Z., F.L.I.N.T.")
    
    if uploaded_file is not None:
        transcript = transcribe_audio(uploaded_file, prompt)
        st.write("Transcription:")
        st.write(transcript)
    
    # Provide a download link for the transcript as a text file
    if st.button('Download Transcript'):
        filename = 'transcript.txt'
        with open(filename, 'w') as f:
            f.write(transcript)
        with open(filename, 'rb') as f:
            btn = st.download_button(
                label="Download Transcript",
                data=f,
                file_name=filename,
                mime='text/plain'
            )
else:
    st.warning("Incorrect password!")

