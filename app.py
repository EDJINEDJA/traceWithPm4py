from configparser import ConfigParser

from src.utils import utils

ENVVAR = ConfigParser()
ENVVAR.read("./config/config.ini")


parser = utils.Preprocessor(
    ENVVAR.get("PATH", "rawPath"),
    ENVVAR.get("PATH", "finalPath"),
    "DATETIMEEVENTS.csv",
    "essai.csv",
)
parser.traceScraper()
