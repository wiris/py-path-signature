#!/bin/bash

# Exit on error
set -o errexit
# Exit pipe on intermediate error
set -o pipefail
# Error on unset variable
set -o nounset

poetry config virtualenvs.in-project true;
