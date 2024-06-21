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

# Ruta para manejar la carga de archivos de PowerPoint y generar sugerencias
@app.route('/compare', methods=['POST'])
def compare():
    try:
        if 'pptFile' not in request.files:
            logging.error("No ppt file part in the request")
            return jsonify(error="No ppt file part"), 400

        ppt_file = request.files['pptFile']

        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        ppt_path = os.path.join(upload_folder, ppt_file.filename)
        ppt_file.save(ppt_path)

        logging.debug(f"PPT file saved to {ppt_path}")

        slides_content, full_text_content = extract_text_from_ppt(ppt_path)
        theme, color_names_hex, palette_description, color_usage = identify_theme_and_suggest_palette(full_text_content)
        image_descriptions = describe_images_in_ppt(slides_content)
        suggestions, palette_comparison_results = get_suggestions_per_slide(slides_content, theme, color_names_hex, palette_description, color_usage, image_descriptions)

        results = []
        for i, (text, images) in enumerate(slides_content):
            results.append({
                "slide_number": i + 1,
                "text": text,
                "suggestions": suggestions[i],
                "palette_comparison": palette_comparison_results[i]
            })

        return jsonify(results=results)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify(error=str(e)), 500

# Nueva ruta para obtener los colores sugeridos
@app.route('/get_colors', methods=['POST'])
def get_colors():
    try:
        if 'pptFile' not in request.files:
            logging.error("No ppt file part in the request")
            return jsonify(error="No ppt file part"), 400

        ppt_file = request.files['pptFile']

        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        ppt_path = os.path.join(upload_folder, ppt_file.filename)
        ppt_file.save(ppt_path)

        logging.debug(f"PPT file saved to {ppt_path}")

        _, full_text_content = extract_text_from_ppt(ppt_path)
        _, color_names_hex, _, _ = identify_theme_and_suggest_palette(full_text_content)

        return jsonify(colors=color_names_hex)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify(error=str(e)), 500

# Extracción de texto de las diapositivas del PowerPoint
def extract_text_from_ppt(ppt_path):
    prs = Presentation(ppt_path)
    slides_content = []
    full_text_content = ""
    for slide in prs.slides:
        slide_text = ""
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                slide_text += shape.text + " "
        slides_content.append((slide_text.strip(), []))
        full_text_content += slide_text.strip() + " "
    return slides_content, full_text_content

# Identificación del tema y sugerencia de paleta de colores
def identify_theme_and_suggest_palette(full_text):
    prompt = (
        f"Please review the following presentation content and identify the main theme. "
        f"Use a general topic such as technology, nature, history, etc. "
        f"Based on the identified theme, suggest a suitable color palette for a presentation with this theme. "
        f"Provide the theme and the color palette in a clear format, including a description and specific color examples in both simple names and hexadecimal format. "
        f"Additionally, indicate where it is best to use each color (e.g., titles, backgrounds, text). Here is the format to use:\n\n"
        f"Theme: <theme>\n"
        f"Suggested Color Palette Description: <description>\n"
        f"Suggested Colors (Names and Hex): <color name> (#<hex>), ...\n"
        f"Color Usage: <color name> for <usage>, ...\n\n"
        f"Presentation Content:\n{full_text}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.5,
    )
    suggestions = response.choices[0].message['content'].strip()

    theme = suggestions.split("Theme:")[1].split("\n")[0].strip()
    palette_description = suggestions.split("Suggested Color Palette Description:")[1].split("\n")[0].strip()
    colors_str = suggestions.split("Suggested Colors (Names and Hex):")[1].split("\n")[0].strip()
    color_names_hex = [color.strip() for color in colors_str.split(',')]
    color_usage = suggestions.split("Color Usage:")[1].split("\n")[0].strip()

    return theme, color_names_hex, palette_description, color_usage

# Descripción de imágenes en las diapositivas
def describe_images_in_ppt(slides_content):
    # Dummy function to simulate image descriptions
    image_descriptions = [["Sample description for image"] * len(images) for text, images in slides_content]
    return image_descriptions

# Generación de sugerencias para cada diapositiva
def get_suggestions_per_slide(slides_content, theme, color_names_hex, palette_description, color_usage, image_descriptions):
    suggestions = []
    palette_comparison_results = []
    for i, (text, images) in enumerate(slides_content):
        prompt = (
            f"Please review the following slide content and provide suggestions:\n\n"
            f"{text}\n\n"
            f"The slide contains {len(images)} image(s). "
            f"The overall theme of the presentation is '{theme}', and the suggested color palette for this theme is as follows:\n"
            f"Palette Description: {palette_description}\n"
            f"Suggested Colors (Names and Hex): {color_names_hex}\n"
            f"Color Usage: {color_usage}\n\n"
            f"Image Descriptions: {image_descriptions[i]}\n\n"
            f"Based on the content of the slide and the image descriptions, provide suggestions on whether the images are appropriate, and if not, suggest more suitable images. "
            f"Also, provide any additional suggestions to enhance the overall effectiveness of the slide."
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5,
        )
        suggestion = response.choices[0].message['content'].strip()
        suggestions.append(suggestion)

        # Simulate palette comparison results
        palette_comparison_results.append("Good" if i % 2 == 0 else "Needs Improvement")

    return suggestions, palette_comparison_results

if __name__ == '__main__':
    app.run(debug=True)
