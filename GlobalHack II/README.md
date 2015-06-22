GlobalHack 2
===========

##### SETUP
```
- Install git
- Install python 2.7.X
- Install pip (e.g. sudo easy_install pip)
$ sudo pip install -r requirements.txt
```

##### DATABASES
```
For Postgres: Install postgres locally and use default port (5432).
For Sqlite: Sqlite comes installed with Python by default and requires no setting up. You can just skip to the next step if you want to run it with sqlite.
$ python manage.py syncdb
```

##### RUNNING THE PROCESSOR
```
$ pip install nltk
$ python
>>> import nltk
>>> nltk.download()
Install "all" in the GUI that pops up.

Download this: PDFMiner
https://pypi.python.org/pypi/pdfminer/
- Unzip
- cd to directory
$ sudo python setup.py install

Now to run the processor, navigate to /processor/.
The files in the various directories serve as the different corpus sources - they are a subset of the files given in the competition.
To process them all and store the resulting ontologies in your database, run:
$ python ontology.py
```

##### RUNNING THE SERVER
```
$ python manage.py runserver
Open browser to http://127.0.0.1:8000
```

##### Notes
```
- Right now the processing of the source files into an ontology is done in a single step, and to add new files to the ontology you need to add them to the appropriate "corpus" directory inside processor/ and then rerun onotology.py - long term, we intended on separating the processing into two steps so we can store the processed files in an intermediate corpus state in the database (before the ontology is created) and add new files individually with low overhead.
- Their are a few bottlenecks in the code right now that cause loading all the files in a corpus at once to take a loooong time. These have been labeled. We have ideas on how to resolve them, but did not have time to in the competition. Boris can elaborate on it.
- The CSV processor is currently on Boris' local machine, and he's attempting to resolve a bug with it - once that's done, he can send that along as well.
```

##### DOCS
[Natural Language Toolkit](http://www.nltk.org/)