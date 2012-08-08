import urllib
import sys, os
from os.path import join
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import sys
import argparse
import json
import ConfigParser

conf_parser = argparse.ArgumentParser(
  description='Creates a mirror of the XKCD JSON files on Amazon S3 as static JSONP.',
  # Turn off help, so we print all options in response to -h
  add_help=False
)
conf_parser.add_argument("-c", "--conf_file", help="Specify config file", action='store', default="altxkcd.conf", metavar="FILE")
args, remaining_argv = conf_parser.parse_known_args()
defaults = {
  "jsonp" : "updateComic",
  "bucket" : "s3bucket",
  "key" : "awskey",
  "secret" : "awssecret",
}

if args.conf_file:
  config = ConfigParser.SafeConfigParser()
  config.read([os.path.dirname(sys.argv[0]) + '/' + args.conf_file])
  defaults = dict(config.items("Defaults"))

# Don't surpress add_help here so it will handle -h
parser = argparse.ArgumentParser(
  # Inherit options from config_parser
  parents=[conf_parser],
  # print script description with -h/--help
  description=__doc__,
  # Don't mess with format of description
  formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.set_defaults(**defaults)
parser.add_argument('-f', '--force', help='Forces refresh of all files.', action='store_true')
parser.add_argument('--jsonp', help='The prefix added to the files.')
parser.add_argument('-b', '--bucket', help='The S3 bucket where files will be stored.')
parser.add_argument('-k', '--key', help='The key for accessing S3.')
parser.add_argument('-s', '--secret', help='The secret for accessing S3.')
args = parser.parse_args(remaining_argv)

conn = S3Connection(args.key, args.secret)
bucket = conn.get_bucket(args.bucket)
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
  if k.exists() and not overwrite:
    log("\rSkipping " + desturl + "\n")
    return False
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
    return False
  log("\rUploading " + desturl + " complete\n")
  return contents

base = "http://xkcd.com"
jsonfile = "info.0.json"
current = int(json.loads(sync(base, "/", jsonfile, "/content/", "", jsonfile + ".gz", args.jsonp, True))[u'num'])

while current > 0:
  if sync(base, "/" + str(current) + "/", jsonfile, "/content/", str(current) + "/", jsonfile + ".gz", args.jsonp, args.force) == False:
    current = 0
  current -= 1