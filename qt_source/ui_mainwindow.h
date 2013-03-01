/********************************************************************************
** Form generated from reading UI file 'mainwindow.ui'
**
** Created: Fri Mar 1 15:19:32 2013
**      by: Qt User Interface Compiler version 4.6.2
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINWINDOW_H
#define UI_MAINWINDOW_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QHBoxLayout>
#include <QtGui/QHeaderView>
#include <QtGui/QLabel>
#include <QtGui/QLineEdit>
#include <QtGui/QMainWindow>
#include <QtGui/QPushButton>
#include <QtGui/QSpacerItem>
#include <QtGui/QStatusBar>
#include <QtGui/QVBoxLayout>
#include <QtGui/QWidget>
#include <QtWebKit/QWebView>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QWidget *centralWidget;
    QVBoxLayout *verticalLayout;
    QLineEdit *addressBar;
    QWebView *webView;
    QLabel *status;
    QLabel *signal;
    QHBoxLayout *horizontalLayout;
    QPushButton *startTest;
    QPushButton *nextVideo;
    QSpacerItem *horizontalSpacer_5;
    QPushButton *settings;
    QStatusBar *statusBar;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName(QString::fromUtf8("MainWindow"));
        MainWindow->resize(644, 708);
        QSizePolicy sizePolicy(QSizePolicy::Preferred, QSizePolicy::Preferred);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(MainWindow->sizePolicy().hasHeightForWidth());
        MainWindow->setSizePolicy(sizePolicy);
        centralWidget = new QWidget(MainWindow);
        centralWidget->setObjectName(QString::fromUtf8("centralWidget"));
        verticalLayout = new QVBoxLayout(centralWidget);
        verticalLayout->setSpacing(6);
        verticalLayout->setContentsMargins(11, 11, 11, 11);
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
        addressBar = new QLineEdit(centralWidget);
        addressBar->setObjectName(QString::fromUtf8("addressBar"));
        addressBar->setMinimumSize(QSize(0, 25));
        addressBar->setMaximumSize(QSize(16777215, 25));

        verticalLayout->addWidget(addressBar);

        webView = new QWebView(centralWidget);
        webView->setObjectName(QString::fromUtf8("webView"));
        QSizePolicy sizePolicy1(QSizePolicy::Expanding, QSizePolicy::Expanding);
        sizePolicy1.setHorizontalStretch(0);
        sizePolicy1.setVerticalStretch(0);
        sizePolicy1.setHeightForWidth(webView->sizePolicy().hasHeightForWidth());
        webView->setSizePolicy(sizePolicy1);
        webView->setUrl(QUrl("about:blank"));

        verticalLayout->addWidget(webView);

        status = new QLabel(centralWidget);
        status->setObjectName(QString::fromUtf8("status"));
        QSizePolicy sizePolicy2(QSizePolicy::Preferred, QSizePolicy::Fixed);
        sizePolicy2.setHorizontalStretch(0);
        sizePolicy2.setVerticalStretch(0);
        sizePolicy2.setHeightForWidth(status->sizePolicy().hasHeightForWidth());
        status->setSizePolicy(sizePolicy2);

        verticalLayout->addWidget(status);

        signal = new QLabel(centralWidget);
        signal->setObjectName(QString::fromUtf8("signal"));
        sizePolicy2.setHeightForWidth(signal->sizePolicy().hasHeightForWidth());
        signal->setSizePolicy(sizePolicy2);

        verticalLayout->addWidget(signal);

        horizontalLayout = new QHBoxLayout();
        horizontalLayout->setSpacing(6);
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        startTest = new QPushButton(centralWidget);
        startTest->setObjectName(QString::fromUtf8("startTest"));
        QSizePolicy sizePolicy3(QSizePolicy::Fixed, QSizePolicy::Fixed);
        sizePolicy3.setHorizontalStretch(0);
        sizePolicy3.setVerticalStretch(0);
        sizePolicy3.setHeightForWidth(startTest->sizePolicy().hasHeightForWidth());
        startTest->setSizePolicy(sizePolicy3);
        startTest->setMaximumSize(QSize(16777215, 23));

        horizontalLayout->addWidget(startTest);

        nextVideo = new QPushButton(centralWidget);
        nextVideo->setObjectName(QString::fromUtf8("nextVideo"));
        sizePolicy3.setHeightForWidth(nextVideo->sizePolicy().hasHeightForWidth());
        nextVideo->setSizePolicy(sizePolicy3);

        horizontalLayout->addWidget(nextVideo);

        horizontalSpacer_5 = new QSpacerItem(455, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout->addItem(horizontalSpacer_5);

        settings = new QPushButton(centralWidget);
        settings->setObjectName(QString::fromUtf8("settings"));
        sizePolicy3.setHeightForWidth(settings->sizePolicy().hasHeightForWidth());
        settings->setSizePolicy(sizePolicy3);

        horizontalLayout->addWidget(settings);


        verticalLayout->addLayout(horizontalLayout);

        MainWindow->setCentralWidget(centralWidget);
        statusBar = new QStatusBar(MainWindow);
        statusBar->setObjectName(QString::fromUtf8("statusBar"));
        MainWindow->setStatusBar(statusBar);

        retranslateUi(MainWindow);

        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QApplication::translate("MainWindow", "Tally Desktop", 0, QApplication::UnicodeUTF8));
        addressBar->setText(QString());
        status->setText(QString());
        signal->setText(QString());
        startTest->setText(QApplication::translate("MainWindow", "Start Test", 0, QApplication::UnicodeUTF8));
        nextVideo->setText(QApplication::translate("MainWindow", "Next Video", 0, QApplication::UnicodeUTF8));
        settings->setText(QApplication::translate("MainWindow", "Settings...", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINWINDOW_H
