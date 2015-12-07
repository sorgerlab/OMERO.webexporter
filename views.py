from django.http import (HttpResponse, HttpResponseNotAllowed,
                         HttpResponseBadRequest, Http404)
from omeroweb.webclient.decorators import login_required
from omeroweb.decorators import ConnCleaningHttpResponse
import omero
from omero.rtypes import wrap
import json
import logging

logger = logging.getLogger(__name__)

@login_required()
def get_files_for_obj(request, obj_type=None, obj_id=None, conn=None, **kwargs):

    if not request.method == 'GET':
        return HttpResponseNotAllowed('Methods allowed: GET')

    if not obj_type:
        return HttpResponseBadRequest('Must specify the type of object')

    if not obj_id:
        return HttpResponseBadRequest('Must specify the id of object')

    obj_id = long(obj_id)

    # group_id = request.session.get('active_group')
    # if group_id is None:
    #     group_id = conn.getEventContext().groupId
    group_id = -1

    # Query config
    params = omero.sys.ParametersI()
    conn.SERVICE_OPTS.setOmeroGroup(group_id)
    params.add('oid', wrap(obj_id))

    qs = conn.getQueryService()

    q = None

    if obj_type == 'image':
        q = """
            SELECT orig.id, orig.name, orig.size, orig.hash
            FROM FilesetEntry fse
            JOIN fse.originalFile orig
            JOIN fse.fileset fs
            JOIN fs.images image
            WHERE image.id = :oid
            """

    elif obj_type == 'dataset':
        q = """
            SELECT orig.id, orig.name, orig.size, orig.hash
            FROM FilesetEntry fse
            JOIN fse.originalFile orig
            WHERE fse.fileset IN (
                SELECT DISTINCT image.fileset.id
                FROM Dataset dataset
                JOIN dataset.imageLinks diLink
                JOIN diLink.child image
                    WHERE dataset.id = :oid
            )
            """

    elif obj_type == 'project':
        q = """
            SELECT orig.id, orig.name, orig.size, orig.hash
            FROM FilesetEntry fse
            JOIN fse.originalFile orig
            WHERE fse.fileset IN (
                SELECT DISTINCT image.fileset.id
                FROM Project project
                JOIN project.datasetLinks pdLink
                JOIN pdLink.child dataset
                JOIN dataset.imageLinks diLink
                JOIN diLink.child image
                WHERE project.id = :oid
            )
            """

    elif obj_type == 'plate':
        q = """
            SELECT orig.id, orig.name, orig.size, orig.hash
            FROM FilesetEntry fse
            JOIN fse.originalFile orig
            WHERE fse.fileset IN (
                SELECT DISTINCT image.fileset.id
                FROM Well well
                JOIN well.wellSamples ws
                JOIN ws.image image
                WHERE well.plate.id = :oid
            )
            """
    # TODO Test this on LINCS
    elif obj_type == 'screen':
        q = """
            SELECT orig.id, orig.name, orig.size, orig.hash
            FROM FilesetEntry fse
            JOIN fse.originalFile orig
            WHERE fse.fileset IN (
                SELECT DISTINCT image.fileset.id
                FROM Screen screen
                JOIN screen.plateLinks spLink
                JOIN spLink.child plate
                JOIN plate.wells well
                JOIN well.wellSamples ws
                JOIN ws.image image
                WHERE screen.id = :oid
            )
            """

    else:
        return HttpResponseBadRequest('Image|Dataset|Plate supported')

    response = []
    for e in qs.projection(q, params, conn.SERVICE_OPTS):
        # print '\t'.join([str(x.val) if x is not None else 'None' for x in e])
        response.append({
            'id': e[0].val,
            'name': e[1].val,
            'size': e[2].val,
            'hash': e[3].val
        })

    if len(response) == 0:
        raise Http404("Object not found")

    return HttpResponse(json.dumps(response), content_type='json')

def omeroFileStream(id, size, conn, buf=2621440):
    rfs = conn.createRawFileStore()
    rfs.setFileId(id, conn.SERVICE_OPTS)

    if size <= buf:
        yield rfs.read(0, long(size))
    else:
        for pos in xrange(0, long(size), buf):
            data = None
            if size - pos < buf:
                data = rfs.read(pos, size-pos)
            else:
                data = rfs.read(pos, buf)
            yield data
    rfs.close()

@login_required(doConnectionCleanup=False)
def download_file(request, file_id, conn=None, **kwargs):

    file_id = long(file_id)

    # Query config
    group_id = -1
    params = omero.sys.ParametersI()
    conn.SERVICE_OPTS.setOmeroGroup(group_id)
    params.add('fid', wrap(file_id))

    q = """
        SELECT orig.size
        FROM OriginalFile orig
        WHERE orig.id = :fid
        """

    qs = conn.getQueryService()

    # Query to ensure that the file exists and to confirm its size
    results = qs.projection(q, params, conn.SERVICE_OPTS)

    if len(results) != 1:
        raise Http404("File not found: %s" % file_id)

    # TODO Check for canDownload permission

    size = results[0][0].val

    rsp = ConnCleaningHttpResponse(omeroFileStream(file_id, size, conn))
    rsp.conn = conn
    rsp['Content-Length'] = size
    # Use the id as the filename for want of something better
    rsp['Content-Disposition'] = 'attachment; filename=%s' % ('partial-%s' % file_id)
    rsp['Content-Type'] = 'application/force-download'
    return rsp
