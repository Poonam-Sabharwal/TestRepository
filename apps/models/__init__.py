import mongoengine as me


class UserModel(me.Document):
    username = me.StringField(required=True)
