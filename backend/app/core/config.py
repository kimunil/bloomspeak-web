from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite:///./dev.db"
    JWT_SECRET: str = "change-me-in-prod"
    JWT_EXPIRE_MIN: int = 10080
    OPENAI_API_KEY: str = ""
    STT_PROVIDER: str = "mock"
    LLM_PROVIDER: str = "mock"
    PG_PROVIDER: str = "mock"
    PG_SECRET_KEY: str = ""
    CORS_ORIGINS: str = "https://bloomspeak.kr,https://www.bloomspeak.kr"

    # ---- 간편 로그인(OAuth) ----
    # 값이 비어 있으면 데모(mock) 모드로 동작해 오프라인에서도 로그인 흐름을 확인할 수 있습니다.
    APP_DEEP_LINK_SCHEME: str = "bloomspeak"   # 앱 딥링크 스킴 (app.json scheme)
    OAUTH_REDIRECT_BASE: str = "https://api.bloomspeak.kr"  # 콜백 베이스 URL

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    NAVER_CLIENT_ID: str = ""
    NAVER_CLIENT_SECRET: str = ""
    KAKAO_REST_API_KEY: str = ""      # 카카오 REST API 키(client_id 역할)
    KAKAO_CLIENT_SECRET: str = ""     # (선택) 카카오 보안 강화 시


settings = Settings()
