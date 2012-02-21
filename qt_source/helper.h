#ifndef HELPER_H
#define HELPER_H

#include <time.h>
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <QMessageBox>
#include <json/json.h>


class objFormat
{
public:
    std::string name;
    int numFields;
    objFormat *fields;
    objFormat();
};

class fileFormat
{
public:
    objFormat root;
    fileFormat();
    ~fileFormat();
private:
    std::vector <objFormat*> memVector;
    objFormat *allocateMemory(int numObj);
};

const char *getTimestamp();
std::string getFileName(std::string testID);
int *randomizeVideoOrder(int numVideos);
bool isSetupFileValid(QString testSetupFile, Json::Value *root);
void recursiveCheck(const Json::Value obj, objFormat file, std::string rootStr, std::stringstream *err, bool *success);


#endif // HELPER_H
