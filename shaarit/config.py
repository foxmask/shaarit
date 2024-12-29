# coding: utf-8
"""
2025 - ShaarIt - 셔릿
"""

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)

DATABASE_URL = config("DATABASE_URL", default="sqlite://db.sqlite3")
LANGUAGE_CODE = config("LANGUAGE_CODE", default="fr-fr")
SHAARIT_NAME = config("SHAARIT_NAME", default="ShaarIt - 셔릿")
SHAARIT_AUTHOR = config("SHAARIT_AUTHOR", default="FoxMaSk")
SHAARIT_DESCRIPTION = config("SHAARIT_DESCRIPTION", default="Share links, thoughts, ideas and more")
SHAARIT_ROBOT = config("SHAARIT_ROBOT", default="index, follow")
SHAARIT_URL = config("SHAARIT_URL", default="http://localhost:8000")
SHAARIT_TZ = config("SHAARIT_TZ", default="Europe/Paris")

# CSRF
SECRET_KEY = config("SECRET_KEY", cast=Secret)
COOKIE_SAMESITE = config("COOKIE_SAMESITE", default="none")
COOKIE_SECURE = config("COOKIE_SECURE", cast=bool, default=True)
TOKEN_LOCATION = config("TOKEN_LOCATION", default="body")
TOKEN_KEY = config("TOKEN_KEY", default="csrf-token")
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS", default="localhost, 127.0.0.1", cast=CommaSeparatedStrings
)
CSRF_SECRET = config("CSRF_SECRET", cast=Secret)

# TRUSTED HOSTS
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost, 127.0.0.1", cast=CommaSeparatedStrings)
ALLOW_ORIGINS = ["*"]
LINKS_PER_PAGE = config("LINKS_PER_PAGE", cast=int, default=5)
DAILY_PER_PAGE = config("DAILY_PER_PAGE", cast=int, default=10)
