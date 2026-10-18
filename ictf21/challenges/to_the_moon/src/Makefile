BINPATH := service/ro/to_the_moon
BUNDLE_PATH := ../to_the_moon.tgz

service: $(BINPATH)

$(BINPATH):
	cd src && cargo build --release
	mv src/target/release/to_the_moon $(BINPATH)

clean:
	rm service/rw/* 2>/dev/null || true
	rm -rf service/append/*

scriptbot_scripts:
	docker build -t $(SERVICE_NAME)_scripts ./scripts

bundle:
	rm $(BUNDLE_PATH) 2>/dev/null || true
	tar -czf $(BUNDLE_PATH) info.yaml scripts service
