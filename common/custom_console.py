# -*- coding: utf-8 -*-
import os

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from decouple import Config, RepositoryEnv, UndefinedValueError

from common.trackers.itt import itt_data


console = Console(log_path=False)

class CustomConsole(Console):

    def __init__(
            self,
            welcome_msg: str,
            welcome_msg_color: str,
            welcome_msg_border_color: str,
            panel_msg_color: str,
            panel_msg_border_color: str,
            normal_color: str,
            error_color: str,
            question_msg_color: str,
    ):

        super().__init__()

        self.welcome_msg: str = welcome_msg
        self.welcome_msg_color: str = welcome_msg_color
        self.welcome_msg_border_color: str = welcome_msg_border_color
        self.panel_msg_color: str = panel_msg_color
        self.panel_msg_border_color: str = panel_msg_border_color
        self.normal_color: str = normal_color
        self.error_color: str = error_color
        self.question_msg_color: str = question_msg_color

    @classmethod
    def load_config(cls):
        """Validate configuration file"""

        current_directory = os.path.dirname(__file__)
        config_file = os.path.abspath(
            os.path.join(current_directory, "..", "console.config")
        )

        try:
            config_load_service = Config(RepositoryEnv(config_file))
            welcome_msg = config_load_service("[welcome_message]")
            welcome_msg_color = config_load_service("[welcome_message_color]")
            welcome_msg_border_color = config_load_service(
                "[welcome_message_border_color]"
            )
            normal_color = config_load_service("[normal_color]")
            error_color = config_load_service("[error_color]")
            panel_msg_border_color = config_load_service("[panel_message_border_color]")
            panel_msg_color = config_load_service("[panel_message_color]")
            question_msg_color = config_load_service("[question_message_color]")

        except UndefinedValueError:
            console.log(f"[Custom Console] Missing attribute")
            exit(1)

        return cls(
            welcome_msg=welcome_msg,
            welcome_msg_color=welcome_msg_color,
            welcome_msg_border_color=welcome_msg_border_color,
            panel_msg_color=panel_msg_color,
            panel_msg_border_color=panel_msg_border_color,
            normal_color=normal_color,
            error_color=error_color,
            question_msg_color=question_msg_color,
        )

    def welcome_message(self):
        title_panel = Panel(
            Text(f"UNIT3Dup - An uploader for the Unit3D torrent tracker - {self.welcome_msg}",
                 style=self.welcome_msg_color, justify="center"),
            border_style=self.welcome_msg_border_color,
            title_align="center",
        )
        self.print(title_panel)

    def panel_message(self, message: str):
        title_panel = Panel(
            Text(message, style=self.panel_msg_color, justify="center"),
            border_style=self.panel_msg_border_color,
            title_align="center",
            expand=False,
        )
        self.print(title_panel, justify="center")

    def bot_log(self, message: str):
        console.log(message, style=self.normal_color)

    def bot_error_log(self, message: str):
        console.log(message, style=self.error_color)

    def bot_warning_log(self, message: str):
        console.log(message, style=self.question_msg_color)

    def bot_input_log(self, message: str):
        console.print(f"{message} ", end="", style=self.normal_color)

    def bot_question_log(self, message: str):
        console.print(message, end="", style=self.question_msg_color)

    def bot_counter_log(self, message: str):
        console.print(message, end="\r", style=self.question_msg_color)

    @staticmethod
    def get_key_by_value(tracker_data, category, value):
        if category in tracker_data:
            if isinstance(tracker_data[category], dict):
                for k, v in tracker_data[category].items():
                    if v == value:
                        return k

    @staticmethod
    def bot_process_table_log(content: list):

        table = Table(
            title="Here is your files list" if content else "There are no files here",
            border_style="bold blue",
            header_style="red blue",
        )

        table.add_column("Torrent Pack", style="dim")
        table.add_column("Media", justify="left", style="bold green")
        table.add_column("Path", justify="left", style="bold green")

        for item in content:
            pack = "Yes" if item.torrent_pack else "No"
            category_name = CustomConsole.get_key_by_value(itt_data, "CATEGORY", item.category)
            if not category_name:
                category_name = ''
            table.add_row(
                pack,
                category_name,
                item.torrent_path,
            )

        console.print(Align.center(table))

    def bot_tmdb_table_log(self, result, title: str, media_info_language: str):

        console.print("\n")
        media_info_audio_languages = (",".join(media_info_language)).upper()
        self.panel_message(f"\nResults for {title.upper()}")

        table = Table(border_style="bold blue")
        table.add_column("TMDB ID", style="dim")
        table.add_column("LANGUAGE", style="dim")
        table.add_column("TMDB POSTER", justify="left", style="bold green")
        table.add_column("TMDB BACKDROP", justify="left", style="bold green")
        # table.add_column("TMDB KEYWORDS", justify="left", style="bold green")
        table.add_row(
            str(result.video_id),
            media_info_audio_languages,
            result.poster_path,
            result.backdrop_path,
        )
        console.print(Align.center(table))

    @staticmethod
    def wait_for_user_confirmation(message: str):
        # Wait for user confirmation in case of validation failure
        try:
            custom_console.bot_error_log(message=message)
            input("> ")
        except KeyboardInterrupt:
            custom_console.bot_error_log("\nOperation cancelled.Please update your config file")
            exit(0)

    @staticmethod
    def user_input(message: str)-> int:
        try:
            while True:
                custom_console.bot_input_log(message=message)
                user_tmdb_id = input()
                if user_tmdb_id.isdigit():
                    user_tmdb_id = int(user_tmdb_id)
                    return user_tmdb_id if user_tmdb_id < 999999 else 0
        except KeyboardInterrupt:
            custom_console.bot_error_log("\nOperation cancelled. Bye !")
            exit(0)


# Init custom Console
custom_console = CustomConsole.load_config()
