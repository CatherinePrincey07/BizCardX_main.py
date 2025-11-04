import streamlit as st
import yaml
import bcrypt
import pandas as pd
import psycopg2
import easyocr
import re
import cv2
import numpy as np
import time
import requests
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie

# Page configuration (this must be the first Streamlit command)
st.set_page_config(page_title="BizCardX", page_icon='random', layout="wide")

# Hide Streamlit main menu and footer
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

# Application background
def app_bg():
    st.markdown(f""" <style>.stApp {{
                        background: url("https://cdn.wallpapersafari.com/7/90/BFUQb1.jpg");
                        background-size: cover;
                     }}
                     </style>""", unsafe_allow_html=True)

app_bg()

# Load credentials
def load_credentials():
    with open('credentials.yaml', 'r') as file:
        return yaml.safe_load(file)

credentials = load_credentials()

def authenticate_user(username, password):
    for user in credentials['users']:
        if user['username'] == username and bcrypt.checkpw(password.encode(), user['password'].encode()):
            return True
    return False

# Login page
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# Check authentication
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    login()
else:
    # Database connection
    mydb = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="****",
        database="bizcard",
        port="5432"
    )
    mycursor = mydb.cursor()

    # Create table if not exists
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS card_data (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            designation VARCHAR(255),
            company VARCHAR(255),
            contact VARCHAR(255),
            email VARCHAR(255),
            website VARCHAR(255),
            address VARCHAR(255),
            city VARCHAR(255),
            state VARCHAR(255),
            pincode VARCHAR(255),
            image BYTEA
        )
    """)
    mydb.commit()

    # Navigation and main sections
    navigation, text_process = st.columns([1.2, 4.55])
    with navigation:
        selected = option_menu('Main Menu', ['Home', "Image to Text", "Database"],
                               icons=["house", 'file-earmark-font', 'gear'], default_index=0)

    with text_process:
        if selected == 'Home':
            left, right = st.columns(2)
            with right:
                url = requests.get("https://assets5.lottiefiles.com/private_files/lf30_euijmy98.json", verify=False)
                url_json = {}
                if url.status_code == 200:
                    url_json = url.json()
                st_lottie(url_json,
                          reverse=False,
                          height=300,
                          speed=1,
                          loop=True,
                          quality='high')
                st.write('### TECHNOLOGIES USED')
                st.write('##### *:red[Python]  *:red[Streamlit] *:red[EasyOCR]  *:red[OpenCV]  *:red[PostgreSQL]')
                st.write("To learn more about EasyOCR [press here](https://pypi.org/project/easyocr/)")

            with left:
                st.markdown("### Welcome to the Business Card Application!")
                st.markdown('###### Bizcard is a Python application designed to extract information from business cards. '
                            'It utilizes various technologies such as :blue[Streamlit, Streamlit_lottie, Python, EasyOCR, '
                            'RegEx function, OpenCV, and PostgreSQL] database to achieve this functionality.')
                st.write('The main purpose of Bizcard is to automate the process of extracting key details from business card images, '
                         'such as the name, designation, company, contact information, and other relevant data. '
                         'By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, '
                         'Bizcard is able to extract text from the images.')
                st.write("Click on the ****:red[Image to text]**** option to start exploring the Bizcard extraction.")

        if selected == 'Image to Text':
            file, text = st.columns([3, 2.5])
            with file:
                uploaded_file = st.file_uploader("Choose an image of a business card", type=["jpg", "jpeg", "png"])
                if uploaded_file is not None:
                    file_bytes = uploaded_file.read()
                    nparr = np.frombuffer(file_bytes, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    st.image(image, channels='BGR', use_column_width=True)

                    if st.button('TEXT BOUNDING'):
                        with st.spinner('Detecting text...'):
                            time.sleep(1)
                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        for i in contours:
                            x, y, w, h = cv2.boundingRect(i)
                            color = (0, 255, 0)
                            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                        st.write('Compare the images')
                        st.image(image, use_column_width=True)
                        st.info('Image might have inaccurate detection of text', icon='ℹ️')

            with text:
                left, right = st.tabs(['Undefined text extraction', 'Pre-defined text extraction'])
                with left:
                    st.markdown('###### *Here you can view an undefined text extraction using :red[EasyOCR]*, '
                                'an advanced tool for random text extraction.')
                    st.write('Please note: It will accept all images and further updates will be available soon!')
                    if st.button('RANDOM EXTRACTION'):
                        if 'image' in locals():
                            with st.spinner('Extracting text...'):
                                reader = easyocr.Reader(['en'])
                                results = reader.readtext(image)
                                for result in results:
                                    st.write(result[1])
                        else:
                            st.error("Please upload an image first.")

                with right:
                    st.markdown("###### *Press the extract button below to view structured text format & upload to database using :blue[EasyOCR] & :blue[Python regular expression]*")
                    st.write('Please note: This tab is only for *:blue[business card images]*; it will not accept random images.')
                    if st.button('EXTRACT & UPLOAD'):
                        if 'image' in locals():
                            with st.spinner('Extracting text...'):
                                reader = easyocr.Reader(['en'])
                                results = reader.readtext(image)
                                card_info = [result[1] for result in results]
                                card = ' '.join(card_info)

                                # Replacements for better extraction
                                replacements = [
                                    (";", ""), (',', ''), ("WWW ", "www."), ("www ", "www."), ('www', 'www.'),
                                    ('www.', 'www'), ('wwW', 'www'), ('wWW', 'www'), ('.com', 'com'), ('com', '.com'),
                                ]
                                for old, new in replacements:
                                    card = card.replace(old, new)

                                # Extract phone number
                                ph_pattern = r"\+?\d{2,3}[-\s]?\d{3}[-\s]?\d{4}"
                                ph = re.findall(ph_pattern, card)
                                Phone = ' '.join(ph)
                                card = re.sub(ph_pattern, '', card)

                                # Extract email id
                                mail_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
                                mail = re.findall(mail_pattern, card)
                                Email_id = ' '.join(mail)
                                card = re.sub(mail_pattern, '', card)

                                # Extract website
                                url_pattern = r"www\.[A-Za-z0-9]+\.[A-Za-z]{2,3}"
                                url = re.findall(url_pattern, card)
                                URL = ' '.join(url)
                                card = re.sub(url_pattern, '', card)

                                # Extract pincode
                                pin_pattern = r'\d{6,7}'
                                match = re.findall(pin_pattern, card)
                                Pincode = ' '.join(match)
                                card = re.sub(pin_pattern, '', card)

                                # Extract name, designation, company
                                name_pattern = r'^[A-Za-z]+ [A-Za-z]+$|^[A-Za-z]+$|^[A-Za-z]+ & [A-Za-z]+$'
                                name_data = [i for i in card_info if re.findall(name_pattern, i) and i not in 'WWW']
                                name = name_data[0] if len(name_data) > 0 else ''
                                designation = name_data[1] if len(name_data) > 1 else ''
                                company = ' '.join(name_data[2:]) if len(name_data) > 2 else ''

                                card = card.replace(name, '').replace(designation, '').replace(company, '')

                                # Extract city, state, address
                                new = card.split()
                                if len(new) >= 5:
                                    city = new[2] if new[4] == 'St' else new[3]
                                    state = new[4] if new[4] == 'St' else new[5]
                                    address = ' '.join(new[:3])
                                else:
                                    city = state = address = ''

                                st.markdown(f'**Name:** {name}')
                                st.markdown(f'**Designation:** {designation}')
                                st.markdown(f'**Company:** {company}')
                                st.markdown(f'**Contact:** {Phone}')
                                st.markdown(f'**Email ID:** {Email_id}')
                                st.markdown(f'**Website:** {URL}')
                                st.markdown(f'**Pincode:** {Pincode}')
                                st.markdown(f'**Address:** {address}')
                                st.markdown(f'**City:** {city}')
                                st.markdown(f'**State:** {state}')

                                # Upload to database
                                mycursor.execute("INSERT INTO card_data (name, designation, company, contact, email, website, address, city, state, pincode, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                                 (name, designation, company, Phone, Email_id, URL, address, city, state, Pincode, file_bytes))
                                mydb.commit()
                                st.success("Uploaded to Database successfully!")
                        else:
                            st.error("Please upload an image first.")

        if selected == 'Database':
            # Display records
            if st.checkbox('Show Database'):
                with st.spinner('Loading data from PostgreSQL'):
                    time.sleep(2)
                mycursor.execute("SELECT * FROM card_data")
                data = mycursor.fetchall()
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Designation', 'Company', 'Contact', 'Email', 'Website', 'Address', 'City', 'State', 'Pincode', 'Image'])
                st.dataframe(df)
            
            # Delete records
            st.markdown("### Delete Record")
            record_id = st.number_input("Enter the ID of the record to delete", min_value=1, step=1)
            if st.button('Delete Record'):
                if record_id:
                    try:
                        mycursor.execute("DELETE FROM card_data WHERE id = %s", (record_id,))
                        mydb.commit()
                        st.success(f"Record with ID {record_id} deleted successfully!")
                    except Exception as e:
                        st.error(f"Error deleting record: {e}")
                else:
                    st.error("Please enter a valid ID to delete.")
            
            # Modify records
            st.markdown("### Modify Record")
            modify_id = st.number_input("Enter the ID of the record to modify", min_value=1, step=1)
            if modify_id:
                mycursor.execute("SELECT * FROM card_data WHERE id = %s", (modify_id,))
                record = mycursor.fetchone()
                if record:
                    name = st.text_input("Name", value=record[1])
                    designation = st.text_input("Designation", value=record[2])
                    company = st.text_input("Company", value=record[3])
                    contact = st.text_input("Contact", value=record[4])
                    email = st.text_input("Email", value=record[5])
                    website = st.text_input("Website", value=record[6])
                    address = st.text_input("Address", value=record[7])
                    city = st.text_input("City", value=record[8])
                    state = st.text_input("State", value=record[9])
                    pincode = st.text_input("Pincode", value=record[10])
                    
                    if st.button('Update Record'):
                        try:
                            # Update record in the database
                            mycursor.execute("""
                                UPDATE card_data
                                SET name = %s, designation = %s, company = %s, contact = %s, email = %s, website = %s, address = %s, city = %s, state = %s, pincode = %s
                                WHERE id = %s
                            """, (name, designation, company, contact, email, website, address, city, state, pincode, modify_id))
                            mydb.commit()
                            st.success(f"Record with ID {modify_id} updated successfully!")
                        except Exception as e:
                            st.error(f"Error updating record: {e}")
                else:
                    st.error("Record not found.")
