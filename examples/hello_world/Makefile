# Makefile for hello_world

# Check if environment is likely set up
ifeq ($(findstring sh4,$(CC)),)
$(warning CC does not seem to be sh4 cross compiler. Did you source env.sh?)
endif

TARGET = hello_world
SRCS = main.c
OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

clean:
	rm -f $(TARGET) $(OBJS)

.PHONY: all clean
