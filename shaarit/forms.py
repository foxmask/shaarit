# coding: utf-8
"""
2025 - ShaarIt - 셔릿
"""

from starlette_wtf import StarletteForm
from wtforms import BooleanField, StringField, TextAreaField, URLField, validators
from wtforms.validators import URL, DataRequired


class LinksForm(StarletteForm):
    url = URLField(
        "URL",
        default="",
        validators=[validators.length(max=2048), URL()],
    )
    title = StringField("Title", validators=[validators.length(max=255), DataRequired()])
    text = TextAreaField(
        "Text",
        default="",
        validators=[validators.optional()],
    )
    tags = StringField(
        "Tags", default="", validators=[validators.length(max=255), validators.optional()]
    )
    private = BooleanField("Private", default=False)
    sticky = BooleanField("Sticky", default=False)


class LinksFormEdit(StarletteForm):
    url = URLField("URL", validators=[validators.length(max=2048), URL()])
    title = StringField("Title", validators=[validators.length(max=255), DataRequired()])
    text = TextAreaField("Text", validators=[validators.optional()])
    tags = StringField("Tags", validators=[validators.length(max=255), validators.optional()])
    private = BooleanField("Private", default=False)
    sticky = BooleanField("Sticky", default=False)
    image = StringField(
        "Image", default="", validators=[validators.length(max=255), validators.optional()]
    )
    video = StringField(
        "Video", default="", validators=[validators.length(max=255), validators.optional()]
    )


class SearchForm(StarletteForm):
    q = StringField("search", validators=[validators.length(max=80), DataRequired()])
