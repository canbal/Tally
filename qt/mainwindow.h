#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <Phonon/VideoWidget>
#include <Phonon/VideoPlayer>
#include <Phonon/MediaObject>
#include <Phonon/MediaSource>

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT
    
public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();
    
private slots:
    void on_selectVideos_clicked();
    void on_play_clicked();
    void on_reset_clicked();
    void onVideoFinished();

private:
    Ui::MainWindow *ui;
    int *randomizeVideoOrder(void);
    int m_numVideos;
    int *m_videoPlayOrder;
    int m_nextVideo;
    QString m_initStatus;
    Phonon::MediaObject *m_media;
    Phonon::VideoWidget *m_vidWidget;
};

#endif // MAINWINDOW_H
