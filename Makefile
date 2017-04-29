all: bb lineup pbp

pbp:
	python pbp.py

bb:
	python bb.py

lineup:
	python lineup.py

clean: clean_all

clean_all:
	rm *pyc
	rm -rf bb_data
	rm -rf pbp_data
	rm -rf lineup_data

cpyc:
	rm *pyc

cf: clean_csv clean_json

clean_csv:
	find bb_data -iname '*csv' | xargs rm

clean_json:
	find pbp_data -iname '*json' | xargs rm
	find bb_data -iname '*json' | xargs rm
	find lineup_data -iname 'txt' | xargs rm
