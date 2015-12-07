# OMERO.webexporter

## Quickstart: Downloading files for an object from OMERO using the helper

To download all the files for an object from OMERO, the OMERO.webexporter extension must have been added to the target servers OMERO.web installation.

* Download [webexporter_helper.py](https://raw.githubusercontent.com/sorgerlab/OMERO.webexporter/master/webexporter_helper.py)
* From the command line run: `python webexporter_helper.py https://example.com plate 123 output_dir`

This will cause all files for the `plate` object `123` to be downloaded into the `output_dir`.

#### Caveats

* Currently the files are downloaded without any notion of hierarchy, so all files will be in the specified output directory. This can be problematic for two reasons.
  * If a set of files contains multiple files with the same names, then there will be collisions. Currently this is disallowed and an error is thrown before attempting download.
  * If a multifile format relies on the original structure of the data according to somewhat inbuilt manifest, then this will be broken and images may not be readable.
  
These caveats are not currently issues for the intended purpose of OMERO.webexporter within the [HMS LINCS](http://lincs.hms.harvard.edu/) Project, so have not been addressed, but may be resolved at a later date if required.

## API

It is possible to make use of the web API directory instead of using the helper script. There are 2 functions offered.

* `https://example.com/webexporter/get_files_for_obj/<object_type>/<object_id>`

  Exampled returned JSON:
  
  ``` JSON
  [
    {
      "hash": "21930034ec08d04c8ec50d2175d134be3badb0bf",
      "id": "871",
      "name": "example_file.dv",
      "size": "98765"
    },
    {
      "hash": "e75f4b85ec277f38f617b73c74b6c576854d6099",
      "id": "872",
      "name": "example_file.txt",
      "size": "24"
    }
  ]
  
  ```
  
* `https://example.com/webexporter/download_file/<file_id>`

  Returns an individual file.

## Installation (For OMERO systems administrators)

* Clone this repository into a directory called `webexporter`. This directory should be on the `PYTHONPATH`, or in the OMERO `lib/python/omeroweb/` directory.

  `$ git clone https://github.com/sorgerlab/OMERO.webexporter.git webexporter`

* Add the app to OMERO.web :

  `$ bin/omero config append omero.web.apps '"webexporter"'`   # NB: double quotes
  
  Or on Windows
  
  `$ bin/omero config append omero.web.apps "\"webexporter\""` # Windows requires escaped double quotes
  
* Restart web:
  ```
  $ bin/omero web stop
  $ bin/omero web start
  ```
