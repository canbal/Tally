#ifndef SETTINGS_H
#define SETTINGS_H

#include <QWidget>

namespace Ui {
    class Settings;
}

class Settings : public QWidget
{
    Q_OBJECT
    
public:
    explicit Settings(QWidget *parent = 0);
    ~Settings();
    int m_videoMode;
    QString m_defaultWebAddress;
    QString m_pathToCLMP;
    QString m_argStringCLMP;
    void setDefaults(QString defaultWebAddress, int defaultVideoMode, QString defaultPathCLMP, QString defaultArgStringCLMP);

signals:
    void settings_changed();
    void change_screen();

private slots:
    void on_radioPhonon_clicked();
    void on_radioCLMP_clicked();
    void on_phononChangeScreen_clicked();
    void on_settingsOK_clicked();
    void on_settingsApply_clicked(bool exit=false);
    void on_settingsCancel_clicked();

private:
    Ui::Settings *ui;
    void toggleTabs(int tabIdx);
    void makeSettingsPublic();
};

#endif // SETTINGS_H
