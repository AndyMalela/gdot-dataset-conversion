#!/bin/bash
# Stage 2 of the demand correction (rerun with sorted lane insertion): controller fit on train days, validation, rule controllers.
cd /home/andy/Downloads/GDOT
set -x
date
date
uv run python atsc/sites/7065/validate.py fit-passage || exit 1
date
uv run python atsc/sites/7065/validate.py run || exit 1
uv run python atsc/sites/7065/validate.py score || exit 1
date
uv run python atsc/sites/7065/baselines.py design || exit 1
uv run python atsc/sites/7065/baselines.py run || exit 1
uv run python atsc/sites/7065/baselines.py report || exit 1
date
echo STAGE2 DONE
