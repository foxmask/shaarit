# coding: utf-8
"""
2025 - ShaarIt - 셔릿
"""

from tortoise import fields, models
from tortoise.validators import RegexValidator

# Regex to match latin and 한글 (hangul) chars
"""
alphanum_hangul = RegexValidator(
    r"^[0-9a-zA-Z\u3131-\ud79d\u1100-\u11ff\u3130-\u318f\ua960-\ua97f\uac00-\ud7af\ud7b0-\ud7ff,]*$",
    "Only alphanumeric characters are allowed.",
)
"""


class Links(models.Model):
    id = fields.IntField(primary_key=True)
    url = fields.CharField(max_length=2048, null=True, default=None, unique=True)
    url_hashed = fields.CharField(max_length=10, null=True, default=None, unique=True)
    title = fields.CharField(max_length=255, null=True, default=None)
    text = fields.TextField(null=True, default=None)
    tags = fields.CharField(
        max_length=255, null=True, default=None
    )  # validators=[alphanum_hangul])
    private = fields.BooleanField(default=False)
    sticky = fields.BooleanField(default=False)
    image = fields.CharField(max_length=255, null=True, default=None)
    video = fields.CharField(max_length=255, null=True, default=None)
    date_created = fields.DatetimeField(auto_now_add=True)
    date_modified = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "links"

    def __str__(self) -> str:
        return f"Links {self.id}: {self.title}"
