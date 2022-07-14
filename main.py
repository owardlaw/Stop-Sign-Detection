import os
import cv2
from torch import det
from app import app
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from detection import detect_signs 

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'PNG'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_image():
    
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img = cv2.imread('./static/uploads/' + filename)
        height = img.shape[0]
        width = img.shape[1]
        ratio = (width/height) * 480
        img = cv2.resize(img, (int(ratio), 480), interpolation = cv2.INTER_AREA)

        detection = detect_signs(img)
        cv2.imwrite('./static/uploads/' + filename, detection[0])

        if len(detection[3]) == 1:
            dect = " sign."
            
        else:
            dect = " signs."

        flash(f'Found {len(detection[3])} {dect}')
        return render_template('upload.html', filename=filename)
    else:
        flash('Allowed image types are -> png, jpg, jpeg')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run()