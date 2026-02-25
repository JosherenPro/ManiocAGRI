import os
from dotenv import load_dotenv

load_dotenv()

def _build_db_url() -> str:
    """
    Retourne simplement la DATABASE_URL définie dans le `.env`
    qui contient déjà les bons identifiants et le port 5432 compatible SQLAlchemy.
    """
    raw_url = os.getenv("DATABASE_URL", "")
    return raw_url or "sqlite:///./manioc_agri.db"

class Settings:
    PROJECT_NAME: str = "ManiocAgri"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-dev-only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    DATABASE_URL: str = _build_db_url()

    # AI & Cerebras
    CEREBRAS_API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")

    # Email Settings
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "info@maniocagri.bj")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "ManiocAgri")

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")

    # PayGateGlobal
    PAYGATE_API_KEY: str = os.getenv("PAYGATE_API_KEY", "")
    PAYGATE_CALLBACK_URL: str = os.getenv("PAYGATE_CALLBACK_URL", "")
    PAYGATE_PAY_URL: str = os.getenv("PAYGATE_PAY_URL", "https://paygateglobal.com/api/v1/pay")
    PAYGATE_STATUS_URL: str = os.getenv("PAYGATE_STATUS_URL", "https://paygateglobal.com/api/v1/status")

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    SUPABASE_BUCKET: str = os.getenv("SUPABASE_BUCKET", "produits-images")

settings = Settings()
