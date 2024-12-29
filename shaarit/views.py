# coding: utf-8
"""
2025 - ShaarIt - 셔릿
"""

from datetime import date, datetime, timedelta, timezone

import pytz
from starlette.datastructures import ImmutableMultiDict
from starlette.responses import RedirectResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates
from starlette_wtf import csrf_protect
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q

from shaarit.forms import LinksForm, LinksFormEdit, SearchForm
from shaarit.hashed_url import small_hash
from shaarit.models import Links
from shaarit.template_filters import filter_datetime, filter_markdown

templates = Jinja2Templates(directory="shaarit/templates")
templates.env.filters["filter_markdown"] = filter_markdown
templates.env.filters["filter_datetime"] = filter_datetime


def url_cleaning(url: str) -> str:
    """
    drop unexpected content of the URL from the bookmarklet

    param url: url of the website
    :return string url
    """

    if url:
        for pattern in ("&utm_source=", "?utm_source=", "&utm_medium=", "#xtor=RSS-"):
            pos = url.find(pattern)
            if pos > 0:
                url = url[0:pos]
    return url


async def home(request):
    limit = request.state.config["LINKS_PER_PAGE"]
    offset = int(request.query_params.get("offset", 0))

    form_search = await SearchForm.from_formdata(request)

    if await form_search.validate_on_submit():
        q = form_search.q.data
        links = (
            await Links.filter(Q(title__icontains=q) | Q(text__icontains=q))
            .offset(offset)
            .limit(limit)
            .order_by("-date_created")
        )
    else:
        links = await Links.all().offset(offset).limit(limit).order_by("-date_created")
    # totals
    total_count = await Links.all().count()
    total_pages = (total_count + limit - 1) // limit

    context = {
        "config": request.state.config,
        "offset": offset,
        "limit": limit,
        "total_count": total_count,
        "total_pages": total_pages,
        "object_list": links,
        "form_search": form_search,
        "url": request.url_for("home"),
    }

    return templates.TemplateResponse(request, name="shaarit/links_list.html", context=context)


@csrf_protect
async def link_create(request):
    initial = {}

    # to manage the bookmarklet
    if request.query_params.get("post"):
        url = request.query_params.get("post")
        title = request.query_params.get("title")
        url = url_cleaning(str(url))
        initial = ImmutableMultiDict(
            {
                "url": url,
                "title": title,
            }
        )

    form = await LinksForm.from_formdata(request, initial)

    if await form.validate_on_submit():
        try:
            link = await Links.get(url=form.url.data)
        except DoesNotExist:
            now = datetime.now(timezone.utc)
            url_hashed = await small_hash(now.strftime("%Y%m%d_%H%M%S"))
            link = await Links.create(
                url=form.url.data,
                text=form.text.data,
                title=form.title.data,
                tags=form.tags.data,
                private=form.private.data,
                sticky=form.sticky.data,
                url_hashed=url_hashed,
            )
        url = request.url_for("link_detail", url_hashed=link.url_hashed)
        return RedirectResponse(url=url, status_code=303)

    context = {
        "config": request.state.config,
        "form": form,
        "edit_link": False,
    }

    return templates.TemplateResponse(request, name="shaarit/links_form.html", context=context)


@csrf_protect
async def link_edit(request):
    link_id = request.path_params["link_id"]
    # get the link
    link = await Links.get(id=link_id)

    if request.method == "GET":
        # prepare data to prefill the form
        data = ImmutableMultiDict(
            {
                "url": link.url,
                "title": link.title,
                "text": link.text,
                "tags": link.tags,
                "sticky": link.sticky,
                "private": link.private,
                "image": link.image,
                "video": link.video,
            }
        )
        # prefill the form
        form = await LinksFormEdit.from_formdata(request, data)
    else:
        form = await LinksFormEdit.from_formdata(request)

    if await form.validate_on_submit():
        await Links.filter(id=link_id).update(
            url=form.url.data,
            text=form.text.data,
            title=form.title.data,
            tags=form.tags.data,
            private=form.private.data,
            sticky=form.sticky.data,
        )
        url = request.url_for("link_detail", url_hashed=link.url_hashed)
        return RedirectResponse(url=url, status_code=303)

    context = {"config": request.state.config, "object": link, "form": form, "edit_link": True}

    return templates.TemplateResponse(request, name="shaarit/links_form.html", context=context)


async def link_detail(request):
    url_hashed = request.path_params["url_hashed"]
    link = await Links.get(url_hashed=url_hashed)

    context = {"config": request.state.config, "object": link}

    return templates.TemplateResponse(request, name="shaarit/links_detail.html", context=context)


async def link_delete(request):
    link_id = request.path_params["link_id"]
    try:
        link = await Links.get(id=link_id)
        await link.delete()
    except DoesNotExist:
        pass
    url = request.url_for("home")
    return RedirectResponse(url=url, status_code=303)


async def tags_list(request):
    links = await Links.all()
    tags = []
    for data in links:
        if data.tags is not None:
            for tag in data.tags.split(","):
                tags.append(tag)
        else:
            tags.append("0Tag")
    tags = sorted(tags)
    tags_dict = {}
    for my_tag in tags:
        tags_dict.update({my_tag: tags.count(my_tag)})

    context = {"config": request.state.config, "tags": tags_dict}

    return templates.TemplateResponse(request, name="shaarit/tags_list.html", context=context)


async def links_by_tag_list(request):
    limit = request.state.config["LINKS_PER_PAGE"]
    offset = int(request.query_params.get("offset", 0))

    tags = None if request.path_params["tags"] == "0Tag" else request.path_params["tags"]
    # when tags is None
    # get the data with tags is null
    if tags:
        links = (
            await Links.filter(tags__icontains=tags)
            .offset(offset)
            .limit(limit)
            .order_by("-date_created")
        )
        url = request.url_for("links_by_tag_list", tags=tags)
    else:
        links = (
            await Links.filter(tags__isnull=True)
            .offset(offset)
            .limit(limit)
            .order_by("-date_created")
        )
        url = request.url_for("links_by_tag_list", tags="0Tag")

    # totals
    total_count = await Links.all().count()
    total_pages = (total_count + limit - 1) // limit

    context = {
        "config": request.state.config,
        "offset": offset,
        "limit": limit,
        "total_count": total_count,
        "total_pages": total_pages,
        "object_list": links,
        "tags": tags,
        "url": url,
    }

    return templates.TemplateResponse(request, name="shaarit/links_list.html", context=context)


async def daily(request):
    """
    get the daily links
    look for the date of "yesterday" and "tomorrow"
    then look for the data
    """
    next_date = ""
    previous_date = ""

    now = datetime.now(tz=pytz.timezone(request.state.config["SHAARIT_TZ"]))
    today = date.today()

    yesterday = request.query_params.get("yesterday", None)

    if yesterday:
        yesterday = datetime.strptime(yesterday, "%Y-%m-%d")
        start_of_day = yesterday
    else:
        yesterday = today - timedelta(days=1, seconds=-1)
        start_of_day = datetime(now.year, now.month, now.day, now.hour, now.second)

    end_of_day = start_of_day + timedelta(days=1, seconds=-1)
    end_of_day_full = start_of_day + timedelta(days=1)

    # @TODO do not return private links
    my_previous_date = (
        await Links.filter(date_created__lte=yesterday).order_by("-date_created").first()
    )

    if my_previous_date:
        previous_date = my_previous_date.date_created.date()

    # @TODO do not return private links
    my_next_date = await Links.filter(date_created__gt=end_of_day).order_by("date_created").first()

    if my_next_date:
        next_date = my_next_date.date_created.date()

    if next_date == previous_date:
        next_date = end_of_day_full

    data = await Links.filter(date_created__range=(start_of_day, end_of_day)).order_by(
        "-date_created"
    )

    context = {
        "config": request.state.config,
        "previous_date": previous_date,
        "next_date": next_date,
        "current_date": yesterday,
        "links": data,
    }

    return templates.TemplateResponse(request, name="shaarit/daily_list.html", context=context)


async def link_private(request):
    limit = request.state.config["LINKS_PER_PAGE"]
    offset = int(request.query_params.get("offset", 0))
    links = await Links.filter(private=True).offset(offset).limit(limit).order_by("-date_created")
    # totals
    total_count = await Links.all().count()
    total_pages = (total_count + limit - 1) // limit

    context = {
        "config": request.state.config,
        "offset": offset,
        "limit": limit,
        "total_count": total_count,
        "total_pages": total_pages,
        "object_list": links,
        "url": request.url_for("link_private"),
    }

    return templates.TemplateResponse(request, name="shaarit/links_list.html", context=context)


async def link_public(request):
    limit = request.state.config["LINKS_PER_PAGE"]
    offset = int(request.query_params.get("offset", 0))
    links = await Links.filter(private=False).offset(offset).limit(limit).order_by("-date_created")
    # totals
    total_count = await Links.all().count()
    total_pages = (total_count + limit - 1) // limit

    context = {
        "config": request.state.config,
        "offset": offset,
        "limit": limit,
        "total_count": total_count,
        "total_pages": total_pages,
        "object_list": links,
        "url": request.url_for("link_public"),
    }

    return templates.TemplateResponse(request, name="shaarit/links_list.html", context=context)


shaarit_routes = [
    Route("/", endpoint=home, methods=["GET", "POST"]),
    Route("/new/", endpoint=link_create, methods=["GET", "POST"]),
    Route("/edit/{link_id}", endpoint=link_edit, methods=["GET", "POST"]),
    Route("/link/{url_hashed}", endpoint=link_detail, methods=["GET"]),
    Route("/delete/{link_id}", endpoint=link_delete, methods=["GET"]),
    Route("/tags/", endpoint=tags_list, methods=["GET"]),
    Route("/tags/{tags}", endpoint=links_by_tag_list, methods=["GET"]),
    Route("/daily/", endpoint=daily, methods=["GET"]),
    Route("/daily/{yesterday}", endpoint=daily, methods=["GET"]),
    Route("/link/private/", endpoint=link_private, methods=["GET"]),
    Route("/link/public/", endpoint=link_public, methods=["GET"]),
]
