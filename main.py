import hashlib
import os
import shutil
import logging
import time
from datetime import datetime
import sys


def synchronization():
    """Synchronize two folders based on the parameters.

    Arguments (in command line):
        arg1 (str): source folder path.
        arg2 (str): replica folder path.
        arg3 (str): log file path.
        arg4 (int): interval between two synchronization progress.
    """

    source_folder_path = sys.argv[1]
    replica_folder_path = sys.argv[2]
    log_file_path = sys.argv[3]
    interval = int(sys.argv[4])

    logging.basicConfig(filename=os.path.join(log_file_path, "log.txt"), level=logging.INFO)

    while True:

        # Here we check the directory paths of replica. If a directory does not exist in source, we are delete the directory (with its contents).
        for dirpath, dirnames, filenames in os.walk(replica_folder_path):

            source_directories_to_check = os.path.join(source_folder_path, dirpath[len(replica_folder_path):]).replace("\\", "/")

            if not os.path.isdir(source_directories_to_check):
                logging.info(f'{datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}: Directory does not exist in source anymore, and it is deleted: {dirpath}')
                shutil.rmtree(dirpath)

        # Here we check the files of replica. If a file does not exist in source, we delete it.
        for dirpath, dirnames, filenames in os.walk(replica_folder_path):

            for item in filenames:
                item_path_in_replica = os.path.join(dirpath, item).replace("\\", "/")
                source_filename_to_check = os.path.join(source_folder_path, item_path_in_replica[len(replica_folder_path):])
                if not os.path.isfile(source_filename_to_check):
                    logging.info(f'{datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}: File does not exist in source anymore, and it is deleted: {item_path_in_replica}')
                    os.remove(item_path_in_replica)
                # print(source_filename_to_check)

        # Here we check the directory of source. If a directory does not exist in replica, we create the directory.
        for dirpath, dirnames, filenames in os.walk(source_folder_path):

            replica_directories_to_check = os.path.join(replica_folder_path, dirpath[len(source_folder_path):]).replace("\\", "/")

            if not os.path.isdir(replica_directories_to_check):
                logging.info(f'{datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}: Directory does not exist in replica, and it is created: {replica_directories_to_check}')
                os.mkdir(replica_directories_to_check)

        # Here we check the files of source. If a file:
        # - does not exist in the replica, we copy it.
        # - exists in the replica, we compare the MD5 hashes and copy only if the MD5 hases are different.
        for dirpath, dirnames, filenames in os.walk(source_folder_path):

            for item in filenames:
                item_path_in_source = os.path.join(dirpath, item).replace("\\", "/")
                replica_filename_to_check = os.path.join(replica_folder_path, item_path_in_source[len(source_folder_path):])

                if not os.path.isfile(replica_filename_to_check):
                    logging.info(f'{datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}: File does not exist in replica, and copied: {item_path_in_source}')
                    shutil.copyfile(item_path_in_source, replica_filename_to_check)

                else:
                    with open(item_path_in_source, "rb") as s:
                        source_file_hexdigest = hashlib.md5(s.read()).hexdigest()

                    with open(replica_filename_to_check, "rb") as t:
                        target_file_hexdigest = hashlib.md5(t.read()).hexdigest()

                    if not source_file_hexdigest == target_file_hexdigest:
                        logging.info(f'{datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}: File changed, and it is updated: {item_path_in_source}')
                        os.remove(replica_filename_to_check)
                        shutil.copyfile(item_path_in_source, replica_filename_to_check)

        time.sleep(interval)


if __name__ == '__main__':

    synchronization()
