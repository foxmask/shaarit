# coding: utf-8
"""
2025 - ShaarIt - 셔릿
"""

import logging

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette_wtf import CSRFProtectMiddleware
from tortoise.contrib.starlette import register_tortoise
from uvicorn.main import run

from shaarit import config
from shaarit.views import shaarit_routes

logging.basicConfig(level=logging.DEBUG)

app = Starlette(
    debug=config.DEBUG,
    # lifespan=lifespan,
    middleware=[
        Middleware(SessionMiddleware, secret_key=config.SECRET_KEY),
        Middleware(CSRFProtectMiddleware, csrf_secret=config.CSRF_SECRET),
        Middleware(CORSMiddleware, allow_origins=config.ALLOW_ORIGINS),
        Middleware(TrustedHostMiddleware, allowed_hosts=config.ALLOWED_HOSTS),
    ],
    routes=[
        Mount("/static", app=StaticFiles(directory="shaarit/static"), name="static"),
        Mount("", routes=shaarit_routes),
    ],
)


register_tortoise(
    app, db_url=config.DATABASE_URL, modules={"models": ["shaarit.models"]}, generate_schemas=True
)

if __name__ == "__main__":
    run(app)
