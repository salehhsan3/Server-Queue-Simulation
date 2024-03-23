CXX = g++
CXXFLAGS = -std=c++11 -Wall

# Source files
SRC = simulator.cpp

# Executable name
EXEC = simulator

all: $(EXEC)

$(EXEC): $(SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<	

clean:
	rm -f $(EXEC)