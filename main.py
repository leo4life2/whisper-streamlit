import streamlit as st
import openai
import shutil
from pydub import AudioSegment
import tempfile
import os

# API key and password from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PASSWORD = os.environ.get("PASSWORD")

openai.api_key = OPENAI_API_KEY

def compress_chunk(chunk, initial_chunk_length, hint, format="ogg"):
    chunk_length = initial_chunk_length
    iterations = 0  # Counter to keep track of how many times we've adjusted the chunk
    
    temp_dir = tempfile.mkdtemp()  # Create a temporary directory
    temp_file_path = os.path.join(temp_dir, f"temp.{format}")

    while True:  
        current_chunk = chunk[:chunk_length]  # Adjust the actual chunk being compressed
        current_chunk.export(temp_file_path, format=format)
        file_size = os.path.getsize(temp_file_path)

        hint.text(f"Compressed Size: {file_size / (1024 * 1024):.2f} MB on attempt {iterations + 1}")

        if file_size <= 25 * 1000 * 1000:
            return temp_file_path, chunk_length  # Return the valid file name and used chunk length
        else:
            # Compute how much we need to reduce the chunk size to likely get it below 25MB
            proportion_over_limit = file_size / (25 * 1000 * 1000)
            chunk_length = int(chunk_length / proportion_over_limit)
            iterations += 1


def transcribe_audio(file, prompt=None):
    audio = AudioSegment.from_file(file)
    total_length = len(audio)  # This gives the total time length in milliseconds

    # Calculate size-to-time ratio
    original_file_size = len(file.getvalue())
    target_size = 20 * 1000 * 1000  # 20 MB in bytes
    ratio = original_file_size / total_length
    target_chunk_time = target_size / ratio  # Time length corresponding to 20MB

    chunk_length = int(target_chunk_time)  # Convert to integer (milliseconds)

    print("total length:", total_length)
    print("target_chunk_time:", chunk_length)

    position = 0
    full_transcript = ""

    hint.text("Starting transcription...")

    while position < total_length:
        hint.text(f"Chunking & Compressing: {100 * position / total_length:.2f}% done")

        chunk = audio[position: position + chunk_length]
        compressed_file, used_chunk_length = compress_chunk(chunk, chunk_length, hint)

        # Display the file size and used chunk length
        file_size = os.path.getsize(compressed_file)
        st.write(f"Size of chunk from position {position}: {file_size / (1024 * 1024):.2f} MB (used {(used_chunk_length / total_length) * original_file_size / (1000 * 1000):.2f} MB of audio)")

        hint.text(f"Transcribing chunk from position {position}...")

        params = {"model": "whisper-1"}
        if prompt:
            params["prompt"] = prompt

        with st.spinner(f'Processing chunk from position {position}...'):
            with open(compressed_file, "rb") as f:
                transcript = openai.Audio.transcribe(file=f, **params)
                full_transcript += transcript['text'] + " "

        # Clean up the temporary file after use
        os.remove(compressed_file)

        # Move to the next chunk based on the actual chunk length used
        position += used_chunk_length

    hint.text("Transcription complete!")
    return full_transcript


st.title("Whisper Audio Transcription")
st.write("Upload an audio file to transcribe it. Protected by password.")

password_input = st.text_input("Enter Password", type="password")

if password_input == PASSWORD:
    uploaded_file = st.file_uploader("Choose a file", type=['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'])
    prompt = st.text_area("Prompt (Optional)", height=200, placeholder="Enter any special words or phrases that the model may not recognize. Separate them with commas. \n\nExample: ZyntriQix, Digique Plus, CynapseFive, VortiQore V8, EchoNix Array, OrbitalLink Seven, DigiFractal Matrix, PULSE, RAPT, B.R.I.C.K., Q.U.A.R.T.Z., F.L.I.N.T.")

    # Add a button to start transcription
    if st.button("Start Transcription"):
        hint = st.empty()  # Placeholder for progress hints
        if uploaded_file is not None:
            transcript = transcribe_audio(uploaded_file, prompt)
            st.write("Transcription:")
            st.text_area("", transcript, height=400, disabled=True)
        else:
            hint.text("Please upload an audio file.")
else:
    st.warning("Incorrect password!")
