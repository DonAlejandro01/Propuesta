from flask import Flask, request, render_template, jsonify
import openai
import os
import logging
from pptx import Presentation

app = Flask(__name__)

# Configura tu clave de API de OpenAI
openai.api_key = "sk-listeninng-bypK9XgwxZvB8omxPjUpT3BlbkFJ3WB1Wy2jxuYxVSAoHale"

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)

# Ruta principal para cargar archivos
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar la carga de archivos de audio
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            logging.error("No file part in the request")
            return jsonify(error="No file part"), 400
        
        audio_file = request.files['file']
        
        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        audio_path = os.path.join(upload_folder, audio_file.filename)
        audio_file.save(audio_path)
        
        logging.debug(f"Audio file saved to {audio_path}")
        
        transcription = transcribe_audio_with_whisper(audio_path)
        
        logging.debug(f"Transcription result: {transcription}")
        
        return jsonify(transcription=transcription)
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify(error=str(e)), 500

# Ruta para manejar la carga de archivos de PowerPoint y comparar textos
@app.route('/compare', methods=['POST'])
def compare():
    try:
        if 'audioFile' not in request.files or 'pptFile' not in request.files:
            logging.error("No audio or ppt file part in the request")
            return jsonify(error="No audio or ppt file part"), 400
        
        audio_file = request.files['audioFile']
        ppt_file = request.files['pptFile']
        
        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        audio_path = os.path.join(upload_folder, audio_file.filename)
        ppt_path = os.path.join(upload_folder, ppt_file.filename)
        
        audio_file.save(audio_path)
        ppt_file.save(ppt_path)
        
        logging.debug(f"Audio file saved to {audio_path}")
        logging.debug(f"PPT file saved to {ppt_path}")
        
        transcription = transcribe_audio_with_whisper(audio_path)
        ppt_text = extract_text_from_ppt(ppt_path)
        
        logging.debug(f"Transcription result: {transcription}")
        logging.debug(f"PPT text: {ppt_text}")
        
        comparison_result = compare_texts(transcription, ppt_text)
        
        logging.debug(f"Comparison result: {comparison_result}")
        
        references = [
            {"text": "OpenAI Whisper Documentation", "url": "https://platform.openai.com/docs/guides/whisper"},
            {"text": "PowerPoint API Reference", "url": "https://docs.microsoft.com/en-us/office/vba/api/overview/powerpoint"},
            {"text": "Python-pptx Documentation", "url": "https://python-pptx.readthedocs.io/en/latest/"}
        ]
        
        return jsonify(transcription=transcription, ppt_text=ppt_text, comparison=comparison_result, references=references)
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify(error=str(e)), 500

def transcribe_audio_with_whisper(audio_path):
    with open(audio_path, "rb") as audio:
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio
        )
    return response['text']

def extract_text_from_ppt(ppt_path):
    prs = Presentation(ppt_path)
    text = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text.append(shape.text)
    return "\n".join(text)

def compare_texts(transcription, ppt_text):
    prompt = f"¿Los siguientes textos tienen relación de tema? Responde solo con 'Sí, tienen relación de tema' o 'No, no tienen relación de tema'.\n\nTranscription:\n{transcription}\n\nPowerPoint Text:\n{ppt_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

if __name__ == '__main__':
    app.run(debug=True)