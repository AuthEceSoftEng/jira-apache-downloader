import pymongo
from properties import database_host_and_port

if __name__ == "__main__":
	client = pymongo.MongoClient(database_host_and_port)
	db = client["jidata"]
	db["issues"].create_index('projectname')
	db["users"].create_index('projectname')
	db["comments"].create_index('issue')
	db["comments"].create_index('projectname')
	db["events"].create_index('issue')
	db["events"].create_index('projectname')
	db["worklogs"].create_index('issue')
	db["worklogs"].create_index('projectname')
