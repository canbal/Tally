#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QtGui>
#include <QFile>
#include <QNetworkReply>
#include <QMessageBox>
#include <QDesktopWidget>
#include <time.h>
#include <sstream>


MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    // initialize UI
    ui->setupUi(this);
    ui->nextVideo->setEnabled(false);
    ui->status->setText("Log into the website and navigate to the start page of the test instance you wish to run.");

    // initialize settings dialog
    m_defaultWebAddress = QString("http://137.110.118.234/");
    m_videoMode = 2;
    m_pathToCLMP = "c:/Program Files (x86)/Windows Media Player/wmplayer.exe";
    m_argsCLMP = QString("/fullscreen /play /close").split(" ");
    m_settings = new Settings::Settings();
    m_settings->setWindowModality(Qt::ApplicationModal);    // disables other windows while this one is open
    m_settings->setDefaults(m_defaultWebAddress,m_videoMode,m_pathToCLMP,m_argsCLMP.join(" "));
    connect(m_settings,SIGNAL(settings_changed()),this,SLOT(copySettings()));

    // initialize network manager and web page
    m_manager = new QNetworkAccessManager(this);
    ui->webAddress->setText(m_defaultWebAddress);
    on_webAddress_returnPressed();
    connect(ui->webView,SIGNAL(urlChanged(const QUrl&)),this,SLOT(onURLChanged(const QUrl&)));

    // initialize internal values
    m_rootURL = "";
    m_testID = 0;
    m_testInstanceID = 0;
    m_key = "";
    m_testCaseDone = false;

    // initialize media player
    m_CLMP = NULL;
    m_phonon = NULL;
    m_videoWidget = NULL;
    setupMediaPlayer();
}


MainWindow::~MainWindow()
{
    if (m_videoWidget != NULL) {
        delete m_videoWidget;
    }
    if (m_phonon != NULL) {
        delete m_phonon;
    }
    if (m_CLMP != NULL) {
        delete m_CLMP;
    }
    if (m_settings != NULL) {
        delete m_settings;
    }
    if (ui != NULL) {
        delete ui;
    }
}



/******************************************************************
 ********************       UI FUNCTIONS       ********************
 ******************************************************************/

void MainWindow::closeEvent(QCloseEvent *event)
{
    event->ignore();
    if (QMessageBox::question(this,"","Are you sure you want to exit?",QMessageBox::Yes | QMessageBox::No,QMessageBox::No) == QMessageBox::Yes) {
        event->accept();
    }
}


void MainWindow::on_webAddress_returnPressed()
{
    ui->webView->setUrl(ui->webAddress->text());
}


void MainWindow::onURLChanged(const QUrl &url)
{
    ui->webAddress->setText(QString(url.toString()));
}


void MainWindow::on_nextVideo_clicked()
{
    ui->nextVideo->setEnabled(false);
    m_testCaseDone = true;
}


void MainWindow::on_startTest_clicked()
{
    // tried to POST to /login/ but get "connection closed" error- this is due to webpage being forbidden (HTTP 403).
    // likely due to CSRF not being handled.  some web searching reveals that @csrf_exempt decorator may
    // not actually remove CSRF handling.  when i tried this (@csrf_exempt), it still didn't work

    bool success = true;
    std::stringstream errMsg;
    ui->startTest->setEnabled(false);
    ui->settings->setEnabled(false);
    if (m_videoMode==2) {
        if (!QFile(m_pathToCLMP).exists()) {
            success = false;
            msgBoxError("Cannot find video player", QString("File '%1' does not exist.").arg(m_pathToCLMP).toStdString());
        }
    }
    if (success) {      // check for valid URL: rootURL/tests/test_pk/instances/test_instance_pk/start/?key={random 20-character code}
        QUrl addr = QUrl(ui->webView->url().toString(QUrl::StripTrailingSlash));
        m_rootURL = QString("http://%1").arg(addr.authority());
        QStringList urlParts = addr.path().remove(0,1).split("/");
        if (urlParts.length() == 5) {
            bool testIDSuccess = false;
            bool testInstanceIDSuccess = false;
            int testID = urlParts.at(1).toInt(&testIDSuccess);
            int testInstanceID = urlParts.at(3).toInt(&testInstanceIDSuccess);
            if ((urlParts.at(0) == "tests") && (urlParts.at(2) == "instances") && (urlParts.at(4) == "start") && testIDSuccess && testInstanceIDSuccess) {
                // check for valid key parameter
                QList<QPair<QString, QString> > urlQueryItems = addr.queryItems();
                if (urlQueryItems.size() == 1) {
                    if (urlQueryItems.at(0).first == "key") {
                        m_testID = testID;
                        m_testInstanceID = testInstanceID;
                        m_key = urlQueryItems.at(0).second;
                    } else {
                        success = false;
                        errMsg << "URL argument must be 'key'" << std::endl;
                    }
                } else {
                    success = false;
                    errMsg << "URL must contain exactly one argument" << std::endl;
                }
            } else {
                success = false;
                errMsg << "Incorrect URL" << std::endl;
            }
        } else {
            success = false;
            errMsg << "Incorrect URL" << std::endl;
        }
        if (success) {
            QNetworkReply *reply = postToServer("init");
            connect(reply, SIGNAL(finished()), this, SLOT(initTest()));
        } else {
            msgBoxError("Error with URL", errMsg.str());
        }
    }
}



/******************************************************************
 *****************       SETTINGS FUNCTIONS       *****************
 ******************************************************************/

void MainWindow::on_settings_clicked()
{
    m_settings->setDefaults(m_defaultWebAddress,m_videoMode,m_pathToCLMP,m_argsCLMP.join(" "));
    m_settings->show();
}


void MainWindow::copySettings()
{
    m_defaultWebAddress = m_settings->m_defaultWebAddress;
    m_pathToCLMP = m_settings->m_pathToCLMP;
    m_argsCLMP = m_settings->m_argStringCLMP.split(" ");
    if (m_videoMode != m_settings->m_videoMode) {
        m_videoMode = m_settings->m_videoMode;
        setupMediaPlayer();
    }
}


void MainWindow::changeScreen()
{
    if (m_videoMode==1 && m_videoWidget != NULL) {
        QDesktopWidget *desktop = QApplication::desktop();
        int nScreens = desktop->screenCount();
        if (nScreens > 0) {
            int screen = (desktop->screenNumber(m_videoWidget->pos()) + 1) % nScreens;
            QRect geom = desktop->screenGeometry(screen);
            m_videoWidget->move(geom.topLeft());
            m_videoWidget->showFullScreen();
        }
    }
}



/******************************************************************
 ***********       SERVER COMMUNICATION FUNCTIONS       ***********
 ******************************************************************/

QNetworkReply *MainWindow::postToServer(std::string path, std::string status)
{
    QNetworkRequest request(QUrl(QString("%1/%2/%3/").arg(m_rootURL).arg(m_testInstanceID).arg(path.c_str())));
    request.setHeader(QNetworkRequest::ContentTypeHeader,"application/x-www-form-urlencoded");
    QUrl params;
    params.addQueryItem("key",m_key.toStdString().c_str());
    if (status.length() > 0) {
        params.addQueryItem("status",status.c_str());
    }
    const QByteArray data = params.encodedQuery();
    return (m_manager->post(request,data));
}


void MainWindow::initTest()
{
    interpretServerCommand("init");
}


void MainWindow::executeServerMediaCommand()
{
    interpretServerCommand("get_media");
}


void MainWindow::interpretServerCommand(std::string mode)
{
    // read command from server
    QString command = readServerResponse();

    // interpret command
    bool success = true;
    std::stringstream errMsg;
    Json::Value root;
    Json::Reader reader;
    if (!reader.parse(command.toStdString().c_str(),root)) {
        success = false;
        errMsg << reader.getFormatedErrorMessages() << std::endl;
    } else if (root.size()==4 && root.isMember("status") && root.isMember("msg") && root.isMember("path") && root.isMember("videoList")) {
        if (mode == "init") {
            processCommand_init(root, &success, &errMsg);
        } else if (mode == "get_media") {
            processCommand_get_media(root, &success, &errMsg);
        } else {
            success = false;
            errMsg << "Invalid server command mode." << std::endl;
        }
    } else {
        success = false;
        errMsg << "Invalid message from server." << std::endl;
    }
    if (success) {
        if (mode == "init") {
            sendStatusToServer("init");
        }
    } else {
        msgBoxError("Error with test instance", errMsg.str());
    }
}


QString MainWindow::readServerResponse()
{
    QNetworkReply *reply = qobject_cast<QNetworkReply *>(sender());
    QString command;
    if (!reply->error()) {
        command = (QString) reply->readAll();
        ui->signal->setText(command);
    } else {
        msgBoxError("Error with server response", reply->errorString().toStdString());
    }
    reply->deleteLater();
    return(command);
}


void MainWindow::processCommand_init(Json::Value root, bool *success, std::stringstream *errMsg)
{
    std::string status = std::string(root["status"].asCString());
    if (status=="valid") {
        std::string path = std::string(root["path"].asCString());
        Json::Value videoList = root["videoList"];
        QString fullVid;
        for (unsigned int ii=0; ii < videoList.size(); ii++) {
            fullVid = QString("%1/%2").arg(path.c_str()).arg(videoList[ii].asCString());
            if (!QFile(fullVid).exists()) {
                *success = false;
                *errMsg << "Missing file: " << fullVid.toStdString() << std::endl;
            }
        }
    } else {
        *success = false;
        std::string errStr = (status=="error") ? std::string(root["msg"].asCString()) : std::string("Unknown status from server.");
        *errMsg << errStr << std::endl;
    }
}


void MainWindow::processCommand_get_media(Json::Value root, bool *success, std::stringstream *errMsg)
{
    std::string status = std::string(root["status"].asCString());
    if (status=="done") {
        // end test
        ui->status->setText(QString("Test complete.  Please exit program."));
    } else if (status=="wait") {
        // re-request data after timeout
        clock_t endwait;
        endwait = clock () + PING_INTERVAL * CLOCKS_PER_SEC;
        while (clock() < endwait) {}
        if (m_testCaseDone) {
            sendStatusToServer("test_case_done");
            m_testCaseDone = false;
        } else {
            sendStatusToServer("waiting");
        }
    } else if (status=="start" || status=="run") {
        std::string path = std::string(root["path"].asCString());
        Json::Value videoList = root["videoList"];
        playVideoList(path, videoList);
    } else {
        *success = false;
        std::string errStr = (status=="error") ? std::string(root["msg"].asCString()) : std::string("Unknown status from server.");
        *errMsg << errStr << std::endl;
    }
}


void MainWindow::sendStatusToServer(std::string status)
{
    QNetworkReply *reply = postToServer("get_media", status);
    connect(reply, SIGNAL(finished()), this, SLOT(executeServerMediaCommand()));
}



/******************************************************************
 ***************       MEDIA PLAYER FUNCTIONS       ***************
 ******************************************************************/

void MainWindow::setupMediaPlayer()
{
    if (m_CLMP != NULL) {
        delete m_CLMP;
        m_CLMP = NULL;
    }
    if (m_videoWidget != NULL) {
        delete m_videoWidget;
        m_videoWidget = NULL;
    }
    if (m_phonon != NULL) {
        delete m_phonon;
        m_phonon = NULL;
    }
    m_settings->disconnect(SIGNAL(change_screen()));
    this->disconnect(SIGNAL(phonon_finished(int,QProcess::ExitStatus)));
    if (m_videoMode==1) {
        m_phonon = new Phonon::MediaObject();
        m_videoWidget = new Phonon::VideoWidget();
        Phonon::createPath(m_phonon, m_videoWidget);
        m_videoWidget->setFullScreen(true);
        m_videoWidget->show();
        changeScreen();
        connect(m_settings,SIGNAL(change_screen()),this,SLOT(changeScreen()));
        connect(m_phonon,SIGNAL(finished()),this,SLOT(onPhononFinished()));
        connect(this,SIGNAL(phonon_finished(int, QProcess::ExitStatus)),this,SLOT(onVideoFinished(int, QProcess::ExitStatus)));
    } else if (m_videoMode==2) {
        m_CLMP = new QProcess(this);        // clmp = command line media player
        connect(m_CLMP,SIGNAL(finished(int, QProcess::ExitStatus)),this,SLOT(onVideoFinished(int, QProcess::ExitStatus)));
        connect(m_CLMP,SIGNAL(error(QProcess::ProcessError)),this,SLOT(handleCLMPError(QProcess::ProcessError)));
    } else {
        msgBoxError("Invalid video mode", "");
    }
}


void MainWindow::playVideoList(std::string path, Json::Value videoList)
{
    QString fullVid;
    QStringList mediaList;
    for (unsigned int ii=0; ii < videoList.size(); ii++) {
        fullVid = QString("%1/%2").arg(path.c_str()).arg(videoList[ii].asCString());
        ui->status->setText(QString("Playing %1").arg(fullVid.toStdString().c_str()));
        mediaList << fullVid;
    }
    if (m_videoMode==1) {
        for (int ii=0; ii < mediaList.size(); ii++) {
            m_phonon->enqueue(mediaList.at(ii));
        }
        m_phonon->play();
    } else if (m_videoMode==2) {
        m_CLMP->start(m_pathToCLMP, mediaList + m_argsCLMP);
    } else {
        msgBoxError("Invalid video mode", "");
    }
}


void MainWindow::onPhononFinished()
{
    // Phonon::MediaObject signal finished() is emitted when last video in the queue is finished playing
    emit phonon_finished(0, QProcess::NormalExit);
}


void MainWindow::onVideoFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    if (m_videoMode == 1) {
        m_phonon->clear();   // so that video player does not pause on final frame
    }
    ui->status->setText(QString("Video is finished.  exitCode = %1, exitStatus = %2").arg(exitCode).arg(exitStatus));
    sendStatusToServer("media_done");
    ui->nextVideo->setEnabled(true);
}


void MainWindow::handleCLMPError(QProcess::ProcessError error)
{
    msgBoxError("Error with video player",QString("Error code = %1").arg(error).toStdString());
}



/******************************************************************
 ******************       HELPER FUNCTIONS       ******************
 ******************************************************************/

void MainWindow::msgBoxError(std::string text, std::string details)
{
    QMessageBox msgBox(QMessageBox::Critical,"",text.c_str());
    msgBox.setDetailedText(details.c_str());
    msgBox.exec();
    ui->startTest->setEnabled(true);
    ui->settings->setEnabled(true);
}
