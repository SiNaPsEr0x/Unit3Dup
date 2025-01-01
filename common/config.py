# -*- coding: utf-8 -*-

import os
from common.custom_console import custom_console
from pydantic_settings import BaseSettings
from pydantic import model_validator
from dotenv import load_dotenv
from urllib.parse import urlparse
from pathlib import Path

service_filename = "Unit3Dbot_service.env"

def create_default_env_file(path: Path):
    """
    Creates a default configuration file if it doesn't already exist
    """
    default_content = """
################################################## CONFIG ###################################################
# TRACKER
ITT_URL=https://itatorrents.xyz
ITT_APIKEY=

# TMDB
TMDB_APIKEY=

# IMAGE UPLOADERS
IMGBB_KEY=
FREE_IMAGE_KEY=
LENSDUMP_KEY=

# QBITTORRENT CLIENT
QBIT_USER=
QBIT_PASS=
QBIT_URL=http://localhost
QBIT_PORT=8080

############################################## USER PREFERENCES ##############################################
# Image uploader priority. 0=first in list
IMGBB_PRIORITY=0
FREE_IMAGE_PRIORITY=1
LENSDUMP_PRIORITY=2

# Search for possible candidates for duplicate files
# True = enabled ; False = disabled
DUPLICATE_ON=False

# Number of screenshots we create
NUMBER_OF_SCREENSHOTS=4

# Level of compression for screenshot (quality) 0 = Best quality
COMPRESS_SCSHOT=4

# Resize image before sending to image hosting 
# True = Resize ; False = No resize
RESIZE_SCSHOT=False

# Path for each torrent file created
TORRENT_ARCHIVE=.

# Torrent file comment (max 100 chars)
TORRENT_COMMENT=no_comment

# Preferred language. Discard videos with a language different from preferred_lang (default=all)
PREFERRED_LANG=all

# Discard videos whose size deviates by more than the specified percentage (size_th) from the video in tracker
SIZE_TH=100

#########################################
################  OPTIONAL  #############  
#########################################
# PW
PW_API_KEY=no_key
PW_URL=http://localhost:9696/api/v1

# FTPX 
FTPX_USER=user
FTPX_PASS=pass
FTPX_IP=127.0.0.1
FTPX_PORT=2121
FTPX_LOCAL_PATH=.
FTPX_ROOT=.
FTPX_KEEP_ALIVE=False

# IGDB
IGDB_CLIENT_ID=client_id
IGDB_ID_SECRET=secret
    """
    with open(path, "w") as f:
        f.write(default_content.strip())


def check_env_variables(path: Path):
    """
       Checks if all required environment variables are present in the configuration file
       If any are missing it adds them with empty values

       Parameters:
       - path (Path): The path to the configuration file to be checked

       """
    required_vars = [
        "ITT_URL",
        "ITT_APIKEY",
        "TMDB_APIKEY",
        "IMGBB_KEY",
        "FREE_IMAGE_KEY",
        "LENSDUMP_KEY",
        "PW_API_KEY",
        "PW_URL",
        "FTPX_USER",
        "FTPX_PASS",
        "FTPX_IP",
        "FTPX_PORT",
        "IGDB_CLIENT_ID",
        "IGDB_ID_SECRET",
        "QBIT_USER",
        "QBIT_PASS",
        "QBIT_URL",
        "QBIT_PORT",
        "IMGBB_PRIORITY",
        "FREE_IMAGE_PRIORITY",
        "LENSDUMP_PRIORITY",
        "DUPLICATE_ON",
        "NUMBER_OF_SCREENSHOTS",
        "COMPRESS_SCSHOT",
        "RESIZE_SCSHOT",
        "TORRENT_ARCHIVE",
        "TORRENT_COMMENT",
        "PREFERRED_LANG",
        "SIZE_TH",
        "FTPX_LOCAL_PATH",
        "FTPX_ROOT",
        "FTPX_KEEP_ALIVE",
    ]

    custom_console.panel_message("Checking configuration file...")
    with open(path, "r+") as f:
        file = f.read()
        for option in required_vars:
            if option not in file:
                f.write(f"{option}=\n")
                custom_console.bot_log(f"New Option Added ! * {option} *")
    print()

class Config(BaseSettings):
    """
    Class to manage the configuration and validation of environment vvariables
    """

    ITT_URL: str = "https://itatorrents.xyz"
    ITT_APIKEY: str | None = None

    TMDB_APIKEY: str | None = None
    IMGBB_KEY: str | None = None
    FREE_IMAGE_KEY: str | None = None
    LENSDUMP_KEY: str | None = None

    PW_API_KEY: str | None = None
    PW_URL: str = "http://localhost:9696/api/v1"
    FTPX_USER: str | None = None
    FTPX_PASS: str | None = None
    FTPX_IP: str | None = None
    FTPX_PORT: str = "2121"
    IGDB_CLIENT_ID: str | None = None
    IGDB_ID_SECRET: str | None = None

    QBIT_USER: str | None = None
    QBIT_PASS: str | None = None
    QBIT_URL: str = "http://127.0.0.1"
    QBIT_PORT: str = "8080"

    IMGBB_PRIORITY: int = 0
    FREE_IMAGE_PRIORITY: int = 1
    LENSDUMP_PRIORITY: int = 2

    DUPLICATE_ON: bool = False
    NUMBER_OF_SCREENSHOTS: int = 6
    COMPRESS_SCSHOT: int = 4
    RESIZE_SCSHOT: bool = False

    TORRENT_ARCHIVE: str | None = None
    TORRENT_COMMENT: str | None = None
    PREFERRED_LANG: str | None = None
    SIZE_TH: int = 100

    FTPX_LOCAL_PATH: str | None = None
    FTPX_ROOT: str = "."
    FTPX_KEEP_ALIVE: bool = False

    @model_validator(mode='before')
    def validate_fields(cls, values: dict) -> dict:
        """
        Validates
        """
        def validate_boolean(value: bool | str, field_name: str, default_value: bool) -> bool:
            """
            Validates boolean
            """
            if isinstance(value, str):
                normalized_value = value.strip().lower()
                if normalized_value in {"true", "1", "yes"}:
                    return True
                elif normalized_value in {"false", "0", "no"}:
                    return False
            custom_console.bot_error_log(
                f"-> not configured {field_name} '{value}' Using default: {default_value}"
            )
            return default_value

        def validate_int(value: int | str, field_name: str, default_value: int) -> int:
            """
            Validates integer
            """
            try:
                return int(value)
            except (ValueError, TypeError):
                custom_console.bot_error_log(
                    f"-> not configured {field_name} '{value}' Using default: {default_value}"
                )
                return default_value

        def validate_str(value: str | None, field_name: str, default_value: str | None) -> str | None:
            """
            Validates strinng
            """
            if isinstance(value, str) and value.strip():
                return value
            custom_console.bot_error_log(
                f"-> not configured {field_name} '{value}'"
            )
            return default_value

        def validate_url(value: str, field_name: str, default_value: str) -> str:
            """
            Validates URL
            """
            if not value:
                return default_value
            parsed_url = urlparse(value)
            if not (parsed_url.scheme and parsed_url.netloc):
                custom_console.bot_error_log(
                    f"->  Invalid URL value for {field_name} '{value}' Using default: {default_value}"
                )
                return default_value
            return value


        def validate_torrent_archive_path(value: str | None, field_name: str, default_value: str | None) -> str | None:
            """
            Validates path
            """
            if value is None or not isinstance(value, str) or not value.strip():
                return default_value
            path = Path(value).expanduser()
            if path.is_dir():
                return str(path)
            custom_console.bot_error_log(
                f"-> Invalid path for {field_name} '{value}' Using default: {default_value}"
            )
            return default_value

        #// Mandatory
        values["ITT_URL"] = validate_url(values.get("ITT_URL", "https://itatorrents.xyz"), "ITT_URL", "https://itatorrents.xyz")
        values["PW_URL"] = validate_url(values.get("PW_URL", "http://localhost:9696/api/v1"), "PW_URL", "http://localhost:9696/api/v1")
        values["QBIT_URL"] = validate_url(values.get("QBIT_URL", "http://127.0.0.1"), "QBIT_URL", "http://127.0.0.1")
        values["QBIT_USER"] = validate_str(values.get("QBIT_USER", None), "QBIT_USER", None)
        values["QBIT_PASS"] = validate_str(values.get("QBIT_PASS", None), "QBIT_PASS", None)
        values["QBIT_URL"] = validate_url(values.get("QBIT_URL", "http://127.0.0.1"), "QBIT_URL", "http://127.0.0.1")
        values["QBIT_PORT"] = validate_str(values.get("QBIT_PORT", "8080"), "QBIT_PORT", "8080")
        values["ITT_APIKEY"] = validate_str(values.get("ITT_APIKEY", None), "ITT_APIKEY", None)
        values["TMDB_APIKEY"] = validate_str(values.get("TMDB_APIKEY", None), "TMDB_APIKEY", None)
        values["IMGBB_KEY"] = validate_str(values.get("IMGBB_KEY", None), "IMGBB_KEY", None)
        values["FREE_IMAGE_KEY"] = validate_str(values.get("FREE_IMAGE_KEY", None), "FREE_IMAGE_KEY", None)
        values["LENSDUMP_KEY"] = validate_str(values.get("LENSDUMP_KEY", None), "LENSDUMP_KEY", None)

        #// Preferences
        values["DUPLICATE_ON"] = validate_boolean(values.get("DUPLICATE_ON", False), "DUPLICATE_ON", False)
        values["NUMBER_OF_SCREENSHOTS"] = validate_int(values.get("NUMBER_OF_SCREENSHOTS", 6), "NUMBER_OF_SCREENSHOTS", 6)
        values["COMPRESS_SCSHOT"] = validate_int(values.get("COMPRESS_SCSHOT", 4), "COMPRESS_SCSHOT", 4)
        values["RESIZE_SCSHOT"] = validate_boolean(values.get("RESIZE_SCSHOT", False), "RESIZE_SCSHOT", False)
        values["PREFERRED_LANG"] = validate_str(values.get("PREFERRED_LANG", None), "PREFERRED_LANG", "all")
        values["SIZE_TH"] = validate_int(values.get("SIZE_TH", 100), "SIZE_TH", 100)
        values["TORRENT_COMMENT"] = validate_str(values.get("TORRENT_COMMENT", None), "TORRENT_COMMENT", "no_comment")
        values["TORRENT_ARCHIVE"] = validate_torrent_archive_path(values.get("TORRENT_ARCHIVE", None), "TORRENT_ARCHIVE", ".")
        values["IMGBB_PRIORITY"] = validate_int(values.get("IMGBB_PRIORITY", 0), "IMGBB_PRIORITY", 0)
        values["FREE_IMAGE_PRIORITY"] = validate_int(values.get("FREE_IMAGE_PRIORITY", 1), "FREE_IMAGE_PRIORITY", 1)
        values["LENSDUMP_PRIORITY"] = validate_int(values.get("LENSDUMP_PRIORITY", 2), "LENSDUMP_PRIORITY", 2)

        #// Optional working in progress...
        values["PW_API_KEY"] = validate_str(values.get("PW_API_KEY", None), "PW_API_KEY", "no_key")
        values["PW_URL"] = validate_url(values.get("PW_URL", "http://localhost:9696/api/v1"), "PW_URL",
                                        "http://localhost:9696/api/v1")

        #// Optional
        values["FTPX_USER"] = validate_str(values.get("FTPX_USER", None), "FTPX_USER", "user")
        values["FTPX_PASS"] = validate_str(values.get("FTPX_PASS", None), "FTPX_PASS", "pass")
        values["FTPX_IP"] = validate_str(values.get("FTPX_IP", None), "FTPX_IP", "127.0.0.1")
        values["FTPX_PORT"] = validate_str(values.get("FTPX_PORT", "2121"), "FTPX_PORT", "2121")
        values["FTPX_LOCAL_PATH"] = validate_str(values.get("FTPX_LOCAL_PATH", None), "FTPX_LOCAL_PATH", ".")
        values["FTPX_ROOT"] = validate_str(values.get("FTPX_ROOT", "."), "FTPX_ROOT", ".")
        values["FTPX_KEEP_ALIVE"] = validate_boolean(values.get("FTPX_KEEP_ALIVE", False), "FTPX_KEEP_ALIVE", False)

        values["IGDB_CLIENT_ID"] = validate_str(values.get("IGDB_CLIENT_ID", None), "IGDB_CLIENT_ID", "client_id")
        values["IGDB_ID_SECRET"] = validate_str(values.get("IGDB_ID_SECRET", None), "IGDB_ID_SECRET", "secret")


        return values

if os.name == "nt":
    default_env_path: Path = Path(os.getenv("LOCALAPPDATA", ".")) / f"{service_filename}"
    torrent_archive_path: Path = Path(os.getenv("LOCALAPPDATA", ".")) / "torrent_archive"
else:
    default_env_path: Path = Path.home() / f"{service_filename}"
    torrent_archive_path: Path = Path.home() / "torrent_archive"


if not default_env_path.exists():
    print(f"Create default configuration file: {default_env_path}")
    create_default_env_file(default_env_path)

if not torrent_archive_path.exists():
    print(f"Create default torrent archive path: {torrent_archive_path}")
    os.makedirs(torrent_archive_path, exist_ok=True)

custom_console.bot_question_log(f"Default configuration path: {default_env_path}\n")
check_env_variables(path=default_env_path)
load_dotenv(dotenv_path=default_env_path)

config = Config()
