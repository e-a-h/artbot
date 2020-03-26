from __future__ import absolute_import
import prometheus_client as prom


class PrometheusMon:
    def __init__(self, bot) -> None:
        self.command_counter = prom.Counter("artbot_command_counter", "Number of commands run", ["command_name"])
        self.word_counter = prom.Counter("artbot_word_counter", "Count of occurrences of words in chat", ["word"])

        self.guild_messages = prom.Counter("artbot_guild_messages", "What messages have been sent and by who", [
            "guild_id"
        ])

        self.user_message_raw_count = prom.Counter("artbot_user_message_raw_count",
                                                   "Raw count of member messages")
        self.bot_message_raw_count = prom.Counter("artbot_bot_message_raw_count",
                                                  "Raw count of bot messages")
        self.own_message_raw_count = prom.Counter("artbot_own_message_raw_count",
                                                  "Raw count of ArtBot messages")

        self.bot_guilds = prom.Gauge("artbot_guilds", "How many guilds the bot is in")
        self.bot_guilds.set_function(lambda: len(bot.guilds))

        self.bot_users = prom.Gauge("artbot_users", "How many users the bot can see")
        self.bot_users.set_function(lambda: sum(len(g.members) for g in bot.guilds))

        self.bot_users_unique = prom.Gauge("artbot_users_unique", "How many unique users the bot can see")
        self.bot_users_unique.set_function(lambda: len(bot.users))

        # self.bot_event_counts = prom.Counter("artbot_bot_event_counts", "Counts for each event", ["event_name"])

        self.bot_latency = prom.Gauge("artbot_latency", "Current bot latency")
        self.bot_latency.set_function(lambda: bot.latency)

        # self.reports_completed = prom.Counter("artbot_", "")  # already handled by mysql report count
        self.bot_cannot_dm_member = prom.Counter("artbot_bot_cannot_dm_member", "Bot tried and failed to send DM to member")
        self.auto_responder_count = prom.Counter("artbot_autor_responder_count",
                                                 "Auto-responder total triggers")
        self.auto_responder_mod_pass = prom.Counter("artbot_auto_responder_mod_pass",
                                                    "Auto-responder - mod action: pass")
        self.auto_responder_mod_manual = prom.Counter("artbot_auto_responder_mod_manual",
                                                      "Auto-responder - mod action: manual intervention")
        self.auto_responder_mod_auto = prom.Counter("artbot_auto_responder_mod_auto",
                                                    "Auto-responder - mod action: auto-respond")
        self.auto_responder_mod_delete_trigger = prom.Counter("artbot_auto_responder_mod_delete_trigger",
                                                              "Auto-responder - mod action: delete trigger")

        bot.metrics_reg.register(self.command_counter)
        bot.metrics_reg.register(self.word_counter)
        bot.metrics_reg.register(self.guild_messages)
        bot.metrics_reg.register(self.user_message_raw_count)
        bot.metrics_reg.register(self.bot_message_raw_count)
        bot.metrics_reg.register(self.own_message_raw_count)
        bot.metrics_reg.register(self.bot_guilds)
        bot.metrics_reg.register(self.bot_users)
        bot.metrics_reg.register(self.bot_users_unique)
        bot.metrics_reg.register(self.bot_latency)
        # bot.metrics_reg.register(self.bot_event_counts)

        bot.metrics_reg.register(self.bot_cannot_dm_member)
        bot.metrics_reg.register(self.auto_responder_count)
        bot.metrics_reg.register(self.auto_responder_mod_pass)
        bot.metrics_reg.register(self.auto_responder_mod_manual)
        bot.metrics_reg.register(self.auto_responder_mod_auto)
        bot.metrics_reg.register(self.auto_responder_mod_delete_trigger)
