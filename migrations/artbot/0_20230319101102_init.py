from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `artchannel` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `serverid` BIGINT NOT NULL,
    `listenchannelid` BIGINT NOT NULL  DEFAULT 0,
    `collectionchannelid` BIGINT NOT NULL  DEFAULT 0,
    `tag` VARCHAR(30) NOT NULL  DEFAULT '',
    UNIQUE KEY `uid_artchannel_serveri_dacf81` (`serverid`, `listenchannelid`, `collectionchannelid`, `tag`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `autoresponder` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `serverid` BIGINT NOT NULL,
    `trigger` VARCHAR(300) NOT NULL,
    `response` VARCHAR(2000) NOT NULL,
    `flags` SMALLINT NOT NULL  DEFAULT 0,
    `chance` SMALLINT NOT NULL  DEFAULT 10000,
    `responsechannelid` BIGINT NOT NULL  DEFAULT 0,
    `listenchannelid` BIGINT NOT NULL  DEFAULT 0,
    `logchannelid` BIGINT NOT NULL  DEFAULT 0,
    UNIQUE KEY `uid_autorespond_trigger_d7d834` (`trigger`, `serverid`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `botadmin` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `userid` BIGINT NOT NULL UNIQUE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `configchannel` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `serverid` BIGINT NOT NULL,
    `configname` VARCHAR(100) NOT NULL,
    `channelid` BIGINT NOT NULL  DEFAULT 0,
    UNIQUE KEY `uid_configchann_confign_21c1ab` (`configname`, `serverid`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `countword` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `serverid` BIGINT NOT NULL,
    `word` VARCHAR(300) NOT NULL,
    UNIQUE KEY `uid_countword_word_931444` (`word`, `serverid`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `customcommand` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `serverid` BIGINT NOT NULL,
    `trigger` VARCHAR(20) NOT NULL,
    `response` VARCHAR(2000) NOT NULL,
    `deletetrigger` BOOL NOT NULL  DEFAULT 0,
    `reply` BOOL NOT NULL  DEFAULT 0,
    UNIQUE KEY `uid_customcomma_trigger_65c25c` (`trigger`, `serverid`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `dropboxchannel` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `serverid` BIGINT NOT NULL,
    `sourcechannelid` BIGINT NOT NULL,
    `targetchannelid` BIGINT NOT NULL  DEFAULT 0,
    `deletedelayms` SMALLINT NOT NULL  DEFAULT 0,
    `sendreceipt` BOOL NOT NULL  DEFAULT 0,
    UNIQUE KEY `uid_dropboxchan_serveri_7254d9` (`serverid`, `sourcechannelid`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `guild` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `serverid` BIGINT NOT NULL UNIQUE,
    `memberrole` BIGINT NOT NULL  DEFAULT 0,
    `nonmemberrole` BIGINT NOT NULL  DEFAULT 0,
    `mutedrole` BIGINT NOT NULL  DEFAULT 0,
    `welcomechannelid` BIGINT NOT NULL  DEFAULT 0,
    `ruleschannelid` BIGINT NOT NULL  DEFAULT 0,
    `logchannelid` BIGINT NOT NULL  DEFAULT 0,
    `entrychannelid` BIGINT NOT NULL  DEFAULT 0,
    `rulesreactmessageid` BIGINT NOT NULL  DEFAULT 0,
    `defaultlocale` VARCHAR(10) NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `adminrole` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `roleid` BIGINT NOT NULL,
    `guild_id` INT NOT NULL,
    UNIQUE KEY `uid_adminrole_roleid_457f6b` (`roleid`, `guild_id`),
    CONSTRAINT `fk_adminrol_guild_56368cba` FOREIGN KEY (`guild_id`) REFERENCES `guild` (`id`) ON DELETE CASCADE,
    KEY `idx_adminrole_guild_i_1576b8` (`guild_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `localization` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `channelid` BIGINT NOT NULL  DEFAULT 0,
    `locale` VARCHAR(10) NOT NULL  DEFAULT '',
    `guild_id` INT NOT NULL,
    UNIQUE KEY `uid_localizatio_guild_i_1e041d` (`guild_id`, `channelid`),
    CONSTRAINT `fk_localiza_guild_9f755aae` FOREIGN KEY (`guild_id`) REFERENCES `guild` (`id`) ON DELETE CASCADE,
    KEY `idx_localizatio_guild_i_2a3780` (`guild_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `modrole` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `roleid` BIGINT NOT NULL,
    `guild_id` INT NOT NULL,
    UNIQUE KEY `uid_modrole_roleid_b1b1c0` (`roleid`, `guild_id`),
    CONSTRAINT `fk_modrole_guild_62488d68` FOREIGN KEY (`guild_id`) REFERENCES `guild` (`id`) ON DELETE CASCADE,
    KEY `idx_modrole_guild_i_cc7b59` (`guild_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `premiumtier` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `roleid` BIGINT NOT NULL,
    `guild_id` INT NOT NULL,
    UNIQUE KEY `uid_premiumtier_guild_i_a70ac3` (`guild_id`, `roleid`),
    CONSTRAINT `fk_premiumt_guild_837e09ee` FOREIGN KEY (`guild_id`) REFERENCES `guild` (`id`) ON DELETE CASCADE,
    KEY `idx_premiumtier_guild_i_fccc23` (`guild_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `premiumtiermember` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `userid` BIGINT NOT NULL,
    `tier_id` INT NOT NULL,
    CONSTRAINT `fk_premiumt_premiumt_88d18cb9` FOREIGN KEY (`tier_id`) REFERENCES `premiumtier` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `premiumtiermemberinfo` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `requirementid` BIGINT NOT NULL,
    `value` VARCHAR(500) NOT NULL,
    `member_id` INT NOT NULL,
    CONSTRAINT `fk_premiumt_premiumt_b72570c3` FOREIGN KEY (`member_id`) REFERENCES `premiumtiermember` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `premiumtierrequirement` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,
    `prompt` VARCHAR(500) NOT NULL,
    `tier_id` INT NOT NULL,
    CONSTRAINT `fk_premiumt_premiumt_cff8c276` FOREIGN KEY (`tier_id`) REFERENCES `premiumtier` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `reactwatch` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `serverid` BIGINT NOT NULL UNIQUE,
    `muteduration` SMALLINT NOT NULL  DEFAULT 600,
    `watchremoves` BOOL NOT NULL  DEFAULT 0
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `trustedrole` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `roleid` BIGINT NOT NULL,
    `guild_id` INT NOT NULL,
    UNIQUE KEY `uid_trustedrole_roleid_215f34` (`roleid`, `guild_id`),
    CONSTRAINT `fk_trustedr_guild_7af9759e` FOREIGN KEY (`guild_id`) REFERENCES `guild` (`id`) ON DELETE CASCADE,
    KEY `idx_trustedrole_guild_i_deb2b1` (`guild_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `userpermission` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `userid` BIGINT NOT NULL,
    `command` VARCHAR(200) NOT NULL  DEFAULT '',
    `allow` BOOL NOT NULL  DEFAULT 1,
    `guild_id` INT NOT NULL,
    UNIQUE KEY `uid_userpermiss_userid_7b40ae` (`userid`, `command`),
    CONSTRAINT `fk_userperm_guild_24ce9edd` FOREIGN KEY (`guild_id`) REFERENCES `guild` (`id`) ON DELETE CASCADE,
    KEY `idx_userpermiss_guild_i_3a0dc1` (`guild_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `watchedemoji` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `emoji` VARCHAR(50) NOT NULL,
    `log` BOOL NOT NULL  DEFAULT 0,
    `remove` BOOL NOT NULL  DEFAULT 0,
    `mute` BOOL NOT NULL  DEFAULT 0,
    `watcher_id` INT NOT NULL,
    UNIQUE KEY `uid_watchedemoj_emoji_4203dc` (`emoji`, `watcher_id`),
    CONSTRAINT `fk_watchede_reactwat_b8aaa411` FOREIGN KEY (`watcher_id`) REFERENCES `reactwatch` (`id`) ON DELETE CASCADE,
    KEY `idx_watchedemoj_watcher_a04b30` (`watcher_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
