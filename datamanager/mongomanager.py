import pymongo
from datamanager.project import Project
from datamanager.filemanager import FileManager
from datamanager.databasemanager import DatabaseManager
from properties import always_write_to_disk, database_host_and_port
from bson import json_util
from pymongo.errors import DocumentTooLarge
from helpers import get_size_of_json_object_in_KB

class MongoDBManager(DatabaseManager, FileManager):
	"""
	Class that implements a MongoDB manager. To use this class, you must first call the method
	initialize_write_to_disk, then optionally call any other method for writing data to
	disk, and finally call the method finalize_write_to_disk.
	"""
	def __init__(self):
		"""
		Initializes this DB manager.
		"""
		self.client = pymongo.MongoClient(database_host_and_port)
		self.db = self.client["jidata"]
		self.projects = self.db["projects"]
		self.issues = self.db["issues"]
		self.users = self.db["users"]
		self.events = self.db["events"]
		self.comments = self.db["comments"]
		self.worklogs = self.db["worklogs"]

	def initialize_write_to_disk(self, project_name):
		"""
		Initializes the writing of a project to disk. In the case of MongoDB, it does nothing.

		:param project_name: the name of the project.
		"""
		pass

	def read_project_from_disk(self, project_name):
		"""
		Reads a project from disk given the name of the project.

		:param project_name: the name of the project to be read from disk.
		:returns: an object of type Project.
		"""
		project = Project()
		project["info"] = self.projects.find_one({"projectname": project_name})
		project["issues"] = {obj["_id"]: obj for obj in self.issues.find({"projectname": project_name})}
		project["users"] = {obj["_id"]: obj for obj in self.users.find({"projectname": project_name})}
		project["events"] = {obj["_id"]: obj for obj in self.events.find({"projectname": project_name})}
		project["comments"] = {obj["_id"]: obj for obj in self.comments.find({"projectname": project_name})}
		project["worklogs"] = {obj["_id"]: obj for obj in self.worklogs.find({"projectname": project_name})}
		return project

	def project_exists(self, project_name):
		"""
		Check if a project exists in the disk given the name of the project. The
		existence of the project is determined by whether it has an info.json file.

		:param project_name: the name of the project to be read from disk.
		:returns: True if the project exists, or False otherwise.
		"""
		return bool(self.projects.find_one({"projectname": project_name}))

	def finalize_write_to_disk(self, project_name, project, crawldatetime, lastcrawlcomplete):
		"""
		Finalizes the writing of a project to disk. Closes any open buffers.

		:param project_name: the name of the project to be written to disk.
		:param project: the project data to be written to disk.
		:param crawldatetime: the time that this crawl started.
		:param lastcrawlcomplete: the status of the last crawl, either True for complete of False otherwise.
		"""
		if not always_write_to_disk:
			project["info"]["_id"] = project["info"]["id"]
			project["info"]["projectname"] = project_name
			self.projects.update_one({"_id": project["info"]["_id"]}, {"$set": project["info"]}, upsert = True)
			for issue in project["issues"].values():
				issue["_id"] = issue["id"]
				issue["projectname"] = project_name
			self.update_multiple(self.issues, project["issues"].values(), upsert = True)
			for user in project["users"].values():
				user["_id"] = user["key"]
				user["projectname"] = [project_name]
				user_from_db = self.users.find_one({"_id": user["_id"]})
				if user_from_db != None:
					user["projectname"] += user_from_db["projectname"]
			self.update_multiple(self.users, project["users"].values(), upsert = True)
			for event in project["events"].values():
				event["_id"] = event["id"]
				event["projectname"] = project_name
			self.update_multiple(self.events, project["events"].values(), upsert = True)
			for comment in project["comments"].values():
				comment["_id"] = comment["id"]
				comment["projectname"] = project_name
			for c in list(project["comments"].keys()):
				if get_size_of_json_object_in_KB(project["comments"][c]) < 15000:
					del project["comments"][c]
			self.update_multiple(self.comments, project["comments"].values(), upsert = True)
			for worklog in project["worklogs"].values():
				worklog["_id"] = worklog["id"]
				worklog["projectname"] = project_name
			self.update_multiple(self.worklogs, project["worklogs"].values(), upsert = True)
		project["info"]["lastcrawlcomplete"] = lastcrawlcomplete
		project["info"]["lastcrawled"] = crawldatetime
		self.projects.update_one({"_id": project["info"]["_id"]}, {"$set": project["info"]}, upsert = True)
		self.client.close()

	def write_project_info_to_disk(self, project_name, info):
		"""
		Writes the info of a project to disk.

		:param project_name: the name of the project.
		:param info: the info to be written to disk.
		"""
		if always_write_to_disk:
			info["_id"] = info["id"]
			info["projectname"] = project_name
			self.projects.update_one({"_id": info["_id"]}, {"$set": info}, upsert = True)

	def write_project_issue_to_disk(self, project_name, issue):
		"""
		Writes an issue of a project to disk.

		:param project_name: the name of the project.
		:param issue: the issue to be written to disk.
		"""
		if always_write_to_disk:
			issue["_id"] = issue["id"]
			issue["projectname"] = project_name
			self.issues.update_one({"_id": issue["_id"]}, {"$set": issue}, upsert = True)

	def write_project_user_to_disk(self, project_name, user):
		"""
		Writes a user of a project to disk.

		:param project_name: the name of the project.
		:param user: the user to be written to disk.
		"""
		if always_write_to_disk:
			user["_id"] = user["key"]
			user["projectname"] = [project_name]
			user_from_db = self.users.find_one({"_id": user["_id"]})
			if user_from_db != None:
				user["projectname"] += user_from_db["projectname"]
			self.users.update_one({"_id": user["_id"]}, {"$set": user}, upsert = True)

	def write_project_event_to_disk(self, project_name, event):
		"""
		Writes an event of a project to disk.

		:param project_name: the name of the project.
		:param event: the event to be written to disk.
		"""
		if always_write_to_disk:
			event["_id"] = event["id"]
			event["projectname"] = project_name
			self.events.update_one({"_id": event["_id"]}, {"$set": event}, upsert = True)

	def write_project_comment_to_disk(self, project_name, comment):
		"""
		Writes a comment of a project to disk.

		:param project_name: the name of the project.
		:param comment: the comment to be written to disk.
		"""
		if always_write_to_disk:
			comment["_id"] = comment["id"]
			comment["projectname"] = project_name
			if get_size_of_json_object_in_KB(comment) < 15000:
				self.comments.update_one({"_id": comment["_id"]}, {"$set": comment}, upsert = True)

	def write_project_worklog_to_disk(self, project_name, worklog):
		"""
		Writes a worklog of a project to disk.

		:param project_name: the name of the project.
		:param worklog: the worklog to be written to disk.
		"""
		if always_write_to_disk:
			worklog["_id"] = worklog["id"]
			worklog["projectname"] = project_name
			self.worklogs.update_one({"_id": worklog["_id"]}, {"$set": worklog}, upsert = True)
