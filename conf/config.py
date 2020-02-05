class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite:///site_aumai.db?check_same_thread=False'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLE = True
    USER_ENABLE_EMAIL = False


class ProductionConfig(Config):
    DATABASE_URI = 'mysql+pymysql://root:aumai123!@mysql:3306/aumaiDB'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True