from marshmallow import Schema, fields, RAISE, validate


class CreateUserSchema(Schema):
    class Meta:
        unknown = RAISE

    first_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=30),
    )
    last_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50),
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=12, max=128),
    )


class UserListSchema(Schema):
    class Meta:
        unknown = RAISE
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()


class UserLoginSchema(Schema):
    class Meta:
        unknown = RAISE
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=1, max=128),
    )


class PaginationSchema(Schema):
    page = fields.Integer(
        load_default=1,
        validate=validate.Range(min=1),
    )
    per_page = fields.Integer(
        load_default=20,
        validate=validate.Range(min=1, max=100),
    )


class PaginationResponseSchema(Schema):
    page = fields.Integer()
    per_page = fields.Integer()
    total = fields.Integer()
    pages = fields.Integer()


class UserListResponseSchema(Schema):
    data = fields.List(fields.Nested(UserListSchema))
    pagination = fields.Nested(PaginationResponseSchema)