import argparse
import logging


def start() -> None:
    """
    Start of the program. Handles argument parsing.
    :return:
    """
    parser = argparse.ArgumentParser(description="TME Analyzer")
    parser.add_argument(
        "-l",
        "--loglevel",
        type=str,
        default="error",
        metavar="\b",
        help="set the loglevel (info, warn, error) default: error",
    )
    args = parser.parse_args()

    if str(args.loglevel).lower() == "warn":
        loglevel = logging.WARN
    elif str(args.loglevel).lower() == "error":
        loglevel = logging.ERROR
    elif str(args.loglevel).lower() == "info":
        loglevel = logging.INFO
    else:
        raise ValueError(f"{args.loglevel} is not a valid loglevel.")
    if __package__ == "tmeanalyzer":
        from .main import check_consent
    else:
        from main import check_consent
    check_consent(loglevel)


if __name__ == "__main__":
    start()
