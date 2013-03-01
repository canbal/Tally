/********************************************************************************
** Form generated from reading UI file 'settings.ui'
**
** Created: Fri Mar 1 15:19:32 2013
**      by: Qt User Interface Compiler version 4.6.2
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_SETTINGS_H
#define UI_SETTINGS_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QGroupBox>
#include <QtGui/QHeaderView>
#include <QtGui/QLabel>
#include <QtGui/QLineEdit>
#include <QtGui/QPushButton>
#include <QtGui/QRadioButton>
#include <QtGui/QTabWidget>
#include <QtGui/QWidget>

QT_BEGIN_NAMESPACE

class Ui_Settings
{
public:
    QGroupBox *groupBoxMediaPlayer;
    QRadioButton *radioCLMP;
    QRadioButton *radioPhonon;
    QTabWidget *tabMediaPlayerOptions;
    QWidget *tabPhonon;
    QPushButton *phononChangeScreen;
    QLabel *label;
    QWidget *tabCLMP;
    QLineEdit *argsCLMP;
    QLineEdit *pathCLMP;
    QLabel *labelPathCLMP;
    QLabel *labelArgsCLMP;
    QGroupBox *groupBoxWebAddress;
    QLineEdit *defaultWebAddress;
    QPushButton *settingsOK;
    QPushButton *settingsApply;
    QPushButton *settingsCancel;

    void setupUi(QWidget *Settings)
    {
        if (Settings->objectName().isEmpty())
            Settings->setObjectName(QString::fromUtf8("Settings"));
        Settings->resize(377, 323);
        groupBoxMediaPlayer = new QGroupBox(Settings);
        groupBoxMediaPlayer->setObjectName(QString::fromUtf8("groupBoxMediaPlayer"));
        groupBoxMediaPlayer->setGeometry(QRect(10, 70, 360, 215));
        radioCLMP = new QRadioButton(groupBoxMediaPlayer);
        radioCLMP->setObjectName(QString::fromUtf8("radioCLMP"));
        radioCLMP->setGeometry(QRect(20, 35, 91, 17));
        radioPhonon = new QRadioButton(groupBoxMediaPlayer);
        radioPhonon->setObjectName(QString::fromUtf8("radioPhonon"));
        radioPhonon->setGeometry(QRect(20, 15, 82, 21));
        tabMediaPlayerOptions = new QTabWidget(groupBoxMediaPlayer);
        tabMediaPlayerOptions->setObjectName(QString::fromUtf8("tabMediaPlayerOptions"));
        tabMediaPlayerOptions->setGeometry(QRect(10, 60, 341, 141));
        tabPhonon = new QWidget();
        tabPhonon->setObjectName(QString::fromUtf8("tabPhonon"));
        phononChangeScreen = new QPushButton(tabPhonon);
        phononChangeScreen->setObjectName(QString::fromUtf8("phononChangeScreen"));
        phononChangeScreen->setGeometry(QRect(234, 80, 91, 23));
        label = new QLabel(tabPhonon);
        label->setObjectName(QString::fromUtf8("label"));
        label->setGeometry(QRect(7, 5, 321, 31));
        label->setWordWrap(true);
        tabMediaPlayerOptions->addTab(tabPhonon, QString());
        tabCLMP = new QWidget();
        tabCLMP->setObjectName(QString::fromUtf8("tabCLMP"));
        argsCLMP = new QLineEdit(tabCLMP);
        argsCLMP->setObjectName(QString::fromUtf8("argsCLMP"));
        argsCLMP->setGeometry(QRect(10, 80, 311, 20));
        pathCLMP = new QLineEdit(tabCLMP);
        pathCLMP->setObjectName(QString::fromUtf8("pathCLMP"));
        pathCLMP->setGeometry(QRect(10, 30, 311, 20));
        labelPathCLMP = new QLabel(tabCLMP);
        labelPathCLMP->setObjectName(QString::fromUtf8("labelPathCLMP"));
        labelPathCLMP->setGeometry(QRect(10, 10, 111, 16));
        labelArgsCLMP = new QLabel(tabCLMP);
        labelArgsCLMP->setObjectName(QString::fromUtf8("labelArgsCLMP"));
        labelArgsCLMP->setGeometry(QRect(10, 60, 291, 16));
        tabMediaPlayerOptions->addTab(tabCLMP, QString());
        groupBoxWebAddress = new QGroupBox(Settings);
        groupBoxWebAddress->setObjectName(QString::fromUtf8("groupBoxWebAddress"));
        groupBoxWebAddress->setGeometry(QRect(10, 10, 360, 50));
        defaultWebAddress = new QLineEdit(groupBoxWebAddress);
        defaultWebAddress->setObjectName(QString::fromUtf8("defaultWebAddress"));
        defaultWebAddress->setGeometry(QRect(10, 20, 341, 20));
        settingsOK = new QPushButton(Settings);
        settingsOK->setObjectName(QString::fromUtf8("settingsOK"));
        settingsOK->setGeometry(QRect(295, 290, 75, 23));
        settingsApply = new QPushButton(Settings);
        settingsApply->setObjectName(QString::fromUtf8("settingsApply"));
        settingsApply->setGeometry(QRect(215, 290, 75, 23));
        settingsCancel = new QPushButton(Settings);
        settingsCancel->setObjectName(QString::fromUtf8("settingsCancel"));
        settingsCancel->setGeometry(QRect(10, 290, 75, 23));

        retranslateUi(Settings);

        tabMediaPlayerOptions->setCurrentIndex(0);


        QMetaObject::connectSlotsByName(Settings);
    } // setupUi

    void retranslateUi(QWidget *Settings)
    {
        Settings->setWindowTitle(QApplication::translate("Settings", "Tally Desktop - Settings", 0, QApplication::UnicodeUTF8));
        groupBoxMediaPlayer->setTitle(QApplication::translate("Settings", "Media Player", 0, QApplication::UnicodeUTF8));
        radioCLMP->setText(QApplication::translate("Settings", "Command line", 0, QApplication::UnicodeUTF8));
        radioPhonon->setText(QApplication::translate("Settings", "Qt", 0, QApplication::UnicodeUTF8));
        phononChangeScreen->setText(QApplication::translate("Settings", "Change Screen", 0, QApplication::UnicodeUTF8));
        label->setText(QApplication::translate("Settings", "Use this button to control the screen on which the Qt media player appears.  If the button is inactive, click 'Apply' to activate it.", 0, QApplication::UnicodeUTF8));
        tabMediaPlayerOptions->setTabText(tabMediaPlayerOptions->indexOf(tabPhonon), QApplication::translate("Settings", "Qt", 0, QApplication::UnicodeUTF8));
        pathCLMP->setText(QString());
        labelPathCLMP->setText(QApplication::translate("Settings", "Path to media player", 0, QApplication::UnicodeUTF8));
        labelArgsCLMP->setText(QApplication::translate("Settings", "Command line arguments (executed after input media list)", 0, QApplication::UnicodeUTF8));
        tabMediaPlayerOptions->setTabText(tabMediaPlayerOptions->indexOf(tabCLMP), QApplication::translate("Settings", "Command line", 0, QApplication::UnicodeUTF8));
        groupBoxWebAddress->setTitle(QApplication::translate("Settings", "Default Web Address", 0, QApplication::UnicodeUTF8));
        settingsOK->setText(QApplication::translate("Settings", "OK", 0, QApplication::UnicodeUTF8));
        settingsApply->setText(QApplication::translate("Settings", "Apply", 0, QApplication::UnicodeUTF8));
        settingsCancel->setText(QApplication::translate("Settings", "Cancel", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class Settings: public Ui_Settings {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_SETTINGS_H
