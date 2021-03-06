from flask import Blueprint, render_template, flash, request, redirect, url_for, make_response

from hummingbirdexport.controllers.api import Hummingbird
import hummingbirdexport.controllers.writeMALXML as wmx
import hummingbirdexport.controllers.writeXML as wx
import tarfile
import time
import logging
import sys
from io import BytesIO

main = Blueprint('main', __name__)
logger = logging.Logger(logging.DEBUG)
logger_handler = logging.StreamHandler(sys.stdout)
logger_handler.setLevel(logging.DEBUG)
logger.addHandler(logger_handler)

def addResource(zfile, url, fname):
    # get the contents
    contents = urlfetch.fetch(url).content
    # write the contents to the zip file
    zfile.writestr(fname, contents)


@main.route('/')
def index():
    return render_template('main.html')

@main.route('/submit', methods=["POST"])
def submit():
    if request.method == 'POST':
        uname =  request.form["uname"]
        method = request.form["method"]

        hummingbird = Hummingbird()

        if method == "1":
            """Write MAL Format XML"""
            xml = wmx.writeXML(logger)

            xml.writeBof()

            data = hummingbird.get_library(uname)
            if data.get("error"):
                print("ERROR: Hummingbird API: {}".format(data["error"]))

            xml.write(data)

            fail = xml.writeEof()

            c = BytesIO()
            t = tarfile.open(mode='w', fileobj=c)

            file1 = BytesIO(xml.xmlData.encode('utf8'))
            fileinfo1 = tarfile.TarInfo("Hummingbird-to-MAL-Export-" + (time.strftime("%m-%d-%Y")) + ".xml")
            fileinfo1.size = len(file1.getvalue())

            file2 = BytesIO(fail.encode('utf8'))
            fileinfo2 = tarfile.TarInfo("Failure-Report.xml")
            fileinfo2.size = len(file2.getvalue())

            t.addfile(fileinfo1, file1)
            t.addfile(fileinfo2, file2)
            t.close()

            s = c.getvalue()

            response = make_response(s)
            response.headers["Content-Disposition"] = "attachment; filename=Hummingbird-to-MAL-Export-" + (time.strftime("%m-%d-%Y")) + ".tar"
            return response

        if method == "0":
            """Write XML using values from Hummingbird API"""
            hummingbird = Hummingbird()
            xml = wx.writeXML()

            xml.writeBof()

            data = hummingbird.get_library(uname)
            xml.write(data)

            xml.writeEof()

            response = make_response(xml.xmlData)
            response.headers["Content-Disposition"] = "attachment; filename=Hummingbird-Export-" + (time.strftime("%m-%d-%Y")) + ".xml"
            return response

    else:
        abort(401)
