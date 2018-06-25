import requests
import os
import csv
import datetime
from ConfReader import ConfReader
from git import Repo
from shutil import rmtree

config = ConfReader("./gh.conf")
path_pref = config.get_value("PATH")
logs = []


def get_dates():
    """
    Counts the folders in GitHub_backup and sorts the dates of the files
    :return: A sorted list of the dates and the number of folders
    """
    dates = []
    count_folders = 0
    for dir in os.listdir(path_pref):
        try:
            if dir.split("_") == "GitHub":
                count_folders += 1
                dates.append(dir.split("_")[1])
        except Exception:
            pass
    dates.sort()
    return dates, count_folders


def manage_dir():
    """
    Ensures that the backups are following the retention days and dispose of the old folders
    :return: path of the new folder to do the backup
    """
    days = int(config.get_value("RETENTION_DAYS"))
    date = datetime.date.today()
    backup_path = os.path.join(path_pref + "GitHub_" + str(date))

    if not os.path.exists(path_pref):
        os.makedirs(path_pref)

    dates, count = get_dates()

    if count == days:
        try:
            rmtree(path_pref + "GitHub_{}".format(dates[0]))
        except Exception:
            print("Could not delete the folder.")
    elif count > days:
        for i in dates[:(count-days)]:
            try:
                rmtree(path_pref + "GitHub_{}".format(i))
            except Exception:
                print("Could not delete the folder.")


    if not os.path.exists(backup_path):
        os.makedirs(backup_path)
    return backup_path


def get_json():
    """
    This function recovers the data about the repositories from the github API and format it in JSON
    :return: JSON data
    """
    git_api_url = "https://api.github.com/orgs/{organization}/repos?per_page=100&page=1".format(
        organization=config.get_value("ORGANIZATION"))
    response = requests.get(git_api_url, auth=(config.get_value("USERNAME"),config.get_value("TOKEN")))
    if response.status_code != 200:
        e = Exception("The webpage returned a code different from 200")
        logs.append(('All', 'ERROR'))
        raise e
    else:
        clean_response = response.json()
        return clean_response


def clone_all(clean_response, backup_path):
    """
    Clones all the repositories found in clean_response in backup_path
    :param clean_response: JSON data containing the clone URL of the repositories
    :param backup_path: String
    :return: /
    """
    for repo in clean_response:
        try:
            name = repo['name']
            repo_path = backup_path + "/{}".format(name)
            Repo.clone_from(repo['clone_url'], repo_path)
            logs.append((repo['name'], "OK"))
        except Exception:
            logs.append((repo['name'], "ERROR"))


def write_logs(backup_path):
    """
    Write logs of the backups
    :return:
    """
    with open(os.path.join(backup_path, '_logs.csv'), mode='wt', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(('Repo', 'Status'))
        for repo in logs:
            writer.writerow(repo)
            print("Repository: {} --- {}".format(repo[0], repo[1]))


if __name__ == "__main__":
    backup_path = ''
    try:
        backup_path = manage_dir()
        clean_response = get_json()
        clone_all(clean_response, backup_path)
    finally:
        write_logs(backup_path)
