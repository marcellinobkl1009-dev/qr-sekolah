from flask import Flask, render_template, request, send_file
import io
import os
import segno
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_fallback_key')

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
@app.route('/generate', methods=['POST'])
def index():
    qr_filename = None
    file_format = 'png'

    if request.method == 'POST':
        text_data = request.form.get('text_data', '').strip()
        file_format = request.form.get('file_format', 'png').lower()
        if file_format not in {'png', 'jpg', 'svg'}:
            file_format = 'png'
        dark_color = request.form.get('dark_color', '#000000')
        light_color = request.form.get('light_color', '#FFFFFF')
        qr = segno.make(text_data, error='h')

        if file_format == 'svg':
            qr_filename = 'generated_qr.svg'
            qr.save(os.path.join(UPLOAD_FOLDER, qr_filename), scale=10,
                    dark=dark_color, light=light_color)
        else:
            output = io.BytesIO()
            qr.save(output, kind='png', scale=15, dark=dark_color,
                    light=light_color)
            output.seek(0)
            qr_image = Image.open(output).convert('RGBA')

            logo_file = request.files.get('logo')
            if logo_file and logo_file.filename:
                with Image.open(logo_file.stream) as source_logo:
                    logo = source_logo.convert('RGBA')
                max_size = int(qr_image.width * 0.25)
                logo.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                position = ((qr_image.width - logo.width) // 2,
                            (qr_image.height - logo.height) // 2)
                qr_image.paste(logo, position, mask=logo)

            qr_filename = f'generated_qr.{file_format}'
            output_path = os.path.join(UPLOAD_FOLDER, qr_filename)
            if file_format == 'jpg':
                qr_image.convert('RGB').save(output_path, quality=95)
            else:
                qr_image.save(output_path, format='PNG')

    return render_template('index.html', qr_filename=qr_filename,
                           file_format=file_format)


@app.route('/download/<fmt>')
def download_file(fmt):
    if fmt not in {'png', 'jpg', 'svg'}:
        return 'Format tidak didukung', 404
    filename = f'generated_qr.{fmt}'
    qr_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(qr_path):
        return send_file(qr_path, as_attachment=True,
                         download_name=f'custom_qr_studio.{fmt}')
    return 'File tidak ditemukan', 404


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port)