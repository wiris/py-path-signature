# The directory to build the package
build_dir="dist"
[[ -d ${build_dir} ]] && (
    rm -rf "${build_dir}"
)
# Build the package in wheel format
poetry build --format wheel
# Install the package 
pip install --upgrade pip
pip install dist/*.whl --force-reinstall
# Install Pillow which will be useful to visualize results
pip install Pillow

# The directory to store results
results_dir="results"
[[ -d ${results_dir} ]] && (
    rm -rf "${results_dir}"
)
mkdir ${results_dir}
python ./scripts/try_library.py