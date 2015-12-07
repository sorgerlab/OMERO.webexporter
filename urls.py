import django
if django.VERSION < (1, 6):
    from django.conf.urls.defaults import *
else:
    from django.conf.urls import *

from webexporter import views

urlpatterns = patterns(
    'django.views.generic.simple',

    # Get file list involved in object
    url(
        r'^get_files_for_obj/'
        r'(?P<obj_type>project|dataset|image|screen|plate|well)?/'
        r'(?P<obj_id>[0-9]+)$',
        views.get_files_for_obj,
        name="webexporter_get_files_for_obj"),

    url(
        r'^download_file/'
        r'(?P<file_id>[0-9]+)$',
        views.download_file,
        name="webexporter_download_file"),
)
