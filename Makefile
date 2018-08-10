CXX=g++
OPT = -O3

CXXFLAGS = $(INCLUDE_FLAG) $(OPT)

all: project

project: arap.cpp
	$(CXX) -fPIC -c -o arap.o $<
	$(CXX) -fPIC -shared -o libarap.dll arap.o $(LIB_FLAGS)

