import asyncio
import io
import re
from datetime import datetime

import discord
import pytz
from pytz import UnknownTimeZoneError
from discord import Role, AllowedMentions, Forbidden
from discord.ext import commands, tasks
from slugify import slugify
from tortoise.exceptions import OperationalError, MultipleObjectsReturned, DoesNotExist, NoValuesFetched
from validate_email import validate_email

import utils.Utils
from cogs.BaseCog import BaseCog
from utils import Logging, Questions, Utils, Configuration
from utils.Database import PremiumTier, PremiumTierMember, PremiumTierMemberInfo, PremiumTierRequirement


class Premium(BaseCog):

    def __init__(self, bot):
        super().__init__(bot)

        self.guild_reg_in_progress = dict()

        for guild in self.bot.guilds:
            self.init_guild(guild)
        # self.periodic_task.start()

    def cog_unload(self):
        # self.periodic_task.cancel()
        pass

    def init_guild(self, guild):
        # init guild-specific dicts and lists
        self.guild_reg_in_progress[guild.id] = set()
        pass

    @tasks.loop(seconds=60)
    async def periodic_task(self):
        # periodic task to run while cog is loaded
        pass

    async def cog_check(self, ctx):
        # command-specific override
        if ctx.command.name in ["register"]:
            return True
        # Minimum permission for all permissions commands: manage_server
        if ctx.guild:
            if ctx.author.guild_permissions.manage_guild:
                return True
            # for role in ctx.author.roles:
            #     if role.id in self.admin_roles[ctx.guild.id]:
            #         return True
        if await self.bot.permission_manage_bot(ctx):
            return True
        return False

    @commands.group(name="tier", aliases=["tiers"], invoke_without_command=True)
    @commands.guild_only()
    async def premium_tier(self, ctx):
        # list tiers
        tiers = []
        guild_row = await self.bot.get_guild_db_config(ctx.guild.id)
        for tier_row in await guild_row.premium_tiers:
            tier_role = ctx.guild.get_role(tier_row.roleid)
            tiers.append(f"{tier_role.name} ({tier_role.id})")
        if not tiers:
            await ctx.send("There are no tiers in this server.")
            return
        tier_list = "\n".join(tiers)
        await ctx.send(f"Tier roles in this server are:\n{tier_list}")

    @premium_tier.group(name="requirement", aliases=["req", "reqs", "requirements"], invoke_without_command=True)
    @commands.guild_only()
    async def requirement(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send_help(ctx.command)

    @requirement.command(aliases=["add"])
    @commands.guild_only()
    async def add_req(self, ctx, tier_role: Role, requirement_name, *, prompt):
        guild_row = await self.bot.get_guild_db_config(ctx.guild.id)
        tier_row = await PremiumTier.get(roleid=tier_role.id, guild=guild_row)
        clean_name = requirement_name.replace(r'[^A-Za-z0-9]', '')
        if clean_name:
            requirement, created = await PremiumTierRequirement.get_or_create(tier=tier_row, name=clean_name)
            requirement.prompt = prompt
            await requirement.save()
            await ctx.send(f"I {'created' if created else 'updated'} a requirement prompt for the `{tier_role.name}` tier. "
                           f"New members will be prompted for {clean_name} with this message:\n"
                           f"{requirement.prompt}")
            return
        await ctx.send(f"I couldn't create a requirement with that name. I can only accept alphanumeric characters")

    @requirement.command(aliases=["remove"])
    @commands.guild_only()
    async def remove_req(self, ctx, tier_role: Role, requirement_name):
        guild_row = await self.bot.get_guild_db_config(ctx.guild.id)
        tier_row = await PremiumTier.get(roleid=tier_role.id, guild=guild_row)
        clean_name = requirement_name.replace(r'[^A-Za-z0-9]', '')
        try:
            requirement = await PremiumTierRequirement.get(tier=tier_row, name=clean_name)
            await requirement.delete()
            await ctx.send(f"I deleted a requirement prompt for the `{tier_role.name}` tier. "
                           f"New members will no longer be prompted for {clean_name} with this message:\n"
                           f"{requirement.prompt}")
        except (OperationalError, MultipleObjectsReturned, DoesNotExist):
            await ctx.send(f"I couldn't delete a requirement with that name. I can only accept alphanumeric characters")

    async def get_guild_and_tier_rows(self, guild_id, tier_role_id):
        guild_row = self.bot.get_guild_db_config(guild_id)
        tier_row = await PremiumTier.get(roleid=tier_role_id, guild=guild_row)
        return guild_row, tier_row

    @requirement.command()
    @commands.guild_only()
    async def list(self, ctx, *, tier_role: Role):
        # list requiremetns
        guild_row = await self.bot.get_guild_db_config(ctx.guild.id)
        try:
            tier_row = await PremiumTier.get(roleid=tier_role.id, guild=guild_row)
        except DoesNotExist:
            await ctx.send("There are no tier for that role")
            return

        reqs = []
        for r in await tier_row.requirements:
            reqs.append(f"```{r.name}:```{r.prompt}")

        if not reqs:
            await ctx.send("There are no requirements in this tier.")
            return

        req_list = "\n".join(reqs)
        await ctx.send(f"Requirements for the `{tier_role.name}` tier are:\n{req_list}")

    async def get_tier_for_role(self, role: Role):
        guild_row = await self.bot.get_guild_db_config(role.guild.id)
        for tier_row in await guild_row.premium_tiers:
            if tier_row.roleid == role.id:
                return tier_row
        return None

    @premium_tier.command(invoke_without_command=True)
    @commands.guild_only()
    async def members(self, ctx, *, tier_role: Role):
        my_tier = await self.get_tier_for_role(tier_role)
        output = []

        if not my_tier:
            await ctx.send("No matching premium tier found in this server")
            return

        for tier_member in await my_tier.members:
            output.append(utils.Utils.get_member_log_name(ctx.guild.get_member(tier_member.userid)))

        if not output:
            await ctx.send(f"Tier **'{tier_role.name}'** has **no members**")
            return

        output = "\n".join(output)
        await ctx.send(f"Tier **'{tier_role.name}'** has members:\n{output}", allowed_mentions=AllowedMentions.none())

    @premium_tier.command(aliases=["memberinfo"], invoke_without_command=True)
    @commands.guild_only()
    async def members_info(self, ctx, *, tier_role: Role):
        my_tier = await self.get_tier_for_role(tier_role)
        output = []

        if not my_tier:
            await ctx.send("No matching premium tier found in this server")
            return

        for tier_member in await my_tier.members:
            output.append(utils.Utils.get_member_log_name(ctx.guild.get_member(tier_member.userid)))
            for req in await my_tier.requirements:
                line = f"\t__{req.name}:__ "
                info = await PremiumTierMemberInfo.get_or_none(requirementid=req.id, member=tier_member)
                if info is None:
                    line += "------"
                else:
                    line += info.value
                output.append(line)

        if not output:
            await ctx.send(f"Tier **'{tier_role.name}'** has **no members**")
            return

        output = "\n".join(output)
        await ctx.send(f"Tier **'{tier_role.name}'** has the following member info recorded:\n"
                       f"{output}",
                       allowed_mentions=AllowedMentions.none())

    @premium_tier.command(invoke_without_command=True)
    @commands.guild_only()
    async def export(self, ctx, *, tier_role: Role):
        my_tier = await self.get_tier_for_role(tier_role)
        data = []

        if not my_tier:
            await ctx.send("No matching premium tier found in this server")
            return

        fields = ["member"]
        for req in await my_tier.requirements:
            fields.append(req.name)

        for tier_member in await my_tier.members:
            info_object = {"member": utils.Utils.get_member_log_name(ctx.guild.get_member(tier_member.userid))}

            for req in await my_tier.requirements:
                info = await PremiumTierMemberInfo.get_or_none(requirementid=req.id, member=tier_member)
                if info is None:
                    info_object[req.name] = "--"
                else:
                    info_object[req.name] = info.value
            data.append(info_object)

        if not data:
            await ctx.send(f"Tier **'{tier_role.name}'** has **no members**")
            return

        # create CSV in buffer and send
        with io.StringIO() as buffer:
            now = datetime.today().isoformat()
            filename = f"TierMembers_{slugify(tier_role.name)}_{slugify(now)}.csv"
            Utils.save_to_buffer(buffer, data, 'csv', fields)
            buffer.seek(0)
            await ctx.send(f"Tier **'{tier_role.name}'** member info export file", file=discord.File(buffer, filename))

    @premium_tier.command()
    @commands.guild_only()
    async def add(self, ctx, *, role: Role):
        # check for existing tier. if not, add role as tier
        guild_row = await self.bot.get_guild_db_config(ctx.guild.id)
        tier_row, created = await PremiumTier.get_or_create(roleid=role.id, guild=guild_row)
        if created:
            await ctx.send(f"ok, '{role.mention}' is now recognized as a premium tier", allowed_mentions=AllowedMentions.none())
        else:
            await ctx.send(f"A premium tier already exists for that role.")

    @premium_tier.command()
    @commands.guild_only()
    async def remove(self, ctx, *, role: Role):
        # check for existing tier and remove.
        try:
            existing = await PremiumTier.get(roleid=role.id)
            await existing.delete()
            await ctx.send(f"ok, '{role.mention}' is no longer recognized as a premium tier",
                           allowed_mentions=AllowedMentions.none())
        except DoesNotExist:
            await ctx.send(f"No premium tier exists for that role.")
        except OperationalError:
            await ctx.send(f"Failed to delete tier for role `{role.name}`")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.init_guild(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # delete guild-specific dicts and lists, remove persistent vars, clean db
        del self.guild_reg_in_progress[guild.id]
        pass

    @commands.command()
    @commands.dm_only()
    async def register(self, ctx):
        tier_count = 0

        for guild in self.bot.guilds:
            if ctx.author.id in self.guild_reg_in_progress[guild.id]:
                await ctx.send("You already have a tier registration in progress. "
                               "Complete that first, or try again later")
                return

            if member := guild.get_member(ctx.author.id):
                guild_row = await self.bot.get_guild_db_config(ctx.guild.id)
                for tier_row in await guild_row.premium_tiers:
                    tier_role = guild.get_role(tier_row.roleid)
                    if tier_role in member.roles:
                        await self.welcome_tier_member(member, tier_row, tier_role)
                        tier_count += 1

        if not tier_count:
            await ctx.send(
                "You don't appear to be a member of any premium tiers. If you have paid for premium access "
                "and believe this message is in error, please contact a staff member")

    async def welcome_tier_member(self, member, tier: PremiumTier, role: Role):
        try:
            requirements = await tier.requirements  # PremiumTier.get(id=tier.id)
        except (OperationalError, NoValuesFetched):
            await self.bot.guild_log(member.guild.id, f"No role requirements for `{role.name}` tier. Nothing recorded "
                                                      f"for new member {Utils.get_member_log_name(member)}")
            return

        channel = None
        restarting = False
        try:
            def offset_validator(o):
                if not re.match(r'GMT|UTC ?[+-] ? \d{1,2}]', o):
                    return "Please specify timezone offset as GMT or UTC offset. "\
                           "For example, US Mountain Standard Time is `UTC-7`"
                return True

            def email_validator(input_email):
                is_valid = validate_email(
                    email_address=input_email,
                    check_format=True,
                    check_blacklist=True,
                    check_dns=True,
                    dns_timeout=10,
                    check_smtp=False,
                    smtp_timeout=10,
                    smtp_from_address=None,
                    smtp_helo_host=None,
                    smtp_skip_tls=True,
                    smtp_tls_context=None,
                    smtp_debug=False)
                if not is_valid:
                    return "it appears that email address is not valid. please try again."
                return True

            def timezone_validator(tz):
                server_zone = pytz.timezone("America/Denver")
                try:
                    tz = pytz.timezone(tz)
                    return True
                except UnknownTimeZoneError as e:
                    return f"I couldn't find a timezone called '{tz}.'\n" \
                           f"Maybe you can find your timezone in this list\n" \
                           f"<https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568>"

            async def restart():
                nonlocal restarting
                restarting = True
                self.bot.loop.create_task(self.welcome_tier_member(member, tier, role))

            async def complete_registration():
                await channel.send("Thank you, that's all the information we need.")
                pass

            channel = await member.create_dm()
            msg = f"Hi and welcome to the `{role.name}` premium tier, and thank you for your support!!\n" \
                  "I'm a bot that gathers information to help Art Prof staff make sure they can fulfil your " \
                  "membership rewards. "
            await channel.send(msg)
            self.guild_reg_in_progress[role.guild.id].add(member.id)

            for requirement in await tier.requirements:
                msg = requirement.prompt
                validator_name = f"{requirement.name}_validator"
                validator = None
                if validator_name in locals() and callable(tmp := locals()[validator_name]):
                    validator = tmp

                guild_row = await self.bot.get_guild_db_config(member.guild.id)
                tier_member = await PremiumTierMember.get(userid=member.id, tier=tier)
                this_info, created = await PremiumTierMemberInfo.get_or_create(
                    requirementid=requirement.id,
                    member=tier_member
                )

                skip = False
                if not created:
                    def confirmed():
                        nonlocal skip
                        skip = True
                    previous_answer = this_info.value
                    review_msg = f"{msg}\n**You've answered this question before and this was your answer:**\n" \
                                 f"{previous_answer}\nWould you like to keep that answer? React **yes** to keep it, " \
                                 f"or **no** to update your answer"
                    await Questions.ask(
                        self.bot,
                        channel,
                        member,
                        review_msg,
                        [Questions.Option("YES", handler=confirmed), Questions.Option("NO")],
                        timeout=240
                    )

                    if skip:
                        continue

                answer = await Questions.ask_text(
                    self.bot,
                    channel,
                    member,
                    msg,
                    validator=validator,
                    escape=False,
                    confirm=True,
                    timeout=900
                )

                this_info.value = answer
                await this_info.save()

            # msg = "Please tell me your physical mailing address:"
            # msg = "Please tell me your timezone offset (for example, UTC-7. google can help you find this):"

            if len(tier.requirements) > 1:
                msg = "```Does all the information you provided look correct?```\n"
                tier_member = await PremiumTierMember.get(userid=member.id, tier=tier)
                output_list = []

                for r in await tier.requirements:
                    output = f"__**{r.name}:**__ "
                    this_info = await PremiumTierMemberInfo.get(member=tier_member, requirementid=r.id)
                    output += this_info.value
                    output_list.append(output)

                msg += "\n".join(output_list)

                await Questions.ask(
                    self.bot, channel, member, msg,
                    [
                        Questions.Option("YES", "Yes, it looks right", complete_registration),
                        Questions.Option("NO", "No, I made a mistake", restart)
                    ], show_embed=True, timeout=300)

                if restarting:
                    return
            else:
                await complete_registration()

        except Forbidden as ex:
            prefix = Configuration.get_var("bot_prefix")
            requirement_names = "\n            ".join([f"__**{i.name}**__" for i in requirements])
            msg = f"""
            __**Unable to send DM**__ to new `{role.name}` tier member {member.mention}.
            Ask them to open DMs and use the command `{prefix}register` in ArtBot's DMs, 
            or provide the following required info directly to you via DM:
            {requirement_names}
            """
            await self.bot.guild_log(member.guild.id, msg)

        except asyncio.TimeoutError as ex:
            prefix = Configuration.get_var("bot_prefix")
            if channel:
                await channel.send(
                    f"You may register the required information at a later time by using the command "
                    f"`{prefix}register` right here in my DMs! If you don't provide the required information, "
                    f"some of your premium benefits may not be fulfilled on time."
                )

            requirement_names = "\n            ".join([f"__**{i.name}**__" for i in requirements])
            msg = f"""
            `{role.name}` __**tier registration timed out**__ for {member.mention}.
            Ask them to open DMs and use the command `{prefix}register` in ArtBot's DMs, 
            or provide the following required info directly to you via DM:
            {requirement_names}
            """
            await self.bot.guild_log( member.guild.id, msg)

        except DoesNotExist:
            if channel:
                await channel.send("I ran into some trouble completing your registration. "
                                   "Please contact a staff member for assistance.")

            prefix = Configuration.get_var("bot_prefix")
            await self.bot.guild_log(
                member.guild.id,
                f"`{role.name}` tier registration failed for {member.mention}"
            )
        finally:
            self.guild_reg_in_progress[role.guild.id].remove(member.id)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        tiers = []
        guild_row = await self.bot.get_guild_db_config(after.guild.id)
        for row in await guild_row.premium_tiers:
            tiers.append(row)
            tier_role = after.guild.get_role(row.roleid)
            if tier_role not in before.roles and tier_role in after.roles:
                tier_member, created = await PremiumTierMember.get_or_create(userid=after.id, tier=row.id)
                msg = f"added member {Utils.get_member_log_name(after)} to tier {tier_role.name}"
                await self.bot.guild_log(after.guild.id, msg)
                Logging.info(msg)
                await self.welcome_tier_member(after, row, tier_role)
                return

            if tier_role in before.roles and tier_role not in after.roles:
                tier_member = await PremiumTierMember.get_or_none(userid=after.id, tier=row.id)
                if tier_member:
                    await tier_member.delete()
                    msg = f"removed member {Utils.get_member_log_name(after)} from tier {tier_role.name}"
                    await self.bot.guild_log(after.guild.id, msg)
                    Logging.info(msg)
                return

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # do something with messages
        pass


async def setup(bot):
    await bot.add_cog(Premium(bot))
