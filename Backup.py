# Attendance System by Koome Franklin (Mburus)
# https://www.koomefranklin.github.io
import datetime
import shutil
import time

# The path to the original database file
original_db = "instance/mdfcs.sqlite3"

# The path to the backup directory
backup_dir = "Backup"

# The format for the backup file name (using the date as the name only one file a day)
backup_name = "{}.db".format(datetime.datetime.now().strftime("%Y-%m-%d"))

# The full path to the backup file
backup_file = "{}/{}".format(backup_dir, backup_name)


# Make a copy of the original database

def backup_job():
    # The script for creating backup
    shutil.copy2(original_db, backup_file)
    print(backup_file)


while True:
    # run the backup function in an endless loop with 30 minute intervals
    backup_job()
    time.sleep(1800)
