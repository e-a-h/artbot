# ArtBot
Art [Bot] for artprof.org discord

## Deployment Checklist
1. Create channels for:
   * Entry
   * Rules
   * Welcome
1. Create member role
1. Create rules message and add **:candle:** reaction
1. Channel permissions:
   * Rules and welcome should be
     * **@everone:** - +read, -send, -add reaction
     * **bot:** +add reaction
   * Any members-only channel should be
     * **@everyone:** -read
     * **members:** +read
1. Config file required. see config.example.json and fill in channel IDs, guild ID, role IDs, SQL creds
1. Issue some bot commands once the bot is up and running
   * `?chanconf set log_channel 000000000000000000`
   * `?chanconf set welcome_channel 000000000000000000`
   * `?chanconf set entry_channel 000000000000000000`
   * `?chanconf set rules_channel 000000000000000000`
   * `?set_rules_message 000000000000000000`