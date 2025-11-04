BizCardX
BizCardX is a Python-based application designed to extract information from business cards using Optical Character Recognition (OCR). It integrates with a PostgreSQL database to store and manage extracted data. This README provides instructions on how to set up and use the application.

Features Business Card Image Upload: Upload images of business cards and extract text information. Text Extraction: Use EasyOCR to extract text from images. Database Integration: Save extracted information to a PostgreSQL database. Record Management: View, update, and delete records in the database. 
User Authentication: Secure access to the application with user authentication. Requirements Python 3.8+ Streamlit EasyOCR OpenCV Pandas psycopg2 PyYAML bcrypt PostgreSQL Installation Clone the Repository

bash Copy code git clone ([https://github.com/CatherinePrincey07/BizCardX_main.py]) cd bizcardx Create a Virtual Environment

bash Copy code python -m venv venv source venv/bin/activate # On Windows use venv\Scripts\activate Install Dependencies

bash Copy code pip install -r requirements.txt Set Up PostgreSQL Database

Ensure PostgreSQL is installed and running. Create a database named bizcard. Update the database configuration in the script with your PostgreSQL credentials. Configure User Authentication

Create a credentials.yaml file in the root directory with the following structure:

yaml Copy code users:

username: "your_username" password: "your_password" Replace "your_username" and "your_password" with your chosen credentials. Passwords should be hashed before storing.
Usage Start the Application

bash Copy code streamlit run app.py Access the Application

Open your browser and go to http://localhost:8501 to access the BizCardX application.

Upload Business Card Image

Go to the "Image to Text" section. Upload a business card image. Click "TEXT BOUNDING" to detect text areas in the image. Click "EXTRACT & UPLOAD" to extract and upload data to the database. Manage Records

Go to the "Database" section. View records in the database. Delete records by entering the record ID and clicking "Delete Record." Modify records by entering the record ID, updating details, and clicking "Update Record." Login

Access the application via the login page. Enter your credentials to authenticate. Configuration app.py: Main application script. credentials.yaml: User credentials for authentication. requirements.txt: Python package dependencies. Troubleshooting Database Connection Errors: Ensure PostgreSQL is running and credentials are correct. Image Upload Issues: Check the file type and size. OCR Accuracy: Text extraction accuracy may vary based on image quality.
