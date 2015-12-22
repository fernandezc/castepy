import numpy
import sys, os, stat
import re

from castepy.cell import Cell
from castepy.calc import CastepCalc
from castepy.templates.nmr import nmr
from castepy.util import calc_from_path

def parse_species(s):
  s, i = re.findall(r'([A-Za-z]+)([0-9]+)', s)[0]
  return (s, int(i))

def make_submit_all_script(root_dir, runs):
  script_path = os.path.join(root_dir, "submit_all.sh")
  script = open(script_path, "w+")

  for target_dir, name in runs:
    print("cd %s" % target_dir, file=script)
    print("qsub %s.sh" % name, file=script)
    print("cd ..", file=script)

  os.chmod(script_path, 0o755)

def make_magres_accum_script(root_dir, root_name, runs):
  script_path = os.path.join(root_dir, "magres_accum.sh")
  script = open(script_path, "w+")

  for target_dir, name in runs:
    print("grep isc %s/%s.magres >> %s-isc.magres" % (target_dir, name, root_name), file=script)

  os.chmod(script_path, 0o755) 

epsilon = 0.2

if __name__ == "__main__":
  source_dir, name = calc_from_path(sys.argv[1])
  target_dir_prefix = sys.argv[2]

  if not os.path.isdir(target_dir_prefix):
    os.mkdir(target_dir_prefix)

  calc = CastepCalc(source_dir, name)
  calc.load(include=["cell"])

  # Do the groundstate
  run_dir = "%s:X:X:0:0:0" % name
  target_dir = os.path.join(target_dir_prefix, run_dir)

  if not os.path.isdir(target_dir):
    os.mkdir(target_dir)

  num_cores = 8

  runs = []
  nmr.make(source_dir, name, target_dir, name, Cell(str(calc.cell)), num_cores=8)
  runs.append((run_dir, name))

  # Do all the differentials at the sites
  for ion in calc.cell.ions:
    p_orig = numpy.array(ion.p)

    for x, y, z in [(1,1,0), (-1,-1,0), (1,0,1), (-1,0,-1), (0,1,1), (0,-1,-1), (1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]:
      print(x, y, z)

      ion.p = p_orig + epsilon * numpy.array([x,y,z])
      run_dir = "%s:%s:%d:%d:%d:%d" % (name, ion.s, ion.i, x, y, z)

      target_dir = os.path.join(target_dir_prefix, run_dir)

      if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

      nmr.make(source_dir, name, target_dir, name, Cell(str(calc.cell)), num_cores=8)
      runs.append((run_dir, name))

    ion.p = p_orig

  make_submit_all_script(target_dir_prefix, runs)
  make_magres_accum_script(target_dir_prefix, name, runs)

