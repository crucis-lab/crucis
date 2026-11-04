"""Fixed B07 executable: returns literal argv/cwd; never evaluates arguments."""
import json
import os
import sys
sys.stdout.write(json.dumps({'argv': sys.argv[1:], 'cwd': os.getcwd()})+'\n')
