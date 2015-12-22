import numpy
import math

from . import constants

from .decorators import lazyproperty

class Atom(object):
  def __init__(self, species, index, position, label=None):
    self._species = species 
    self._index = int(index)
    self._position = numpy.array(position)

    if label is not None:
      self._label = label
    else:
      self._label = self._species

  def copy(self):
    """
      Return a deep copy of the object.
    """
    return Atom(self.species, self.index, numpy.array(self.position), self.label)

  def __str__(self):
    if self.species != self.label:
      return "%s(%s)%d" % (self.species, self.label, self.index)
    else:
      return "%s%d" % (self.species, self.index)

  def dist(self, r):
    """
      Calculate distance from this atom to another position or atom.
    """

    if hasattr(r, 'position'):
      r = r.position

    dr = self.position - r

    return math.sqrt(numpy.dot(dr, dr))

  @property
  def label(self):
    """
      This atom's label.
    """
    return self._label
  
  @label.setter
  def label(self, value):
    self._label = value

  @property
  def species(self):
    """
      This atom's species.
    """
    return self._species
 
  @species.setter
  def species(self, value):
    self._species = value

  @property
  def index(self):
    """
      This atom's label index.
    """
    return self._index
  
  @property
  def position(self):
    """
      This atom's position in cartesian coordinates. Units are Angstroms.
    """
    return self._position

class AtomImage(object):
  """
    A periodic image of a particular atom. Exactly like the underlying atom except for its position.
  """

  def __init__(self, atom, position):
    object.__setattr__(self, "position", position)
    object.__setattr__(self, "atom", atom)

  def dist(self, r):
    if hasattr(r, 'position'):
      r = r.position

    dr = self.position - r
    return math.sqrt(numpy.dot(dr, dr))

  def __str__(self):
    return str(self.atom)
  
  def __unicode__(self):
    return str(self.atom)

  def __getattribute__(self, name):
    if name == "atom":
      return object.__getattribute__(self, "atom")
    elif name == "position":
      return object.__getattribute__(self, "position")
    elif name == "dist":
      return object.__getattribute__(self, "dist")
    else:
      return getattr(object.__getattribute__(self, "atom"), name)

  def __setattr__(self, name, value):
    if name == "position":
      object.__setattr__(self, "position", value)
    elif name == "atom":
      object.__setattr__(self, "atom", value)
    else:
      setattr(object.__getattribute__(self, "atom"), name, value)


class MagresAtom(Atom):
  def __init__(self, magres_atom):
    self.magres_atom = magres_atom
    self.reference = 0.0

    super(MagresAtom, self).__init__(magres_atom['species'],
                                     magres_atom['index'],
                                     magres_atom['position'],
                                     magres_atom['label'])

  def __str__(self):
    if self.species != self.label:
      return "%d%s(%s)%d" % (self.isotope, self.species, self.label, self.index)
    else:
      return "%d%s%d" % (self.isotope, self.species, self.index)

  @property
  def isotope(self):
    """
      The isotope of this atom. Assumed to be most common NMR-active nucleus unless specified otherwise.
    """
    if hasattr(self, '_isotope'):
      return self._isotope
    else:
      if self.species in constants.gamma_iso:
        return constants.gamma_iso[self.species]
      else:
        return None

  @isotope.setter
  def isotope(self, value):
    if (self.species, value) in constants.gamma:
      self._isotope = value
    else:
      raise ValueError("Unknown NMR isotope %d%s" % (value, self.species))

  @property
  def gamma(self):
    """
      The gyromagnetic ratio constant of this atom's species and isotope.
    """
    if (self.species, self.isotope) in constants.gamma:
      return constants.gamma[(self.species, self.isotope)]
    else:
      return 0.0
  
  @property
  def Q(self):
    """
      The quadrupole moment of this atom's species and isotope.
    """
    if (self.species, self.isotope) in constants.Q:
      return constants.Q[(self.species, self.isotope)]
    else:
      return 0.0

  @property
  def spin(self):
    if (self.species, self.isotope) in constants.iso_spin:
      return constants.iso_spin[(self.species, self.isotope)]
    else:
      return None # We don't even know what spin this isotope is.


