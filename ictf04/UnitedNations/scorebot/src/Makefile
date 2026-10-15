VALIDATE_OBJECTS = validate.o CTFFlag.o tokenizer.o statefile.o lockfile.o flaglog.o

SCOREBOT_OBJECTS =  eventprocessor.o util.o tokenizer.o scorebot.o networkobjects.o \
                    scorebotconf.o scoreevents.o asyncscript.o CTFFlag.o statefile.o \
                    flaglog.o lockfile.o

HEADERS = $(shell ls *.hpp)
CPPFLAGS = -Wall -pedantic

all : scorebot validate test

scorebot : $(SCOREBOT_OBJECTS) $(HEADERS)
	g++ -o scorebot $(SCOREBOT_OBJECTS) -lcrypto

validate : $(VALIDATE_OBJECTS)
	g++ -o validate $(VALIDATE_OBJECTS) -lcrypto

test : test.o CTFFlag.o asyncscript.o tokenizer.o
	g++ -o test test.o CTFFlag.o asyncscript.o tokenizer.o -lcrypto

clean:
	$(RM) *.o test
