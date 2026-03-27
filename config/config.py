from config.settings import *

if ENV == "PROD":
    BASE_URL = SIFODS_URL_PROD
    TOKEN = SIFODS_TOKEN_PROD
else:
    BASE_URL = SIFODS_URL_DEV
    TOKEN = SIFODS_TOKEN_DEV