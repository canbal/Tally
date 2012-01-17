#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QFileDialog>
#include <time.h>
#include <vector>


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
    m_vidWidget->setFullScreen(true);
    connect(m_media,SIGNAL(finished()),this,SLOT(onVideoFinshed());       // needs work
}

MainWindow::~MainWindow()
{
    if (m_videoPlayOrder!=NULL) {
        delete [] m_videoPlayOrder;
    }
    delete m_media;
    delete m_vidWidget;
    delete ui;
}

void MainWindow::on_selectVideos_clicked()
{
    // dialog to select video
    QStringList fileNames = QFileDialog::getOpenFileNames(this,
         tr("Select Videos"), "", tr(""));
    // update video list
    if (!fileNames.isEmpty()) {
        ui->videoList->clear();
        ui->videoList->addItems(fileNames);
        if (m_videoPlayOrder!=NULL) {
            delete [] m_videoPlayOrder;
        }
        m_numVideos = fileNames.count();
        m_videoPlayOrder = randomizeVideoOrder();
        m_nextVideo = 0;
        ui->status->setText(QString("Click '%1' to start test").arg(ui->play->text()));
    }
}

int *MainWindow::randomizeVideoOrder(void)
{
    int *list = new int[m_numVideos];
    std::vector <int> *listVector = new std::vector<int>;
    int r;
    // initialize ordered list vector
    for (int ii=0; ii<m_numVideos; ii++) {
        listVector->push_back(ii);
    }
    // randomize list
    srand((unsigned int)time(NULL));
    for (int ii=0; ii < m_numVideos; ii++) {
        r = rand() % (m_numVideos-ii);
        list[ii] = listVector->at(r);
        listVector->erase(listVector->begin()+r);
    }
    delete listVector;
    return(list);
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
}

void MainWindow::onVideoFinished()
{
    if (m_videoPlayOrder!=NULL) {
        ui->videoList->item(m_videoPlayOrder[m_nextVideo-1])->setBackground(Qt::red);
        ui->status->setText(QString("Status: Finished playing Video %1 (Video %2 in the randomization)").arg(m_nextVideo+1).arg(m_videoPlayOrder[m_nextVideo]+1));
    }
}
