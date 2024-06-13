from pathlib import Path, PurePosixPath
from datetime import datetime, timedelta

import io, os, jwt, functools, itertools, json

from robyn import Response, SubRouter

from multipart import parse_form

from http import cookies

import urllib.parse
from urllib.parse import quote

from passlib.hash import pbkdf2_sha1

from sqlalchemy import update as sqlalchemy_update, func
from sqlalchemy.future import select

from mail.verify import verify_mail

from db_config.settings import settings
from db_config.storage_config import async_session

from options_select.opt_slc import templates, in_all, left_right_all, left_right_first

from account.token import mail_verify, encode_reset_password, decode_reset_password
from account.opt_slc import get_id_token_visited, get_visited_user, get_token_visited_payload

from account.models import User
from .models import Recording, Schedule


handlers = SubRouter(__name__, prefix="/schedule")


@handlers.get("/select")
async def sch_select(request):
    template = "/schedule/select.html"
    async with async_session() as session:

        stmt = await session.execute(
            select(Schedule).where(Schedule.en_hour >= datetime.now())
        )
        result = stmt.scalars().all()
        context = {
            "request": request,
            "result": result,
        }
        if request.method == "GET":
            template = templates.render_template(template, **context)
            return template


@handlers.get("/detail/:id")
async def sch_detail(request):

    id = int(request.path_params["id"])
    template = "/schedule/detail.html"
    async with async_session() as session:

        result = await left_right_first(session, Schedule, Schedule.id, id)

        obj_list = []
        if result.occupied is not None:
            obj_list = list(set(result.hours) - set(result.occupied))
            print("obj..", obj_list)

        context = {
            "request": request,
            "result": result,
            "obj_list": obj_list,
        }
        if request.method == "GET":
            template = templates.render_template(template, **context)
            return template


@handlers.post("/detail/:id")
async def post_sch_detail(request):
    async with async_session() as session:

        id = int(request.path_params["id"])
        qsl = dict(urllib.parse.parse_qsl(request.body))
        owner = await get_id_token_visited(request)

        str_date = qsl["date"]
        str_split = str_date.split(" ")[0]
        str_hour = qsl["hour"]

        dates = datetime.strptime(str_split, settings.DATE)
        hour = datetime.strptime(str_hour, settings.TIME_FORMAT)

        new = Recording()
        new.owner = owner
        new.to_schedule = id
        new.record_d = dates
        new.record_h = hour
        new.created_at = datetime.now()

        session.add(new)
        await session.commit()

        hour_list = []
        hour_list.append(hour)

        query = (
            sqlalchemy_update(Schedule)
            .where(Schedule.id == id)
            .values(
                occupied=func.array_cat(Schedule.occupied, hour_list),
                modified_at=datetime.now(),
            )
            .execution_options(synchronize_session="fetch")
        )

        await session.execute(query)
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


# func SchAll(w http.ResponseWriter, r *http.Request) {

# 	if r.Method == "GET" {

# 		conn := connect.ConnSql()
# 		rows, err := qSch(w, conn)
# 		if err != nil {
# 			return
# 		}
# 		list, err := allSch(w, rows)
# 		if err != nil {
# 			return
# 		}

# 		defer conn.Close()

# 		tpl := template.Must(
# 			template.ParseFiles("./tpl/navbar.html", "./tpl/schedule/all.html", "./tpl/base.html"),
# 		)

# 		tpl.ExecuteTemplate(w, "base", list)
# 	}
# }
