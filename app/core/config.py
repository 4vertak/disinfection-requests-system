import os


class Config(object):
    APPNAME = 'app'
    ROOT = os.path.abspath(APPNAME)
    UPLOAD_PATH = '/static/upload/'
    SERVER_PATH = os.path.join(ROOT, UPLOAD_PATH.lstrip('/'))
    
    DB_HOST = os.environ.get('POSTGRES_HOST', 'postgres')
    DB_PORT = int(os.environ.get('POSTGRES_PORT', '5432'))
    DB_NAME = os.environ.get('POSTGRES_DB', 'mydb')
    DB_USER = os.environ['POSTGRES_USER']
    DB_PASSWORD = os.environ['POSTGRES_PASSWORD'] 
    
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    
    
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }