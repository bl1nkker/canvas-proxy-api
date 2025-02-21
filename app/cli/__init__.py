from cleo import Application

from cli.dbinit import DbInitCommand
from cli.dbdrop import DbDropCommand


def main():
    print("Hello")
    application = Application()
    application.add(DbDropCommand())
    application.add(DbInitCommand())
    # application.add(RedisFlushDbCommand())
    application.run()


if __name__ == "__main__":
    main()
