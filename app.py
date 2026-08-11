
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, time

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Clinic Appointment System",
    page_icon="🏥",
    layout="wide"
)

# Hide Streamlit menu, header and footer
st.markdown("""
<style>
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE CONNECTION
# =========================================================

conn = sqlite3.connect(
    "clinic.db",
    check_same_thread=False
)

cursor = conn.cursor()

# =========================================================
# CREATE TABLES
# =========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    phone TEXT,
    address TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    specialization TEXT,
    available_time TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    date TEXT,
    time TEXT,
    reason TEXT,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bills (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    consultation REAL,
    medicine REAL,
    tests REAL,
    total REAL
)
""")

conn.commit()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🏥 Clinic Management")

menu = st.sidebar.selectbox(
    "Select Page",
    [
        "Dashboard",
        "Patients",
        "Doctors",
        "Appointments",
        "Billing",
        "Reports"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Clinic Appointment Management System\n\n"
    "Developed using Python, Streamlit and SQLite."
)

# =========================================================
# DASHBOARD
# =========================================================

if menu == "Dashboard":

    st.title("🏥 Clinic Dashboard")

    st.write(
        "Welcome to the Clinic Appointment Management System."
    )

    patient_count = cursor.execute(
        "SELECT COUNT(*) FROM patients"
    ).fetchone()[0]

    doctor_count = cursor.execute(
        "SELECT COUNT(*) FROM doctors"
    ).fetchone()[0]

    appointment_count = cursor.execute(
        "SELECT COUNT(*) FROM appointments"
    ).fetchone()[0]

    confirmed_count = cursor.execute(
        "SELECT COUNT(*) FROM appointments WHERE status='Confirmed'"
    ).fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "👤 Total Patients",
            patient_count
        )

    with col2:
        st.metric(
            "👨‍⚕️ Total Doctors",
            doctor_count
        )

    with col3:
        st.metric(
            "📅 Total Appointments",
            appointment_count
        )

    with col4:
        st.metric(
            "✅ Confirmed",
            confirmed_count
        )

    st.markdown("---")

    st.subheader("📅 Recent Appointments")

    recent = pd.read_sql_query("""
        SELECT
            appointments.appointment_id AS ID,
            patients.name AS Patient,
            doctors.name AS Doctor,
            appointments.date AS Date,
            appointments.time AS Time,
            appointments.status AS Status
        FROM appointments
        JOIN patients
        ON appointments.patient_id = patients.patient_id
        JOIN doctors
        ON appointments.doctor_id = doctors.doctor_id
        ORDER BY appointments.appointment_id DESC
        LIMIT 10
    """, conn)

    if recent.empty:
        st.info("No appointments available.")
    else:
        st.dataframe(
            recent,
            use_container_width=True
        )

# =========================================================
# PATIENT MANAGEMENT
# =========================================================

elif menu == "Patients":

    st.title("👤 Patient Management")

    tab1, tab2 = st.tabs(
        ["➕ Add Patient", "🔎 Search Patients"]
    )

    # -----------------------------------------------------
    # ADD PATIENT
    # -----------------------------------------------------

    with tab1:

        st.subheader("Register New Patient")

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Patient Name"
            )

            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=18
            )

            gender = st.selectbox(
                "Gender",
                [
                    "Male",
                    "Female",
                    "Other"
                ]
            )

        with col2:

            phone = st.text_input(
                "Phone Number"
            )

            address = st.text_area(
                "Address"
            )

        if st.button(
            "➕ Register Patient",
            use_container_width=True
        ):

            if name.strip() == "":

                st.error(
                    "Please enter the patient's name."
                )

            else:

                cursor.execute("""
                    INSERT INTO patients
                    (name, age, gender, phone, address)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    name,
                    age,
                    gender,
                    phone,
                    address
                ))

                conn.commit()

                st.success(
                    "✅ Patient registered successfully!"
                )

        st.markdown("---")

        st.subheader("📋 Registered Patients")

        patients = pd.read_sql_query(
            "SELECT * FROM patients",
            conn
        )

        if patients.empty:

            st.info(
                "No patients registered yet."
            )

        else:

            st.dataframe(
                patients,
                use_container_width=True
            )

    # -----------------------------------------------------
    # SEARCH PATIENTS
    # -----------------------------------------------------

    with tab2:

        st.subheader("🔎 Search Patient")

        search = st.text_input(
            "Enter patient name or phone number"
        )

        if search:

            search_result = pd.read_sql_query(
                """
                SELECT *
                FROM patients
                WHERE name LIKE ?
                OR phone LIKE ?
                """,
                conn,
                params=(
                    f"%{search}%",
                    f"%{search}%"
                )
            )

            if search_result.empty:

                st.warning(
                    "No patient found."
                )

            else:

                st.dataframe(
                    search_result,
                    use_container_width=True
                )

        else:

            st.info(
                "Enter a name or phone number to search."
            )

# =========================================================
# DOCTOR MANAGEMENT
# =========================================================

elif menu == "Doctors":

    st.title("👨‍⚕️ Doctor Management")

    st.subheader("Add New Doctor")

    col1, col2 = st.columns(2)

    with col1:

        doctor_name = st.text_input(
            "Doctor Name"
        )

        specialization = st.selectbox(
            "Specialization",
            [
                "General Physician",
                "Dentist",
                "Dermatologist",
                "Cardiologist",
                "Pediatrician",
                "Orthopedic",
                "Neurologist",
                "ENT Specialist",
                "Other"
            ]
        )

    with col2:

        available_time = st.text_input(
            "Available Time",
            placeholder="Example: 10:00 AM - 2:00 PM"
        )

    if st.button(
        "➕ Add Doctor",
        use_container_width=True
    ):

        if doctor_name.strip() == "":

            st.error(
                "Please enter doctor's name."
            )

        else:

            cursor.execute("""
                INSERT INTO doctors
                (name, specialization, available_time)
                VALUES (?, ?, ?)
            """, (
                doctor_name,
                specialization,
                available_time
            ))

            conn.commit()

            st.success(
                "✅ Doctor added successfully!"
            )

    st.markdown("---")

    st.subheader("📋 Doctor List")

    doctors = pd.read_sql_query(
        "SELECT * FROM doctors",
        conn
    )

    if doctors.empty:

        st.info(
            "No doctors added yet."
        )

    else:

        st.dataframe(
            doctors,
            use_container_width=True
        )

# =========================================================
# APPOINTMENT MANAGEMENT
# =========================================================

elif menu == "Appointments":

    st.title("📅 Appointment Management")

    patients = pd.read_sql_query(
        "SELECT * FROM patients",
        conn
    )

    doctors = pd.read_sql_query(
        "SELECT * FROM doctors",
        conn
    )

    st.subheader("📅 Book New Appointment")

    if patients.empty:

        st.warning(
            "⚠️ Please register at least one patient first."
        )

    elif doctors.empty:

        st.warning(
            "⚠️ Please add at least one doctor first."
        )

    else:

        patient_options = {
            row["name"]: row["patient_id"]
            for _, row in patients.iterrows()
        }

        doctor_options = {
            row["name"]: row["doctor_id"]
            for _, row in doctors.iterrows()
        }

        col1, col2 = st.columns(2)

        with col1:

            selected_patient = st.selectbox(
                "Select Patient",
                list(patient_options.keys())
            )

            appointment_date = st.date_input(
                "Appointment Date",
                value=date.today()
            )

        with col2:

            selected_doctor = st.selectbox(
                "Select Doctor",
                list(doctor_options.keys())
            )

            appointment_time = st.time_input(
                "Appointment Time",
                value=time(10, 0)
            )

        reason = st.text_area(
            "Reason for Visit"
        )

        if st.button(
            "📅 Book Appointment",
            use_container_width=True
        ):

            cursor.execute("""
                INSERT INTO appointments
                (patient_id, doctor_id, date, time, reason, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                patient_options[selected_patient],
                doctor_options[selected_doctor],
                str(appointment_date),
                str(appointment_time),
                reason,
                "Confirmed"
            ))

            conn.commit()

            st.success(
                "✅ Appointment booked successfully!"
            )

    st.markdown("---")

    st.subheader("📋 Appointment History")

    appointments = pd.read_sql_query("""
        SELECT
            appointments.appointment_id AS ID,
            patients.name AS Patient,
            doctors.name AS Doctor,
            doctors.specialization AS Specialization,
            appointments.date AS Date,
            appointments.time AS Time,
            appointments.reason AS Reason,
            appointments.status AS Status
        FROM appointments
        JOIN patients
        ON appointments.patient_id = patients.patient_id
        JOIN doctors
        ON appointments.doctor_id = doctors.doctor_id
        ORDER BY appointments.appointment_id DESC
    """, conn)

    if appointments.empty:

        st.info(
            "No appointments booked yet."
        )

    else:

        st.dataframe(
            appointments,
            use_container_width=True
        )

        st.subheader("❌ Cancel Appointment")

        appointment_ids = appointments["ID"].tolist()

        selected_id = st.selectbox(
            "Select Appointment ID",
            appointment_ids
        )

        if st.button(
            "❌ Cancel Selected Appointment"
        ):

            cursor.execute("""
                UPDATE appointments
                SET status = 'Cancelled'
                WHERE appointment_id = ?
            """, (selected_id,))

            conn.commit()

            st.success(
                "Appointment cancelled successfully."
            )

# =========================================================
# BILLING
# =========================================================

elif menu == "Billing":

    st.title("💳 Billing Management")

    patients = pd.read_sql_query(
        "SELECT * FROM patients",
        conn
    )

    if patients.empty:

        st.warning(
            "Please register a patient first."
        )

    else:

        patient_options = {
            row["name"]: row["patient_id"]
            for _, row in patients.iterrows()
        }

        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_options.keys())
        )

        st.subheader("💰 Enter Charges")

        col1, col2, col3 = st.columns(3)

        with col1:

            consultation = st.number_input(
                "Consultation Fee (₹)",
                min_value=0.0,
                value=500.0
            )

        with col2:

            medicine = st.number_input(
                "Medicine (₹)",
                min_value=0.0,
                value=0.0
            )

        with col3:

            tests = st.number_input(
                "Tests (₹)",
                min_value=0.0,
                value=0.0
            )

        total = (
            consultation +
            medicine +
            tests
        )

        st.metric(
            "Total Amount",
            f"₹{total:.2f}"
        )

        if st.button(
            "💳 Generate Bill",
            use_container_width=True
        ):

            cursor.execute("""
                INSERT INTO bills
                (patient_id, consultation, medicine, tests, total)
                VALUES (?, ?, ?, ?, ?)
            """, (
                patient_options[selected_patient],
                consultation,
                medicine,
                tests,
                total
            ))

            conn.commit()

            st.success(
                "✅ Bill generated successfully!"
            )

        st.markdown("---")

        st.subheader("📋 Billing History")

        bills = pd.read_sql_query("""
            SELECT
                bills.bill_id AS ID,
                patients.name AS Patient,
                bills.consultation AS Consultation,
                bills.medicine AS Medicine,
                bills.tests AS Tests,
                bills.total AS Total
            FROM bills
            JOIN patients
            ON bills.patient_id = patients.patient_id
            ORDER BY bills.bill_id DESC
        """, conn)

        if bills.empty:

            st.info(
                "No bills generated yet."
            )

        else:

            st.dataframe(
                bills,
                use_container_width=True
            )

# =========================================================
# REPORTS
# =========================================================

elif menu == "Reports":

    st.title("📊 Clinic Reports")

    appointments = pd.read_sql_query("""
        SELECT
            appointments.date AS Date,
            appointments.status AS Status,
            doctors.name AS Doctor,
            doctors.specialization AS Specialization
        FROM appointments
        JOIN doctors
        ON appointments.doctor_id = doctors.doctor_id
    """, conn)

    if appointments.empty:

        st.info(
            "Not enough data to generate reports."
        )

    else:

        st.subheader(
            "📊 Appointments by Status"
        )

        status_data = (
            appointments["Status"]
            .value_counts()
        )

        fig1, ax1 = plt.subplots()

        status_data.plot(
            kind="bar",
            ax=ax1
        )

        ax1.set_xlabel("Status")
        ax1.set_ylabel("Number of Appointments")
        ax1.set_title("Appointment Status")

        st.pyplot(fig1)

        st.subheader(
            "👨‍⚕️ Appointments by Doctor"
        )

        doctor_data = (
            appointments["Doctor"]
            .value_counts()
        )

        fig2, ax2 = plt.subplots()

        doctor_data.plot(
            kind="bar",
            ax=ax2
        )

        ax2.set_xlabel("Doctor")
        ax2.set_ylabel("Appointments")
        ax2.set_title("Doctor-wise Appointments")

        plt.xticks(
            rotation=45,
            ha="right"
        )

        st.pyplot(fig2)

        st.subheader(
            "🩺 Appointments by Specialization"
        )

        specialization_data = (
            appointments["Specialization"]
            .value_counts()
        )

        fig3, ax3 = plt.subplots()

        specialization_data.plot(
            kind="pie",
            autopct="%1.1f%%",
            ax=ax3
        )

        ax3.set_ylabel("")

        ax3.set_title(
            "Specialization-wise Appointments"
        )

        st.pyplot(fig3)

# =========================================================
# SAVE DATABASE
# =========================================================

conn.commit()
