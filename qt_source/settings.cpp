#include "settings.h"
#include "ui_settings.h"
#include <QFile>
#include <QMessageBox>


Settings::Settings(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::Settings)
{
    ui->setupUi(this);
}


Settings::~Settings()
{
    delete ui;
}


// makes the phonon options tab active when its radio button is selected
void Settings::on_radioPhonon_clicked()
{
    toggleTabs(ui->tabMediaPlayerOptions->indexOf(ui->tabPhonon));
}


// makes the command-line media plyer options tab active when its radio button is selected
void Settings::on_radioCLMP_clicked()
{
    toggleTabs(ui->tabMediaPlayerOptions->indexOf(ui->tabCLMP));
}


// makes the specified options tab active and deactivates the rest
void Settings::toggleTabs(int tabIdx)
{
    for (int ii=0; ii<ui->tabMediaPlayerOptions->count(); ii++) {
        ui->tabMediaPlayerOptions->setTabEnabled(ii,false);
    }
    ui->tabMediaPlayerOptions->setCurrentIndex(tabIdx);
    ui->tabMediaPlayerOptions->setTabEnabled(tabIdx,true);
}


// signals that the user wishes to change the screen of the Phonon media player
void Settings::on_phononChangeScreen_clicked()
{
    emit change_screen();
}


// exits the settings dialog, no changes are saved
void Settings::on_settingsCancel_clicked()
{
    this->hide();
}


// saves the settings and exits the dialog
void Settings::on_settingsOK_clicked()
{
    on_settingsApply_clicked(true);
}


// saves the settings without exiting
void Settings::on_settingsApply_clicked(bool exit)
{
    QString fileCLMP = ui->pathCLMP->text();
    if (ui->radioCLMP->isChecked() && !QFile(fileCLMP).exists()) {
        QMessageBox msgBox(QMessageBox::Critical,"","Error with settings");
        msgBox.setDetailedText(QString("File '%1' does not exist.").arg(fileCLMP));
        msgBox.exec();
    } else {
        makeSettingsPublic();
        if (exit) {
            this->hide();
        }
        emit settings_changed();
    }
}


// initializes the dialog with the specified defaults
void Settings::setDefaults(QString defaultWebAddress, int defaultVideoMode, QString defaultPathCLMP, QString defaultArgStringCLMP)
{
    if (defaultVideoMode == 2) {
        ui->radioCLMP->setChecked(true);
        ui->radioPhonon->setChecked(false);
        on_radioCLMP_clicked();
    } else {        // if invalid video mode is passed in, defaults to Phonon video player
        ui->radioPhonon->setChecked(true);
        ui->radioCLMP->setChecked(false);
        on_radioPhonon_clicked();
    }
    ui->defaultWebAddress->setText(defaultWebAddress);
    ui->pathCLMP->setText(defaultPathCLMP);
    ui->argsCLMP->setText(defaultArgStringCLMP);
    makeSettingsPublic();
}


// copies the choices in the settings dialog to their public variables so they can be updated outside of this class.
void Settings::makeSettingsPublic()
{
    if (ui->radioPhonon->isChecked()) {
        m_videoMode = 1;
        ui->phononChangeScreen->setEnabled(true);
    } else if (ui->radioCLMP->isChecked()) {
        m_videoMode = 2;
        ui->phononChangeScreen->setEnabled(false);
    }
    m_defaultWebAddress = ui->defaultWebAddress->text();
    m_pathToCLMP = ui->pathCLMP->text();
    m_argStringCLMP = ui->argsCLMP->text();
}
