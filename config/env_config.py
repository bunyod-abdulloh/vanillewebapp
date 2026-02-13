from environs import Env

env = Env()
env.read_env()

# BOT
ADMINS = env.list("ADMINS")
BOT_TOKEN = env.str("BOT_TOKEN")
ADMIN_GROUP = env.str("ADMIN_GROUP")
