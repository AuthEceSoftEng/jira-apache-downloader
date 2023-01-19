jira-apache-downloader
======================
This is a tool that allows retrieving Jira issue tracking data from the [Apache Jira server](https://issues.apache.org/jira/rest/api/2/).
It is based on the JIDownloader tool (available [here](https://github.com/thdiaman/JIDownloader)), and is part of the paper
`Jira Issue Tracking Data of Apache Software Foundation` that has been submitted. The dataset is available in [this link](https://zenodo.org/record/5665896).

Prerequisites
-------------
The python requirements are available in file `requirements.txt` and may be installed using the command
`pip install -r requirements.txt`. To run this tool, you must have a Jira account in the [Apache Jira server](https://issues.apache.org/jira/rest/api/2/).
Furthermore, you must set a MongoDB instance (and set up users - check file instructions.md of this repo). These details must be set in file `properties.py`.

Execution Instructions
----------------------
To run the tool, one must first correctly assign the properties in file `properties.py`.
After that, the tool can be executed by running `python jidownloader.py [jira_project_name_or_list_of_names]`,
where `jira_project_name_or_list_of_names` must be replaced by either one of the following:
- a Jira project name (e.g. `MyJiraProject`)
- a list of Jira project names, as a text file where each file is a Jira project name
If a project already exists, then its data are updated.

The main parameters are the following:
- `JiraAPI`: the API URL of the Jira installation, leave this to `https://issues.apache.org/jira/rest/api/2/` for the Apache Jira installation
- `JiraCredentials`: the username and the password of your Jira account (provided as a tuple, e.g. `('myusername', 'mypassword')`)
- `JiraWaitTimeInSeconds`: the time for the tool to wait between consecutive requests
- `update_existing_projects`: controls whether the existing (already downloaded) projects will be updated or skipped
- `verbose`: controls the messages in the standard output (0 for no messages, 1 for simple messages, and 2 for progress bars)
- `always_write_to_disk`: controls whether the project data will be written on download (always) or after fully downloading them (either in database or at the disk for debugging purposes)

The tool supports two storage options: disk storage and MongoDB. The MongoDB storage is the default and is the one supported. Disk storage exists only for debugging purposes. If disk storage is preferred one must set the `use_database` and `dataFolderPath` parameters of the properties file to `"disk"` and to the path where the data will be downloaded accordingly.

For database storage, one has to download and set up [MongoDB](https://www.mongodb.com/) and then set the
parameter `use_database` to `"mongo"`. The `database_host_and_port` must also be set and must include the credentials, the hostname, and the port of the database. See file instructions.md of this repo for setting up the MongoDB instance. Finally, `num_bulk_operations`: controls the number of operations that are sent as a bulk to the database (optimization parameter)

Citation information
--------------------
If your use this tool or the corresponding dataset in your work, you can cite it using the following bibtex entry:

```
@unpublished{JiraApacheData,
  author = {Themistoklis Diamantopoulos, Dimitrios Nastos and Andreas Symeonidis},
  title = {Jira Issue Tracking Data with Semantic Topics},
  year = {2023},
  note = {Paper submitted}
}
```


