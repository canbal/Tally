#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QNetworkAccessManager>
#include <Phonon/VideoWidget>
#include <Phonon/MediaObject>


namespace Ui {
class MainWindow;
}

const int PING_INTERVAL = 3;     // seconds to wait before requesting next video from server

class MainWindow : public QMainWindow
{
    Q_OBJECT
    
public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

signals:
    void initComplete();

private slots:
    void onVideoFinished();
    void on_startTest_clicked();
    void getMediaHTTP();
    void on_webAddress_returnPressed();
    void initTest();
    void on_changeScreen_clicked();
    void authenticate(QNetworkReply* reply, QAuthenticator* auth);

private:
    Ui::MainWindow *ui;
    QString m_rootURL;
    int m_testInstanceID;
    QNetworkAccessManager *m_manager;
    Phonon::MediaObject *m_media;
    Phonon::VideoWidget *m_vidWidget;
    QString readHTTPResponse();
};

#endif // MAINWINDOW_H
