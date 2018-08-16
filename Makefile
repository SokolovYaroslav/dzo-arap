CXX=g++
OPT = -O3 -fPIC --std=c++17

CXXFLAGS = $(INCLUDE_FLAG) $(OPT)

all: project

project: arap.cpp
	$(CXX) $(CXXFLAGS) -c -o arap.o $<
	$(CXX) $(CXXFLAGS) -shared -o libarap arap.o $(LIB_FLAGS)

