# -*- coding: utf-8 -*-
import os
from thefuzz import fuzz


class Manage_titles:
    # todo: rimvuoere '.' senza rimuoverli da DD5.1 H.264 ecc
    marks = [
        ".",
        ",",
        ";",
        ":",
        "!",
        "?",
        '"',
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
        "/",
        "\\",
        "&",
        "*",
        "$",
        "%",
        "#",
        "@",
        "_",
        "+",
    ]  # '-','’' ,'\'','–'

    @staticmethod
    def clean(filename: str):
        name = filename
        for punct in Manage_titles.marks:
            name = name.replace(punct, " ")
        name = name.split()
        return " ".join(name)

    # - rimuovo lettere accentate non sempre presenti in entrambi le parti
    @staticmethod
    def accented_remove(string: str):
        accented_letters = [
            "à",
            "è",
            "é",
            "ì",
            "ò",
            "ù",
            "á",
            "í",
            "ó",
            "ú",
            "ñ",
            "ä",
            "ö",
            "ü",
            "ß",
            "â",
            "ê",
            "î",
            "ô",
            "û",
            "ë",
            "ï",
            "ü",
            "ÿ",
            "ç",
            "ã",
            "ẽ",
            "ĩ",
            "õ",
            "ũ",
            "ä",
            "ë",
            "ï",
            "ö",
            "ü",
            "ÿ",
            "á",
            "é",
            "í",
            "ó",
            "ú",
            "å",
            "ä",
            "ö",
            "æ",
            "ø",
            "ş",
            "ç",
            "ğ",
            "ı",
            "ą",
            "ć",
            "ę",
            "ł",
            "ń",
            "ó",
            "ś",
            "ź",
            "ż",
            "š",
        ]

        return "".join(char for char in string if char.lower() not in accented_letters)

    @staticmethod
    def filter_ext(file: str) -> bool:
        video_ext = [
            ".mp4",
            ".mkv",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".webm",
            ".3gp",
            ".ogg",
            ".mpg",
            ".mpeg",
            ".m4v",
            ".rm",
            ".rmvb",
            ".vob",
            ".ts",
            ".m2ts",
            ".divx",
            ".asf",
            ".swf",
            ".ogv",
            ".drc",
            ".m3u8",
            ".pdf",
        ]

        return os.path.splitext(file)[1].lower() in video_ext

    @staticmethod
    def media_docu_type(file_name: str) -> str:
        ext = os.path.splitext(file_name)[1].lower()
        type_ = {".pdf": "edicola"}

        return type_.get(ext, None)

    @staticmethod
    def fuzzyit(str1: str, str2: str) -> int:
        return fuzz.ratio(str1.lower(), str2.lower())


class System:

    @staticmethod
    def get_size(folder_path) -> float:

        # Size of single file
        if os.path.isfile(folder_path):
            return round(os.path.getsize(folder_path) / (1024**3), 2)
        else:
            # size of folder
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for file in filenames:
                    file_path = os.path.join(dirpath, file)
                    if not os.path.islink(file_path):
                        total_size += os.path.getsize(file_path)
            return round(total_size / (1024**3), 2)
