#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QNetworkAccessManager>
#include <QProcess>
#include <QSettings>
#include "settings.h"


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
    //void phonon_finished(int exitCode, QProcess::ExitStatus exitStatus);

private slots:
        // related to UI
    void on_addressBar_returnPressed();
    void onURLChanged(const QUrl &url);
    void on_nextVideo_clicked();
    void on_startTest_clicked();
        // related to UI settings
    void on_settings_clicked();
    void copySettings();
    //void changeScreen();
        // server signals
    void initTest();
    void executeServerMediaCommand();
        // media player responses
    //void onPhononFinished();
    //void onVideoFinished(int exitCode, QProcess::ExitStatus exitStatus);
    //void handleCLMPError(QProcess::ProcessError error);

private:
        // controls and widgets
    Ui::MainWindow *ui;
    Settings *m_settings;
    QNetworkAccessManager *m_manager;
    //Phonon::MediaObject *m_phonon;
    //Phonon::VideoWidget *m_videoWidget;
    QProcess *m_CLMP;
        // internal parameters
    QString m_rootURL;
    int m_testID;
    int m_testInstanceID;
    QString m_key;
    bool m_testCaseDone;
        // settings
    QSettings *m_savedPrefs;
    int m_videoMode;
    QString m_defaultWebAddress;
    QString m_pathToCLMP;
    QStringList m_argsCLMP;
        // functions
    void closeEvent(QCloseEvent *event);
    QNetworkReply *postToServer(std::string path, std::string status="");
    void interpretServerCommand(std::string mode);
    QString readServerResponse();
    void processCommand_init(QJsonObject serverCmdObj, bool *success, std::stringstream *errMsg);
    void processCommand_get_media(QJsonObject serverCmdObj, bool *success, std::stringstream *errMsg);
    void sendStatusToServer(std::string status);
    //void setupMediaPlayer();
    //void playMediaList(std::string path, QJsonArray mediaList);
    void msgBoxError(std::string text, std::string details="");
};

#endif // MAINWINDOW_H
