import ipaddress
import json
import os

from pydantic import BaseModel, model_validator
from urllib.parse import urlparse
from pathlib import Path

from common.custom_console import custom_console
from common.utility import ManageTitles


class TrackerConfig(BaseModel):
    ITT_URL: str
    ITT_APIKEY: str | None = None
    TMDB_APIKEY: str | None = None
    LENSDUMP_KEY: str | None = None
    FREE_IMAGE_KEY: str | None = None
    PTSCREENS_KEY: str | None = None
    IMGBB_KEY: str | None = None
    IMGFI_KEY: str | None = None
    IGDB_CLIENT_ID: str | None = None
    IGDB_ID_SECRET: str | None = None


class TorrentClientConfig(BaseModel):
    QBIT_USER: str | None = None
    QBIT_PASS: str | None = None
    QBIT_HOST: str = "http://localhost"
    QBIT_PORT: int = 8080
    TRASM_USER: str | None = None
    TRASM_PASS: str | None = None
    TRASM_HOST: str = "http://localhost"
    TRASM_PORT: int = 9091
    TORRENT_CLIENT: str | None = None


class UserPreferences(BaseModel):
    PTSCREENS_PRIORITY: int = 0
    LENSDUMP_PRIORITY: int = 1
    FREE_IMAGE_PRIORITY: int = 2
    IMGBB_PRIORITY: int = 3
    IMGFI_PRIORITY: int = 4
    YOUTUBE_FAV_CHANNEL_ID: str | None = None
    YOUTUBE_CHANNEL_ENABLE: bool = False
    DUPLICATE_ON: bool = False
    SKIP_DUPLICATE: bool = False
    SIZE_TH: int = 50
    WATCHER_INTERVAL: int = 60
    WATCHER_PATH: str | None = None
    WATCHER_DESTINATION_PATH: str | None = None
    NUMBER_OF_SCREENSHOTS: int = 4
    COMPRESS_SCSHOT: int = 4
    RESIZE_SCSHOT: bool = False
    TORRENT_ARCHIVE: str | None = None
    TORRENT_COMMENT: str | None = "no_comment"
    PREFERRED_LANG: str | None = "all"
    ANON: bool = False
    CACHE_SCR: bool = False
    CACHE_PATH: str | None = None



class Options(BaseModel):
    PW_API_KEY: str | None = None
    PW_URL: str = "http://localhost:9696/api/v1"
    PW_TORRENT_ARCHIVE_PATH: str | None = None
    PW_DOWNLOAD: str | None = None
    FTPX_USER: str = "user"
    FTPX_PASS: str = "pass"
    FTPX_IP: str = "127.0.0.1"
    FTPX_PORT: int = 2121
    FTPX_LOCAL_PATH: str | None = None
    FTPX_ROOT: str = "."
    FTPX_KEEP_ALIVE: bool = False


class Validate:

    @staticmethod
    def url(value: str, field_name: str) -> str:
        """
        Validates URL
        """
        parsed_url = urlparse(value)
        if not (parsed_url.scheme and parsed_url.netloc) or parsed_url.scheme not in ["http", "https"]:
            custom_console.bot_error_log(
                f"->  Invalid URL value for {field_name} '{value}'"
            )
            exit(1)
        return value

    @staticmethod
    def string(value: str | None, field_name: str) -> str | None:
        """
        Validates string
        """
        if isinstance(value, str) and value.strip():
            return value
        custom_console.bot_error_log(
            f"-> not configured {field_name} '{value}'"
        )
        exit(1)

    @staticmethod
    def iso3166(value: str | None, field_name: str) -> str | None:
        """
        Validates iso3166
        """
        if isinstance(value, str) and value.strip():
            if ManageTitles.convert_iso(value):
                return value
            if value.lower() == 'all':
                return value
        custom_console.bot_error_log(
            f"-> not configured {field_name} '{value}'"
        )
        exit(1)

    @staticmethod
    def ip(value: str, field_name: str, default_value: str) -> str:
        """
        Validates IP address
        """
        if not value:
            return default_value
        try:
            parsed_ip = ipaddress.ip_address(value)
            return value
        except ValueError:
            custom_console.bot_error_log(
                f"->  Invalid IP address value for {field_name} '{value}'"
            )
            exit(1)

    @staticmethod
    def integer(value: int | str, field_name: str) -> int:
        """
        Validates integer
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            custom_console.bot_error_log(
                f"-> not configured {field_name} '{value}'"
            )
            exit(1)

    @staticmethod
    def boolean(value: bool | str, field_name: str) -> bool:
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
            f"-> not configured {field_name} '{value}'"
        )
        exit(1)

    @staticmethod
    def torrent_archive_path(value: str | None, field_name: str, default_value: str | None) -> str | None:
        """
        Validates path
        """
        if value is None or not isinstance(value, str) or not value.strip():
            return default_value
        path = Path(value).expanduser()
        if path.is_dir():
            return str(path)
        custom_console.bot_error_log(
            f"-> Invalid path for {field_name} '{value}'"
        )
        exit(1)

class Config(BaseModel):
    tracker_config: TrackerConfig
    torrent_client_config: TorrentClientConfig
    user_preferences: UserPreferences
    options: Options

    @model_validator(mode='before')
    def set_default_tracker_config(cls, v):

        section = v['tracker_config']
        for field,value in section.items():
            if value is None:
                custom_console.bot_error_log(f"Please fix the '{field}' value")
                exit(1)
            else:
                if field=='ITT_URL':
                    section[field] = Validate.url(value=section[field], field_name=field)
                else:
                    section[field] = Validate.string(value=section[field], field_name=field)
        return v

    @model_validator(mode='before')
    def set_default_torrent_client_config(cls, v):

        section = v['torrent_client_config']
        for field,value in section.items():
            if value is None:
                custom_console.bot_error_log(f"Please fix the '{field}' value")
                exit(1)
            else:
                if field in  ['QBIT_HOST','TRASM_HOST']:
                    section[field] = Validate.ip(value=section[field], field_name=field, default_value="127.0.0.1")

                if field == 'QBIT_PORT':
                    section[field] = Validate.integer(value=section[field], field_name=field)

                if field =='TRASM_PORT':
                    section[field] = Validate.integer(value=section[field], field_name=field)

                if field in ['QBIT_PASS','TRASM_PASS','QBIT_USER','TRASM_USER']:
                    section[field] = Validate.string(value=section[field], field_name=field)

                if field == 'TORRENT_CLIENT':
                    section[field] = Validate.string(value=section[field], field_name=field)
        return v


    @model_validator(mode='before')
    def set_default_user_preferences(cls, v):
        section = v['user_preferences']

        for field,value in section.items():
            if value is None:
                custom_console.bot_error_log(f"Please fix the '{field}' value")
                exit(1)
            else:
                field = field.upper()

                if field in ['DUPLICATE_ON','SKIP_DUPLICATE','RESIZE_SCSHOT','ANON','CACHE_SCR']:
                    section[field] = Validate.boolean(value=section[field], field_name=field)

                if field in ['TORRENT_COMMENT','PW_TORRENT_ARCHIVE_PATH','WATCHER_PATH']:
                    section[field] = Validate.string(value=section[field], field_name=field)

                if field in ['NUMBER_OF_SCREENSHOTS','COMPRESS_SCSHOT','IMGBB_PRIORITY','FREE_IMAGE_PRIORITY',
                             'LENSDUMP_PRIORITY','WATCHER_INTERVAL','SIZE_TH']:
                    section[field] = Validate.integer(value=section[field], field_name=field)

                if field == 'PREFERRED_LANG':
                    section[field] =Validate.iso3166(value=section[field], field_name=field)

                if field in  ['TORRENT_ARCHIVE','PW_DOWNLOAD_PATH', 'WATCHER_DESTINATION_PATH','CACHE_PATH']:
                    section[field] =Validate.torrent_archive_path(value=section[field], field_name=field, default_value='.')
        return v

    @model_validator(mode='before')
    def set_default_options(cls, v):
        return v or Options()


class Load:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Load, cls).__new__(cls, *args, **kwargs)
            # La configurazione viene caricata solo una volta
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        self.config = self.load_config()


    @staticmethod
    def create_default_json_file(path: Path):
        """
        Creates a default configuration file if it doesn't already exist
        """

        default_content = {
            "tracker_config": {
                "ITT_URL": "https://itatorrents.xyz",
                "ITT_APIKEY": "no_key",
                "TMDB_APIKEY": "no_key",
                "IMGBB_KEY": "no_key",
                "FREE_IMAGE_KEY": "no_key",
                "LENSDUMP_KEY": "no_key",
                "PTSCREENS_KEY": "no_key",
                "IMGFI_KEY": "no_key",
                "YOUTUBE_KEY": "no_apikey",
                "IGDB_CLIENT_ID": "client_id",
                "IGDB_ID_SECRET": "secret",
            },
            "torrent_client_config": {
                "QBIT_USER": "admin",
                "QBIT_PASS": "no_pass",
                "QBIT_HOST": "127.0.0.1",
                "QBIT_PORT": "8080",
                "TRASM_USER": "admin",
                "TRASM_PASS": "no_pass",
                "TRASM_HOST": "127.0.0.1",
                "TRASM_PORT": "9091",
                "TORRENT_CLIENT": "qbittorrent",
            },
            "user_preferences": {
                "PTSCREENS_PRIORITY": 0,
                "LENSDUMP_PRIORITY": 1,
                "FREE_IMAGE_PRIORITY": 2,
                "IMGBB_PRIORITY": 3,
                "IMGFI_PRIORITY": 4,
                "YOUTUBE_FAV_CHANNEL_ID": "UCGCbxpnt25hWPFLSbvwfg_w",
                "YOUTUBE_CHANNEL_ENABLE": False,
                "DUPLICATE_ON": False,
                "SKIP_DUPLICATE": False,
                "SIZE_TH": 50,
                "WATCHER_INTERVAL": 60,
                "WATCHER_PATH": "watcher_path",
                "WATCHER_DESTINATION_PATH": ".",
                "NUMBER_OF_SCREENSHOTS": 4,
                "COMPRESS_SCSHOT": 4,
                "RESIZE_SCSHOT": False,
                "TORRENT_ARCHIVE": ".",
                "TORRENT_COMMENT": "no_comment",
                "PREFERRED_LANG": "all",
                "ANON": False,
                "CACHE_SCR": False,
                "CACHE_PATH": ".",
            },
            "options": {
                "PW_API_KEY": "no_key",
                "PW_URL": "http://localhost:9696/api/v1",
                "PW_TORRENT_ARCHIVE_PATH": ".",
                "PW_DOWNLOAD": ".",
                "FTPX_USER": "user",
                "FTPX_PASS": "pass",
                "FTPX_IP": "127.0.0.1",
                "FTPX_PORT": 2121,
                "FTPX_LOCAL_PATH": ".",
                "FTPX_ROOT": ".",
                "FTPX_KEEP_ALIVE": False,
            }
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as json_file:
            json.dump(default_content, json_file, indent=4)


    @staticmethod
    def validate_json(file_path: Path):
        try:
            with open(file_path, 'r') as file:
                json_data = file.read()
                # allow single '\' character in JSON file not '\\'
                json_data = json_data.replace('\\', '\\\\')
                return json.loads(json_data)

        except json.JSONDecodeError as e:
            print(f"Config Loading error.. {e}")
            return None
        except FileNotFoundError:
            print(f"Configuration '{file_path}' not found")
            return None


    @staticmethod
    def load_config():
        service_jsonfile = "Unit3Dbot_service.json"

        if os.name == "nt":
            default_json_path: Path = Path(os.getenv("LOCALAPPDATA", ".")) / f"{service_jsonfile}"
            PW_TORRENT_ARCHIVE_PATH: Path = Path(os.getenv("LOCALAPPDATA", ".")) / "pw_torrent_archive"
            PW_DOWNLOAD_PATH: Path = Path(os.getenv("LOCALAPPDATA", ".")) / "pw_download"
            WATCHER_DESTINATION_PATH: Path = Path(os.getenv("LOCALAPPDATA", ".")) / "watcher_destination_path"

        else:
            default_json_path: Path = Path.home() / f"{service_jsonfile}"
            PW_TORRENT_ARCHIVE_PATH: Path = Path.home() / "pw_torrent_archive"
            PW_DOWNLOAD_PATH: Path = Path.home() / "pw_download"
            WATCHER_DESTINATION_PATH: Path = Path.home() / "watcher_destination_path"

        if not PW_TORRENT_ARCHIVE_PATH.exists():
            print(f"Create default pw torrent archive path: {PW_TORRENT_ARCHIVE_PATH}")
            os.makedirs(PW_TORRENT_ARCHIVE_PATH)

        if not PW_DOWNLOAD_PATH.exists():
            print(f"Create default pw download path: {PW_DOWNLOAD_PATH}")
            os.makedirs(PW_DOWNLOAD_PATH)

        if not WATCHER_DESTINATION_PATH.exists():
            print(f"Create default destination watcher path: {WATCHER_DESTINATION_PATH}")
            os.makedirs(WATCHER_DESTINATION_PATH)

        if not default_json_path.exists():
            print(f"Create default configuration file: {default_json_path}")
            Load.create_default_json_file(default_json_path)


        config_data = Load.validate_json(default_json_path)
        if not config_data:
            print(default_json_path)
            exit(1)

        json_data = Load.validate_json(default_json_path)
        if not json_data:
            print("Failed to Load default configuration file")
            exit(1)

        c = Config(**json_data)
        return c



