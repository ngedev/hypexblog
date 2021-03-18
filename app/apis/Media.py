import os

from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import current_user
from marshmallow import Schema, fields
from zemfrog.decorators import authenticate
from zemfrog.extensions.apispec import FileField
from zemfrog.models import DefaultResponseSchema

from core.helpers import delete_file_media
from core.media import save_image_file
from core.validators import image_file_required
from models.Article import Article


class MediaResponse(Schema):
    url = fields.Url(required=True)
    filename = fields.String(required=True)


@authenticate()
@use_kwargs({"article_id": fields.Integer(required=True)}, location="form")
@use_kwargs(
    {"image": FileField(validate=image_file_required, required=True)}, location="files"
)
@marshal_with(MediaResponse, 200)
@marshal_with(DefaultResponseSchema, 404)
def article_post(**kwds):
    article_id = kwds["article_id"]
    image = kwds["image"]
    article = Article.query.filter_by(id=article_id, user_id=current_user.id)
    if article.count() == 0:
        return {"code": 404, "message": "Article not found"}

    outdir = os.path.join(current_user.nickname, str(article_id))
    url = save_image_file(image, outdir)
    filename = os.path.basename(url)
    return {"url": url, "filename": filename}


@authenticate()
@use_kwargs(
    {
        "article_id": fields.Integer(required=True),
        "filename": fields.String(required=True),
    }
)
@marshal_with(DefaultResponseSchema, 200)
@marshal_with(DefaultResponseSchema, 404)
def article_delete(**kwds):
    article_id = kwds["article_id"]
    filename = kwds["filename"]
    article = Article.query.filter_by(id=article_id, user_id=current_user.id)
    if article.count() == 0:
        status_code = 404
        message = "Article not found"
    else:
        status_code = 200
        message = "Ok"
        delete_file_media(current_user.nickname, str(article_id), filename)

    return {"code": status_code, "message": message}


docs = {"tags": ["Media"]}
endpoint = "media"
url_prefix = "/media"
routes = [
    ("/article", article_post, ["POST"]),
    ("/article", article_delete, ["DELETE"]),
]
