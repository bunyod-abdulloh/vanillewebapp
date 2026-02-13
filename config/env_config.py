from environs import Env

env = Env()
env.read_env()

# BOT
ADMINS = env.list("ADMINS")
BOT_TOKEN = env.str("BOT_TOKEN")
ADMIN_GROUP = env.str("ADMIN_GROUP")

# DJANGO
DJ_SECRET_KEY = env.str("SECRET_KEY")
DJ_ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
DJ_DEBUG = env.bool("DEBUG")
CSRF_TRUSTED = env.list("CSRF_TRUSTED")

# DATABASE
DB_NAME = env.str("DB_NAME")
DB_USER = env.str("DB_USER")
DB_PASSWORD = env.str("DB_PASSWORD")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.str("DB_PORT")
