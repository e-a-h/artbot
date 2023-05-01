from tortoise import Tortoise
from tortoise.models import Model
from tortoise.fields import \
    BooleanField, BigIntField, IntField, SmallIntField, CharField, ForeignKeyField, OneToOneField, ReverseRelation
from utils import tortoise_settings, Logging
import os


async def init(db_name=''):
    #  specify the app name of 'models'
    #  which contain models from "app.models"

    # env var ARTBOT_DB will override db name from both init call AND config.json
    override_db_name = os.getenv('ARTBOT_DB')
    if override_db_name:
        db_name = override_db_name

    settings = tortoise_settings.TORTOISE_ORM
    if db_name:
        settings['connections']['default']['credentials']['database'] = db_name

    Logging.info(f"Database init - \"{settings['connections']['default']['credentials']['database']}\"")
    await Tortoise.init(settings)


class AbstractBaseModel(Model):
    id = IntField(pk=True)

    class Meta:
        abstract = True


class DeprecatedServerIdMixIn:
    serverid = BigIntField()


class AdminRole(AbstractBaseModel):
    guild = ForeignKeyField('artbot.Guild', related_name='admin_roles', index=True)
    roleid = BigIntField()

    def __str__(self):
        return str(self.roleid)

    class Meta:
        unique_together = ('roleid', 'guild')
        table = 'adminrole'


class ArtChannel(AbstractBaseModel, DeprecatedServerIdMixIn):
    # guild = ForeignKeyField('artbot.Guild', related_name='artchannels')
    listenchannelid = BigIntField(default=0)
    collectionchannelid = BigIntField(default=0)
    tag = CharField(max_length=50, default="")

    def __str__(self):
        return str(self.listenchannelid)

    class Meta:
        unique_together = ('serverid', 'listenchannelid', 'collectionchannelid', 'tag')
        table = 'artchannel'


class AutoResponder(AbstractBaseModel, DeprecatedServerIdMixIn):
    trigger = CharField(max_length=300)
    response = CharField(max_length=2000)
    flags = SmallIntField(default=0)
    chance = SmallIntField(default=10000)
    responsechannelid = BigIntField(default=0)
    listenchannelid = BigIntField(default=0)
    logchannelid = BigIntField(default=0)

    def __str__(self):
        return self.trigger

    class Meta:
        unique_together = ('trigger', 'serverid')
        table = 'autoresponder'


class BotAdmin(AbstractBaseModel):
    userid = BigIntField(unique=True)

    def __str__(self):
        return str(self.userid)

    class Meta:
        table = 'botadmin'


class ConfigChannel(AbstractBaseModel, DeprecatedServerIdMixIn):
    configname = CharField(max_length=100)
    channelid = BigIntField(default=0)

    def __str__(self):
        return str(self.channelid)

    class Meta:
        unique_together = ('configname', 'serverid')
        table = 'configchannel'


class CountWord(AbstractBaseModel, DeprecatedServerIdMixIn):
    # guild = ForeignKeyField('artbot.Guild', related_name='watchwords')
    word = CharField(max_length=300)

    def __str__(self):
        return self.word

    class Meta:
        unique_together = ('word', 'serverid')
        table = 'countword'


class CustomCommand(AbstractBaseModel, DeprecatedServerIdMixIn):
    trigger = CharField(max_length=20)
    response = CharField(max_length=2000)
    deletetrigger = BooleanField(default=False)
    reply = BooleanField(default=False)

    def __str__(self):
        return self.trigger

    class Meta:
        unique_together = ('trigger', 'serverid')
        table = 'customcommand'


class DropboxChannel(AbstractBaseModel, DeprecatedServerIdMixIn):
    sourcechannelid = BigIntField()
    targetchannelid = BigIntField(default=0)
    deletedelayms = SmallIntField(default=0)
    sendreceipt = BooleanField(default=False)

    def __str__(self):
        return str(self.sourcechannelid)

    class Meta:
        unique_together = ('serverid', 'sourcechannelid')
        table = 'dropboxchannel'


class Guild(AbstractBaseModel):
    serverid = BigIntField(unique=True)
    memberrole = BigIntField(default=0)
    nonmemberrole = BigIntField(default=0)
    mutedrole = BigIntField(default=0)
    welcomechannelid = BigIntField(default=0)
    ruleschannelid = BigIntField(default=0)
    logchannelid = BigIntField(default=0)
    entrychannelid = BigIntField(default=0)
    rulesreactmessageid = BigIntField(default=0)
    defaultlocale = CharField(max_length=10)

    admin_roles: ReverseRelation["AdminRole"]
    locales: ReverseRelation["Localization"]
    mod_roles: ReverseRelation["ModRole"]
    trusted_roles: ReverseRelation["TrustedRole"]
    command_permissions: ReverseRelation["UserPermission"]
    premium_tiers: ReverseRelation["PremiumTier"]

    def __str__(self):
        return self.serverid

    class Meta:
        table = 'guild'


class Localization(AbstractBaseModel):
    guild = ForeignKeyField('artbot.Guild', related_name='locales', index=True)
    channelid = BigIntField(default=0)
    locale = CharField(max_length=10, default='')

    def __str__(self):
        return f"localized channel {str(self.channelid)} uses language: {self.locale}"

    class Meta:
        unique_together = ('guild', 'channelid')
        table = 'localization'


class ModRole(AbstractBaseModel):
    guild = ForeignKeyField('artbot.Guild', related_name='mod_roles', index=True)
    roleid = BigIntField()

    def __str__(self):
        return str(self.roleid)

    class Meta:
        unique_together = ('roleid', 'guild')
        table = 'modrole'


class PremiumTier(AbstractBaseModel):
    guild = ForeignKeyField('artbot.Guild', related_name='premium_tiers', index=True)
    roleid = BigIntField()

    members: ReverseRelation["PremiumTierMember"]
    requirements: ReverseRelation["PremiumTierRequirement"]

    class Meta:
        unique_together = ('guild', 'roleid')
        table = 'premiumtier'


class PremiumTierMember(AbstractBaseModel):
    userid = BigIntField()
    tier = ForeignKeyField('artbot.PremiumTier', related_name='members')

    info: ReverseRelation["PremiumTierMemberInfo"]

    class Meta:
        table = 'premiumtiermember'


class PremiumTierMemberInfo(AbstractBaseModel):
    requirementid = BigIntField()
    member = ForeignKeyField('artbot.PremiumTierMember', related_name='info')
    value = CharField(max_length=500)

    class Meta:
        table = 'premiumtiermemberinfo'


class PremiumTierRequirement(AbstractBaseModel):
    tier = ForeignKeyField('artbot.PremiumTier', related_name='requirements')
    name = CharField(max_length=100)
    prompt = CharField(max_length=500)

    class Meta:
        table = 'premiumtierrequirement'


class ReactWatch(AbstractBaseModel):
    # guild = OneToOneField('artbot.Guild', related_name='watchemoji')
    serverid = BigIntField(unique=True)
    muteduration = SmallIntField(default=600)
    watchremoves = BooleanField(default=False)

    emoji: ReverseRelation["WatchedEmoji"]

    def __str__(self):
        return f"Server: {self.serverid} - Mute Time: {self.muteduration}s - " \
               f"Watching for react removal: {'YES' if self.watchremoves else 'NO'}"

    class Meta:
        table = 'reactwatch'


class TrustedRole(AbstractBaseModel):
    guild = ForeignKeyField('artbot.Guild', related_name='trusted_roles', index=True)
    roleid = BigIntField()

    def __str__(self):
        return str(self.roleid)

    class Meta:
        unique_together = ('roleid', 'guild')
        table = 'trustedrole'


class UserPermission(AbstractBaseModel):
    guild = ForeignKeyField('artbot.Guild', related_name='command_permissions', index=True)
    userid = BigIntField()
    command = CharField(max_length=200, default='')
    allow = BooleanField(default=True)

    def __str__(self):
        return f"{str(self.userid)}: {self.command} = {'true' if self.allow else 'false'}"

    class Meta:
        unique_together = ('userid', 'command')
        table = 'userpermission'


class WatchedEmoji(AbstractBaseModel):
    watcher = ForeignKeyField('artbot.ReactWatch', related_name='emoji', index=True)
    emoji = CharField(max_length=50)
    log = BooleanField(default=False)
    remove = BooleanField(default=False)
    mute = BooleanField(default=False)

    def __str__(self):
        return self.emoji

    class Meta:
        unique_together = ('emoji', 'watcher')
        table = 'watchedemoji'
