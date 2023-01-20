export PYTHONPATH_CUSTOM="../src:./src:$DIR_PY:"
export PYTHONPATH="$PYTHONPATH:$PYTHONPATH_CUSTOM"

python src/tlk/Predictor.py