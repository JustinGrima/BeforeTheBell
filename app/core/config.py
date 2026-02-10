from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "BeforeTheBell"
    environment: str = "dev"
    database_url: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/beforethebell"
    redis_url: str = "redis://redis:6379/0"

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    base_url: str = "http://localhost:8000"

    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_sender: str = "beforethebell@example.com"

    admin_emails: str = "admin@example.com"
    admin_sms_numbers: str = ""

    max_dispatch_minutes: int = 30
    sms_wait_minutes: int = 3
    school_timezone: str = "America/Toronto"
    summary_cron: str = "0 6 * * 1-5"


settings = Settings()
