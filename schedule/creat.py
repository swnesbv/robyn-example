from pathlib import Path, PurePosixPath
from datetime import datetime, timedelta

import io, os, jwt, functools, itertools, json

from multipart import parse_form

from http import cookies

import urllib.parse
from urllib.parse import quote

from passlib.hash import pbkdf2_sha1

from sqlalchemy import update as sqlalchemy_update, func
from sqlalchemy.future import select

from robyn import Response, SubRouter

from mail.verify import verify_mail

from db_config.settings import settings
from db_config.storage_config import async_session

from options_select.opt_slc import templates, in_all, left_right_all, left_right_first

from account.token import mail_verify, encode_reset_password, decode_reset_password
from account.opt_slc import (
    get_id_token_visited,
    get_visited_user,
    get_token_visited_payload,
)

from account.models import User
from .models import Recording, Schedule


schedule = SubRouter(__name__, prefix="/schedule")


@schedule.get("/creat")
async def get_creat(request):
    template = "/schedule/creat.html"
    context = {"request": request}
    template = templates.render_template(template, **context)
    return template


@schedule.post("/creat")
async def post_creat(request):
    owner = await get_id_token_visited(request)

    async with async_session() as session:
        qsl = dict(urllib.parse.parse_qsl(request.body))
        title = qsl["title"]
        description = qsl["description"]
        str_start = qsl["start"]
        str_end = qsl["end"]
        qs = dict(urllib.parse.parse_qs(request.body))
        str_hour = qs["list"]

        start = datetime(
            *[int(v) for v in str_start.replace("T", "-").replace(":", "-").split("-")]
        )
        end = datetime(
            *[int(v) for v in str_end.replace("T", "-").replace(":", "-").split("-")]
        )

        hour_list = []
        for v in str_hour:
            obj = v.split("T")[1]
            hour = datetime.strptime(obj, settings.TIME_HM)
            hour_list.append(hour)

        new = Schedule()
        new.title = title
        new.description = description
        new.owner = owner
        new.st_hour = start
        new.en_hour = end
        new.hours = hour_list
        new.created_at = datetime.now()

        session.add(new)
        await session.commit()

        return Response(
            status_code=302,
            headers={
                "location": quote(
                    "/",
                    safe=":/%#?=@[]!$&'()*+,;",
                )
            },
            description=("Ok..!"),
        )
