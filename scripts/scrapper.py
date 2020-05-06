#!/usr/bin/env python3
import argparse
import json
import pathlib
import sys

from vin_scrapper import VinScrapper


def main():
    parser = argparse.ArgumentParser(
        description="Web scrapping tool for Vehicle information by VIN number", formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--url", required=True, type=str, help="Accessing URL",
    )
    parser.add_argument(
        "--licence-number", required=True, type=str, help="A licence number."
    )
    parser.add_argument(
        "--location",
        required=True,
        type=str,
        help=("A location where licence is registered.\n"
            "\tExample: --location CA [ie California]."),
    )
    parser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        help="Open browser [Debugging mode].",
    )
    parser.add_argument(
        "--no-json-output", action="store_false", help="Output as json.",
    )
    parser.add_argument("--host", dest="host", help="Proxy address. [Optional]")
    parser.add_argument("--port", dest="port", help="Proxy port. [Optional]")
    parser.add_argument(
        "--username", dest="username", help="Username to access proxy. [Optional]"
    )
    parser.add_argument(
        "--password", dest="password", help="Password to access proxy. [Optional]"
    )
    parser.add_argument(
        "--web_username", help="Username to access the website (if any)."
    )
    parser.add_argument(
        "--web_password", help="Password to access the website (if any)."
    )
    parser.add_argument(
        "--loglevel",
        dest="log_level",
        default="INFO",
        help="log level to use, default [INFO], options [INFO, DEBUG, ERROR]",
    )
    args = vars(parser.parse_args())
    data = []
    try:
        licence_plate = VinScrapper(**args)
        licence_plate.open_site(headless=args.get("headless"))
        licence_plate.login()
        licence_plate.navigate_site()
        licence_plate.get_vehicle_details()
        data.append(licence_plate.data_structure)
        licence_plate.close_session()
    except Exception as err:
        print(err)
        licence_plate.close_session()
    finally:
        return (
            json.dumps(data, indent=4, sort_keys=True)
            if args.get("no_json_output")
            else data
        )


if __name__ == "__main__":
    data = main()
    print(f"JSON output: {data}")
