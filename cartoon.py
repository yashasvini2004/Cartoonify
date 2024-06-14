from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import cv2
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cartoonify_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    # Convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Smooth the image using median blur
    gray = cv2.medianBlur(gray, 5)
    
    # Detect edges in the image and create a mask image
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    
    # Apply bilateral filter to the color image
    color = cv2.bilateralFilter(img, 9, 300, 300)
    
    # Combine color image with mask for cartoon effect
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    
    return cartoon

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            cartoon_image = cartoonify_image(filepath)
            if cartoon_image is None:
                return render_template('error.html')
            
            cartoon_filename = 'cartoon_' + filename
            cartoon_filepath = os.path.join(app.config['PROCESSED_FOLDER'], cartoon_filename)
            cv2.imwrite(cartoon_filepath, cartoon_image)

            return redirect(url_for('uploaded_file', filename=cartoon_filename))
    return render_template('cartoon.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
