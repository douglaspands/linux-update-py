#! /usr/bin/env python3

if __name__ == "__main__":
    import argparse

    from linux_update import LinuxUpdate

    with LinuxUpdate() as linux_update:
        parser = argparse.ArgumentParser(description="Linux Update")
        subparser = parser.add_subparsers(dest="command", required=True)

        # subparser
        update_parser = subparser.add_parser("update")
        update_parser.add_argument(
            "application",
            help="Update the application and all installed packages.",
            choices=linux_update.available_managers() + ["all"],
        )

        args = parser.parse_args()
        if args.command == "update":
            linux_update.update(app=args.application)
