#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <Phonon/VideoWidget>
#include <Phonon/VideoPlayer>
#include <Phonon/MediaObject>
#include <Phonon/MediaSource>
#include <json/json.h>
#include <QNetworkAccessManager>
#include <QWebView>


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
    void resetFinished();

private slots:
    void onVideoFinished();
    void on_startTest_clicked();
    void getMediaHTTP();
    void on_webAddress_returnPressed();
    void readHTTPResponseSignal();
    void on_changeScreen_clicked();

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
