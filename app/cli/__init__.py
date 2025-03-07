from cleo import Application

from cli.dbdrop import DbDropCommand
from cli.dbinit import DbInitCommand


def main():
    application = Application()
    application.add(DbDropCommand())
    application.add(DbInitCommand())
    # application.add(RedisFlushDbCommand())
    application.run()


if __name__ == "__main__":
    main()
