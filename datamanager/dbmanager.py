import os
from datamanager.project import Project
from datamanager.filemanager import FileManager
from properties import dataFolderPath, always_write_to_disk

class DBManager(FileManager):
	"""
	Class that implements a DB manager. To use this class, you must first call the method
	initialize_write_to_disk, then optionally call any other method for writing data to
	disk, and finally call the method finalize_write_to_disk.
	"""
	def __init__(self):
		"""
		Initializes this DB manager.
		"""
		self.create_folder_if_it_does_not_exist(dataFolderPath)

	def initialize_write_to_disk(self, project_name):
		"""
		Initializes the writing of a project to disk. Creates all the necessary directories.

		:param project_name: the name of the project to be written to disk.
		"""
		rootfolder = os.path.join(dataFolderPath, project_name)
		self.create_folder_if_it_does_not_exist(rootfolder)
		self.create_folder_if_it_does_not_exist(os.path.join(rootfolder, "issues"))
		self.create_folder_if_it_does_not_exist(os.path.join(rootfolder, "users"))
		self.create_folder_if_it_does_not_exist(os.path.join(rootfolder, "events"))
		self.create_folder_if_it_does_not_exist(os.path.join(rootfolder, "comments"))

	def read_project_from_disk(self, project_name):
		"""
		Reads a project from disk given the name of the project that is also the folder
		of the project.

		:param project_name: the name of the project to be read from disk.
		:returns: an object of type Project.
		"""
		project = Project()
		rootfolder = os.path.join(dataFolderPath, project_name)
		project["info"] = self.read_json_from_file_if_it_exists(os.path.join(rootfolder, "info.json"))
		project["issues"] = self.read_jsons_from_folder(os.path.join(rootfolder, "issues"), "id")
		project["users"] = self.read_jsons_from_folder(os.path.join(rootfolder, "users"), "id")
		project["events"] = self.read_jsons_from_folder(os.path.join(rootfolder, "events"), "id")
		project["comments"] = self.read_jsons_from_folder(os.path.join(rootfolder, "comments"), "id")
		return project

	def project_exists(self, project_name):
		"""
		Check if a project exists in the disk given the name of the project that is also the folder
		of the project. The existence of the project is determined by whether it has an info.json file.

		:param project_name: the name of the project to be read from disk.
		:returns: True if the project exists, or False otherwise.
		"""
		return os.path.exists(os.path.join(dataFolderPath, project_name, "info.json"))

	def finalize_write_to_disk(self, project_name, project, crawldatetime, lastcrawlcomplete):
		"""
		Finalizes the writing of a project to disk. Closes any open buffers.

		:param project_name: the name of the project to be written to disk.
		:param project: the project data to be written to disk.
		:param crawldatetime: the time that this crawl started.
		:param lastcrawlcomplete: the status of the last crawl, either True for complete of False otherwise.
		"""
		if not always_write_to_disk:
			rootfolder = os.path.join(dataFolderPath, project_name)
			self.write_json_to_file(os.path.join(rootfolder, "info.json"), project["info"])
			for issue in project["issues"].values():
				self.write_json_to_file(os.path.join(rootfolder, "issues", str(issue["id"]) + ".json"), issue)
			for user in project["users"].values():
				self.write_json_to_file(os.path.join(rootfolder, "users", str(user["key"]) + ".json"), user)
			for event in project["events"].values():
				self.write_json_to_file(os.path.join(rootfolder, "events", str(event["id"]) + ".json"), event)
			for comment in project["comments"].values():
				self.write_json_to_file(os.path.join(rootfolder, "comments", str(comment["id"]) + ".json"), comment)
		project["info"]["lastcrawlcomplete"] = lastcrawlcomplete
		project["info"]["lastcrawled"] = crawldatetime
		rootfolder = os.path.join(dataFolderPath, project_name)
		self.write_json_to_file(os.path.join(rootfolder, "info.json"), project["info"])

	def write_project_info_to_disk(self, project_name, info):
		"""
		Writes the info of a project to disk.

		:param project_name: the name of the project.
		:param info: the info to be written to disk.
		"""
		if always_write_to_disk:
			rootfolder = os.path.join(dataFolderPath, project_name)
			self.write_json_to_file(os.path.join(rootfolder, "info.json"), info)

	def write_project_issue_to_disk(self, project_name, issue):
		"""
		Writes an issue of a project to disk.

		:param project_name: the name of the project.
		:param issue: the issue to be written to disk.
		"""
		if always_write_to_disk:
			rootfolder = os.path.join(dataFolderPath, project_name)
			self.write_json_to_file(os.path.join(rootfolder, "issues", str(issue["id"]) + ".json"), issue)

	def write_project_user_to_disk(self, project_name, user):
		"""
		Writes a user of a project to disk.

		:param project_name: the name of the project.
		:param user: the user to be written to disk.
		"""
		if always_write_to_disk:
			rootfolder = os.path.join(dataFolderPath, project_name)
			self.write_json_to_file(os.path.join(rootfolder, "users", str(user["key"]) + ".json"), user)

	def write_project_event_to_disk(self, project_name, event):
		"""
		Writes an event of a project to disk.

		:param project_name: the name of the project.
		:param event: the event to be written to disk.
		"""
		if always_write_to_disk:
			rootfolder = os.path.join(dataFolderPath, project_name)
			self.write_json_to_file(os.path.join(rootfolder, "events", str(event["id"]) + ".json"), event)

	def write_project_comment_to_disk(self, project_name, comment):
		"""
		Writes a comment of a project to disk.

		:param project_name: the name of the project.
		:param comment: the comment to be written to disk.
		"""
		if always_write_to_disk:
			rootfolder = os.path.join(dataFolderPath, project_name)
			self.write_json_to_file(os.path.join(rootfolder, "comments", str(comment["id"]) + ".json"), comment)

	def write_project_worklog_to_disk(self, project_name, worklog):
		"""
		Writes a worklog of a project to disk.

		:param project_name: the name of the project.
		:param worklog: the worklog to be written to disk.
		"""
		if always_write_to_disk:
			rootfolder = os.path.join(dataFolderPath, project_name)
			self.write_json_to_file(os.path.join(rootfolder, "worklogs", str(worklog["id"]) + ".json"), worklog)

