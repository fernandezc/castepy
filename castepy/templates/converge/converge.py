import sys, os
import shutil

from castepy import castepy
from castepy import constraint
from castepy import cell
from castepy.calc import CastepCalc
from castepy.util import calc_from_path

relax_path = "/home/green/pylib/castepy/templates/relax"
merge_cell = cell.Cell(open(os.path.join(relax_path, "relax.cell")).read())

def make(source_dir, source_name, target_dir, relax_species=["H"]):
  calc = calc.CastepCalc(source_dir, source_name)
  calc.load(include=['cell', 'param'])

  if relax_species is None:
    filter = lambda ion: False
  else:
    filter = lambda ion: ion.s not in relax_species

  #c.other += merge_cell.other

  target_cell = os.path.join(target_dir, "%s.cell" % source_name)
  target_param = os.path.join(target_dir, "%s.param" % source_name)
  target_sh = os.path.join(target_dir, "%s.sh" % source_name)

  shutil.copyfile(os.path.join(relax_path, "relax.param"), target_param)
  shutil.copyfile(os.path.join(relax_path, "relax.sh"), target_sh)

  cell_out = open(target_cell, "w+")

  print(str(c), file=cell_out)

if __name__ == "__main__":
  source_calc = str(sys.argv[1])
  source_dir, source_name = calc_from_path(source_calc)
  target_dir = str(sys.argv[2])

  make(source_dir, source_name, target_dir)

