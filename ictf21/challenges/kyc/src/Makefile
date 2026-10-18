build: ;

bundle:
	rm -f ../kyc.tgz
	tar -czf ../kyc.tgz service scripts info.yaml

clean:
	rm -f ../kyc.tgz

scriptbot_scripts:
	docker build -t $(SERVICE_NAME)_scripts ./scripts

