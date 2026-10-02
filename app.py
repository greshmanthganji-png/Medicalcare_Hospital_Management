import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-secret-key')

DB = dict(host=os.getenv('MYSQL_HOST','localhost'), user=os.getenv('MYSQL_USER','root'), password=os.getenv('MYSQL_PASSWORD',''), database=os.getenv('MYSQL_DATABASE','medicare_hospital'))

def get_db(): return mysql.connector.connect(**DB)
def q(sql, params=(), fetch=False, one=False):
    cn=get_db(); cur=cn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        if fetch: return cur.fetchone() if one else cur.fetchall()
        cn.commit(); return cur.lastrowid
    finally: cur.close(); cn.close()

def login_required(f):
    @wraps(f)
    def w(*a,**kw):
        if 'user_id' not in session: return redirect(url_for('login'))
        return f(*a,**kw)
    return w

def admin_required(f):
    @wraps(f)
    def w(*a,**kw):
        if session.get('role')!='admin': flash('Admin access required.','danger'); return redirect(url_for('dashboard'))
        return f(*a,**kw)
    return w

@app.context_processor
def globals(): return {'hospital_name':'MediCare Multispeciality Hospital'}

@app.route('/')
def index(): return redirect(url_for('dashboard')) if 'user_id' in session else redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=q('SELECT * FROM users WHERE username=%s',(request.form['username'],),True,True)
        if u and check_password_hash(u['password_hash'],request.form['password']):
            session.update(user_id=u['id'],username=u['username'],role=u['role']); return redirect(url_for('dashboard'))
        flash('Invalid username or password.','danger')
    return render_template('login.html')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

@app.cli.command('create-admin')
def create_admin():
    existing=q('SELECT id FROM users WHERE username=%s',('admin',),True,True)
    if existing: print('Admin already exists: admin / admin123'); return
    q('INSERT INTO users(username,password_hash,role) VALUES(%s,%s,%s)',('admin',generate_password_hash('admin123'),'admin'))
    print('Created admin: admin / admin123')

@app.route('/dashboard')
@login_required
def dashboard():
    stats={
      'patients':q('SELECT COUNT(*) c FROM patients',fetch=True,one=True)['c'],
      'doctors':q('SELECT COUNT(*) c FROM doctors',fetch=True,one=True)['c'],
      'appointments':q("SELECT COUNT(*) c FROM appointments WHERE appointment_date=CURDATE()",fetch=True,one=True)['c'],
      'admitted':q("SELECT COUNT(*) c FROM admissions WHERE status='Admitted'",fetch=True,one=True)['c'],
      'revenue':q("SELECT COALESCE(SUM(total_amount),0) s FROM bills WHERE payment_status='Paid'",fetch=True,one=True)['s']
    }
    upcoming=q('''SELECT a.*,p.name patient_name,d.name doctor_name FROM appointments a JOIN patients p ON p.id=a.patient_id JOIN doctors d ON d.id=a.doctor_id WHERE a.appointment_date>=CURDATE() ORDER BY a.appointment_date,a.appointment_time LIMIT 8''',fetch=True)
    return render_template('dashboard.html',stats=stats,upcoming=upcoming)

@app.route('/patients')
@login_required
def patients(): return render_template('patients.html',patients=q('SELECT * FROM patients ORDER BY id DESC',fetch=True))

@app.route('/patients/add',methods=['GET','POST'])
@login_required
def add_patient():
    if request.method=='POST':
        code='P'+datetime.now().strftime('%y%m%d%H%M%S')
        q('''INSERT INTO patients(patient_code,name,gender,dob,phone,email,address,blood_group,emergency_contact,emergency_phone) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(code,request.form['name'],request.form['gender'],request.form.get('dob') or None,request.form.get('phone'),request.form.get('email'),request.form.get('address'),request.form.get('blood_group'),request.form.get('emergency_contact'),request.form.get('emergency_phone')))
        flash('Patient registered successfully.','success'); return redirect(url_for('patients'))
    return render_template('patient_form.html')

@app.route('/doctors')
@login_required
def doctors(): return render_template('doctors.html',doctors=q('''SELECT d.*,dp.name department_name FROM doctors d LEFT JOIN departments dp ON dp.id=d.department_id ORDER BY d.name''',fetch=True))

@app.route('/appointments',methods=['GET','POST'])
@login_required
def appointments():
    if request.method=='POST':
        q('INSERT INTO appointments(patient_id,doctor_id,appointment_date,appointment_time,reason) VALUES(%s,%s,%s,%s,%s)', (request.form['patient_id'],request.form['doctor_id'],request.form['appointment_date'],request.form['appointment_time'],request.form.get('reason')))
        flash('Appointment scheduled.','success'); return redirect(url_for('appointments'))
    return render_template('appointments.html',appointments=q('''SELECT a.*,p.name patient_name,d.name doctor_name FROM appointments a JOIN patients p ON p.id=a.patient_id JOIN doctors d ON d.id=a.doctor_id ORDER BY a.appointment_date DESC,a.appointment_time DESC''',fetch=True),patients=q('SELECT id,name,patient_code FROM patients ORDER BY name',fetch=True),doctors=q('SELECT id,name,specialization FROM doctors ORDER BY name',fetch=True))

@app.route('/appointments/<int:id>/status/<status>')
@login_required
def appointment_status(id,status):
    if status not in ['Scheduled','Completed','Cancelled']: return redirect(url_for('appointments'))
    q('UPDATE appointments SET status=%s WHERE id=%s',(status,id)); flash('Appointment status updated.','success'); return redirect(url_for('appointments'))

@app.route('/rooms')
@login_required
def rooms(): return render_template('rooms.html',rooms=q('SELECT * FROM rooms ORDER BY room_no',fetch=True))

@app.route('/admissions',methods=['GET','POST'])
@login_required
def admissions():
    if request.method=='POST':
        room=request.form.get('room_id') or None
        aid=q('INSERT INTO admissions(patient_id,doctor_id,room_id,diagnosis) VALUES(%s,%s,%s,%s)',(request.form['patient_id'],request.form.get('doctor_id') or None,room,request.form.get('diagnosis')))
        if room: q("UPDATE rooms SET status='Occupied' WHERE id=%s",(room,))
        flash('Patient admitted.','success'); return redirect(url_for('admissions'))
    data=q('''SELECT a.*,p.name patient_name,p.patient_code,d.name doctor_name,r.room_no FROM admissions a JOIN patients p ON p.id=a.patient_id LEFT JOIN doctors d ON d.id=a.doctor_id LEFT JOIN rooms r ON r.id=a.room_id ORDER BY a.id DESC''',fetch=True)
    return render_template('admissions.html',admissions=data,patients=q('SELECT id,name,patient_code FROM patients ORDER BY name',fetch=True),doctors=q('SELECT id,name FROM doctors ORDER BY name',fetch=True),rooms=q("SELECT id,room_no,room_type FROM rooms WHERE status='Available' ORDER BY room_no",fetch=True))

@app.route('/admissions/<int:id>/discharge',methods=['POST'])
@login_required
def discharge(id):
    a=q('SELECT room_id FROM admissions WHERE id=%s',(id,),True,True)
    q("UPDATE admissions SET status='Discharged',discharge_date=NOW() WHERE id=%s",(id,))
    if a and a['room_id']: q("UPDATE rooms SET status='Available' WHERE id=%s",(a['room_id'],))
    flash('Patient discharged and room released.','success'); return redirect(url_for('admissions'))

@app.route('/prescriptions',methods=['GET','POST'])
@login_required
def prescriptions():
    if request.method=='POST':
        q('INSERT INTO prescriptions(patient_id,doctor_id,medicine_name,dosage,frequency,duration,instructions) VALUES(%s,%s,%s,%s,%s,%s,%s)',(request.form['patient_id'],request.form.get('doctor_id') or None,request.form['medicine_name'],request.form.get('dosage'),request.form.get('frequency'),request.form.get('duration'),request.form.get('instructions')))
        flash('Prescription added.','success'); return redirect(url_for('prescriptions'))
    data=q('''SELECT pr.*,p.name patient_name,d.name doctor_name FROM prescriptions pr JOIN patients p ON p.id=pr.patient_id LEFT JOIN doctors d ON d.id=pr.doctor_id ORDER BY pr.id DESC''',fetch=True)
    return render_template('prescriptions.html',prescriptions=data,patients=q('SELECT id,name,patient_code FROM patients ORDER BY name',fetch=True),doctors=q('SELECT id,name FROM doctors ORDER BY name',fetch=True))

@app.route('/billing',methods=['GET','POST'])
@login_required
def billing():
    if request.method=='POST':
        vals=[float(request.form.get(x) or 0) for x in ['consultation_amount','room_amount','medicine_amount','other_amount']]
        total=sum(vals)
        q('INSERT INTO bills(patient_id,admission_id,consultation_amount,room_amount,medicine_amount,other_amount,total_amount,payment_status,payment_method) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',(request.form['patient_id'],request.form.get('admission_id') or None,*vals,total,request.form['payment_status'],request.form['payment_method']))
        flash('Bill created successfully.','success'); return redirect(url_for('billing'))
    return render_template('billing.html',bills=q('''SELECT b.*,p.name patient_name FROM bills b JOIN patients p ON p.id=b.patient_id ORDER BY b.id DESC''',fetch=True),patients=q('SELECT id,name,patient_code FROM patients ORDER BY name',fetch=True),admissions=q("SELECT id,patient_id FROM admissions WHERE status='Admitted'",fetch=True))

@app.route('/reports')
@login_required
def reports():
    revenue=q("SELECT COALESCE(SUM(total_amount),0) total FROM bills WHERE payment_status='Paid'",fetch=True,one=True)['total']
    dept=q('''SELECT dp.name,COUNT(d.id) doctor_count FROM departments dp LEFT JOIN doctors d ON d.department_id=dp.id GROUP BY dp.id,dp.name ORDER BY doctor_count DESC''',fetch=True)
    return render_template('reports.html',revenue=revenue,dept=dept)

@app.route('/staff')
@admin_required
def staff(): return render_template('staff.html',staff=q('SELECT id,username,role,created_at FROM users ORDER BY id',fetch=True))

@app.route('/staff/add',methods=['POST'])
@admin_required
def add_staff():
    try: q('INSERT INTO users(username,password_hash,role) VALUES(%s,%s,%s)',(request.form['username'],generate_password_hash(request.form['password']),request.form['role'])); flash('Staff account created.','success')
    except Exception as e: flash('Could not create account. Username may already exist.','danger')
    return redirect(url_for('staff'))

if __name__=='__main__': app.run(debug=True)
