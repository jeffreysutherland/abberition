import os
from pathlib import Path
import sys

# add abberition to the path
abberition_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(abberition_path)


#expose the astronomy data path
astronomy_data_dir = '../../astrodev/astronomy.data/'
astronomy_data_path = Path(astronomy_data_dir)


