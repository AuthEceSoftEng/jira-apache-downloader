from datetime import datetime
from dateutil.parser import parse

class Project(dict):
	"""
	Class that includes the data of a Jira project. This class is implemented as a dict
	and includes also several helper functions for adding data and checking for data.
	"""
	def info_exists(self):
		"""
		Checks if the info of the project exists.

		:returns: True if the project info exists, or False otherwise.
		"""
		return bool(self["info"])

	def add_info(self, info):
		"""
		Adds the info of the project.

		:param info: the info to be added to the project.
		"""
		self["info"] = info

	def issue_exists(self, issue):
		"""
		Checks if the given issue exists in the project.

		:param issue: the issue to be checked.
		:returns: True if the given issue exists in the project, or False otherwise.
		"""
		return issue["id"] in self["issues"]

	def add_issue(self, issue):
		"""
		Adds an issue to the project.

		:param issue: the issue to be added to the project.
		"""
		self["issues"][issue["id"]] = issue

	def user_exists(self, user):
		"""
		Checks if the given user exists in the project.

		:param user: the user to be checked.
		:returns: True if the given user exists in the project, or False otherwise.
		"""
		return user["key"] in self["users"]

	def add_user(self, user):
		"""
		Adds a user to the project.

		:param user: the user to be added to the project.
		"""
		self["users"][user["key"]] = user

	def event_exists(self, event):
		"""
		Checks if the given event exists in the project.

		:param event: the event to be checked.
		:returns: True if the given event exists in the project, or False otherwise.
		"""
		return event["id"] in self["events"]

	def add_event(self, event):
		"""
		Adds an event to the project.

		:param event: the event to be added to the project.
		"""
		self["events"][event["id"]] = event

	def comment_exists(self, comment):
		"""
		Checks if the given comment exists in the project.

		:param comment: the comment to be checked.
		:returns: True if the given comment exists in the project, or False otherwise.
		"""
		return comment["id"] in self["comments"]

	def add_comment(self, comment):
		"""
		Adds a comment to the project.

		:param comment: the comment to be added to the project.
		"""
		self["comments"][comment["id"]] = comment

	def worklog_exists(self, worklog):
		"""
		Checks if the given worklog exists in the project.

		:param worklog: the worklog to be checked.
		:returns: True if the given worklog exists in the project, or False otherwise.
		"""
		return worklog["id"] in self["worklogs"]

	def add_worklog(self, worklog):
		"""
		Adds a worklog to the project.

		:param worklog: the comment to be added to the project.
		"""
		self["worklogs"][worklog["id"]] = worklog

	def last_crawl_complete(self):
		"""
		Returns true if the last crawl was completed normally, or false otherwise.

		:returns: true if the last crawl was completed normally, or false otherwise.
		"""
		return self["info"]["lastcrawlcomplete"] if "lastcrawlcomplete" in self["info"] else False

	def last_crawled(self):
		"""
		Returns the datetime when the project was last crawled.

		:returns: the datetime when the project was last crawled as a datetime object.
		"""
		return parse(str(self["info"]["lastcrawled"])) if "lastcrawled" in self["info"] else None

	def last_updated(self):
		"""
		Returns the update datetime of the last updated issue.

		:returns: the update datetime of the last updated issue as a datetime object.
		"""
		return max(datetime.strptime(str(issue["updated"]), "%Y-%m-%d %H:%M:%S") for issue in self["issues"].values()) if len(self["issues"]) > 0 else None
