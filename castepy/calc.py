import os, sys

from .input.parameters import Parameters
from .input.cell import Cell
from .output.nmr import MagresResult
from magres.oldmagres import OldMagres

from .output.finished import error_check, castep_finished

from . import output.energy
from . import output.bonds
from . import output.mulliken

def calcs_on_path(dir, load=False):
  from util import find_all_calcs, calc_from_path

  calcs = []

  for dir, name in map(calc_from_path, find_all_calcs(dir)):
    calc = CastepCalc(dir, name)

    if load:
      calc.load()

    calcs.append(calc)

  return calcs

class CastepCalc:
  types = {'cell':'%s.cell',
           'param': '%s.param',
           'castep': '%s.castep',
           'magres': '%s.magres',}

  def __init__(self, dir=None, name=None, include=None, exclude=None):
    if dir is None:
      root = "."
    else:
      root = dir

    self.dir = dir
    self.name = name

    self.files = []

    for t, file in list(self.types.items()):
      file_path = os.path.join(root, file % name)
      if os.path.isfile(file_path):
        self.files.append(file_path)
        try:
          f = open(file_path)
          setattr(self, "%s_file" % t, f.read())
        except:
          pass

    if include is not None:
      self.load(include, exclude)


  def state(self):
    if castep_finished(self.dir, self.name):
      return 'finished'
    elif error_check(self.dir, self.name):
      return 'error'
    else:
      return 'fresh'

  def write(self, dir, seedname):
    """
      Write the cell and param file to a particular dir and seedname
    """

    cell_path = os.path.join(dir, seedname + ".cell")
    f_cell = open(os.path.join(dir, seedname + ".cell"))
    print(self.cell, file=f_cell)

    param_path = os.path.join(dir, seedname + ".param")
    f_param = open(os.path.join(dir, seedname + ".param"))
    print(self.params, file=f_param)

    return (cell_path, param_path)

  def load(self, include=None, exclude=None):
    if include is None:
      include = set(["cell", "params", "magres", "bonds"])
    else:
      include = set(include)

    if exclude is None:
      exclude = set()
    else:
      exclude = set(exclude)

    to_load = include - exclude

    if hasattr(self, 'cell_file') and "cell" in to_load:
      self.cell = Cell(self.cell_file)

    if hasattr(self, 'param_file') and "params" in to_load:
      self.params = Parameters(self.param_file)

    if hasattr(self, 'magres_file') and "magres" in to_load:
      self.magres = MagresResult(self.magres_file)

      # Nothing there? Try using the old-style parser
      if self.magres.magres_file.data_dict == {}:
        old_magres_file = OldMagres(self.magres_file, self.castep_file)
        #self.magres_file.data_dict = old_magres_file.as_new_format()
        self.magres.magres_file = old_magres_file.as_new_format()

        print(self.magres)

    if hasattr(self, 'castep_file') and "bonds" in to_load:
        try:
          bonds.add_bonds(self.cell.ions, self.castep_file)
        except:
          pass

    if hasattr(self, 'castep_file') and "energy" in to_load:
      try:
        self.energy = energy.parse(self.castep_file)
      except energy.CantFindEnergy:
        self.energy = None

      self.scf = energy.SCFResult.load(self.castep_file)

    if hasattr(self, 'castep_file') and "mulliken" in to_load:
      self.mulliken = mulliken.MullikenResult.load(self.castep_file)

