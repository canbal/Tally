#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QFileDialog>
#include <time.h>
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <QMessageBox>
#include <QUrl>
#include <QNetworkRequest>
#include <QNetworkReply>

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    m_numVideos = 0;
    m_videoPlayOrder = NULL;
    m_nextVideo = 0;
    m_initStatus = ui->status->text();
    m_media = new Phonon::MediaObject();
    m_vidWidget = new Phonon::VideoWidget();
    Phonon::createPath(m_media, m_vidWidget);
    m_vidWidget->show();
    m_vidWidget->setFullScreen(true);       // look at QDesktopWidget for how to control which screen this appears on
    connect(m_media,SIGNAL(finished()),this,SLOT(onVideoFinished()));
    connect(ui->testID,SIGNAL(textChanged()),this,SIGNAL(enableStartTest()));
    connect(this,SIGNAL(enableStartTest()),this,SLOT(enableStartButton()));
    setTestState(INITIAL);

    m_tcpSocket = new QTcpSocket(this);     // parent is MainWindow; no need to delete
    //connect(m_tcpSocket, SIGNAL(readyRead()), this, SLOT(readSignal()));
    //connect(m_tcpSocket, SIGNAL(error(QAbstractSocket::SocketError)),
    //        this, SLOT(displayError(QAbstractSocket::SocketError)));

    m_manager = new QNetworkAccessManager(this);
    m_url = "http://137.110.118.234/";
    connect(m_manager, SIGNAL(finished(QNetworkReply*)),
            this, SLOT(readSignalHTTP(QNetworkReply*)));
}


MainWindow::~MainWindow()
{
    if (m_videoPlayOrder!=NULL) {
        delete [] m_videoPlayOrder;
    }
    m_tcpSocket->abort();
    delete m_media;
    delete m_vidWidget;
    delete ui;
}


void MainWindow::enableStartButton()
{
    bool enable = (ui->videoList->count()!=0) && (!ui->testID->document()->isEmpty());
    ui->startTest->setEnabled(enable);
}


void MainWindow::on_selectVideos_clicked()
{
    // dialog to select video
    QStringList fileNames = QFileDialog::getOpenFileNames(this,
         tr("Select Videos"), "", tr(""));
    // update video list
    if (!fileNames.isEmpty()) {
        ui->videoList->clear();
        ui->videoList->addItems(fileNames);
        ui->status->setText(QString("Click '%1' to start test").arg(ui->play->text()));
    }
    emit enableStartTest();
}


int *MainWindow::randomizeVideoOrder(void)
{
    int *list = new int[m_numVideos];
    std::vector <int> *listVector = new std::vector<int>;
    int r;
    // initialize ordered list vector
    for (int ii=0; ii<m_numVideos; ii++) {
        listVector->push_back(ii);
    }
    // randomize list
    srand((unsigned int)time(NULL));
    for (int ii=0; ii < m_numVideos; ii++) {
        r = rand() % (m_numVideos-ii);
        list[ii] = listVector->at(r);
        listVector->erase(listVector->begin()+r);
    }
    delete listVector;
    return(list);
}


void MainWindow::on_play_clicked()
{
    if (m_videoPlayOrder!=NULL) {
        if (m_nextVideo>0) {
            m_media->stop();
            ui->videoList->item(m_videoPlayOrder[m_nextVideo-1])->setBackground(Qt::gray);
        }
        if (m_nextVideo==m_numVideos) {
            ui->status->setText(QString("All videos played.  Click '%1' or '%2' to start over").arg(ui->reset->text()).arg(ui->selectVideos->text()));
        } else {
            ui->videoList->item(m_videoPlayOrder[m_nextVideo])->setBackground(Qt::green);
            ui->status->setText(QString("Status: Playing Video %1 (Video %2 in the randomization)").arg(m_nextVideo+1).arg(m_videoPlayOrder[m_nextVideo]+1));
            m_media->setCurrentSource(ui->videoList->item(m_videoPlayOrder[m_nextVideo])->text());
            m_media->play();
            m_nextVideo++;
        }
    }
}


void MainWindow::on_reset_clicked()
{
    ui->status->setText(m_initStatus);
    m_numVideos = 0;
    m_media->stop();
    if (m_videoPlayOrder!=NULL) {
        delete [] m_videoPlayOrder;
    }
    m_videoPlayOrder = NULL;
    m_nextVideo = 0;
    ui->videoList->clear();

    ui->testID->clear();
    ui->testNotes->clear();

    m_tcpSocket->abort();

    setTestState(INITIAL);
}


void MainWindow::onVideoFinished()
{
    if (m_videoPlayOrder!=NULL) {
        ui->videoList->item(m_videoPlayOrder[m_nextVideo-1])->setBackground(Qt::red);
        ui->status->setText(QString("Status: Finished playing Video %1 (Video %2 in the randomization)").arg(m_nextVideo).arg(m_videoPlayOrder[m_nextVideo-1]+1));
    }
    m_manager->get(QNetworkRequest(m_url));
}


void MainWindow::on_startTest_clicked()
{
    // test setup
    if (m_videoPlayOrder!=NULL) {
        delete [] m_videoPlayOrder;
    }
    m_numVideos = ui->videoList->count();
    m_videoPlayOrder = randomizeVideoOrder();
    m_nextVideo = 0;
/*
    QString test;
    for (int ii=0; ii<m_numVideos; ii++) {
        test.append(QString("%1 ").arg(m_videoPlayOrder[ii]));
    }
    ui->signal->setText(test); */

    // export JSON document describing test
        // input general test information
    Json::Value object;
    object["testID"] = ui->testID->document()->toPlainText().toStdString();     // check that encoding matches (utf8, etc.)
    time_t rawtime;
    time(&rawtime);
    std::string tm = ctime(&rawtime);
    tm = tm.substr(0,tm.size()-1);      // remove trailing "\n" character (interpreted as single character)
    object["timestamp"] = tm.c_str();
    object["testNotes"] = ui->testNotes->document()->toPlainText().toStdString();     // check that encoding matches (utf8, etc.)
        // input video/randomization information
    for (int ii=0; ii<m_numVideos; ii++) {
        // stores video and order as pairs as an array of objects
        object["videoList"][ii]["video"] = ui->videoList->item(ii)->text().toStdString();     // check that encoding matches (utf8, etc.)
        object["videoList"][ii]["order"] = m_videoPlayOrder[ii];        // randomization is zero-based
        // stores randomization and video list as separate arrays
        //object["videoList2"][ii] = ui->videoList->item(ii)->text().toStdString();     // check that encoding matches (utf8, etc.)
        //object["randomization"][ii] =  m_videoPlayOrder[ii];        // randomization is zero-based
    }
        // write to file
    std::ofstream testFile;
    std::string fileName = "SSTT_config_" + ui->testID->document()->toPlainText().toStdString() + ".json";
    testFile.open(fileName.c_str());
    Json::StyledStreamWriter writer;
    writer.write(testFile,object);
    //Json::StyledWriter writer;      // denser formatting
    //testFile << writer.write(object);
    testFile.close();

    // disable test setup buttons
    setTestState(RUNNING);

    // connect to server
    //m_tcpSocket->connectToHost(m_url,9000);
    m_manager->get(QNetworkRequest(m_url));
}


void MainWindow::on_importTest_clicked()
{
    // dialog to select JSON document
    QString testSetupFile = QFileDialog::getOpenFileName(this,
         tr("Select Test Setup File"), "", tr("JSON documents (*.json)"));
    if (testSetupFile.isEmpty()) {
        return;
    }

    // parse document
    Json::Value root;
    if (!isSetupFileValid(testSetupFile,&root)) {
        on_reset_clicked();
        return;
    } else {
        // populate test setup with appropriate data
        const Json::Value testID_obj = root["testID"];
        ui->testID->setPlainText(QString(testID_obj.asCString()));
        const Json::Value testNotes_obj = root["testNotes"];
        ui->testNotes->setPlainText(QString(testNotes_obj.asCString()));
        // populate video list
        const Json::Value videoList_obj = root["videoList"];
        m_numVideos = videoList_obj.size();
        if (m_videoPlayOrder!=NULL) {
            delete [] m_videoPlayOrder;
        }
        m_videoPlayOrder = new int[m_numVideos];
        m_nextVideo = 0;
        ui->videoList->clear();

        //QString test;
        for (int ii=0; ii<m_numVideos; ii++) {
            ui->videoList->addItem(QString(videoList_obj[ii]["video"].asCString()));
            m_videoPlayOrder[ii] = videoList_obj[ii]["order"].asInt();
        //    test.append(QString("%1 ").arg(m_videoPlayOrder[ii]));
        }
        //ui->signal->setText(test);
    }

    // disable test setup buttons
    setTestState(RUNNING);

    // connect to server
    //m_tcpSocket->connectToHost(m_url,9000);
    m_manager->get(QNetworkRequest(m_url));
}


bool MainWindow::isSetupFileValid(QString testSetupFile, Json::Value *root)         // no error-checking for type of data (string, int, etc.)
{
    Json::Reader reader;
    std::ifstream inFile(testSetupFile.toStdString().c_str(), std::ios_base::in);
    std::stringstream err;
    if (!reader.parse(inFile,*root)) {
        err << reader.getFormatedErrorMessages() << std::endl;
    }
    if (!root->isMember("testID")) {
        err << "Missing \"testID\" member" << std::endl;
    }
    if (!root->isMember("testNotes")) {
        err << "Missing \"testNotes\" member" << std::endl;
    }
    if (!root->isMember("timestamp")) {
        err << "Missing \"timestamp\" member" << std::endl;
    }
    if (!root->isMember("videoList")) {
        err << "Missing \"videoList\" member" << std::endl;
    } else {
        const Json::Value videoList_obj = (*root)["videoList"];
        for (int ii=0; ii<(int)videoList_obj.size(); ii++) {
            if (!videoList_obj[ii].isMember("video")) {
                err << "Missing \"video\" member of \"videoList\" entry " << ii << std::endl;
            }
            if (!videoList_obj[ii].isMember("order")) {
                err << "Missing \"order\" member of \"videoList\" entry " << ii << std::endl;
            }
        }
    }
    bool success = (err.str().size()==0);
    if (!success) {
        QMessageBox msgBox;
        msgBox.setIcon(QMessageBox::Critical);
        msgBox.setText(QString("Invalid configuration file: \n %1 \n Please select a different configuration file or start a new test.").arg(testSetupFile));
        msgBox.setDetailedText(QString(err.str().c_str()));
        msgBox.exec();
    }
    return (success);
}


void MainWindow::setTestState(TEST_STATE state)
{
    bool setup, run;
    if (state==INITIAL) {
        setup = true;
        run = false;
    } else if (state==RUNNING) {
        setup = false;
        run = true;
    }
    ui->selectVideos->setEnabled(setup);
    ui->importTest->setEnabled(setup);
    ui->testID->setEnabled(setup);
    ui->testNotes->setEnabled(setup);
    ui->startTest->setEnabled(false);       // always false; enable depends on other buttons
    ui->play->setEnabled(run);
    ui->reset->setEnabled(run);
}


void MainWindow::readSignal()
{
    int numChars = 4;
    quint64 ba = m_tcpSocket->bytesAvailable();
    if (ba < (unsigned)numChars) {        // expects a string of 4 characters
        return;
    }

    QDataStream in(m_tcpSocket);
    in.setVersion(QDataStream::Qt_4_0);
    quint8 *signal = new quint8[numChars];
    QString command;
    for (int ii=0; ii<numChars; ii++) {     // read out signal as uint8 array, convert to string
        in >> signal[ii];
        command.append(QString(char(signal[ii])));
    }
    ui->signal->setText(QString("%1, %2, %3").arg(command).arg(ba).arg(m_tcpSocket->bytesAvailable()));
    if (command=="play") {
        on_play_clicked();
    }
    delete [] signal;
}


void MainWindow::readSignalHTTP(QNetworkReply *networkReply)
{
    QUrl url = networkReply->url();
    if (!networkReply->error()) {
        QString command = (QString) networkReply->readAll();
        ui->signal->setText(command);
        QMessageBox::information(this, tr("Fortune Client"), command);
    } else {
        QMessageBox::information(this, tr("Fortune Client"), networkReply->errorString());
    }
    networkReply->deleteLater();
}


void MainWindow::displayError(QAbstractSocket::SocketError socketError)
{
    switch (socketError) {
    case QAbstractSocket::RemoteHostClosedError:
        break;
    case QAbstractSocket::HostNotFoundError:
        QMessageBox::information(this, tr("Fortune Client"),
                                 tr("The host was not found. Please check the host name and port settings."));
        break;
    case QAbstractSocket::ConnectionRefusedError:
        QMessageBox::information(this, tr("Fortune Client"),
                                 tr("The connection was refused by the peer. Make sure the fortune server is running, "
                                    "and check that the host name and port settings are correct."));
        break;
    default:
        QMessageBox::information(this, tr("Fortune Client"),
                                 tr("The following error occurred: %1.").arg(m_tcpSocket->errorString()));
    }
}
