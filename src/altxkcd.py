import urllib
import os
from os.path import join
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import sys
import argparse

parser = argparse.ArgumentParser(description='Creates a mirror of the XKCD JSON files on Amazon S3 as static JSONP.')
parser.add_argument('-f', '--force', help='Forces refresh of all files.', action='store_true')
parser.add_argument('jsonp', help='The prefix added to the files.')
parser.add_argument('bucket', help='The S3 bucket where files will be stored.')
parser.add_argument('key', help='The key for accessing S3.')
parser.add_argument('secret', help='The secret for accessing S3.')
args = parser.parse_args()

conn = S3Connection(args.key, args.secret)
bucket = conn.get_bucket(args.bucket)
incremental = True
headers = {}
headers['Content-Encoding'] = 'gzip'
headers['Content-Type'] = 'text/javascript'

def logToConsole( msg):
  sys.stdout.write(str(msg))
  sys.stdout.flush()

def log(msg):
  logToConsole(msg)
  
def s3Progress(complete, total):
  if (complete > 0 and total > 0):
    percentComplete = float(complete)/float(total)
    log("\r" + str(round((percentComplete*1000), 0) / 10) + "%")

def compressString(s):
    """Gzip a given string."""
    import cStringIO, gzip
    zbuf = cStringIO.StringIO()
    zfile = gzip.GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
    zfile.write(s)
    zfile.close()
    return zbuf.getvalue()

def sync(sourcebase, sourcepath, sourcefile, destbase, destpath, destfile, prefix, overwrite = False):
  desturl = destbase + destpath + destfile
  k = Key(bucket)
  k.key = desturl
  if incremental and k.exists() and not overwrite:
    log("\rSkipping " + desturl + "\n")
    return
  try:
    sourceurl = sourcebase + sourcepath + sourcefile
    log("\rDownloading from " + sourceurl + "\n")
    stream = urllib.urlopen(sourceurl)
    contents = stream.read()
    log("\rUploading to " + desturl + "\n")
    jsonp = prefix + '(' + contents + ');'
    k.set_contents_from_string(compressString(jsonp), headers=headers, cb=s3Progress, num_cb=1000)
    k.set_acl('public-read')
  except:
    log("\rThere was an error uploading " + desturl + "\n")
    return
  log("\rUploading " + desturl + " complete\n")
  return contents

base = "http://xkcd.com"
jsonfile = "info.0.json"
current = int(eval(sync(base, "/", jsonfile, "/content/", "", jsonfile + ".gz", args.jsonp, True))["num"])

while current > 0:
  sync(base, "/" + str(current) + "/", jsonfile, "/content/", str(current) + "/", jsonfile + ".gz", args.jsonp, args.force)
  current -= 1