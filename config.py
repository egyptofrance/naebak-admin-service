# config.py

class Config:
    DEBUG = False
    TESTING = False
    DATABASE_URL = "sqlite:///./test.db"

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    pass

