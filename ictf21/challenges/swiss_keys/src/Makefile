
service/service/keys.ch: source/keys.ch
	cp source/keys.ch service/service/keys.ch

source/keys.ch: source/*.go
	docker run --rm -t -v "$(shell pwd)/source:/mnt" golang:1.17-alpine /bin/sh -c 'apk add gcc musl-dev && cd /mnt && go build && strip --strip-debug keys.ch'

../swiss_keys.tgz: service/service/keys.ch
	rm    -f ../swiss_keys.tgz
	tar -czf ../swiss_keys.tgz info.yaml scripts service

bundle: ../swiss_keys.tgz

clean:
	rm -rf ../swiss_keys.tgz #service/service/keys.ch source/keys.ch

scriptbot_scripts:
	docker build --tag $(SERVICE_NAME)_scripts scripts


.PHONY: bundle clean scriptbot_scripts
