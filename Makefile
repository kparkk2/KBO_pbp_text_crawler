all: bb lineup pbp

pbp:
	python pbp.py

bb:
	python bb.py

lineup:
	python lineup.py

clean: clean_all

clean_all: cpyc clean_folder

cpyc:
	@if [ -f "*pyc" ]; then \
		rm *pyc; \
	else \
		echo 'no pyc'; \
	fi

clean_folder:
	@if [ -d "bb_data" ]; then \
		rm -rf bb_data; \
	else \
		echo 'no bb_data'; \
	fi
	@if [ -d "pbp_data" ]; then \
		rm -rf pbp_data; \
	else \
		echo 'no pbp_data'; \
	fi

cf: clean_csv clean_json

clean_csv:
	@find bb_data -iname '*.csv' | xargs rm
	@find pbp_data -iname '*.csv' | xargs rm

clean_json:
	@find pbp_data -iname '*.json' | xargs rm
	@find bb_data -iname '*.json' | xargs rm

clean_log:
	@find pbp_data -iname '*Log.*' | xargs rm
	@find bb_data -iname '*Log.*' | xargs rm
