#include <iostream>
#include <string>
#include <sstream>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cerr << "Error, not enough arguments!" << std::endl;
        return 1;
    }

    std::ostringstream command;
    for (int i = 1; i < argc; i++) {
        command << argv[i] << " ";
    }

    std::string pythonCommand = "python3 simulator.py ";
    pythonCommand += command.str();
    system(pythonCommand.c_str());
    return 0;
}