# coding=utf-8
# author:xsl

from mongoengine import (
    Document,
    StringField,
    ObjectIdField,
    DateTimeField,
    IntField
)
from bson import ObjectId
import time
import datetime

class BaseDocument(Document):
    pk_name = 'id'
    meta = {'abstract': True}

    @classmethod
    def get(cls, pk):
        if not pk:
            return None
        return cls.objects(**{cls.pk_name: pk}).first()

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()
        return obj

class SLLog(BaseDocument):
    meta = {
        'db_alias': 'logdb'
    }
    STATUS_READ = 1
    STATUS_UNREAD = 0

    id = ObjectIdField(primary_key=True, default=ObjectId)
    msg = StringField()
    type = StringField()
    status = IntField(default=0)
    points = IntField(default=0)
    created_time = DateTimeField(default=datetime.datetime.now)

    @classmethod
    def create(cls, **kwargs):
        qkw = {k: v for k, v in kwargs.items() \
            if k != 'text' and v}
        if cls.objects(**qkw).first():
            return None
        return super().create(**kwargs)

    def pack(self):
        res = {
            'id': str(self.id),
            'msg': str(self.msg),
            'created_time': self.created_time,
            'status': self.status
        }
        return res