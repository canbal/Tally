#include "helper.h"


objFormat::objFormat()
{
    name = "";
    numFields = 0;
    fields = NULL;
}


fileFormat::fileFormat()
{
    root.name = "root";
    root.numFields = 4;
    root.fields = allocateMemory(root.numFields);
    root.fields[0].name = "testID";
    root.fields[1].name = "testNotes";
    root.fields[2].name = "timestamp";
    root.fields[3].name = "videoList";
    root.fields[3].numFields = 2;
    root.fields[3].fields = allocateMemory(root.fields[3].numFields);
    root.fields[3].fields[0].name = "order";
    root.fields[3].fields[1].name = "video";
}


fileFormat::~fileFormat()
{
    for (int ii=0; ii<(int)memVector.size(); ii++) {
        delete [] memVector.at(ii);
    }
}


objFormat *fileFormat::allocateMemory(int numObj)
{
    // store memory pointers in a vector to avoid recursive destructor
    objFormat *p = new objFormat[numObj];
    memVector.push_back(p);
    return (p);
}


const char *getTimestamp()
{
    time_t rawtime;
    time(&rawtime);
    std::string tm = ctime(&rawtime);
    tm = tm.substr(0,tm.size()-1);      // remove trailing "\n" character
    return (tm.c_str());
}


std::string getFileName(std::string testID)
{
    return ("SSTT_config_" + testID + ".json");
}


int *randomizeVideoOrder(int numVideos)
{
    int *list = new int[numVideos];
    std::vector <int> listVector;
    int r;
    // initialize ordered list vector
    for (int ii=0; ii<numVideos; ii++) {
        listVector.push_back(ii);
    }
    // randomize list
    srand((unsigned int)time(NULL));
    for (int ii=0; ii < numVideos; ii++) {
        r = rand() % (numVideos-ii);
        list[ii] = listVector.at(r);
        listVector.erase(listVector.begin()+r);
    }
    return(list);
}


bool isSetupFileValid(QString testSetupFile, Json::Value *root)
{
    Json::Reader reader;
    std::ifstream inFile(testSetupFile.toStdString().c_str(), std::ios_base::in);
    std::stringstream err;
    bool success = true;
    if (!reader.parse(inFile,*root)) {
        err << reader.getFormatedErrorMessages() << std::endl;
        success = false;
    }
    fileFormat file;
    recursiveCheck(*root,file.root,"",&err,&success);
    if (!success) {
        QMessageBox msgBox;
        msgBox.setIcon(QMessageBox::Critical);
        msgBox.setText(QString("Invalid configuration file: \n%1\nPlease select a different configuration file or start a new test.").arg(testSetupFile));
        msgBox.setDetailedText(QString(err.str().c_str()));
        msgBox.exec();
    }
    return (success);
}


void recursiveCheck(const Json::Value obj, objFormat file, std::string rootStr, std::stringstream *err, bool *success)
{
    Json::Value tmpObj;
    std::string arrayEl, origRootStr = rootStr;      // no error-checking for empty fields or type of data (string, int, etc.)

    int max = (obj.isArray()) ? obj.size() : 1;
    for (int ii=0; ii<max; ii++) {
        if (obj.isArray()) {
            tmpObj = obj[ii];
            char tmpStr[10] = {0};
            sprintf(tmpStr,"[%d]",ii);
            arrayEl = std::string(tmpStr);
        } else {
            tmpObj = obj;
            arrayEl = "";
        }
        rootStr = origRootStr + file.name + arrayEl + ":";
        for (int jj=0; jj<file.numFields; jj++) {
            if (!tmpObj.isMember(file.fields[jj].name)) {
                *err << "Missing " << rootStr << file.fields[jj].name << " member" << std::endl;
                *success = false;
            } else {
                const Json::Value subObj = tmpObj[file.fields[jj].name];
                recursiveCheck(subObj, file.fields[jj], rootStr, err, success);
            }
        }
    }
}
