from __future__ import absolute_import
from peewee import MySQLDatabase, Model, PrimaryKeyField, BigIntegerField, CharField, ForeignKeyField, AutoField, \
    TimestampField, SmallIntegerField, BooleanField

from utils import Configuration

connection = MySQLDatabase(Configuration.get_var("DATABASE_NAME"),
                           user=Configuration.get_var("DATABASE_USER"),
                           password=Configuration.get_var("DATABASE_PASS"),
                           host=Configuration.get_var("DATABASE_HOST"),
                           port=Configuration.get_var("DATABASE_PORT"),
                           use_unicode=True,
                           charset="utf8mb4")


class Guild(Model):
    id = PrimaryKeyField()
    serverid = BigIntegerField()
    memberrole = BigIntegerField()
    nonmemberrole = BigIntegerField()
    mutedrole = BigIntegerField()
    welcomechannelid = BigIntegerField()
    ruleschannelid = BigIntegerField()
    logchannelid = BigIntegerField()
    entrychannelid = BigIntegerField()
    rulesreactmessageid = BigIntegerField()
    defaultlocale = CharField(max_length=10)

    class Meta:
        database = connection


class ConfigChannel(Model):
    id = AutoField()
    configname = CharField(max_length=100, collation="utf8mb4_general_ci")
    channelid = BigIntegerField(default=0)
    serverid = BigIntegerField()

    class Meta:
        database = connection


class CustomCommand(Model):
    id = PrimaryKeyField()
    serverid = BigIntegerField()
    trigger = CharField(max_length=20, collation="utf8mb4_general_ci")
    response = CharField(max_length=2000, collation="utf8mb4_general_ci")

    class Meta:
        database = connection


class AutoResponder(Model):
    id = PrimaryKeyField()
    serverid = BigIntegerField()
    trigger = CharField(max_length=300, collation="utf8mb4_general_ci")
    response = CharField(max_length=2000, collation="utf8mb4_general_ci")
    flags = SmallIntegerField(default=0)
    chance = SmallIntegerField(default=10000)
    responsechannelid = BigIntegerField(default=0)
    listenchannelid = BigIntegerField(default=0)

    class Meta:
        database = connection


class CountWord(Model):
    id = PrimaryKeyField()
    serverid = BigIntegerField()
    # guild = ForeignKeyField(Guild, backref='watchwords')
    word = CharField(max_length=300, collation="utf8mb4_general_ci")

    class Meta:
        database = connection


class ReactWatch(Model):
    id = PrimaryKeyField()
    serverid = BigIntegerField()
    # guild = ForeignKeyField(Guild, backref='watchemoji')
    logtochannel = BigIntegerField(default=0)
    watchlist = CharField(max_length=2000, collation="utf8mb4_general_ci", default="")
    banlist = CharField(max_length=2000, collation="utf8mb4_general_ci", default="")
    mutebanned = BooleanField(default=True)
    watchremoves = BooleanField(default=False)

    class Meta:
        database = connection


class ArtChannel(Model):
    id = PrimaryKeyField()
    serverid = BigIntegerField()
    # guild = ForeignKeyField(Guild, backref='artchannels')
    listenchannelid = BigIntegerField(default=0)
    collectionchannelid = BigIntegerField(default=0)
    tag = CharField(max_length=30, collation="utf8mb4_general_ci")

    class Meta:
        database = connection


class AdminRole(Model):
    id = PrimaryKeyField()
    guild = ForeignKeyField(Guild, backref='admin_roles')
    roleid = BigIntegerField()

    class Meta:
        database = connection


class ModRole(Model):
    id = PrimaryKeyField()
    guild = ForeignKeyField(Guild, backref='mod_roles')
    roleid = BigIntegerField()

    class Meta:
        database = connection


def init():
    global connection
    connection.connect()
    connection.create_tables([
        Guild,
        ArtChannel,
        AutoResponder,
        ConfigChannel,
        CountWord,
        CustomCommand,
        ReactWatch,
        AdminRole,
        ModRole
    ])
    connection.close()
