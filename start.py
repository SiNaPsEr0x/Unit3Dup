# -*- coding: utf-8 -*-
import argparse
from unit3dup.uploader import UploadBot
from unit3dup.contents import Cli
from rich.console import Console

console = Console(log_path=False)


def user_arguments():
    parser = argparse.ArgumentParser(description='Commands', add_help=False)
    parser.add_argument('-u', '--upload', nargs=1, type=str, help='Upload Path')
    parser.add_argument('-t', '--tracker', nargs=1, type=str, help='Tracker Name')
    return parser.parse_args()


def start_info(bot, user_input):
    console.log(f"\n[TORRENT NAME] {bot.name}")
    console.log(f"[SIZE]         {user_input.size}")


def process_upload(user_input):
    bot = UploadBot(user_input.content)
    start_info(bot, user_input)
    if user_input.content.category == user_input.serie:
        data = bot.serie_data()
    else:
        data = bot.movie_data()
    bot.process_data(data)


def main():
    args = user_arguments()

    console.rule(f"\n[bold blue] Unit3D uploader", style="#ea00d9")
    user_input = Cli(args=args, tracker=args.tracker)

    if args.upload:
        if user_input:
            process_upload(user_input)
    else:
        console.print("Sintassi non valida o valore nullo. Controlla..")
        console.print(f"[-u] {args.upload}")
        console.print(f"[-t] {args.tracker}")


if __name__ == "__main__":
    main()
