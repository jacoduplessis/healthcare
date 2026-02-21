# Prompt 1

This folder contains a zip file with multiple CSVs. They need to be extracted and imported into a SQLite database. The table names should "geography", "households" etc. Create a python import script.

Create a COICOP lookup from the international standard for human descriptions of codes.

Then explore the data, to help the reader understand the size of the data and the contents. Output your findings in a markdown file data.md

Read the PDF document that contains Metadata about the file. Based on this, run some queries and do analyis. Look for and find interesting trends in the data. Put your findings in a file findings.md
Do a broad exploration first, then look into the following subject: out-of-pocket medical expenses for people on medical aid vs people not on medical aid. Look at how these expenses increase relative to inflation.

Create HTML versions of data.md and findings.md

Then build a web app that allows the user to run queries on the data. Use uv to boostrap a Python project, then use flask and SQLalchemy to setup the DB access.
Design an interface that would allow someone that does not have a masters degree in stats to also interrogate the data. Using vega-lite, allow the user to visualise queries. Create a section
where you show how to do this with some example queries and charts.
Use bootstrap v5 for styling.

Add gunicorn to the webapp and create a Dockerfile. Then init a git repo, and add a GitHub CI file that builds the Docker image. The SQlite file should be baked into the docker image. Add the zip and pdf into the repo, and then inside the Dockerfile, build the database by extracting the zip and running the data import script.

# Prompt 2

Do a deep analysis on the following subject.

Compare whether medical scheme members have statistically bigger co-payments for healthcare than non-scheme members, using a nearest neighbour statistical approach. Do a national and provincial analysis.

Be very thorough - the output should good enough for publishing in an academic journal. Place the output in report.md, then also typset it using Typst. place that in report.typ. Use the typst CLI to create a PDF.

# Prompt 3

Create a readme.md with an overview of the project.

