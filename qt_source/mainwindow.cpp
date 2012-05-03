#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QFileDialog>
#include <QUrl>
#include <QDir>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QMessageBox>
#include <QDesktopWidget>
#include <time.h>
#include <sstream>


MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    ui->startTest->setEnabled(false);
    m_media = new Phonon::MediaObject();
    m_vidWidget = new Phonon::VideoWidget();
    Phonon::createPath(m_media, m_vidWidget);
    m_vidWidget->setFullScreen(true);
    m_vidWidget->show();
    on_changeScreen_clicked();
    connect(m_media,SIGNAL(finished()),this,SLOT(onVideoFinished()));
    m_manager = new QNetworkAccessManager(this);
    m_rootURL = "";
    m_testInstanceID = 0;
}


MainWindow::~MainWindow()
{
    delete m_media;
    delete m_vidWidget;
    delete ui;
}


void MainWindow::on_startTest_clicked()
{
    ui->startTest->setEnabled(false);
    ui->changeScreen->setEnabled(false);
    QNetworkRequest request(QUrl(QString("%1/%2/reset/").arg(m_rootURL).arg(m_testInstanceID)));
    QNetworkReply *reply = m_manager->get(request);
    connect(reply, SIGNAL(finished()), this, SLOT(initTest()));
    connect(this, SIGNAL(initComplete()), this, SLOT(onVideoFinished()));
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


void MainWindow::onVideoFinished()
{
    // Phonon::MediaObject signal finished() is emitted when last video in the queue is finished playing
    m_media->clear();   // so that video player does not pause on final frame
    QNetworkRequest request(QUrl(QString("%1/%2/get_media/").arg(m_rootURL).arg(m_testInstanceID)));
    QNetworkReply *reply = m_manager->get(request);
    connect(reply, SIGNAL(finished()), this, SLOT(getMediaHTTP()));
}


void MainWindow::getMediaHTTP()
{
    // read command from server
    QString command = readHTTPResponse();

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
            onVideoFinished();
        } else {
            // play video list
            QString fullVid;
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
        }
    }
}


void MainWindow::initTest()
{
    // read command from server
    QString command = readHTTPResponse();

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
        emit initComplete();
    } else {
        QMessageBox msgBox;
        msgBox.setIcon(QMessageBox::Critical);
        msgBox.setText("Error with test instance");
        msgBox.setDetailedText(QString(err.str().c_str()));
        msgBox.exec();
    }
}


QString MainWindow::readHTTPResponse()
{
    QNetworkReply *reply = qobject_cast<QNetworkReply *>(sender());
    QString command;
    if (!reply->error()) {
        command = (QString) reply->readAll();
        ui->signal->setText(command);
    } else {
        QMessageBox::information(this, tr("SSTT"), reply->errorString());
    }
    reply->deleteLater();
    return(command);
}


void MainWindow::on_changeScreen_clicked()
{
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
