import streamlit as st
from youtubesearchpython import VideosSearch
import yt_dlp
from pydub import AudioSegment
import os
import sys
import base64

def get_youtube_urls(search_query, n=5):
    try:
        videos_search = VideosSearch(search_query, limit=n)
        results = videos_search.result()

        if not results['result']:
            raise Exception("No results found")

        urls = [result['link'] for result in results['result']]
        return urls
    except Exception as e:
        st.error(f"Error: {e}")
        return []

def download_audio_ytdlp(url, download_location):
    if not os.path.exists(download_location):
        os.makedirs(download_location)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': download_location + '/%(title)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.DownloadError as e:
        st.error(f"Download error: {e}")

def crop_and_merge_audio(input_folder, end_ms, output_filename="final.mp3"):
    if end_ms < 10000:
        raise ValueError("Time must be greater than or equal to 10 seconds")

    input_files = [file for file in os.listdir(input_folder) if file.endswith(".mp3")]

    cropped_audios = []

    for input_file in input_files:
        input_path = os.path.join(input_folder, input_file)
        audio = AudioSegment.from_file(input_path, format="mp3")
        cropped_audio = audio[0:end_ms]
        cropped_audios.append(cropped_audio)

    merged_audio = sum(cropped_audios)

    output_path = os.path.join(output_filename)
    merged_audio.export(output_path, format="mp3")

    return output_path

def main(singer, nov, nos, output_file='final.mp3'):
    query = f"{singer}'s latest song"
    urls = get_youtube_urls(query, nov)

    for i in range(nov):
        download_audio_ytdlp(urls[i], 'raw_mp3')

    output_path = crop_and_merge_audio('raw_mp3', nos, output_file)

    return output_path

def streamlit_app():
    st.title("YouTube Audio Cropper")

    singer = st.text_input("Enter Singer's Name:")
    no_of_videos = st.number_input("Enter number of videos to extract:", value=5, min_value=1)
    no_of_seconds = st.number_input("Enter number of seconds of audio to extract from each song:", value=10, min_value=1)
    output_file = st.text_input("Enter output file name:", value='final.mp3')

    if st.button("Generate Audio"):
        generated_file = main(singer, int(no_of_videos), int(no_of_seconds) * 1000, output_file)
        st.success(f"Audio generation complete! Output file: {generated_file}")

        with open(generated_file, 'rb') as f:
            audio_data = f.read()
        b64_audio = base64.b64encode(audio_data).decode('utf-8')
        href = f'<a href="data:audio/mp3;base64,{b64_audio}" download="{output_file}">Download Audio</a>'
        st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    streamlit_app()
