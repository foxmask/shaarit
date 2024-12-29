# coding: utf-8
"""
2025 - ShaarIt - 셔릿
"""

from starlette.middleware.base import BaseHTTPMiddleware

from shaarit import config


class ConfigMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.state.config = {
            "DEBUG": config.DEBUG,
            "DATABASE_URL": config.DATABASE_URL,
            "LANGUAGE_CODE": config.LANGUAGE_CODE,
            "SHAARIT_NAME": config.SHAARIT_NAME,
            "SHAARIT_AUTHOR": config.SHAARIT_AUTHOR,
            "SHAARIT_DESCRIPTION": config.SHAARIT_DESCRIPTION,
            "SHAARIT_ROBOT": config.SHAARIT_ROBOT,
            "SHAARIT_URL": config.SHAARIT_URL,
            "SHAARIT_TZ": config.SHAARIT_TZ,
            # CSRF
            "COOKIE_SAMESITE": config.COOKIE_SAMESITE,
            "COOKIE_SECURE": config.COOKIE_SECURE,
            "TOKEN_LOCATION": config.TOKEN_LOCATION,
            "TOKEN_KEY": config.TOKEN_KEY,
            "CSRF_TRUSTED_ORIGINS": config.CSRF_TRUSTED_ORIGINS,
            "CSRF_SECRET": config.CSRF_SECRET,
            # TRUSTED HOSTS
            "ALLOWED_HOSTS": config.ALLOWED_HOSTS,
            "ALLOW_ORIGINS": config.ALLOW_ORIGINS,
            # PAGINATION
            "LINKS_PER_PAGE": config.LINKS_PER_PAGE,
            "DAILY_PER_PAGE": config.DAILY_PER_PAGE,
        }

        response = await call_next(request)
        return response
