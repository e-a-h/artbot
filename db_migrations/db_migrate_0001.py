from playhouse.migrate import *
from utils import Configuration

connection = MySQLDatabase(Configuration.get_var("DATABASE_NAME"),
                           user=Configuration.get_var("DATABASE_USER"),
                           password=Configuration.get_var("DATABASE_PASS"),
                           host=Configuration.get_var("DATABASE_HOST"),
                           port=Configuration.get_var("DATABASE_PORT"),
                           use_unicode=True,
                           charset="utf8mb4")

migrator = MySQLMigrator(connection)
reply = BooleanField(default=False)
new_boolean_false = BooleanField(default=False)
new_react_field = SmallIntegerField(default=600)

# Run the migration, specifying the database table, field name and field.
migrate(
    migrator.drop_column('reactwatch', 'logtochannel'),
    migrator.drop_column('reactwatch', 'watchlist'),
    migrator.drop_column('reactwatch', 'banlist'),
    migrator.drop_column('reactwatch', 'mutebanned'),
    migrator.add_column('customcommand', 'deletetrigger', new_boolean_false),
    migrator.add_column('customcommand', 'reply', reply),
    migrator.add_column('reactwatch', 'muteduration', new_react_field)
)
