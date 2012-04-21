#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QFileDialog>
#include <QUrl>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QMessageBox>
#include <time.h>


MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    m_media = new Phonon::MediaObject();
    m_vidWidget = new Phonon::VideoWidget();
    Phonon::createPath(m_media, m_vidWidget);
    m_vidWidget->show();
    m_vidWidget->setFullScreen(true);       // look at QDesktopWidget for how to control which screen this appears on
    connect(m_media,SIGNAL(finished()),this,SLOT(onVideoFinished()));
    m_manager = new QNetworkAccessManager(this);
}


MainWindow::~MainWindow()
{
    delete m_media;
    delete m_vidWidget;
    delete ui;
}


void MainWindow::on_startTest_clicked()
{
    onVideoFinished();
}


void MainWindow::on_webAddress_returnPressed()
{
    ui->webView->setUrl(ui->webAddress->text());
    m_url = ui->webView->url().toString();
    //QMessageBox::information(this, tr("SSTT"), QString("URL = %1").arg(m_url));
}


void MainWindow::onVideoFinished()
{
    // Phonon::MediaObject signal finished() is emitted when last video in the queue is finished playing
    int testInstance = 1;
    QNetworkRequest request(QUrl(QString("%1%2/get_media/").arg(m_url).arg(testInstance)));
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
                fullVid = QString("%1\\%2.mp4").arg(path.c_str()).arg(videoList[ii].asCString());
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
