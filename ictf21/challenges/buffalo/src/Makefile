.PHONY: clean
clean:
	rm -f ../kyc.tgz

.PHONY: bundle
bundle:
	rm -f ../buffalo.tgz
	tar -czf ../buffalo.tgz service scripts info.yaml

scriptbot_scripts:
	docker build -t buffalo_scripts ./scripts

