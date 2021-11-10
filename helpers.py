import json
from dateutil.parser import parse

def process_field(jiraobject, fieldkey, fieldtype="datetime", fieldvalue=None):
	"""
	Processes the field of the given Jira object and transforms the numbers to integers and floats,
	and the date strings to datetime objects.

	:param jiraobject: the Jira object (issue, comment or event) of which the field is processed.
	:param fieldkey: the key of the field that is processed.
	:param fieldtype: the type to trasform the value of the field to, default is "datetime".
	:param fieldvalue: the value of the field that is processed, default is jiraobject[fieldkey].
	"""
	if fieldvalue == None:
		fieldvalue = jiraobject[fieldkey]
	if fieldtype == "int":
		jiraobject[fieldkey] = int(fieldvalue)
	elif fieldtype == "float":
		jiraobject[fieldkey] = float(fieldvalue)
	elif fieldtype == "datetime":
		jiraobject[fieldkey] = parse(fieldvalue)
	elif fieldkey == "lastpubliccommentdate":
		jiraobject[fieldkey] = parse(fieldvalue)
	else:
		jiraobject[fieldkey] = fieldvalue

def extract_users(jiraobject, jira_api_address):
	"""
	Iterates over the fields of the given Jira object and extracts the users. The user objects
	are returned and their keys are put in their place.

	:param jiraobject: the Jira object (issue, comment or event) from where the users are extracted.
	:param jira_api_address: the address of the Jira API.
	:returns: the found user objects.
	"""
	for key in jiraobject:
		if type(jiraobject[key]) is dict and "key" in jiraobject[key] and "self" in jiraobject[key] \
				and jiraobject[key]["self"].startswith(jira_api_address + "user?username"):
			user = jiraobject[key]
			user["id"] = user["key"]
			jiraobject[key] = jiraobject[key]["key"]
			yield user
		if type(jiraobject[key]) is list:
			for i, elem in enumerate(jiraobject[key]):
				if type(elem) is dict and "key" in elem and "self" in elem \
						and elem["self"].startswith(jira_api_address + "user?username"):
					user = jiraobject[key][i]
					user["id"] = user["key"]
					jiraobject[key][i] = jiraobject[key][i]["key"]
					yield user

def get_issue_fields(jdownloader, custom_fields_api_address):
	"""
	Posts a request using an instance of JiraDownloader and returns the fields
	of the Jira instance. For Jira fields, they are returned as-is (e.g. name), while
	the custom fields are renamed (e.g. custom2442 is replaced by its name in lower case
	without punctuation-that is description). The fields are returned as a dictionary with keys
	having the original key of each field and values having the new key of each field. For
	example, a returned dictionary would be {"name": "name", "custom2442": "description", ...}.
	Also, this function returns the type of each field as a separate dictionary, for example
	{"name": "string", "custom2442": "string", ...}.

	:param jdownloader: an instance of JiraDownloader.
	:param custom_fields_api_address: the address from where the fields are downloaded.
	:returns: a dictionary containing the old field keys as keys and the new field keys as values
	          and a dictionary containing the old field keys as keys and the types as values.
	"""
	fields = jdownloader.download_object(custom_fields_api_address)
	fieldids = {}
	fieldtypes = {}
	for field in [field for field in fields if not field["custom"]]:
		fieldids[field["id"]] = field["id"]
		fieldtypes[field["id"]] = field.get("schema", {"type": None})["type"]
		if fieldtypes[field["id"]] == "number" and "schema" in field and "custom" in field["schema"] and field["schema"]["custom"].endswith("float"):
			fieldtypes[field["id"]] = "float"
		elif fieldtypes[field["id"]] == "number":
			fieldtypes[field["id"]] = "int"
	for field in [field for field in fields if field["custom"]]:
		fieldid = "".join(c.lower() for c in field["name"] if c.isalnum())
		if fieldid in fieldids.values():
			i = 2
			while fieldid + str(i) in fieldids.values():
				i += 1
			fieldid = fieldid + str(i)
		fieldids[field["id"]] = fieldid
		fieldtypes[field["id"]] = field.get("schema", {"type": None})["type"]
		if fieldtypes[field["id"]] == "number" and "schema" in field and "custom" in field["schema"] and field["schema"]["custom"].endswith("float"):
			fieldtypes[field["id"]] = "float"
		elif fieldtypes[field["id"]] == "number":
			fieldtypes[field["id"]] = "int"
	return fieldids, fieldtypes

def get_size_of_json_object_in_KB(json_obj):
	"""
	Returns the size of a json object in KB. This is used to check that the relevant record can
	be stored to databases having a document size limitation.

	:param json_obj: the json object of which the size is measured.
	:returns: the size of the given json object in KB.
	"""
	return len(json.dumps(json_obj, indent = 4, default=str).encode("utf-8")) / 1024

def get_number_of(jdownloader, project_api_address, parameter = None):
	"""
	Posts a request using an instance of JiraDownloader and returns the number of
	a given statistic (e.g. number of issues, number of commits, etc.).

	:param jdownloader: an instance of JiraDownloader.
	:param project_api_address: the address from where the statistic is downloaded.
	:param parameter: an optional parameter for the statistic.
	:returns: the value for the statistic as an absolute number.
	"""
	r = jdownloader.download_request(project_api_address, ["maxResults=1"] if parameter == None else ["maxResults=1", parameter])
	data = json.loads(r.text or r.content) if r.status_code != 204 else {}
	return data["total"]

def read_file_in_lines(filename):
	"""
	Reads a file into lines. If the file is comma-separated with ';' then the first column is read

	:param filename: the filename of the file to be read.
	:returns: a list with the lines of the file.
	"""
	with open(filename) as infile:
		lines = infile.readlines()
	return [line.strip().split(';')[0] for line in lines]

def print_usage():
	"""
	Prints the usage information of this python file.
	"""
	print("Usage: python jidownloader.py arg")
	print("where arg can be one of the following:")
	print("   project name (e.g. MyProject)")
	print("   path to txt file containing project names")

