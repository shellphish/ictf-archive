build:
	go build -ldflags '-w' -o service/ro/gopher_coin src/gopher_coin.go

bundle:
	rm -f ../gopher_coin.tgz
	tar -czf ../gopher_coin.tgz scripts service info.yaml

scriptbot_scripts:
	docker build -t $(SERVICE_NAME)_scripts ./scripts

clean:
	rm -f ../oly_consensus.tgz

run:
	docker-compose up --build
