# Conda Recipe for py-allotax

This directory contains the conda recipe for building and distributing py-allotax via conda/conda-forge.

## Why Conda?

The conda package solves the Node.js dependency installation problem by:

1. **Automatically installing Node.js** as a dependency
2. **Running `npm install` automatically** via the `post-link.sh` script after installation
3. **No manual steps required** for end users

## Building the Package Locally

```bash
# From the repository root
conda build conda-recipe

# Install the locally built package
conda install --use-local py-allotax
```

## Testing the Package

```bash
# Create a test environment
conda create -n test-allotax python=3.11
conda activate test-allotax

# Install your locally built package
conda install --use-local py-allotax

# Test it
python -c "from py_allotax.generate_svg import generate_svg; print('Success!')"
```

## Publishing to Conda-Forge

To publish to conda-forge, follow the [conda-forge contribution guide](https://conda-forge.org/docs/maintainer/adding_pkgs.html):

1. Fork the [staged-recipes repository](https://github.com/conda-forge/staged-recipes)
2. Copy this recipe to `recipes/py-allotax/`
3. Submit a pull request
4. Address any feedback from conda-forge reviewers

## Recipe Files

- **meta.yaml**: Package metadata, dependencies, and build configuration
- **build.sh**: Build script for Unix systems
- **post-link.sh**: Post-installation script that runs `npm install` automatically
