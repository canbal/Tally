#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QFile>
#include <QNetworkReply>
#include <QMessageBox>
#include <QDesktopWidget>
#include <time.h>
#include <sstream>
#include <QNetworkCookie>
#include <QAuthenticator>


MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    ui->startTest->setEnabled(false);

    m_videoMode = 2;
    if (m_videoMode==1) {
        m_media = new Phonon::MediaObject();
        m_vidWidget = new Phonon::VideoWidget();
        Phonon::createPath(m_media, m_vidWidget);
        m_vidWidget->setFullScreen(true);
        m_vidWidget->show();
        on_changeScreen_clicked();
        connect(m_media,SIGNAL(finished()),this,SLOT(onVideoFinished()));
    } else if (m_videoMode==2) {
        ui->changeScreen->setEnabled(false);
        m_wmp = new QProcess(this);
        connect(m_wmp,SIGNAL(finished(int, QProcess::ExitStatus)),this,SLOT(onVideoFinishedWMP(int, QProcess::ExitStatus)));
    }
    m_manager = new QNetworkAccessManager(this);
    //m_manager->setCookieJar(new QNetworkCookieJar(this));
    //connect(m_manager, SIGNAL(authenticationRequired(QNetworkReply*,QAuthenticator*)),
    //            SLOT(authenticate(QNetworkReply*,QAuthenticator*)));
    m_rootURL = "";
    m_testInstanceID = 0;

}


MainWindow::~MainWindow()
{
    if (m_videoMode==1) {
        delete m_media;
        delete m_vidWidget;
    } else if (m_videoMode==2) {
        delete m_wmp;
    }
    delete ui;
}


void MainWindow::authenticate(QNetworkReply* reply, QAuthenticator* auth)
{
    QMessageBox::information(this, tr("SSTT"), "adfadfad");
    auth->setUser(QString("tester"));
    auth->setPassword(QString("1234"));
}


void MainWindow::on_webAddress_returnPressed()
{
    ui->webView->setUrl(ui->webAddress->text());
    QUrl addr = QUrl(ui->webView->url().toString(QUrl::StripTrailingSlash));
    m_rootURL = QString("http://%1").arg(addr.authority());
    QString tmp = addr.path().remove(0,1);    // remove '/'
    bool success = false;
    m_testInstanceID = tmp.toInt(&success);
    if (!success) {
        QMessageBox::information(this, tr("SSTT"), "error resolving Test Instance ID");
    } else {
        ui->startTest->setEnabled(true);
    }
}


void MainWindow::on_changeScreen_clicked()
{
    if (m_videoMode==1) {
        QDesktopWidget *desktop = QApplication::desktop();
        int nScreens = desktop->screenCount();
        if (nScreens > 0) {
            int screen = (desktop->screenNumber(m_vidWidget->pos()) + 1) % nScreens;
            QRect geom = desktop->screenGeometry(screen);
            m_vidWidget->move(geom.topLeft());
            m_vidWidget->showFullScreen();
            ui->changeScreen->setText(QString("Screen %1").arg(screen));
        }
    }
}


void MainWindow::on_startTest_clicked()
{
    ui->startTest->setEnabled(false);
    ui->changeScreen->setEnabled(false);

   // tried to POST to /login/ but get "connection closed" error- this is due to webpage being forbidden (HTTP 403).
   // likely due to CSRF not being handled.  some web searching reveals that @csrf_exempt decorator may
   // not actually remove CSRF handling.  when i tried this (@csrf_exempt), it still didn't work

    QNetworkRequest request(QUrl(QString("%1/%2/reset/").arg(m_rootURL).arg(m_testInstanceID)));
    QNetworkReply *reply = m_manager->get(request);
    connect(reply, SIGNAL(finished()), this, SLOT(initTest()));
    connect(this, SIGNAL(initComplete(QString)), this, SLOT(sendStatusToServer(QString)));
}


void MainWindow::initTest()
{
    // read command from server
    QString command = readServerResponse();

    // interpret command
    std::stringstream err;
    bool success = true;
    Json::Value root;
    Json::Reader reader;
    if (!reader.parse(command.toStdString().c_str(),root)) {
        err << reader.getFormatedErrorMessages() << std::endl;
        success = false;
    } else {
        std::string path = std::string(root["path"].asCString());
        Json::Value videoList = root["videoList"];
        QString fullVid;
        for (int ii=0; ii < videoList.size(); ii++) {
            fullVid = QString("%1/%2").arg(path.c_str()).arg(videoList[ii].asCString());
            if (!QFile(fullVid).exists()) {
                err << "Missing file: " << fullVid.toStdString() << std::endl;
                success = false;
            }
        }
    }
    if (success) {
        emit initComplete(QString("init"));
    } else {
        QMessageBox msgBox;
        msgBox.setIcon(QMessageBox::Critical);
        msgBox.setText("Error with test instance");
        msgBox.setDetailedText(QString(err.str().c_str()));
        msgBox.exec();
    }
}


void MainWindow::sendStatusToServer(QString status)
{
    QNetworkRequest request(QUrl(QString("%1/%2/get_media/").arg(m_rootURL).arg(m_testInstanceID)));
    request.setHeader(QNetworkRequest::ContentTypeHeader,"application/x-www-form-urlencoded");
    QUrl params;
    params.addQueryItem("status",status.toStdString().c_str());
    const QByteArray data = params.encodedQuery();
    QNetworkReply *reply = m_manager->post(request,data);
    connect(reply, SIGNAL(finished()), this, SLOT(executeServerMediaCommand()));
}


void MainWindow::executeServerMediaCommand()
{
    // read command from server
    QString command = readServerResponse();

    // interpret command
    Json::Value root;
    Json::Reader reader;
    if (!reader.parse(command.toStdString().c_str(),root)) {
        QMessageBox::information(this, tr("SSTT"), QString(reader.getFormatedErrorMessages().c_str()));
    } else {
        std::string path = std::string(root["path"].asCString());
        Json::Value videoList = root["videoList"];
        bool testDone = root["testDone"].asBool();
        if (path=="error" && videoList.empty()) {
            QMessageBox::information(this, tr("SSTT"), QString("error with server data"));
        } else if (testDone) {
            // end test
            ui->status->setText(QString("Test complete.  Please exit program."));
        } else if (path.empty() || videoList.empty()) {
            // re-request data after timeout
            clock_t endwait;
            endwait = clock () + PING_INTERVAL * CLOCKS_PER_SEC;
            while (clock() < endwait) {}
            sendStatusToServer(QString("waiting"));
        } else {
            playVideoList(path, videoList);
        }
    }
}


void MainWindow::playVideoList(std::string path, Json::Value videoList)
{
    QString fullVid;
    if (m_videoMode==1) {
        for (int ii=0; ii < videoList.size(); ii++) {
            fullVid = QString("%1/%2").arg(path.c_str()).arg(videoList[ii].asCString());
            ui->status->setText(QString("Playing %1").arg(fullVid.toStdString().c_str()));
            if (ii==0) {
                m_media->setCurrentSource(fullVid);
            } else {
                m_media->enqueue(fullVid);
            }
        }
        m_media->play();
    } else if (m_videoMode==2) {
        QStringList args;
        for (int ii=0; ii < videoList.size(); ii++) {
            fullVid = QString("%1/%2").arg(path.c_str()).arg(videoList[ii].asCString());
            ui->status->setText(QString("Playing %1").arg(fullVid.toStdString().c_str()));
            args << fullVid;
        }
        args << "/fullscreen" << "/play" << "/close";
        m_wmp->start("c:/Program Files (x86)/Windows Media Player/wmplayer.exe", args);
    } else {
        QMessageBox msgBox;
        msgBox.setIcon(QMessageBox::Critical);
        msgBox.setText("Invalid video mode");
        msgBox.exec();
    }
}


void MainWindow::onVideoFinished()
{
    // Phonon::MediaObject signal finished() is emitted when last video in the queue is finished playing
    m_media->clear();   // so that video player does not pause on final frame
    sendStatusToServer(QString("media_done"));
}


void MainWindow::onVideoFinishedWMP(int exitCode, QProcess::ExitStatus exitStatus)
{
    ui->status->setText(QString("Video is finished.  exitCode = %1, exitStatus = %2").arg(exitCode).arg(exitStatus));
    sendStatusToServer(QString("media_done"));
}


QString MainWindow::readServerResponse()
{
    QNetworkReply *reply = qobject_cast<QNetworkReply *>(sender());
    QString command;
    if (!reply->error()) {
        command = (QString) reply->readAll();
        ui->signal->setText(command);
    } else {
        QMessageBox::information(this, tr("SSTT"), reply->errorString());
    }

/*   QVariant cookieVar = reply->header(QNetworkRequest::SetCookieHeader);
    QList<QNetworkReply::RawHeaderPair> cookieVar = reply->rawHeaderPairs();
    qDebug() << cookieVar;
    qDebug() << reply->readAll();
    //if (cookieVar.isValid()) {
       // QList<QNetworkCookie> cookies = cookieVar.value<QList<QNetworkCookie> >();
        //std::stringstream cnames;
        //for (int ii = 0; ii < cookies.size(); ii++) {
          //  QNetworkCookie cookie = cookies.at(ii);
            //cnames << std::string(cookie.name().data()) << std::endl;
            //if (cookie.name()=="csrfmiddlewaretoken") {
                //QMessageBox::information(this, tr("SSTT"), cookie.value());
            //}
            // do whatever you want here
     //   }
        //QMessageBox::information(this, tr("SSTT"), QString("%1").arg(cookies.size()).toStdString().c_str());//cnames.str().c_str());
    //}
*/

    reply->deleteLater();
    return(command);
}
