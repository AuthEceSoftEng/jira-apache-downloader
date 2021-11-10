import os
import sys
import traceback
from datetime import datetime
from logger.downloadlogger import Logger
from datamanager.dbmanager import DBManager
from datamanager.mongomanager import MongoDBManager
from downloader.jiradownloader import JiraDownloader
from helpers import get_number_of, print_usage, read_file_in_lines, get_issue_fields, extract_users, process_field
from properties import JiraAPI, JiraCredentials, JiraWaitTimeInSeconds, update_existing_projects, verbose, use_database

# Initialize all required objects
db = MongoDBManager() if use_database == 'mongo' else DBManager()
lg = Logger(verbose)
jd = JiraDownloader(JiraAPI, JiraCredentials, wait_time_in_seconds=JiraWaitTimeInSeconds)

def download_project(project_name):
	"""
	Downloads all the data of a project given its Jira name.

	:param project_name: the name of the projects of which the data are downloaded.
	"""
	project_custom_fields_api_address = JiraAPI + "field"
	project_api_address = JiraAPI + "project/" + project_name

	lg.log_action("Downloading project " + project_name)
	project_update = db.project_exists(project_name)
	if project_update:
		if update_existing_projects:
			lg.log_action("Project already exists! Updating...")
		else:
			lg.log_action("Project already exists! Skipping...")
			return

	db.initialize_write_to_disk(project_name)

	project = db.read_project_from_disk(project_name)
	if project_update:
		last_crawled = project.last_crawled()
		last_crawl_complete = project.last_crawl_complete()
		print("Project last crawled: " + (str(last_crawled) if last_crawled else "never") + " (crawl " + ("successful" if last_crawl_complete else "unsuccesful") + ")")
		print("Project last updated: " + (str(project.last_updated()) if project.last_updated() else "never"))

	crawldatetime = datetime.utcnow().replace(microsecond=0)
	try:
		fieldids, fieldtypes = get_issue_fields(jd, project_custom_fields_api_address)

		project_info = jd.download_object(project_api_address)
		project.add_info(project_info)
		db.write_project_info_to_disk(project_name, project["info"])

		jql_query = "jql=project=" + project_name
		if project_update and last_crawl_complete:
			jql_query += " AND updatedDate > '" + str(last_crawled)[:-3] + "'"

		project_issues_address = JiraAPI + "search"
		number_of_issues = get_number_of(jd, project_issues_address, jql_query)
		issue_params = [jql_query, "fields=*all", "expand=changelog"]

		lg.start_action("Retrieving " + str(number_of_issues) + " issues, including their events and comments...", number_of_issues)
		for issue in jd.download_paginated_object(project_issues_address, "issues", issue_params):
			# Process fields
			for key, value in issue["fields"].items():
				if value != None:
					fieldtype = fieldtypes.get(key, None)
					fieldkey = fieldids.get(key, key)
					process_field(issue, fieldkey, fieldtype, value)

			# Extract users
			for user in extract_users(issue, JiraAPI):
				if not project.user_exists(user):
					project.add_user(user)
					db.write_project_user_to_disk(project_name, user)
			# Extract events
			for event in issue["changelog"]["histories"]:
				# Extract users
				for user in extract_users(event, JiraAPI):
					if not project.user_exists(user):
						project.add_user(user)
						db.write_project_user_to_disk(project_name, user)
				event["issue"] = issue["id"]
				process_field(event, "created")
				project.add_event(event)
				db.write_project_event_to_disk(project_name, event)
			# Extract comments
			for comment in issue["fields"]["comment"]["comments"]:
				# Extract users
				for user in extract_users(comment, JiraAPI):
					if not project.user_exists(user):
						project.add_user(user)
						db.write_project_user_to_disk(project_name, user)
				comment["issue"] = issue["id"]
				process_field(comment, "created")
				process_field(comment, "updated")
				project.add_comment(comment)
				db.write_project_comment_to_disk(project_name, comment)
			# Extract worklog
			if "worklog" in issue["fields"]:
				for worklog in issue["fields"]["worklog"]["worklogs"]:
					# Extract users
					for user in extract_users(worklog, JiraAPI):
						if not project.user_exists(user):
							project.add_user(user)
							db.write_project_user_to_disk(project_name, user)
					worklog["issue"] = issue["id"]
					process_field(worklog, "created")
					process_field(worklog, "updated")
					process_field(worklog, "started")
					project.add_comment(worklog)
					db.write_project_worklog_to_disk(project_name, worklog)
			# Clean up unused fields
			del issue["fields"]
			del issue["project"]
			del issue["changelog"]
			del issue["comment"]
			if "worklog" in issue:
				del issue["worklog"]
			project.add_issue(issue)
			db.write_project_issue_to_disk(project_name, issue)
			lg.step_action()
		lg.end_action()
		lastcrawlcomplete = True
	except Exception:
		# Catch any exception and print it before exiting
		lastcrawlcomplete = False
		sys.exit(traceback.format_exc())
	finally:
		# This line of code is always executed even if an exception occurs
		db.finalize_write_to_disk(project_name, project, crawldatetime, lastcrawlcomplete)

if __name__ == "__main__":
	if ((not sys.argv) or len(sys.argv) <= 1):
		print_usage()
	elif(os.path.exists(sys.argv[1])):
		projects = read_file_in_lines(sys.argv[1])
		for project in projects:
			download_project(project)
	elif(len(sys.argv[1]) > 0):
		download_project(sys.argv[1])
	else:
		print_usage()

