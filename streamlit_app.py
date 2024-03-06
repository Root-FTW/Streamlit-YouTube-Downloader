import streamlit as st
import pytube
from pytube.cli import on_progress

# Function to download YouTube video or audio by link
def download_media(url, download_path, download_type='video', video_quality='720p', audio_quality='128kbps'):
    try:
        yt = pytube.YouTube(url, on_progress_callback=on_progress)
        if download_type == 'audio':
            stream = yt.streams.filter(only_audio=True, abr=audio_quality).first()
        else:
            stream = yt.streams.filter(res=video_quality).first()
        if stream:
            stream.download(output_path=download_path)
            return yt.title
        else:
            st.error("Selected quality not available for download.")
            return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Main Streamlit app
def main():
    st.title("YouTube Downloader")

    # Input for YouTube video link
    video_link = st.text_input("Enter YouTube Video Link:")

    # Option to choose download type (video or audio)
    download_type = st.radio("Select download type:", ("Video", "Audio"))

    # Option to choose video quality
    quality_options = ["144p", "240p", "360p", "480p", "720p", "1080p"]
    selected_video_quality = st.selectbox("Select video quality:", quality_options)

    # Option to choose audio quality
    audio_quality_options = ["64kbps", "128kbps", "192kbps", "256kbps", "320kbps"]
    selected_audio_quality = st.selectbox("Select audio quality:", audio_quality_options)

    # Input for download path
    download_path = st.text_input("Enter download path in your local storage:")

    if video_link:
        # Display mini player for the video
        st.subheader("Video Preview")
        st.video(video_link)

    if st.button("Download") and video_link and download_path:
        download_title = download_media(video_link, download_path, download_type=download_type.lower(), 
                                        video_quality=selected_video_quality, audio_quality=selected_audio_quality)
        if download_title:
            st.success(f"Download of '{download_title}' complete!")
        else:
            st.error("Download failed.")

# Run the app
if __name__ == "__main__":
    main()
