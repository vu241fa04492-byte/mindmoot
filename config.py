class Config:

    SECRET_KEY = 'mysecretkey'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///debate.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = 'mysecretkey'