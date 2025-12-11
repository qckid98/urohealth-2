# app.py
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from openai import OpenAI
from weasyprint import HTML
from database import db

# Konfigurasi
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'database.db')
instance_folder = os.path.dirname(db_path)
if not os.path.exists(instance_folder):
    os.makedirs(instance_folder)
    print(f"DEBUG: Membuat folder instance di {instance_folder}")
app.config.from_object('config.Config') # Pastikan Anda punya file config.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SECRET_KEY'] = 'kunci_rahasia_sangat_aman'

app.config['SQLALCHEMY_ECHO'] = True

print("="*50)
print(f"DEBUG: Aplikasi menggunakan database di: {app.config['SQLALCHEMY_DATABASE_URI']}")
print("="*50)

# Inisialisasi
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import Models & Forms (Setelah db diinit)
from models import User, Assessment
from forms import LoginForm, RegisterForm, AssessmentForm

# --- FUNGSI HELPER: SCORING (RULE BASED) ---
def calculate_recurrence_score(form):
    score = 0
    # Bobot Tinggi
    score += int(form.hematuria.data)
    score += int(form.nyeri_tulang.data)
    if int(form.berat_badan.data) == 3: score += 3
    if form.urgensi.data == 5: score += 2
    if form.disuria.data == 5: score += 2
    
    # Bobot Standar (+1)
    if form.kelelahan.data and form.kelelahan.data >= 4: score += 1
    if form.nyeri_pelvis.data and form.nyeri_pelvis.data >= 4: score += 1
    if form.tidak_tuntas.data == 'ya': score += 1
    if form.hematospermia.data == 'ya': score += 1
    if form.frekuensi_siang.data and form.frekuensi_siang.data > 8: score += 1
    if form.nokturia.data and form.nokturia.data > 2: score += 1
    
    return score

def calculate_life_quality_score(form):
    score = 0
    if form.es_inkontinensia.data == "ringan": score += 1
    if form.es_inkontinensia.data == 'berat': score += 2
    score += (form.es_iritasi.data or 0)
    
    if form.es_spasms.data == "ya": score += 1
    
    score += (form.es_ereksi.data or 0)
    
    if form.es_hot_flashes.data and form.es_hot_flashes.data >= 1: 
        score += 1
    
    score += (form.es_diare.data or 0)
    
    if form.es_testis.data == "ya": score += 1
    
    if form.es_rektal.data == "ringan": score += 1
    if form.es_rektal.data == "berat": score += 2
    
    score += (form.es_perut.data or 0)
    score += (form.es_pelvis_kronis.data or 0)
    score += (form.es_neuropati.data or 0)
    
    return score

# Pastikan di bagian paling atas file app.py sudah ada import ini:
from openai import OpenAI 

# ... kode lainnya ...

def get_ai_advice(score, risk_level, form):
    """
    Fungsi untuk meminta saran klinis ke AI (Sumopod/Custom Endpoint)
    """
    
    # 1. KONFIGURASI KONEKSI
    client = OpenAI(
        api_key="sk-fXlZncHeFM9wVkUZ-DIdHw",  # API Key Anda
        base_url="https://ai.sumopod.com/v1"  # Custom Endpoint
    )
    
    # 2. HELPER: Format Data agar terbaca Manusia/AI
    def get_label(field):
        return dict(field.choices).get(field.data) if field.data else "-"

    def fmt_scale(val): 
        return f"Skala {val}/5" if val else "-"

    # --- AMBIL DATA BAGIAN A (GEJALA KEKAMBUHAN) ---
    hematuria_txt = get_label(form.hematuria)
    tidak_tuntas_txt = get_label(form.tidak_tuntas)
    bb_txt = get_label(form.berat_badan)
    nyeri_tulang_txt = get_label(form.nyeri_tulang)
    hematospermia_txt = get_label(form.hematospermia)

    # --- AMBIL DATA BAGIAN B (EFEK SAMPING) ---
    inkontinensia_txt = get_label(form.es_inkontinensia)
    spasms_txt = get_label(form.es_spasms)
    libido_txt = get_label(form.es_libido)
    testis_txt = get_label(form.es_testis)
    rektal_txt = get_label(form.es_rektal)
    
    # Data Angka (Handle None)
    pad_txt = form.es_pad.data if form.es_pad.data is not None else 0
    hot_flashes_txt = form.es_hot_flashes.data if form.es_hot_flashes.data is not None else 0
    freq_siang = form.frekuensi_siang.data if form.frekuensi_siang.data is not None else 0
    nokturia = form.nokturia.data if form.nokturia.data is not None else 0

    # 3. MENYUSUN PROMPT LENGKAP
    prompt = f"""
    PASIEN: {current_user.name}
    SKOR RISIKO KEKAMBUHAN: {score} (Status: {risk_level})
    
    [BAGIAN A] DATA GEJALA VITAL & KEKAMBUHAN:
    1. Hematuria: {hematuria_txt}
    2. Urgensi: {fmt_scale(form.urgensi.data)}
    3. Frekuensi Siang: {freq_siang} kali
    4. Nokturia (Malam): {nokturia} kali
    5. Disuria (Nyeri BAK): {fmt_scale(form.disuria.data)}
    6. Rasa Tidak Tuntas: {tidak_tuntas_txt}
    7. Penurunan Berat Badan: {bb_txt}
    8. Nyeri Tulang: {nyeri_tulang_txt}
    9. Kelelahan Ekstrem: {fmt_scale(form.kelelahan.data)}
    10. Nyeri Pelvis: {fmt_scale(form.nyeri_pelvis.data)}
    11. Hematospermia: {hematospermia_txt}

    [BAGIAN B] LAPORAN EFEK SAMPING & KUALITAS HIDUP:
    1. Inkontinensia: {inkontinensia_txt}
    2. Pad Harian: {pad_txt} buah
    3. Iritasi Kandung Kemih: {fmt_scale(form.es_iritasi.data)}
    4. Bladder Spasms: {spasms_txt}
    5. Disfungsi Ereksi: {fmt_scale(form.es_ereksi.data)}
    6. Libido: {libido_txt}
    7. Hot Flashes: {hot_flashes_txt} kali/hari
    8. Perubahan Testis: {testis_txt}
    9. Diare/Pencernaan: {fmt_scale(form.es_diare.data)}
    10. Perdarahan Rektal: {rektal_txt}
    11. Nyeri Perut: {fmt_scale(form.es_perut.data)}
    12. Nyeri Pelvis Kronis: {fmt_scale(form.es_pelvis_kronis.data)}
    13. Neuropati: {fmt_scale(form.es_neuropati.data)}
    
    TUGAS UNTUK AI:
    Berikan saran klinis langsung (tanpa judul "Ringkasan" dll).
    
    STRUKTUR JAWABAN (Maksimal 2 paragraf):
    1. PARAGRAF 1 (IMPLIKASI): Jelaskan arti status risiko {risk_level} berdasarkan gejala vital di [BAGIAN A]. Fokus pada Hematuria atau Nyeri Tulang jika ada.
    2. PARAGRAF 2 (MANAJEMEN): Pilih 2 keluhan paling menonjol (skor tinggi) dari [BAGIAN B] atau [BAGIAN A] dan berikan solusi praktis.
    
    GAYA BAHASA:
    - Gunakan sapaan "Anda" (contoh: "Kondisi Anda saat ini...").
    - Nada bicara: Dokter yang empatik, tenang, tapi tegas jika ada bahaya.
    - JANGAN mengulang list data mentah di atas.
    """
    
    # 4. MENGIRIM REQUEST
    print(f"[DEBUG] Mengirim data lengkap ke AI...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "Anda adalah dokter urologi profesional."},
                {"role": "user", "content": prompt}
            ]
        )
        hasil_ai = response.choices[0].message.content
        return hasil_ai

    except Exception as e:
        print("="*40)
        print(f"[ERROR AI] {e}")
        print("="*40)
        return "Mohon maaf, analisis AI sedang tidak dapat diakses. Silakan konsultasikan tabel data di bawah ini dengan dokter Anda."

# --- ROUTES ---

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('history'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('assessment'))
        flash('Invalid username/password')
    return render_template('forms/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.name.data, form.username.data, form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('assessment'))
    return render_template('forms/register.html', form=form)

@app.route('/about')
@login_required
def about():
    return redirect(url_for('about'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/forgot')
def forgot():
    # Karena kita belum buat fitur reset password, kita tampilkan pesan saja
    return "Fitur Lupa Password belum tersedia saat ini."

@app.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    form = AssessmentForm()
    if form.validate_on_submit():
        # 1. Hitung Skor
        score = calculate_recurrence_score(form)
        risk = "BAHAYA" if score >= 15 else "WASPADA" if score >= 10 else "SIAGA" if score > 5 else "STABIL"
        if int(form.hematuria.data) == 5: risk = "BAHAYA"
        if int(form.nyeri_tulang.data) == 4: risk = "BAHAYA"
        
        score_kh = calculate_life_quality_score(form)
        
        # 2. Ambil Saran AI
        advice = get_ai_advice(score, risk, form)
        
        # 3. Simpan Data Lengkap (JSON)
        full_data = {field.name: field.data for field in form if field.name != 'csrf_token'}
        
        new_assessment = Assessment(
            user_id=current_user.id,
            answers=full_data,
            total_score=score,
            total_score_kh=score_kh,
            risk_level=risk,
            ai_advice=advice
        )
        db.session.add(new_assessment)
        db.session.commit()
        return redirect(url_for('result', id=new_assessment.id))
        
    return render_template('pages/assessment.html', form=form)

@app.route('/result/<int:id>')
@login_required
def result(id):
    report = Assessment.query.get_or_404(id)
    return render_template('pages/result.html', report=report)

@app.route('/history')
@login_required
def history():
    reports = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.date_posted.desc()).all()
    return render_template('pages/history.html', reports=reports)

@app.route('/download/<int:id>')
@login_required
def download_pdf(id):
    report = Assessment.query.get_or_404(id)
    
    # 1. Format Tanggal (menjadi dd-mm-yyyy)
    date_str = report.date_posted.strftime('%d-%m-%Y')
    
    # 2. Format Nama (Ganti spasi dengan underscore biar tidak error di browser)
    # Contoh: "Ivan Febriand" -> "Ivan_Febriand"
    safe_name = current_user.name.replace(" ", "_")
    
    rendered = render_template('layouts/pdf_template.html', report=report, user=current_user)
    pdf = HTML(string=rendered).write_pdf()
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    
    # 3. Masukkan Nama & Tanggal ke Filename
    # Hasil: "Laporan_Ivan_Febriand_12-12-2025.pdf"
    filename = f"Laporan_{safe_name}_{date_str}.pdf"
    
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)