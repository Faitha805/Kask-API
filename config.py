# With the use of enviroment variables, sensitive information like email and password will be secured and kept in encrypted format instead of plain text.
import os

# Getting environment variables from the .env file.
from dotenv import load_dotenv

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/kasokoso_db'
    # dialect+driver://username:password@host:port/database The port is optional.
    JWT_SECRET_KEY = 'customers'

    # Email (SMTP) settings.
    load_dotenv = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')