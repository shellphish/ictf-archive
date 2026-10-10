# Makefile

CXXFLAGS = -ggdb -O0 -pipe

all: monitor firmware.img solution.img
	ctags -R

monitor: monitor.o
	$(CXX) $(CXXFLAGS) -o monitor monitor.o -ldl

firmware.img: firmware.asm
	nasm -f elf32 -o firmware.o firmware.asm
	ld -shared -s -o firmware.img firmware.o

solution.img: solution.asm
	nasm -f elf32 -o solution.o solution.asm
	ld -shared -s -o solution.img solution.o
clean:
	rm -f *.o firmware.img solution.img monitor

