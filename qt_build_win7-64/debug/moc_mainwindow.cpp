/****************************************************************************
** Meta object code from reading C++ file 'mainwindow.h'
**
** Created: Thu Mar 15 18:08:08 2012
**      by: The Qt Meta Object Compiler version 62 (Qt 4.7.4)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../qt_source/mainwindow.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'mainwindow.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 62
#error "This file was generated using the moc from 4.7.4. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_MainWindow[] = {

 // content:
       5,       // revision
       0,       // classname
       0,    0, // classinfo
      12,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       1,       // signalCount

 // signals: signature, parameters, type, tag, flags
      12,   11,   11,   11, 0x05,

 // slots: signature, parameters, type, tag, flags
      30,   11,   11,   11, 0x08,
      56,   11,   11,   11, 0x08,
      74,   11,   11,   11, 0x08,
      93,   11,   11,   11, 0x08,
     111,   11,   11,   11, 0x08,
     134,   11,   11,   11, 0x08,
     158,   11,   11,   11, 0x08,
     190,  178,   11,   11, 0x08,
     233,   11,   11,   11, 0x08,
     249,   11,   11,   11, 0x08,
     266,   11,   11,   11, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_MainWindow[] = {
    "MainWindow\0\0enableStartTest()\0"
    "on_selectVideos_clicked()\0on_play_clicked()\0"
    "on_reset_clicked()\0onVideoFinished()\0"
    "on_startTest_clicked()\0on_importTest_clicked()\0"
    "enableStartButton()\0socketError\0"
    "displayError(QAbstractSocket::SocketError)\0"
    "readSignalTCP()\0readSignalHTTP()\0"
    "getMediaHTTP()\0"
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
        case 0: enableStartTest(); break;
        case 1: on_selectVideos_clicked(); break;
        case 2: on_play_clicked(); break;
        case 3: on_reset_clicked(); break;
        case 4: onVideoFinished(); break;
        case 5: on_startTest_clicked(); break;
        case 6: on_importTest_clicked(); break;
        case 7: enableStartButton(); break;
        case 8: displayError((*reinterpret_cast< QAbstractSocket::SocketError(*)>(_a[1]))); break;
        case 9: readSignalTCP(); break;
        case 10: readSignalHTTP(); break;
        case 11: getMediaHTTP(); break;
        default: ;
        }
        _id -= 12;
    }
    return _id;
}

// SIGNAL 0
void MainWindow::enableStartTest()
{
    QMetaObject::activate(this, &staticMetaObject, 0, 0);
}
QT_END_MOC_NAMESPACE
