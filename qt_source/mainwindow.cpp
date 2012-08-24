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
    ui->addressBar->setText(m_defaultWebAddress);
    on_addressBar_returnPressed();
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

// pops up a confirmation dialog when the exit button is pressed
void MainWindow::closeEvent(QCloseEvent *event)
{
    event->ignore();
    if (QMessageBox::question(this,"","Are you sure you want to exit?",QMessageBox::Yes | QMessageBox::No,QMessageBox::No) == QMessageBox::Yes) {
        event->accept();
    }
}


// navigates to the URL in the address bar when the return key is pressed
void MainWindow::on_addressBar_returnPressed()
{
    ui->webView->setUrl(ui->addressBar->text());
}


// updates the address bar text to the appropriate URL while navigating with the browser
void MainWindow::onURLChanged(const QUrl &url)
{
    ui->addressBar->setText(QString(url.toString()));
}


// when the 'next video' button is pressed, it sets the 'done' flag for the present test case
void MainWindow::on_nextVideo_clicked()
{
    ui->nextVideo->setEnabled(false);
    m_testCaseDone = true;
}


// when the 'start test' button is pressed, it checks for the media player and the validity of the URL.
// if everything is valid, it will communicate with the server and begin the test.
void MainWindow::on_startTest_clicked()
{
    // tried to POST to /login/ but get "connection closed" error- this is due to webpage being forbidden (HTTP 403).
    // likely due to CSRF not being handled.  some web searching reveals that @csrf_exempt decorator may
    // not actually remove CSRF handling.  when i tried this (@csrf_exempt), it still didn't work

    bool success = true;
    ui->startTest->setEnabled(false);
    ui->settings->setEnabled(false);
    // check media player
    if (m_videoMode!=1 && m_videoMode!=2) {
        success = false;
        msgBoxError("Invalid media player.  Please choose a media player from the settings menu.", "");
    } else if (m_videoMode==2) {
        if (!QFile(m_pathToCLMP).exists()) {
            success = false;
            msgBoxError("Cannot find video player", QString("File '%1' does not exist.").arg(m_pathToCLMP).toStdString());
        }
    }
    // check for valid URL
    std::stringstream errMsg;
    if (success) {
        QUrl currentUrl = QUrl(ui->webView->url().toString(QUrl::StripTrailingSlash));
        m_rootURL = QString("http://%1").arg(currentUrl.authority());
        QRegExp urlPattern("/tests/(\\d+)/instances/(\\d+)/start");
        if (urlPattern.exactMatch(currentUrl.path())) {
            // check for valid key parameter
            QList<QPair<QString, QString> > urlQueryItems = currentUrl.queryItems();
            if ((urlQueryItems.size() == 1) && (urlQueryItems.at(0).first == "key")) {
                m_testID = urlPattern.cap(1).toInt();
                m_testInstanceID = urlPattern.cap(2).toInt();
                m_key = urlQueryItems.at(0).second;
            } else {
                success = false;
                errMsg << "Could not extract key." << std::endl;
            }
        } else {
            success = false;
            errMsg << "Incorrect URL." << std::endl;
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

// launches the settings dialog
void MainWindow::on_settings_clicked()
{
    m_settings->setDefaults(m_defaultWebAddress,m_videoMode,m_pathToCLMP,m_argsCLMP.join(" "));
    m_settings->show();
}


// updates the settings that the user just selected.  settings validation is done in the Settings class.
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


// if the phonon media player is selected, this function switches the screen on which it appears.
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

// posts a message to the specified URL along with the test instance key and a status message if desired.
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


// interprets and acts on server response from the init URL
void MainWindow::initTest()
{
    interpretServerCommand("init");
}


// interprets and acts on server response from the get_media URL
void MainWindow::executeServerMediaCommand()
{
    interpretServerCommand("get_media");
}


// decodes a JSON response from the server
void MainWindow::interpretServerCommand(std::string mode)
{
    // read command from server
    QString command = readServerResponse();

    // interpret command
    bool success = true;
    QStringList keys = (QStringList() << "status" << "msg" << "path" << "mediaList" << "counter");
    std::stringstream errMsg;
    Json::Value root;
    Json::Reader reader;
    if (!reader.parse(command.toStdString().c_str(),root)) {
        success = false;
        errMsg << reader.getFormatedErrorMessages() << std::endl;
    } else {
        bool keysValid = root.size()==(unsigned)keys.size();
        int ii = 0;
        while (keysValid && ii<keys.size()) {
            keysValid = root.isMember(keys.at(ii).toStdString()) ;
            ii++;
        }
        if (keysValid) {
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
    }
    if (success) {
        if (mode == "init") {
            sendStatusToServer("init");
        }
    } else {
        msgBoxError("Error with test instance", errMsg.str());
    }
}


// reads a response from the server
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


// interprets the JSON string from the init response
void MainWindow::processCommand_init(Json::Value root, bool *success, std::stringstream *errMsg)
{
    std::string status = std::string(root["status"].asCString());
    if (status=="valid") {
        std::string path = std::string(root["path"].asCString());
        Json::Value mediaList = root["mediaList"];
        QString fullMedia;
        for (unsigned int ii=0; ii < mediaList.size(); ii++) {
            fullMedia = QString("%1/%2").arg(path.c_str()).arg(mediaList[ii].asCString());
            if (!QFile(fullMedia).exists()) {
                *success = false;
                *errMsg << "Missing file: " << fullMedia.toStdString() << std::endl;
            }
        }
    } else {
        *success = false;
        std::string errStr = (status=="error") ? std::string(root["msg"].asCString()) : std::string("Unknown status from server.");
        *errMsg << errStr << std::endl;
    }
}


// interprets the JSON string from the get_media response
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
    } else if (status=="run") {
        std::string path = std::string(root["path"].asCString());
        Json::Value mediaList = root["mediaList"];
        playMediaList(path, mediaList);
    } else {
        *success = false;
        std::string errStr = (status=="error") ? std::string(root["msg"].asCString()) : std::string("Unknown status from server.");
        *errMsg << errStr << std::endl;
    }
}


// posts to the get_media URL and then interprets the response
void MainWindow::sendStatusToServer(std::string status)
{
    QNetworkReply *reply = postToServer("get_media", status);
    connect(reply, SIGNAL(finished()), this, SLOT(executeServerMediaCommand()));
}



/******************************************************************
 ***************       MEDIA PLAYER FUNCTIONS       ***************
 ******************************************************************/

// instantiates a media player based on the selected mode and cleans up the previous media player
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
        msgBoxError("Invalid media player.  Please choose a media player from the settings menu.");
    }
}


// plays the videos within a test case
void MainWindow::playMediaList(std::string path, Json::Value mediaList)
{
    QString fullMedia;
    QStringList fullMediaList;
    for (unsigned int ii=0; ii < mediaList.size(); ii++) {
        fullMedia = QString("%1/%2").arg(path.c_str()).arg(mediaList[ii].asCString());
        ui->status->setText(QString("Playing %1").arg(fullMedia.toStdString().c_str()));
        fullMediaList << fullMedia;
    }
    if (m_videoMode==1) {
        for (int ii=0; ii < fullMediaList.size(); ii++) {
            m_phonon->enqueue(fullMediaList.at(ii));
        }
        m_phonon->play();
    } else if (m_videoMode==2) {
        m_CLMP->start(m_pathToCLMP, fullMediaList + m_argsCLMP);
    } else {
        msgBoxError("Invalid media player.  Please choose a media player from the settings menu.");
    }
}


// wrapper for the finished() signal from the Phonon player that re-emits the signal with arguments.
// this way, a common slot (onVideoFinished) can be used regardless of the media player.
void MainWindow::onPhononFinished()
{
    // Phonon::MediaObject signal finished() is emitted when last video in the queue is finished playing
    emit phonon_finished(0, QProcess::NormalExit);
}


// tells the server that the videos in the present test case are done playing
void MainWindow::onVideoFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    if (m_videoMode == 1) {
        m_phonon->clear();   // so that video player does not pause on final frame
    }
    ui->status->setText(QString("Video is finished.  exitCode = %1, exitStatus = %2").arg(exitCode).arg(exitStatus));
    sendStatusToServer("media_done");
    ui->nextVideo->setEnabled(true);
}


// pops up an error message if there is a problem with the command-line media player
void MainWindow::handleCLMPError(QProcess::ProcessError error)
{
    msgBoxError("Error with video player",QString("Error code = %1").arg(error).toStdString());
}



/******************************************************************
 ******************       HELPER FUNCTIONS       ******************
 ******************************************************************/

// pops up an error message and resets the test (makes the start and settings buttons active)
void MainWindow::msgBoxError(std::string text, std::string details)
{
    QMessageBox msgBox(QMessageBox::Critical,"",text.c_str());
    msgBox.setDetailedText(details.c_str());
    msgBox.exec();
    ui->startTest->setEnabled(true);
    ui->settings->setEnabled(true);
}
