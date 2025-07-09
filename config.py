class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/kasokoso_db'
    # dialect+driver://username:password@host:port/database The port is optional.
    JWT_SECRET_KEY = 'customers'