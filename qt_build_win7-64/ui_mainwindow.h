/********************************************************************************
** Form generated from reading UI file 'mainwindow.ui'
**
** Created: Tue Feb 21 14:51:08 2012
**      by: Qt User Interface Compiler version 4.7.4
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINWINDOW_H
#define UI_MAINWINDOW_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QGroupBox>
#include <QtGui/QHeaderView>
#include <QtGui/QLabel>
#include <QtGui/QListWidget>
#include <QtGui/QMainWindow>
#include <QtGui/QPlainTextEdit>
#include <QtGui/QPushButton>
#include <QtGui/QStatusBar>
#include <QtGui/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QWidget *centralWidget;
    QGroupBox *testSetup;
    QPlainTextEdit *testID;
    QPushButton *startTest;
    QPushButton *selectVideos;
    QPushButton *importTest;
    QLabel *testNotesLabel;
    QLabel *testIDLabel;
    QPlainTextEdit *testNotes;
    QPushButton *reset;
    QPushButton *play;
    QGroupBox *groupBox;
    QLabel *status;
    QListWidget *videoList;
    QLabel *signal;
    QStatusBar *statusBar;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName(QString::fromUtf8("MainWindow"));
        MainWindow->resize(572, 372);
        centralWidget = new QWidget(MainWindow);
        centralWidget->setObjectName(QString::fromUtf8("centralWidget"));
        testSetup = new QGroupBox(centralWidget);
        testSetup->setObjectName(QString::fromUtf8("testSetup"));
        testSetup->setGeometry(QRect(10, 10, 181, 341));
        testID = new QPlainTextEdit(testSetup);
        testID->setObjectName(QString::fromUtf8("testID"));
        testID->setGeometry(QRect(10, 70, 161, 25));
        startTest = new QPushButton(testSetup);
        startTest->setObjectName(QString::fromUtf8("startTest"));
        startTest->setGeometry(QRect(100, 310, 75, 23));
        selectVideos = new QPushButton(testSetup);
        selectVideos->setObjectName(QString::fromUtf8("selectVideos"));
        selectVideos->setGeometry(QRect(10, 310, 75, 23));
        importTest = new QPushButton(testSetup);
        importTest->setObjectName(QString::fromUtf8("importTest"));
        importTest->setGeometry(QRect(10, 20, 75, 23));
        testNotesLabel = new QLabel(testSetup);
        testNotesLabel->setObjectName(QString::fromUtf8("testNotesLabel"));
        testNotesLabel->setGeometry(QRect(14, 107, 46, 13));
        testIDLabel = new QLabel(testSetup);
        testIDLabel->setObjectName(QString::fromUtf8("testIDLabel"));
        testIDLabel->setGeometry(QRect(12, 55, 46, 13));
        testNotes = new QPlainTextEdit(testSetup);
        testNotes->setObjectName(QString::fromUtf8("testNotes"));
        testNotes->setGeometry(QRect(10, 124, 161, 171));
        reset = new QPushButton(centralWidget);
        reset->setObjectName(QString::fromUtf8("reset"));
        reset->setGeometry(QRect(300, 320, 85, 23));
        play = new QPushButton(centralWidget);
        play->setObjectName(QString::fromUtf8("play"));
        play->setGeometry(QRect(210, 320, 85, 23));
        groupBox = new QGroupBox(centralWidget);
        groupBox->setObjectName(QString::fromUtf8("groupBox"));
        groupBox->setGeometry(QRect(197, 10, 361, 341));
        status = new QLabel(groupBox);
        status->setObjectName(QString::fromUtf8("status"));
        status->setGeometry(QRect(12, 280, 351, 16));
        videoList = new QListWidget(groupBox);
        videoList->setObjectName(QString::fromUtf8("videoList"));
        videoList->setGeometry(QRect(10, 26, 341, 251));
        signal = new QLabel(groupBox);
        signal->setObjectName(QString::fromUtf8("signal"));
        signal->setGeometry(QRect(190, 300, 161, 31));
        MainWindow->setCentralWidget(centralWidget);
        groupBox->raise();
        testSetup->raise();
        reset->raise();
        play->raise();
        statusBar = new QStatusBar(MainWindow);
        statusBar->setObjectName(QString::fromUtf8("statusBar"));
        MainWindow->setStatusBar(statusBar);

        retranslateUi(MainWindow);

        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QApplication::translate("MainWindow", "MainWindow", 0, QApplication::UnicodeUTF8));
        testSetup->setTitle(QApplication::translate("MainWindow", "Test Setup", 0, QApplication::UnicodeUTF8));
        testID->setPlainText(QString());
        startTest->setText(QApplication::translate("MainWindow", "Start Test", 0, QApplication::UnicodeUTF8));
        selectVideos->setText(QApplication::translate("MainWindow", "Select Videos", 0, QApplication::UnicodeUTF8));
        importTest->setText(QApplication::translate("MainWindow", "Import Test", 0, QApplication::UnicodeUTF8));
        testNotesLabel->setText(QApplication::translate("MainWindow", "Notes", 0, QApplication::UnicodeUTF8));
        testIDLabel->setText(QApplication::translate("MainWindow", "Test ID", 0, QApplication::UnicodeUTF8));
        reset->setText(QApplication::translate("MainWindow", "Reset", 0, QApplication::UnicodeUTF8));
        play->setText(QApplication::translate("MainWindow", "Play", 0, QApplication::UnicodeUTF8));
        groupBox->setTitle(QApplication::translate("MainWindow", "Test Environment", 0, QApplication::UnicodeUTF8));
        status->setText(QApplication::translate("MainWindow", "Status: Please fill out Test Setup and click 'Start Test'", 0, QApplication::UnicodeUTF8));
        signal->setText(QString());
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINWINDOW_H
