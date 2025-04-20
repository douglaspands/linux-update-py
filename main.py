if __name__ == "__main__":
    import argparse

    from ubuntu_update import UbuntuUpdate

    parser = argparse.ArgumentParser(description="Ubuntu Update")
    subparser = parser.add_subparsers(dest="command", required=True)

    # subparser
    update_parser = subparser.add_parser("update")
    update_parser.add_argument(
        "application",
        help="Update the application and all installed packages.",
        choices=("apt", "snap", "flatpak", "all"),
    )

    args = parser.parse_args()
    if args.command == "update":
        with UbuntuUpdate() as uu:
            uu.update(app=args.application)
