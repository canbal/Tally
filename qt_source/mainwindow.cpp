#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QFileDialog>
#include <QUrl>
#include <QNetworkRequest>
#include <QNetworkReply>
#include "helper.h"


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
    //connect(ui->testID,SIGNAL(textChanged()),this,SIGNAL(enableStartTest()));
    //connect(this,SIGNAL(enableStartTest()),this,SLOT(enableStartButton()));
    setTestState(INITIAL);

    /*
    m_tcpSocket = new QTcpSocket(this);     // parent is MainWindow; no need to delete
    m_numChars = SENTINEL_TCP;
    m_url = "137.110.118.234";
    connect(m_tcpSocket, SIGNAL(readyRead()), this, SLOT(readSignalTCP()));
    connect(m_tcpSocket, SIGNAL(error(QAbstractSocket::SocketError)),
            this, SLOT(displayError(QAbstractSocket::SocketError)));
*/
    m_manager = new QNetworkAccessManager(this);
    m_url = "http://127.0.0.1:8000/";
    //m_url = "http://137.110.118.234/";
}


MainWindow::~MainWindow()
{
    if (m_videoPlayOrder!=NULL) {
        delete [] m_videoPlayOrder;
    }
    //m_tcpSocket->abort();
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
    QStringList fileNames = QFileDialog::getOpenFileNames(this, tr("Select Videos"), "", tr(""));
    if (!fileNames.isEmpty()) {
        ui->videoList->clear();
        ui->videoList->addItems(fileNames);
    }
    emit enableStartTest();
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
    //m_tcpSocket->abort();
    setTestState(INITIAL);
}


void MainWindow::onVideoFinished()
{
    // Phonon::MediaObject signal finished() is emitted when last video in the queue is finished playing
    /*
    if (m_videoPlayOrder!=NULL) {
        ui->videoList->item(m_videoPlayOrder[m_nextVideo-1])->setBackground(Qt::red);
        ui->status->setText(QString("Status: Finished playing Video %1 (Video %2 in the randomization)").arg(m_nextVideo).arg(m_videoPlayOrder[m_nextVideo-1]+1));
    }*/

    int testInstance = 1;
    QNetworkRequest request(QUrl(QString("%1%2/get_media/").arg(m_url).arg(testInstance)));
    QNetworkReply *reply = m_manager->get(request);
    connect(reply, SIGNAL(finished()), this, SLOT(getMediaHTTP()));
}


void MainWindow::getMediaHTTP()
{
    // read command from server
    QNetworkReply *reply = qobject_cast<QNetworkReply *>(sender());
    QString command;
    if (!reply->error()) {
        command = (QString) reply->readAll();
        ui->signal->setText(command);
    } else {
        QMessageBox::information(this, tr("SSTT"), reply->errorString());
    }

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
            ui->status->setText(QString("All videos played.  Click '%1' or '%2' to start over").arg(ui->reset->text()).arg(ui->selectVideos->text()));
        } else if (path.empty() || videoList.empty()) {
            // re-request data after timeout
            clock_t endwait;
            endwait = clock () + 3 * CLOCKS_PER_SEC ;
            while (clock() < endwait) {}
            onVideoFinished();
        } else {
            // play video list
            QString fullVid;
            for (int ii=0; ii<videoList.size(); ii++) {
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
    reply->deleteLater();
}


void MainWindow::on_startTest_clicked()
{
    // test setup
    if (m_videoPlayOrder!=NULL) {
        delete [] m_videoPlayOrder;
    }
    m_numVideos = ui->videoList->count();
    m_videoPlayOrder = randomizeVideoOrder(m_numVideos);
    m_nextVideo = 0;
/*
    QString test;
    for (int ii=0; ii<m_numVideos; ii++) {
        test.append(QString("%1 ").arg(m_videoPlayOrder[ii]));
    }
    ui->signal->setText(test); */

    /*
    // export JSON document describing test
        // input general test information
    Json::Value object;
    object["testID"] = ui->testID->document()->toPlainText().toStdString();     // check that encoding matches (utf8, etc.)
    object["timestamp"] = getTimestamp().c_str();
    object["testNotes"] = ui->testNotes->document()->toPlainText().toStdString();     // check that encoding matches (utf8, etc.)
        // input video/randomization information
    for (int ii=0; ii<m_numVideos; ii++) {
        object["videoList"][ii]["video"] = ui->videoList->item(ii)->text().toStdString();     // check that encoding matches (utf8, etc.)
        object["videoList"][ii]["order"] = m_videoPlayOrder[ii];        // randomization is zero-based
    }
        // write to file
    std::ofstream testFile;
    std::string fileName = getFileName(ui->testID->document()->toPlainText().toStdString());
    testFile.open(fileName.c_str());
    Json::StyledStreamWriter writer;
    writer.write(testFile,object);
    testFile.close();

    // disable test setup buttons
    setTestState(RUNNING);

    // connect to server
    //m_tcpSocket->connectToHost(m_url,9000);
    //m_manager->get(QNetworkRequest(m_url));
*/
    onVideoFinished();
}


void MainWindow::on_importTest_clicked()
{
    // create request
    QNetworkRequest request(QUrl(m_url+"add_test/"));
    //request.setHeader(QNetworkRequest::ContentTypeHeader,"application/x-www-form-urlencoded");
    request.setHeader(QNetworkRequest::ContentTypeHeader,"application/json");
    //request.setHeader(QNetworkRequest::ContentTypeHeader,"multipart/form-data");  // need QHttpMultiPart for this

    // create data
    Json::Value jsonData;
    jsonData["title"] = ui->testID->document()->toPlainText().toStdString().c_str();

    // encode data in URL
    QUrl params;
    params.addQueryItem("data",QString(jsonData.toStyledString().c_str()));

    // send POST request
    QNetworkReply *reply = m_manager->post(request,params.encodedQuery());


    // "A signal-slot connection is removed when either of the objects involved are destroyed."
    // from: http://doc.qt.nokia.com/4.7-snapshot/qobject.html
    connect(reply, SIGNAL(finished()), this, SLOT(readSignalHTTP()));

    /*
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
        ui->testID->setPlainText(QString(root["testID"].asCString()));
        ui->testNotes->setPlainText(QString(root["testNotes"].asCString()));
        const Json::Value videoList_obj = root["videoList"];
        m_numVideos = videoList_obj.size();
        if (m_videoPlayOrder!=NULL) {
            delete [] m_videoPlayOrder;
        }
        m_videoPlayOrder = new int[m_numVideos];
        m_nextVideo = 0;
        ui->videoList->clear();

        //QString test;
        for (int ii=0; ii<m_numVideos; ii++) {      // populate video list
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
    //m_manager->get(QNetworkRequest(m_url));
    */
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
    } else {
        QMessageBox::critical(this, tr("SSTT"), QString("'state' must be \"INITIAL\" or \"RUNNING\"."));
        on_reset_clicked();
        return;
    }
    ui->selectVideos->setEnabled(setup);
    ui->importTest->setEnabled(setup);
    ui->testID->setEnabled(setup);
    ui->testNotes->setEnabled(setup);
    //ui->startTest->setEnabled(false);       // always false; enable depends on other buttons
    ui->startTest->setEnabled(true);       // always false; enable depends on other buttons
    ui->play->setEnabled(run);
    ui->reset->setEnabled(run);
}


void MainWindow::readSignalTCP()
{
    if (m_numChars==SENTINEL_TCP) {
        m_numChars = readSignalTCPsize();
    }
    if (m_tcpSocket->bytesAvailable() < (unsigned)m_numChars) {       // maybe add a timeout in case there is a problem with the socket
        return;
    }

    QDataStream in(m_tcpSocket);
    in.setVersion(QDataStream::Qt_4_0);
    char *signal = new char[m_numChars];
    int br = in.readRawData(signal,m_numChars);
    if (br!=m_numChars) {       // not necessary since we know m_numChars bytes are available
        // call error
        return;
    }
    std::string command(signal);
    Json::Value root;
    Json::Reader reader;
    std::stringstream err;
    if (!reader.parse(command,root)) {
        err << reader.getFormatedErrorMessages() << std::endl;
        ui->signal->setText(QString(err.str().c_str()));
    } else {
        ui->signal->setText(QString("%1, %2").arg(root["iter"].asInt()).arg(root["timestamp"].asCString()));
        if (root["playVideo"].asBool()) {
            on_play_clicked();
        }
    }
    delete [] signal;
    m_numChars = SENTINEL_TCP;
}


int MainWindow::readSignalTCPsize()
{
    int delimiter = 58;     // ":", assumed to be a single character
    QDataStream in(m_tcpSocket);
    in.setVersion(QDataStream::Qt_4_0);
    quint8 signal;
    QString command;
    int ii = 0;
    while (ii <= MAX_DIGITS_TCP) {
        if (m_tcpSocket->bytesAvailable() >=1 ) {       // maybe add a timeout in case there is a problem with the socket
            in >> signal;
            if (char(signal)==delimiter) {
                break;
            }
            if (ii==MAX_DIGITS_TCP) {     // haven't received delimiter
                // call error
                return (SENTINEL_TCP);
            }
            command.append(char(signal));
            ii++;
        }
    }
    return (command.toInt());       // add error-checking for non-int type
}


// use this function to process reply from POST
void MainWindow::readSignalHTTP()
{
    QNetworkReply *reply = qobject_cast<QNetworkReply *>(sender());

    if (!reply->error()) {
        QString command = (QString) reply->readAll();
        ui->signal->setText(command);
    } else {
        QMessageBox::information(this, tr("SSTT"), reply->errorString());
    }
    reply->deleteLater();
}


void MainWindow::displayError(QAbstractSocket::SocketError socketError)
{
    QString errStr;
    switch (socketError) {
    case QAbstractSocket::RemoteHostClosedError:
        return;
    case QAbstractSocket::HostNotFoundError:
        errStr = "The host was not found. Please check the host name and port settings.";
        break;
    case QAbstractSocket::ConnectionRefusedError:
        errStr = "The connection was refused by the peer. Make sure the server is running, and that the host name and port settings are correct.";
        break;
    default:
        errStr = QString("The following error occurred: %1.").arg(m_tcpSocket->errorString());
    }
    QMessageBox::information(this, tr("SSTT"), errStr);
}
