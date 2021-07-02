from peewee import MySQLDatabase, Model, BigIntegerField, CharField, ForeignKeyField, AutoField, \
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
    id = AutoField()
    serverid = BigIntegerField()
    memberrole = BigIntegerField(default=0)
    nonmemberrole = BigIntegerField(default=0)
    mutedrole = BigIntegerField(default=0)
    welcomechannelid = BigIntegerField(default=0)
    ruleschannelid = BigIntegerField(default=0)
    logchannelid = BigIntegerField(default=0)
    entrychannelid = BigIntegerField(default=0)
    rulesreactmessageid = BigIntegerField(default=0)
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
    id = AutoField()
    serverid = BigIntegerField()
    trigger = CharField(max_length=20, collation="utf8mb4_general_ci")
    response = CharField(max_length=2000, collation="utf8mb4_general_ci")
    deletetrigger = BooleanField(default=False)
    reply = BooleanField(default=False)

    class Meta:
        database = connection


class AutoResponder(Model):
    id = AutoField()
    serverid = BigIntegerField()
    trigger = CharField(max_length=300, collation="utf8mb4_general_ci")
    response = CharField(max_length=2000, collation="utf8mb4_general_ci")
    flags = SmallIntegerField(default=0)
    chance = SmallIntegerField(default=10000)
    responsechannelid = BigIntegerField(default=0)
    listenchannelid = BigIntegerField(default=0)
    logchannelid = BigIntegerField(default=0)

    class Meta:
        database = connection


class CountWord(Model):
    id = AutoField()
    serverid = BigIntegerField()
    # guild = ForeignKeyField(Guild, backref='watchwords')
    word = CharField(max_length=300, collation="utf8mb4_general_ci")

    class Meta:
        database = connection


class ReactWatch(Model):
    id = AutoField()
    serverid = BigIntegerField()
    # guild = ForeignKeyField(Guild, backref='watchemoji')
    muteduration = SmallIntegerField(default=600)
    watchremoves = BooleanField(default=False)

    class Meta:
        database = connection


class WatchedEmoji(Model):
    id = AutoField()
    watcher = ForeignKeyField(ReactWatch, backref='emoji')
    emoji = CharField(max_length=50, collation="utf8mb4_general_ci", default="")
    log = BooleanField(default=False)
    remove = BooleanField(default=False)
    mute = BooleanField(default=False)

    class Meta:
        database = connection


class ArtChannel(Model):
    id = AutoField()
    serverid = BigIntegerField()
    # guild = ForeignKeyField(Guild, backref='artchannels')
    listenchannelid = BigIntegerField(default=0)
    collectionchannelid = BigIntegerField(default=0)
    tag = CharField(max_length=30, collation="utf8mb4_general_ci")

    class Meta:
        database = connection


class DropboxChannel(Model):
    id = AutoField()
    serverid = BigIntegerField()
    sourcechannelid = BigIntegerField()
    targetchannelid = BigIntegerField(default=0)
    deletedelayms = SmallIntegerField(default=0)

    class Meta:
        database = connection


class Localization(Model):
    id = AutoField()
    guild = ForeignKeyField(Guild, backref='locales')
    channelid = BigIntegerField(default=0)
    locale = CharField(max_length=10, default='')

    class Meta:
        database = connection


class AdminRole(Model):
    id = AutoField()
    guild = ForeignKeyField(Guild, backref='admin_roles')
    roleid = BigIntegerField()

    class Meta:
        database = connection


class ModRole(Model):
    id = AutoField()
    guild = ForeignKeyField(Guild, backref='mod_roles')
    roleid = BigIntegerField()

    class Meta:
        database = connection


class BotAdmin(Model):
    id = AutoField()
    userid = BigIntegerField()

    class Meta:
        database = connection


class TrustedRole(Model):
    id = AutoField()
    guild = ForeignKeyField(Guild, backref='trusted_roles')
    roleid = BigIntegerField()

    class Meta:
        database = connection


class UserPermission(Model):
    id = AutoField()
    guild = ForeignKeyField(Guild, backref='command_permissions')
    userid = BigIntegerField()
    command = CharField(max_length=200, default='')
    allow = BooleanField(default=True)

    class Meta:
        database = connection


def init():
    global connection
    connection.connect()
    connection.create_tables([
        Guild,
        BotAdmin,
        AdminRole,
        ModRole,
        TrustedRole,
        UserPermission,
        ArtChannel,
        AutoResponder,
        ConfigChannel,
        CountWord,
        CustomCommand,
        ReactWatch,
        WatchedEmoji,
        Localization,
        DropboxChannel
    ])
    connection.close()
