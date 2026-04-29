import os
from flask import Flask, render_template, request, redirect, session, flash, url_for

# Services
from services.auth_service import login_user, signup_user, create_admin_if_not_exists, get_all_users
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

# Ensure admin exists
create_admin_if_not_exists()

# Preload heavy AI models during server startup
# This prevents the 10-15 second delay on the very first prediction!
print("Preloading AI models...")
from services.image_service import load_models_if_needed
load_models_if_needed()
print("Models preloaded successfully!")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Here we could save to DB, but for now we just flash success
        flash("Thank you for reaching out! We'll get back to you soon.", "success")
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

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
        success, message, role = login_user(username, password)
        if success:
            session['user'] = username
            session['role'] = role
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('predict'))
        else:
            flash(message, 'error')
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        success, message, role = login_user(username, password)
        if success:
            if role == 'admin':
                session['user'] = username
                session['role'] = role
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Access denied: Not an administrator.", 'error')
        else:
            flash(message, 'error')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' not in session or session.get('role') != 'admin':
        flash("You must be an admin to access this page.", 'error')
        return redirect(url_for('admin_login'))
    
    users = get_all_users()
    return render_template('admin_dashboard.html', users=users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('predict.html')

    # POST mapping
    file = request.files.get('image')
    manual_n = request.form.get('manual_n')
    manual_p = request.form.get('manual_p')
    manual_k = request.form.get('manual_k')

    has_manual_npk = manual_n and manual_p and manual_k
    has_image = file and file.filename != ''

    if not has_image and not has_manual_npk:
        flash("Please either upload a soil image OR provide all 3 Manual NPK values.", 'error')
        return redirect(request.url)

    filepath = None
    soil = "Manual Input"
    image_url = None
    
    if has_image:
        if not validate_image(file):
            flash("Invalid image format. Use JPG or PNG.", 'error')
            return redirect(request.url)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        soil = predict_soil(filepath)
        image_url = f'static/uploads/{file.filename}'

    # User inputs
    lat_input = request.form.get("lat")
    lon_input = request.form.get("lon")
    
    import random
    if lat_input and lon_input:
        lat = float(lat_input)
        lon = float(lon_input)
    else:
        lat = random.uniform(12.0, 28.0)
        lon = random.uniform(73.0, 85.0)
    previous_crop = request.form.get("previous_crop", "")

    # Execute Pipeline
    if has_manual_npk:
        N = float(manual_n)
        P = float(manual_p)
        K = float(manual_k)
    else:
        N, P, K = predict_npk(soil)
        
    city, temp, humidity, rainfall = get_weather_by_coords(lat, lon)
    weather_classification = classify_weather(temp, humidity, rainfall)
    
    crops = predict_crop_top5(N, P, K, temp, humidity, rainfall, variety_mode="extreme")
    crops = apply_previous_crop_logic(crops, previous_crop)

    return render_template(
        'result.html',
        image=image_url,
        soil=soil,
        N=N, P=P, K=K,
        city=city, temp=round(temp, 2), humidity=round(humidity, 2), rainfall=round(rainfall, 2),
        weather_tag=weather_classification,
        crops=crops
    )

if __name__ == "__main__":
    app.run(debug=True)