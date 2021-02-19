import string

from rest_framework.schemas.openapi import AutoSchema


class CustomSchema(AutoSchema):
    """
    AutoSchema subclass using schema_extra_info on the view.
    """
    def __init__(self, tags=None):
        super().__init__(tags=tags)

