import sys, os
import shutil
import math
import re
import random
import pipes
import itertools

import castepy.settings as settings
from castepy.input import pot, parameters
from castepy.input.cell import Cell
from castepy.input.parameters import Parameters
from castepy.utils import calc_from_path
from castepy.templates.submission_scripts import SubmissionScript

jc_path = os.path.join(settings.CASTEPY_ROOT, "templates/jc")


regex_species = re.compile('([A-Za-z]+)([0-9]+)')

import argparse

parser = argparse.ArgumentParser(description='Create a CASTEP J-coupling calculation.')
parser.add_argument('target_dir', help='Directory to build the calculation(s) in.')
parser.add_argument('source', nargs=argparse.REMAINDER, help='Cell file(s) to build the calculation from.')
parser.add_argument('-n', '--num_cores', type=int, help='Number of cores to use.', default=8)
parser.add_argument('-q', '--queue', type=str, help='SGE queue to use.', default="parallel.q")
parser.add_argument('-s', '--site', help='Target J-coupling site(s), separated by commas. Warning if site not present in structure.', type=str)
parser.add_argument('-r', '--rel', action="store_const", help='Use relativity', default=False, const=True)
parser.add_argument('-p', '--pot', help='What type(s) of pseudopotentials to use, separated by commas.', type=str, default="ncp")
parser.add_argument('-x', '--xc_functional', help='The XC functional(s) to use, separated by commas.', default="PBE")
parser.add_argument('-c', '--cut_off_energy', type=str, help='The cut-off energy(s) to use (Rydberg), separated by commas.', default="80")

def make_command(args):
  a = parser.parse_args(args)

  print(a.__dict__)

  sites = []
  if a.site is not None:
    for site in a.site.split(","):
      sites.append(regex_species.findall(site)[0])
  else:
    sites = [None]

  cut_off_energies = list(map(int,a.cut_off_energy.split(",")))
  xc_functionals = [s.lower() for s in a.xc_functional.split(",")]
  pots = a.pot.split(",")
  sources = a.source

  param_prod = list(itertools.product(sources, sites, cut_off_energies, xc_functionals, pots))

  for source,site,cut_off_energy,xc_functional,pot in param_prod:

    source_dir, source_name = calc_from_path(source)

    # Set up following directory structure:
    # [rel/nrel]/[usp/ncp]/[xc_functional]/[structure]/[cutoff]/[site]

    dir_path = [a.target_dir]

    if len(pots) > 1:
      dir_path.append(pot)
    
    if len(xc_functionals) > 1:
      dir_path.append(xc_functional)

    if len(sources) > 1:
      dir_path.append(source_name)

    if len(cut_off_energies) > 1:
      dir_path.append("%dry" % cut_off_energy)

    if len(sites) > 1:
      dir_path.append("".join(site))

    print(dir_path)

    new_dir = False

    for i in range(len(dir_path)):
      d = os.path.join(*dir_path[:i+1])

      if not os.path.isdir(d):
        os.mkdir(d)
        new_dir = True

    target_dir = os.path.join(*dir_path)

    if site is not None:
      jc_s, jc_i = site
      jc_i = int(jc_i)
    else:
      jc_s = None
      jc_i = None

    if pot == "usp":
      usp_pot = True
    elif pot == "ncp":
      usp_pot = False

    try:
      task = JcouplingTask(num_cores=a.num_cores,
                           rel_pot=a.rel,
                           usp_pot=usp_pot,
                           xc_functional=xc_functional,
                           cut_off_energy=cut_off_energy,
                           queue=a.queue,
                           jc_s=jc_s,
                           jc_i=jc_i,
                           source=source)

      task.make(target_dir)

    except SiteNotPresent as e:
      print(e)

      # If we've just made this directory, trash it
      if new_dir:
        shutil.rmtree(target_dir)

class SiteNotPresent(Exception):
  pass

def round_cores_up(n, m):
  return int(math.ceil(float(n)/m)*m)

class JcouplingTask(object):
  merge_cell = Cell(open(os.path.join(jc_path, "jc.cell")).read())
  params = Parameters(open(os.path.join(jc_path, "jc.param")).read())
  code = "castep-jcusp.mpi"

  def __init__(self, num_cores=32, rel_pot=False, usp_pot=False, xc_functional='pbe', cut_off_energy=80, queue="parallel.q", jc_s=None, jc_i=None, cell=None, target_name=None, source=None):
    self.num_cores = num_cores
    self.rel_pot = rel_pot
    self.xc_functional = xc_functional.lower()
    self.cut_off_energy = cut_off_energy
    self.usp_pot = usp_pot
    self.queue = queue
    self.jc_s = jc_s
    self.jc_i = jc_i
    self.cell = cell
    self.target_name = target_name
    self.source = source

  def get_jcoupling_site(self, target_dir):
    """
      Prompt the user to enter a J-coupling site
    """

    species_matches = regex_species.findall(target_dir) 

    if species_matches:
      self.jc_s = species_matches[0][0]
      self.jc_i = int(species_matches[0][1])
      jsiteraw = input("Specify the j-coupling site ({:s} {:d}): ".format(jc_s, jc_i))

      if jsiteraw:
        j_site = jsiteraw.split()
        self.jc_s = j_site[0]
        self.jc_i = int(j_site[1])
    else:
      jsiteraw = input("Specify the j-coupling site: ")

      j_site = jsiteraw.split()
      self.jc_s = j_site[0]
      self.jc_i = int(j_site[1])
  
    return (self.jc_s, self.jc_i)

  def get_cell(self):
    """
      Make sure that self.cell is loaded, possibly by loading from source cell file.
    """

    if self.cell is None and self.source is None:
      raise Exception("One of cell or source must be provided")
    
    if self.source is None and self.target_name is None:
      raise Exception("If no cell is provided, target_name must be specified")

    if self.source is not None:
      source_dir, source_name = calc_from_path(self.source)

      if self.cell is None:
        self.cell = Cell(os.path.join(source_dir, "{}.cell".format(source_name)))

  def make(self, target_dir):
    """
      Write the calculation to the specified target directory.
    """

    self.get_cell()

    # Get the J-coupling site if we don't have it already
    if self.jc_s is None:
      self.get_jcoupling_site(target_dir) 

    # Set up the site in the cell
    if self.jc_s is not None:
      try:
        jc_ion = cell.ions.species(self.jc_s)[self.jc_i-1]
      except IndexError:
        raise SiteNotPresent("Site {:s} {:d} not present".format(self.jc_s, self.jc_i))
    
      cell.otherdict['jcoupling_site'] = "{:s} {:d}".format(self.jc_s, self.jc_i)

    # Remove extraneous kpoints and add in default cell setup
    if 'KPOINTS_LIST' in cell.blocks:
      del cell.blocks['KPOINTS_LIST']
    
    self.cell.otherdict.update(self.merge_cell.otherdict)
    
    # Sort out .param file
    self.params.xc_functional = self.xc_functional
    self.params.cut_off_energy = self.cut_off_energy

    # Add pseudopotentials
    if self.usp_pot:
      pot.add_potentials_usp(cell, self.rel_pot)
    else:
      potentials = pot.add_potentials_asc(cell, self.xc_functional, self.rel_pot)

      for potential in potentials:
        potential.link_files(target_dir)
    
    # Generate submission script and write all the files out
    target_name = source_name

    cell_target = os.path.join(target_dir, "%s.cell" % target_name)
    param_target = os.path.join(target_dir, "%s.param" % target_name)
    sh_target = os.path.join(target_dir, "%s.sh" % target_name)

    submission_script = SubmissionScript(self.queue,
                                         self.num_cores,
                                         self.code,
                                         target_name)

    sh_target_file = open(sh_target, "w+")
    param_target_file = open(param_target, "w+")
    cell_target_file = open(cell_target, "w+")

    print(submission_script, file=sh_target_file)
    print(self.params, file=param_target_file)
    print(cell, file=cell_target_file)

    sh_target_file.close()
    param_target_file.close()
    cell_target_file.close()

if __name__ == "__main__":
  make_command(sys.argv[1:])

