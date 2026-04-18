import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    TESTING = False

    ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
    COGNITO_REGION = os.environ.get("COGNITO_REGION")
    COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
    COGNITO_APP_CLIENT_ID = os.environ.get("COGNITO_APP_CLIENT_ID")

    COGNITO_JWKS_URL = (
        f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/"
        f"{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    )
    
    @classmethod
    def validate(cls):
        if not cls.TESTING and not cls.ALPHA_VANTAGE_API_KEY:
            raise RuntimeError("ALPHA_VANTAGE_API_KEY not configured")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite+pysqlite:///:memory:"
    SQLALCHEMY_ECHO = False

    ALPHA_VANTAGE_API_KEY = "test-key"
    COGNITO_REGION = "test-region"
    COGNITO_USER_POOL_ID = "test-pool"
    COGNITO_APP_CLIENT_ID = "test-client"

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        f"mysql+pymysql://{os.environ.get('DB_USER', '')}:"
        f"{os.environ.get('DB_PASSWORD', '')}@"
        f"{os.environ.get('DB_HOST', 'localhost')}:"
        f"{os.environ.get('DB_PORT', '3306')}/"
        f"{os.environ.get('DB_NAME', '')}"
    )
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        f'mysql+pymysql://{os.environ.get("DB_USER", "")}:'
        f'{os.environ.get("DB_PASSWORD", "")}@'
        f'{os.environ.get("DB_HOST", "")}:'
        f'{os.environ.get("DB_PORT", "3306")}/'
        f'{os.environ.get("DB_NAME", "")}'
    )
    DEBUG = False
    SQLALCHEMY_ECHO = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "test": TestConfig,
}


def get_config(env: str):
    if env is None:
        env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, DevelopmentConfig)