/****************************************************************************
** Meta object code from reading C++ file 'mainwindow.h'
**
** Created: Fri Mar 1 15:19:36 2013
**      by: The Qt Meta Object Compiler version 62 (Qt 4.6.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "mainwindow.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'mainwindow.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 62
#error "This file was generated using the moc from 4.6.2. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_MainWindow[] = {

 // content:
       4,       // revision
       0,       // classname
       0,    0, // classinfo
      13,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       1,       // signalCount

 // signals: signature, parameters, type, tag, flags
      32,   12,   11,   11, 0x05,

 // slots: signature, parameters, type, tag, flags
      74,   11,   11,   11, 0x08,
     108,  104,   11,   11, 0x08,
     127,   11,   11,   11, 0x08,
     150,   11,   11,   11, 0x08,
     173,   11,   11,   11, 0x08,
     195,   11,   11,   11, 0x08,
     210,   11,   11,   11, 0x08,
     225,   11,   11,   11, 0x08,
     236,   11,   11,   11, 0x08,
     264,   11,   11,   11, 0x08,
     283,   12,   11,   11, 0x08,
     331,  325,   11,   11, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_MainWindow[] = {
    "MainWindow\0\0exitCode,exitStatus\0"
    "phonon_finished(int,QProcess::ExitStatus)\0"
    "on_addressBar_returnPressed()\0url\0"
    "onURLChanged(QUrl)\0on_nextVideo_clicked()\0"
    "on_startTest_clicked()\0on_settings_clicked()\0"
    "copySettings()\0changeScreen()\0initTest()\0"
    "executeServerMediaCommand()\0"
    "onPhononFinished()\0"
    "onVideoFinished(int,QProcess::ExitStatus)\0"
    "error\0handleCLMPError(QProcess::ProcessError)\0"
};

const QMetaObject MainWindow::staticMetaObject = {
    { &QMainWindow::staticMetaObject, qt_meta_stringdata_MainWindow,
      qt_meta_data_MainWindow, 0 }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &MainWindow::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *MainWindow::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *MainWindow::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_MainWindow))
        return static_cast<void*>(const_cast< MainWindow*>(this));
    return QMainWindow::qt_metacast(_clname);
}

int MainWindow::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QMainWindow::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        switch (_id) {
        case 0: phonon_finished((*reinterpret_cast< int(*)>(_a[1])),(*reinterpret_cast< QProcess::ExitStatus(*)>(_a[2]))); break;
        case 1: on_addressBar_returnPressed(); break;
        case 2: onURLChanged((*reinterpret_cast< const QUrl(*)>(_a[1]))); break;
        case 3: on_nextVideo_clicked(); break;
        case 4: on_startTest_clicked(); break;
        case 5: on_settings_clicked(); break;
        case 6: copySettings(); break;
        case 7: changeScreen(); break;
        case 8: initTest(); break;
        case 9: executeServerMediaCommand(); break;
        case 10: onPhononFinished(); break;
        case 11: onVideoFinished((*reinterpret_cast< int(*)>(_a[1])),(*reinterpret_cast< QProcess::ExitStatus(*)>(_a[2]))); break;
        case 12: handleCLMPError((*reinterpret_cast< QProcess::ProcessError(*)>(_a[1]))); break;
        default: ;
        }
        _id -= 13;
    }
    return _id;
}

// SIGNAL 0
void MainWindow::phonon_finished(int _t1, QProcess::ExitStatus _t2)
{
    void *_a[] = { 0, const_cast<void*>(reinterpret_cast<const void*>(&_t1)), const_cast<void*>(reinterpret_cast<const void*>(&_t2)) };
    QMetaObject::activate(this, &staticMetaObject, 0, _a);
}
QT_END_MOC_NAMESPACE
