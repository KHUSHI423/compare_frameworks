from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from marshmallow import Schema, fields

from .models import Board, Task


class BoardSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Board
        include_fk = True
        load_instance = True


class TaskSchema(SQLAlchemyAutoSchema):
    status = fields.Function(lambda task: task.status.value if task.status else None)

    class Meta:
        model = Task
        include_fk = True
        load_instance = True


class PaginatedSchema(Schema):
    items = fields.List(fields.Dict())
    total = fields.Integer()
    page = fields.Integer()
    page_size = fields.Integer()
