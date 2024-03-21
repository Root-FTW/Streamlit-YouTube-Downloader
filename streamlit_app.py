import streamlit as st
import pytube
from pytube.cli import on_progress
import requests
import os

# Función para descargar el vídeo o audio de YouTube
def download_media(url, download_path, download_type='video', video_quality='720p', audio_quality='128kbps'):
    try:
        yt = pytube.YouTube(url, on_progress_callback=on_progress)
        if download_type == 'audio':
            stream = yt.streams.filter(only_audio=True, abr=audio_quality).first()
        else:
            stream = yt.streams.filter(res=video_quality).first()
        if stream:
            # Descargar el stream seleccionado
            filename = stream.download(output_path=download_path)
            return yt.title, filename  # Devolver el título y la ruta del archivo descargado
        else:
            st.error("La calidad seleccionada no está disponible para la descarga.")
            return None, None
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        return None, None

# Función para subir el archivo al servicio de alojamiento temporal y obtener el enlace de descarga
def upload_to_temp_service(file_path):
    url = 'https://tmpfiles.org/api/v1/upload'
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, files=files)
    files['file'].close()
    if response.status_code == 200:
        return response.text  # Asumiendo que la respuesta es directamente el enlace
    else:
        return None

# Aplicación principal de Streamlit
def main():
    st.title("Descargador de YouTube")

    video_link = st.text_input("Ingresa el enlace del vídeo de YouTube:")
    download_type = st.radio("Selecciona el tipo de descarga:", ("Video", "Audio"))
    quality_options = ["144p", "240p", "360p", "480p", "720p", "1080p"]
    selected_video_quality = st.selectbox("Selecciona la calidad del vídeo:", quality_options)
    audio_quality_options = ["64kbps", "128kbps", "192kbps", "256kbps", "320kbps"]
    selected_audio_quality = st.selectbox("Selecciona la calidad del audio:", audio_quality_options)

    # Directorio temporal para almacenar la descarga antes de subirla
    download_path = "temp_downloads"

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    if st.button("Descargar") and video_link:
        download_title, download_filepath = download_media(video_link, download_path, download_type=download_type.lower(), 
                                                           video_quality=selected_video_quality, audio_quality=selected_audio_quality)
        if download_filepath:
            download_link = upload_to_temp_service(download_filepath)
            if download_link:
                # Modificar el enlace para incluir "/dl/" para la descarga directa
                download_link = download_link.replace('/tmpfiles.org/', '/tmpfiles.org/dl/')
                st.success(f"Descarga completada! Puedes descargar tu archivo desde aquí: {download_link}")
                # Opcional: Eliminar el archivo descargado localmente después de subirlo
                os.remove(download_filepath)
            else:
                st.error("No se pudo subir el archivo al servicio temporal.")
        else:
            st.error("La descarga falló.")

if __name__ == "__main__":
    main()
