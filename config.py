class Config:
    # Flask configuration
    SECRET_KEY = 'your_secret_key_12345'
    DATABASE = 'database.db'

    # Celery configuration
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'