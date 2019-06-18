pip install -r requirements.txt

export PATH=$PATH:/usr/local/ncbi/blast/bin/
export PYTHONPATH=$PYTHONPATH:.

python assembly/app/lcr3/lcr3_pipeline.py \
	data/lcr3/DoE_SBC00013.csv \
	https://ice.synbiochem.co.uk \
	[USER.NAME]@manchester.ac.uk \
	[PASSWORD] \
	out/lcr3/ \
	out/lcr3/summary.txt