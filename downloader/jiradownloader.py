import re
import sys
import json
import time
import requests
from urllib3.exceptions import TimeoutError

class JiraDownloader:
	"""
	Class that implements a downloader for the Jira API v2.
	"""
	def __init__(self, jira_url, username, password=None, wait_time_in_seconds=1):
		"""
		Initializes this Jira API Downloader.

		:param jira_url: the API URL where Jira is set up.
		:param username: the Jira username (or the credentials as a tuple if no password is given).
		:param password: the Jira password (or None if the credentials are given as a tuple in the username parameter).
		:param wait_time_in_seconds: the time to wait until the next request.
		"""
		self.jira_url = jira_url
		self.credentials = (username, password) if password != None else username
		self.wait_time_in_seconds = wait_time_in_seconds
		if not self.check_credentials(self.credentials):
			sys.stdout.write("Wrong Credentials!\n")
			exit()

	def wait_after_request(self):
		"""
		Waits the specified amount of seconds after every request.
		"""
		#sys.stdout.write('\nRequest made. Waiting for ' + str(self.wait_time_in_seconds) + ' seconds..')
		time.sleep(self.wait_time_in_seconds)
		#sys.stdout.write(' Done!!\n\n')

	def check_credentials(self, credentials):
		"""
		Checks whether the credentials are correct.

		:param credentials: the Jira credentials as a tuple (username, password).
		:returns: True if the credentials are correct, or False otherwise.
		"""
		try:
			r = requests.get(self.jira_url + "project", auth=credentials)
			if int(r.status_code) == 200:
				self.wait_after_request()
				return True
			else:
				return False
		except:
			return False

	def download_request(self, address, parameters = None, headers = None):
		"""
		Implements a download request.

		:param address: the URL of the request.
		:param parameters: the parameters of the request.
		:param headers: the headers of the request.
		:returns: the response of the request.
		"""
		for _ in range(3):
			try:
				if parameters:
					parameters = '?' + '&'.join(parameters)
				else:
					parameters = ""
				if headers:
					headers = {headers.split(':')[0].strip() : headers.split(':')[1].strip()}
				else:
					headers = {}
				reserved_keywords = ["EXEC", "TRANSACTION", "FOR"] # these project names are jql reserved keywords so they must be escaped
				for keyword in reserved_keywords:
					parameters = re.sub("project=" + keyword + "\\b", "project='" + keyword + "'", parameters)
				r = requests.get(address + parameters, headers = headers, auth = self.credentials)
				self.wait_after_request()
				return r
			except TimeoutError:
				return None

	def download_object(self, address, parameters = None, per_page=50):
		"""
		Downloads an object of the Jira API.

		:param address: the URL of the Jira request.
		:param parameters: the parameters of the Jira request.
		:param per_page: the number of objects per page if the object is paginated.
		:returns: the contents of the response of the request.
		"""
		if parameters:
			parameters.append("maxResults=" + str(per_page))
		else:
			parameters = ["maxResults=" + str(per_page)]
		r = self.download_request(address, parameters)
		if r.ok:
			content = json.loads(r.text or r.content) if r.status_code != 204 else {}
			return content

	def download_paginated_object(self, address, object_name, parameters = None, per_page=50):
		"""
		Downloads a paginated object of the Jira API.

		:param address: the URL of the Jira request.
		:param object_name: the name of the object that is downloaded.
		:param parameters: the parameters of the Jira request.
		:param per_page: the number of objects per page.
		:returns: a generator containing all the pages of the response of the request.
		"""
		if parameters:
			parameters.append("maxResults=" + str(per_page))
		else:
			parameters = ["maxResults=" + str(per_page)]
		r = self.download_request(address, parameters)
		if r.ok:
			data = json.loads(r.text or r.content)
			for obj in data[object_name]:
				yield obj

		while data["startAt"] < data["total"] and len(data[object_name]) > 0:
			r = self.download_request(address, parameters + ["startAt=" + str(data["startAt"] + data["maxResults"])])
			if r.ok:
				data = json.loads(r.text or r.content)
				for obj in data[object_name]:
					yield obj
