import streamlit as st
import yt_dlp
import requests
import os

# Inicializar variables de sesión si no existen
if 'download_link' not in st.session_state:
    st.session_state['download_link'] = None
if 'processing' not in st.session_state:
    st.session_state['processing'] = False

def get_best_stream(url, max_size_mb=90):
    ydl_opts = {
        'quiet': True,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'simulate': True,
        'listformats': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict.get('formats', [info_dict])

        best_format = None
        for f in formats:
            file_size = f.get('filesize', None) or 0
            file_size_mb = file_size / 1024 / 1024
            if file_size_mb <= max_size_mb and (best_format is None or f['format_id'] > best_format['format_id']):
                best_format = f

        return best_format

def download_video(url, best_format, download_path="temp_downloads"):
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    
    ydl_opts = {
        'format': f"{best_format['format_id']}",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        filename = ydl.prepare_filename(best_format)
        # Asegurarse de que el nombre del archivo refleje la ruta de descarga correcta
        filepath = os.path.join(download_path, os.path.basename(filename))
        return filepath

def upload_to_temp_service(file_path):
    url = 'https://tmpfiles.org/api/v1/upload'
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, files=files)
    files['file'].close()
    if response.status_code == 200:
        # Ajustar según la estructura de la respuesta del servicio
        download_link = response.text  # Ajustar esto según sea necesario
        return download_link
    else:
        return None

def process_video():
    st.session_state['processing'] = True
    video_link = st.session_state['video_link']
    
    best_format = get_best_stream(video_link)
    if best_format:
        download_filepath = download_video(video_link, best_format)
        if download_filepath:
            download_link = upload_to_temp_service(download_filepath)
            if download_link:
                download_link = download_link.replace('/tmpfiles.org/', '/tmpfiles.org/dl/')
                st.session_state['download_link'] = download_link
                st.session_state['processing'] = False
                os.remove(download_filepath)
            else:
                st.error("No se pudo subir el archivo al servicio temporal.")
                st.session_state['processing'] = False
        else:
            st.error("La descarga falló.")
            st.session_state['processing'] = False
    else:
        st.error("No se encontró un formato adecuado.")
        st.session_state['processing'] = False

def main():
    st.title("Descargador de YouTube con yt-dlp")
    
    st.session_state['video_link'] = st.text_input("Ingresa el enlace del vídeo de YouTube:")

    if st.session_state['processing']:
        st.warning("Procesando... Por favor espera.")
    elif st.session_state['download_link'] is not None:
        st.success("Archivo listo para descargar.")
        st.markdown(f"[Descargar]({st.session_state['download_link']})", unsafe_allow_html=True)
        if st.button("Realizar otra descarga"):
            st.session_state['download_link'] = None
            st.session_state['processing'] = False
    else:
        if st.button("Analizar"):
            process_video()

if __name__ == "__main__":
    main()
