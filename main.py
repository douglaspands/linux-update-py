#! /usr/bin/env python3

if __name__ == "__main__":
    import argparse
    from time import perf_counter as time

    from linux_update import LinuxUpdate

    with LinuxUpdate() as linux_update:
        parser = argparse.ArgumentParser(description="Linux Update")
        subparser = parser.add_subparsers(dest="command", required=True)

        # subparser
        update_parser = subparser.add_parser("update")
        update_parser.add_argument(
            "application",
            help="Update the application and all installed packages.",
            choices=linux_update.available_managers(),
        )

        args = parser.parse_args()
        if args.command == "update":
            print(">> LINUX DISTRO UPDATE STARTED\n")

            time_start = time()
            linux_update.update(app=args.application)
            time_total = time() - time_start

            print(f"\n>> TOTAL TIME TAKEN: {time_total:.2f} seconds")
            print(">> LINUX DISTRO UPDATE COMPLETED")
