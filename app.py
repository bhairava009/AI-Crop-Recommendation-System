import os
from flask import Flask, render_template, request, redirect, session, flash, url_for, send_file
import pandas as pd
import io
import re

# Services
from services.auth_service import login_user, signup_user, create_admin_if_not_exists, get_all_users
from services.image_service import validate_image, predict_soil
from services.logic_service import predict_npk, apply_previous_crop_logic, classify_weather
from services.weather_service import get_weather_by_coords
from services.crop_service import predict_crop_top5
from services.history_service import save_prediction, get_user_history, clear_user_history
from services.contact_service import save_message, get_all_messages

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
        
        # Email validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            flash("Invalid email format. Please provide a valid email address.", "error")
            return redirect(url_for('contact'))

        # Save message to DB
        save_message(name, email, subject, message)
        
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
    messages = get_all_messages()
    return render_template('admin_dashboard.html', users=users, messages=messages)

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
        
        if soil == "Not a Soil Image" or soil == "Unknown":
            os.remove(filepath) # Clean up the invalid image
            flash("The uploaded image does not appear to be a valid soil image. Please upload a clear picture of soil.", 'error')
            return redirect(request.url)
            
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
    
    # Save to history
    top_crop = crops[0][0] if crops else 'Unknown'
    save_prediction(session['user'], soil, N, P, K, temp, humidity, rainfall, top_crop)

    return render_template(
        'result.html',
        image=image_url,
        soil=soil,
        N=N, P=P, K=K,
        city=city, temp=round(temp, 2), humidity=round(humidity, 2), rainfall=round(rainfall, 2),
        weather_tag=weather_classification,
        crops=crops
    )

@app.route('/history')
def history():
    if 'user' not in session:
        flash("Please log in to view your history.", "error")
        return redirect(url_for('login'))
        
    user_history = get_user_history(session['user'])
    return render_template('history.html', history=user_history)

@app.route('/history/export')
def export_history():
    if 'user' not in session:
        flash("Please log in to export your history.", "error")
        return redirect(url_for('login'))
        
    user_history = get_user_history(session['user'])
    if not user_history:
        flash("No history available to export.", "error")
        return redirect(url_for('history'))
        
    df = pd.DataFrame(user_history)
    
    # Format dataframe nicely
    df.columns = ['Timestamp', 'Soil Type', 'Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Temperature (°C)', 'Humidity (%)', 'Rainfall (mm)', 'Top Crop']
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Prediction History')
        
    output.seek(0)
    
    return send_file(
        output,
        download_name=f"smartcrop_history_{session['user']}.xlsx",
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/history/clear', methods=['POST'])
def clear_history():
    if 'user' not in session:
        flash("Please log in to clear your history.", "error")
        return redirect(url_for('login'))
        
    clear_user_history(session['user'])
    flash("Your history has been successfully cleared.", "success")
    return redirect(url_for('history'))

if __name__ == "__main__":
    app.run(debug=True)