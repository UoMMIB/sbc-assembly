pip install synbiochem-py

export PYTHONPATH=$PYTHONPATH:.

python assembly/app/lcr2/lcr2_pipeline.py \
	https://ice.synbiochem.co.uk \
	[USER.NAME]@manchester.ac.uk \
	[PASSWORD] \
	LCR \
	True \
	SBC008019 \
	SBC008028