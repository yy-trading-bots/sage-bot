from bot.sage_bot import SageBot


def main() -> None:
    """
    Entry point of the trading bot.

    Initializes the SageBot instance and starts its execution loop.
    """
    sagebot: SageBot = SageBot()
    sagebot.run()


if __name__ == "__main__":
    main()
