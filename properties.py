# Set this to your Jira installation API URL
JiraAPI = "https://issues.apache.org/jira/rest/api/2/"

# Set this to your Jira username and password
JiraCredentials = ('USERNAME', 'PASSWORD')

# Set this to the time between consecutive requests
JiraWaitTimeInSeconds = 2

# Set this to False to skip existing projects
update_existing_projects = True

# Set to 0 for no messages, 1 for simple messages, and 2 for progress bars
verbose = 2

# Select how to write to disk (or how to send queries to the database)
always_write_to_disk = True

# Change these settings to store data in disk/database
use_database = 'mongo' # (available options: disk, mongo)
dataFolderPath = 'data' # Set this to the folder where data are downloaded

# Database settings
database_host_and_port = "mongodb://USERNAME:PASSWORD@HOSTNAME:PORT/"  # change this to the hostname and port of your database
num_bulk_operations = 1000 # set the number of operations that are sent as a bulk to the database
