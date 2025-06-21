CC = gcc
CFLAGS = -std=gnu99 -Wall -Wextra -D_POSIX_C_SOURCE=199309L -D__FAVOR_BSD -D_DEFAULT_SOURCE
TARGET = doos_inC
SRC = doos_inC.c

all: $(TARGET)

doos_inC: ddos.c
	gcc -o $@ ddos.c -lm

clean:
	rm -f $(TARGET)

python:
	sudo python3 ddos.py
	
cprog:
	sudo ./doos_inC