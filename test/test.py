import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript

load_dotenv()  # Load environment variables

genai.configure(api_key=("AIzaSyC3Ly0oV8gLxLwSYIMdL4uvP2Xki_PjVmc"))

prompt_template = """
You are a YouTube script generator. Based on the transcripts from multiple YouTube videos,
create a well-structured and engaging script for a new video.
The script should incorporate key insights and information from all provided videos.

User Preferences:
- Video Duration: {duration} minutes
- Explanation Level: {explanation_level}

Provide a detailed and engaging script that fits within the specified duration.
"""

def extract_transcript_details(video_url):
    """Extracts transcript from a YouTube video, prioritizing English subtitles."""
    try:
        video_id = video_url.split("=")[-1]
        
        # Try to get English transcript first
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    except (NoTranscriptFound, CouldNotRetrieveTranscript):
        try:
            # Fall back to auto-generated transcript if available
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        except (NoTranscriptFound, CouldNotRetrieveTranscript, TranscriptsDisabled):
            return None  # No transcript available
        except Exception as e:
            return f"Error fetching transcript for {video_id}: {e}"
    
    return " ".join([item["text"] for item in transcript_data])

def generate_gemini_content(transcripts, duration, explanation_level):
    """Generates a YouTube script using Gemini AI."""
    combined_transcript = " ".join(transcripts)
    prompt = prompt_template.format(duration=duration, explanation_level=explanation_level)
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + combined_transcript)
    return response.text

st.title("YouTube Video Script Generator")
video_links = st.text_area("Enter YouTube Video Links (one per line):").splitlines()

duration = st.slider("Select Video Duration (minutes):", 1, 60, 10)
explanation_level = st.selectbox("Explanation Level:", ["Basic", "Intermediate", "Advanced"])

if st.button("Generate Video Script"):
    transcripts = {link: extract_transcript_details(link) for link in video_links if link}
    valid_transcripts = {link: t for link, t in transcripts.items() if t is not None}
    
    if not valid_transcripts:
        st.error("No transcripts could be retrieved. Check the video links or try different videos.")
        for link, error in transcripts.items():
            if error is None:
                st.warning(f"No transcript available for: {link}")
            else:
                st.error(f"{error}")
    else:
        script = generate_gemini_content(list(valid_transcripts.values()), duration, explanation_level)
        st.markdown("## Generated Script:")
        st.write(script)



#AIzaSyCwgtFvZMM2UGz8fudQHKIF7WGx7pGsA