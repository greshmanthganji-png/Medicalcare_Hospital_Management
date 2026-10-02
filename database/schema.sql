CREATE DATABASE IF NOT EXISTS medicare_hospital;
USE medicare_hospital;

CREATE TABLE IF NOT EXISTS users (
 id INT AUTO_INCREMENT PRIMARY KEY,
 username VARCHAR(50) UNIQUE NOT NULL,
 password_hash VARCHAR(255) NOT NULL,
 role ENUM('admin','receptionist','doctor','nurse') DEFAULT 'receptionist',
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS departments (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(100) UNIQUE NOT NULL,
 description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS doctors (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(120) NOT NULL,
 specialization VARCHAR(120) NOT NULL,
 department_id INT,
 phone VARCHAR(20), email VARCHAR(120), consultation_fee DECIMAL(10,2) DEFAULT 0,
 FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS patients (
 id INT AUTO_INCREMENT PRIMARY KEY,
 patient_code VARCHAR(30) UNIQUE NOT NULL,
 name VARCHAR(120) NOT NULL,
 gender ENUM('Male','Female','Other') NOT NULL,
 dob DATE,
 phone VARCHAR(20), email VARCHAR(120), address VARCHAR(255), blood_group VARCHAR(5), emergency_contact VARCHAR(120), emergency_phone VARCHAR(20), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
 id INT AUTO_INCREMENT PRIMARY KEY,
 patient_id INT NOT NULL,
 doctor_id INT NOT NULL,
 appointment_date DATE NOT NULL,
 appointment_time TIME NOT NULL,
 reason VARCHAR(255), status ENUM('Scheduled','Completed','Cancelled') DEFAULT 'Scheduled',
 FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
 FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rooms (
 id INT AUTO_INCREMENT PRIMARY KEY,
 room_no VARCHAR(20) UNIQUE NOT NULL,
 room_type ENUM('General','Semi-Private','Private','ICU') NOT NULL,
 daily_charge DECIMAL(10,2) NOT NULL,
 status ENUM('Available','Occupied','Maintenance') DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS admissions (
 id INT AUTO_INCREMENT PRIMARY KEY,
 patient_id INT NOT NULL,
 doctor_id INT,
 room_id INT,
 admission_date DATETIME DEFAULT CURRENT_TIMESTAMP,
 discharge_date DATETIME NULL,
 diagnosis VARCHAR(255),
 status ENUM('Admitted','Discharged') DEFAULT 'Admitted',
 FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
 FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE SET NULL,
 FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS prescriptions (
 id INT AUTO_INCREMENT PRIMARY KEY,
 patient_id INT NOT NULL,
 doctor_id INT,
 medicine_name VARCHAR(150) NOT NULL,
 dosage VARCHAR(100),
 frequency VARCHAR(100),
 duration VARCHAR(100),
 instructions VARCHAR(255),
 prescribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
 FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS bills (
 id INT AUTO_INCREMENT PRIMARY KEY,
 patient_id INT NOT NULL,
 admission_id INT,
 bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 consultation_amount DECIMAL(10,2) DEFAULT 0,
 room_amount DECIMAL(10,2) DEFAULT 0,
 medicine_amount DECIMAL(10,2) DEFAULT 0,
 other_amount DECIMAL(10,2) DEFAULT 0,
 total_amount DECIMAL(10,2) DEFAULT 0,
 payment_status ENUM('Pending','Paid','Partially Paid') DEFAULT 'Pending',
 payment_method ENUM('Cash','Card','UPI','Insurance') DEFAULT 'Cash',
 FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
 FOREIGN KEY (admission_id) REFERENCES admissions(id) ON DELETE SET NULL
);

INSERT IGNORE INTO departments(name,description) VALUES
('Cardiology','Heart and cardiovascular care'),('General Medicine','General medical care'),('Orthopedics','Bones and joints'),('Pediatrics','Child healthcare'),('Neurology','Brain and nervous system'),('Emergency','24x7 emergency services');

INSERT IGNORE INTO doctors(name,specialization,department_id,phone,email,consultation_fee) VALUES
('Dr. Arjun Rao','Cardiologist',(SELECT id FROM departments WHERE name='Cardiology'),'9876501001','arjun@medicare.local',800),
('Dr. Priya Sharma','General Physician',(SELECT id FROM departments WHERE name='General Medicine'),'9876501002','priya@medicare.local',500),
('Dr. Kiran Kumar','Orthopedic Surgeon',(SELECT id FROM departments WHERE name='Orthopedics'),'9876501003','kiran@medicare.local',700),
('Dr. Sneha Reddy','Pediatrician',(SELECT id FROM departments WHERE name='Pediatrics'),'9876501004','sneha@medicare.local',600);

INSERT IGNORE INTO rooms(room_no,room_type,daily_charge,status) VALUES
('G101','General',1200,'Available'),('G102','General',1200,'Available'),('SP201','Semi-Private',2200,'Available'),('P301','Private',3500,'Available'),('P302','Private',3500,'Available'),('ICU01','ICU',6500,'Available');
