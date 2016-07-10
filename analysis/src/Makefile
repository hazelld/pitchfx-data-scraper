CC       = gcc
CFLAGS   = -Wall -std=c99 -pthread -g
LIB		 = -lrt

# Source files 
SRC= main.c core.c thread_manager.c analysis.c data.c heap.c db.c

# Object files built with macro
OBJ= $(SRC:.c=.o)

# Main executable
MAIN= core

#	
#	Generic part of makefile; should be able to build
#	any executable based on above info
#
.PHONY: depend clean

all: $(MAIN)

$(MAIN): $(OBJ)
	$(CC) $(CFLAGS) $(INCLUDES) -o $(MAIN) $(OBJ) $(LIB)

# Build object files
.c.o:
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@ $(LIB)

clean:
	$(RM) *.o $(MAIN)
