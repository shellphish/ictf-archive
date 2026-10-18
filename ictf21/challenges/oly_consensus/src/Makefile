build:
	make -C src/objectively/c_src oly
	cp src/objectively/c_src/* service/ro
	cp src/objectively/py_compiler/*.py scripts
	./scripts/compiler.py ./src/consensus.oly service/ro/consensus.olc

bundle:
	rm -f ../oly_consensus.tgz
	tar -czf ../oly_consensus.tgz service scripts info.yaml

clean:
	rm -f ../oly_consensus.tgz

scriptbot_scripts:
	docker build -t $(SERVICE_NAME)_scripts ./scripts
