.PHONY: service recreate bundle clean

service: clean

recreate: service
	# swiftc src/wallet.eth,swift -static-stdlib -emit-executable -o service/ro/wallet.eth
	cp src/verify.py service/ro

bundle:
	rm -f ../wall.eth.tgz
	tar -czf ../wall.eth.tgz service scripts info.yaml

scriptbot_scripts:
	docker build -t $(SERVICE_NAME)_scripts ./scripts

clean:
	rm -rf service/rw/*
	rm -rf service/append/*
