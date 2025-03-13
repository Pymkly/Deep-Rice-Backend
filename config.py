import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.ini')

# Using INI configuration file
from configparser import ConfigParser

config = ConfigParser()
config.read(CONFIG_PATH)
DB_PATH = str(config.get("PATHS", "DB_PATH"))
MODEL_PATH = str(config.get("PATHS", "MODEL_PATH"))
RICE_RAG_PATH = str(config.get("PATHS", "RICE_RAG_PATH"))


RANDOM_STATE = int(config.get("ML", "RANDOM_STATE"))
TARGET_NAME = str(config.get("ML", "TARGET_NAME"))

HOST = str(config.get("POSTGRESQL", "HOST"))
DATABASE = str(config.get("POSTGRESQL", "DATABASE"))
USER = str(config.get("POSTGRESQL", "USER"))
PASSWORD = str(config.get("POSTGRESQL", "PASSWORD"))

MONGODB_DATABASE = str(config.get("MONGODB", "DATABASE"))


PROMPT_TEMPLATE = str(config.get("QUERY", "PROMPT_TEMPLATE"))
RICE_PDF_TEMPLATE = str(config.get("RICE_TEMPLATE", "PDF_TEMPLATE"))
RICE_CSV_TEMPLATE = str(config.get("RICE_TEMPLATE", "CSV_TEMPLATE"))
RICE_IMAGE_TEMPLATE = str(config.get("RICE_TEMPLATE", "IMAGE_TEMPLATE"))

PDF_EXTENSION = str(config.get("DATA_EXTENSION", "PDF_EXTENSION"))
CSV_EXTENSION = str(config.get("DATA_EXTENSION", "CSV_EXTENSION"))
IMAGE_EXTENSION = str(config.get("DATA_EXTENSION", "IMAGE_EXTENSION"))

