from helpers import get_number_of
from logger.downloadlogger import Logger
from downloader.jiradownloader import JiraDownloader
from properties import JiraAPI, JiraCredentials, verbose, JiraWaitTimeInSeconds

if __name__ == "__main__":
	jd = JiraDownloader(JiraAPI, JiraCredentials, wait_time_in_seconds=JiraWaitTimeInSeconds)
	lg = Logger(verbose)
	projects = jd.download_object(JiraAPI + "project")
	lg.start_action("Retrieving the number of issues for " + str(len(projects)) + " projects...", len(projects))
	with open("projects.txt", 'w') as outfile:
		for project in projects:
			number_of_issues = get_number_of(jd, JiraAPI + "search", "jql=project=" + project["key"])
			outfile.write(project["key"] + ";" + project["name"] + ";" + str(number_of_issues) + "\n")
			outfile.flush()
	lg.end_action()
