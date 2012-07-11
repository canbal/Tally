#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QNetworkAccessManager>
#include <Phonon/VideoWidget>
#include <Phonon/MediaObject>
#include <QProcess>
#include <json/json.h>


namespace Ui {
    class MainWindow;
}

const int PING_INTERVAL = 3;     // seconds to wait before requesting next set of videos from server

class MainWindow : public QMainWindow
{
    Q_OBJECT
    
public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

signals:
    void initComplete(QString status);

private slots:
    void authenticate(QNetworkReply* reply, QAuthenticator* auth);
    void on_webAddress_returnPressed();
    void on_changeScreen_clicked();
    void on_startTest_clicked();
    void initTest();
    void sendStatusToServer(QString status);
    void executeServerMediaCommand();
    void onVideoFinished();
    void onVideoFinishedWMP(int exitCode, QProcess::ExitStatus exitStatus);

    void on_nextVideo_clicked();

private:
    Ui::MainWindow *ui;
    Phonon::MediaObject *m_media;
    Phonon::VideoWidget *m_vidWidget;
    QNetworkAccessManager *m_manager;
    QString m_rootURL;
    int m_testInstanceID;
    QProcess *m_wmp;
    int m_videoMode;
    QString readServerResponse();
    void playVideoList(std::string path, Json::Value videoList);
    bool m_testCaseDone;
};

#endif // MAINWINDOW_H
