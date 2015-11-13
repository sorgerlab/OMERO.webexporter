from django.http import (HttpResponse, HttpResponseNotAllowed,
                         HttpResponseBadRequest)

from omeroweb.webclient.decorators import login_required
from omeroweb.http import HttpJsonResponse

import omero
from omero.rtypes import rstring, rlong, wrap, unwrap

from copy import deepcopy

from omeroweb.webclient import tree

import json
import logging

logger = logging.getLogger(__name__)


@login_required(setGroupContext=True)
def get_files_for_obj(request, conn=None, **kwargs):

    if not request.GET:
        return HttpResponseNotAllowed('Methods allowed: GET')

    # Check that one and only one object was requested
    args = 0

    image_id = request.GET.get('imageId')
    dataset_id = request.GET.get('datasetId')
    project_id = request.GET.get('projectId')
    plate_id = request.GET.get('plateId')
    screen_id = request.GET.get('screenId')

    

    reduce(lambda x, y: , [image_id, dataset_id, project_id, plate_id, screen_id])

    if not obj_id:
        return HttpResponseBadRequest('Object ID required')

    obj_id = long(obj_id)

    group_id = request.session.get('active_group')
    if group_id is None:
        group_id = conn.getEventContext().groupId

    # Query config
    params = omero.sys.ParametersI()
    service_opts = deepcopy(conn.SERVICE_OPTS)
    service_opts.setOmeroGroup(group_id)
    params.add('oid', wrap(obj_id))

    qs = conn.getQueryService()

    # Obj might be Image, Dataset, Project, Plate, Screen

    # Get the type of the object we have been asked to retrieve
    q = """
        SELECT

        """


    # Get the tags that are applied to individual images
    q = """
        SELECT DISTINCT itlink.parent.id, itlink.child.id
        FROM ImageAnnotationLink itlink
        WHERE itlink.child.class=TagAnnotation
        AND itlink.parent.id IN (:iids)
        """

    tags_on_images = {}
    for e in qs.projection(q, params, service_opts):
        tags_on_images.setdefault(unwrap(e[0]), []).append(unwrap(e[1]))

    # Get the images' details
    q = """
        SELECT new map(image.id AS id,
               image.name AS name,
               image.details.owner.id AS ownerId,
               image AS image_details_permissions,
               image.fileset.id AS filesetId,
               filesetentry.clientPath AS clientPath)
        FROM Image image
        JOIN image.fileset fileset
        JOIN fileset.usedFiles filesetentry
        WHERE index(filesetentry) = 0
        AND image.id IN (:iids)
        ORDER BY lower(image.name), image.id
        """

    images = []

    for e in qs.projection(q, params, service_opts):
        e = unwrap(e)[0]
        d = [e["id"],
             e["name"],
             e["ownerId"],
             e["image_details_permissions"],
             e["filesetId"],
             e["clientPath"]]
        images.append(_marshal_image(conn, d, tags_on_images))

    # Get the users from this group for reference
    users = tree.marshal_experimenters(conn, group_id=group_id, page=None)

    return HttpJsonResponse(
        {
            'tags': tags,
            'images': images,
            'users': users
        }
    )
