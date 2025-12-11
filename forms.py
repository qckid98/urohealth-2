from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

class AssessmentForm(FlaskForm):
    # ==========================================
    # BAGIAN A: GEJALA KEKAMBUHAN (VITAL)
    # ==========================================
    
    # SelectField otomatis memilih opsi pertama sebagai default ('0' / 'tidak')
    
    hematuria = SelectField('1. Hematuria', choices=[
        ('0', 'Tidak Ada'), ('1', 'Mikroskopis'), ('5', 'Kasar/Makroskopis (BAHAYA)')
    ], default='0', validators=[DataRequired()])

    # IntegerField kita beri default=1 untuk Skala, dan default=0 untuk Jumlah
    
    urgensi = IntegerField('2. Urgensi (0-5)', default=0, validators=[NumberRange(min=0, max=5)])
    
    frekuensi_siang = IntegerField('3. Frekuensi Siang', default=0, validators=[Optional()])
    
    nokturia = IntegerField('4. Nokturia/Malam', default=0, validators=[Optional()])
    
    disuria = IntegerField('5. Disuria (0-5)', default=0, validators=[NumberRange(min=0, max=5)])
    
    tidak_tuntas = SelectField('6. Rasa Tidak Tuntas', choices=[
        ('tidak', 'Tidak'), ('ya', 'Ya')
    ], default='tidak')
    
    berat_badan = SelectField('7. Berat Badan', choices=[
        ('0', 'Tidak Ada'), ('1', '< 5 kg'), ('3', '> 5 kg (Signifikan)')
    ], default='0')
    
    nyeri_tulang = SelectField('8. Nyeri Tulang', choices=[
        ('0', 'Tidak Ada'), ('1', 'Ringan'), ('4', 'Parah/Progresif')
    ], default='0', validators=[DataRequired()])
    
    kelelahan = IntegerField('9. Kelelahan (0-5)', default=0, validators=[NumberRange(min=0, max=5)])
    
    nyeri_pelvis = IntegerField('10. Nyeri Pelvis (0-5)', default=0, validators=[NumberRange(min=0, max=5)])
    
    hematospermia = SelectField('11. Hematospermia', choices=[
        ('tidak', 'Tidak'), ('ya', 'Ya')
    ], default='tidak')

    # ==========================================
    # BAGIAN B: EFEK SAMPING (AI ADVICE)
    # ==========================================
    
    es_inkontinensia = SelectField('1. Inkontinensia', choices=[
        ('tidak_ada', 'Tidak Ada'), ('ringan', 'Ringan'), ('berat', 'Berat')
    ], default='tidak_ada')
    
    es_pad = IntegerField('2. Jumlah Pad', default=0, validators=[Optional()])
    
    es_iritasi = IntegerField('3. Iritasi (1-5)', default=0, validators=[Optional(), NumberRange(min=0, max=5)])
    
    es_spasms = SelectField('4. Bladder Spasms', choices=[
        ('tidak', 'Tidak'), ('ya', 'Ya')
    ], default='tidak')
    
    es_ereksi = IntegerField('5. Disfungsi Ereksi (0-5)', default=0, validators=[Optional(), NumberRange(min=0, max=5)])
    
    es_libido = SelectField('6. Libido', choices=[
        ('sama', 'Sama'), ('naik', 'Meningkat'), ('turun', 'Menurun')
    ], default='sama')
    
    es_hot_flashes = IntegerField('7. Hot Flashes', default=0, validators=[Optional()])
    
    es_testis = SelectField('8. Perubahan Testis', choices=[
        ('tidak', 'Tidak'), ('ya', 'Ya')
    ], default='tidak')
    
    es_diare = IntegerField('9. Diare (0-5)', default=0, validators=[Optional(), NumberRange(min=0, max=5)])
    
    es_rektal = SelectField('10. Perdarahan Rektal', choices=[
        ('tidak', 'Tidak'), ('ringan', 'Ringan'), ('berat', 'Berat')
    ], default='tidak')
    
    es_perut = IntegerField('11. Nyeri Perut (0-5)', default=0, validators=[Optional(), NumberRange(min=0, max=5)])
    
    es_pelvis_kronis = IntegerField('12. Pelvis Kronis (0-5)', default=0, validators=[Optional(), NumberRange(min=0, max=5)])
    
    es_neuropati = IntegerField('13. Neuropati (0-5)', default=0, validators=[Optional(), NumberRange(min=0, max=5)])

    submit = SubmitField('Analisa Kesehatan')