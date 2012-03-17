#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <Phonon/VideoWidget>
#include <Phonon/VideoPlayer>
#include <Phonon/MediaObject>
#include <Phonon/MediaSource>
#include <json/json.h>
#include <QTcpSocket>
#include <QNetworkAccessManager>

namespace Ui {
class MainWindow;
}

enum TEST_STATE {
    INITIAL,
    RUNNING
};

const int SENTINEL_TCP = -1;    // should be <= 0
const int MAX_DIGITS_TCP = 5;

class MainWindow : public QMainWindow
{
    Q_OBJECT
    
public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

signals:
    void enableStartTest();
    
private slots:
    void on_selectVideos_clicked();
    void on_play_clicked();
    void on_reset_clicked();
    void onVideoFinished();
    void on_startTest_clicked();
    void on_importTest_clicked();
    void enableStartButton();
    void displayError(QAbstractSocket::SocketError socketError);
    void readSignalTCP();
    void readSignalHTTP();
    void getMediaHTTP();

private:
    Ui::MainWindow *ui;
    int m_numVideos;
    int *m_videoPlayOrder;
    int m_nextVideo;
    int m_numChars;
    QString m_initStatus;
    QString m_url;
    QTcpSocket *m_tcpSocket;
    QNetworkAccessManager *m_manager;
    Phonon::MediaObject *m_media;
    Phonon::VideoWidget *m_vidWidget;
    void setTestState(TEST_STATE state);
    int readSignalTCPsize();
};

#endif // MAINWINDOW_H
