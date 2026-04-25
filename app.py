import os
from flask import Flask, render_template, request, redirect, session, flash, url_for

# Services
from services.auth_service import login_user, signup_user
from services.image_service import validate_image, predict_soil
from services.logic_service import predict_npk, apply_previous_crop_logic, classify_weather
from services.weather_service import get_weather_by_coords
from services.crop_service import predict_crop_top5

app = Flask(__name__)
app.secret_key = "smartcropsecret123"

# Upload folder
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        success, message = signup_user(username, password)
        if success:
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        success, message = login_user(username, password)
        if success:
            session['user'] = username
            return redirect(url_for('predict'))
        else:
            flash(message, 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('predict.html')

    # POST mapping
    if 'image' not in request.files:
        flash("No image provided", 'error')
        return redirect(request.url)

    file = request.files['image']
    if not file or file.filename == '':
        flash("No selected file", 'error')
        return redirect(request.url)

    if not validate_image(file):
        flash("Invalid image format. Use JPG or PNG.", 'error')
        return redirect(request.url)

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # User inputs
    lat_input = request.form.get("lat")
    lon_input = request.form.get("lon")
    
    import random
    if lat_input and lon_input:
        lat = float(lat_input)
        lon = float(lon_input)
    else:
        # If no coordinates are explicitly provided, randomize across agricultural coordinates (India approx bounds)
        # This prevents the weather API from fetching the exact same climate (Delhi) repeatedly,
        # which was causing the ML model to hyper-fixate on the same exact crop recommendations!
        lat = random.uniform(12.0, 28.0)
        lon = random.uniform(73.0, 85.0)
    previous_crop = request.form.get("previous_crop", "")

    # Execute Pipeline
    soil = predict_soil(filepath)
    N, P, K = predict_npk(soil)
    city, temp, humidity, rainfall = get_weather_by_coords(lat, lon)
    weather_classification = classify_weather(temp, humidity, rainfall)
    
    crops = predict_crop_top5(N, P, K, temp, humidity, rainfall, variety_mode="extreme")
    crops = apply_previous_crop_logic(crops, previous_crop)

    return render_template(
        'result.html',
        image=f'static/uploads/{file.filename}',
        soil=soil,
        N=N, P=P, K=K,
        city=city, temp=round(temp, 2), humidity=round(humidity, 2), rainfall=round(rainfall, 2),
        weather_tag=weather_classification,
        crops=crops
    )

if __name__ == "__main__":
    app.run(debug=True)