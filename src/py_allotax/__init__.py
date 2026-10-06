"""py-allotax: allotaxonographs and rank-turbulence divergence in Python."""

from py_allotax.allotaxonograph import allotaxonograph, generate_svg
from py_allotax.utils import as_system

__all__ = [
    "allotaxonograph",
    "as_system",
    "generate_svg",  # deprecated alias
]
