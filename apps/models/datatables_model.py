import mongoengine as me
from mongoengine.queryset.visitor import Q
from apps.common import utils


class DatatablesModel:
    # see https://datatables.net/manual/server-side for meaning of
    # parameters that datatables sends in the ajax call.

    mongo_collection_cls: me.Document = None
    columns = None
    draw = 1
    recordsTotal = 0
    recordsFiltered = 0
    data = None
    error = None

    search_value = None

    # Number of records that the table can display in the current draw.
    length = 10
    start = 0

    def __init__(self, mongo_collection_cls, draw, search_value, length) -> None:
        self.mongo_collection_cls = mongo_collection_cls
        self.draw = draw
        self.search_value = search_value
        self.length = length

    def prepare_companies_list_data(self):
        if utils.string_is_not_empty(self.search_value):
            self.mongo_collection_cls.objects[self.start : self.length]
        else:
            self.mongo_collection_cls.objects()[self.start : self.length]
