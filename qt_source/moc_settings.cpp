/****************************************************************************
** Meta object code from reading C++ file 'settings.h'
**
** Created: Fri Mar 1 15:19:37 2013
**      by: The Qt Meta Object Compiler version 62 (Qt 4.6.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "settings.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'settings.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 62
#error "This file was generated using the moc from 4.6.2. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_Settings[] = {

 // content:
       4,       // revision
       0,       // classname
       0,    0, // classinfo
       9,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       2,       // signalCount

 // signals: signature, parameters, type, tag, flags
      10,    9,    9,    9, 0x05,
      29,    9,    9,    9, 0x05,

 // slots: signature, parameters, type, tag, flags
      45,    9,    9,    9, 0x08,
      70,    9,    9,    9, 0x08,
      93,    9,    9,    9, 0x08,
     125,    9,    9,    9, 0x08,
     154,  149,    9,    9, 0x08,
     185,    9,    9,    9, 0x28,
     212,    9,    9,    9, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_Settings[] = {
    "Settings\0\0settings_changed()\0"
    "change_screen()\0on_radioPhonon_clicked()\0"
    "on_radioCLMP_clicked()\0"
    "on_phononChangeScreen_clicked()\0"
    "on_settingsOK_clicked()\0exit\0"
    "on_settingsApply_clicked(bool)\0"
    "on_settingsApply_clicked()\0"
    "on_settingsCancel_clicked()\0"
};

const QMetaObject Settings::staticMetaObject = {
    { &QWidget::staticMetaObject, qt_meta_stringdata_Settings,
      qt_meta_data_Settings, 0 }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &Settings::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *Settings::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *Settings::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_Settings))
        return static_cast<void*>(const_cast< Settings*>(this));
    return QWidget::qt_metacast(_clname);
}

int Settings::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QWidget::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        switch (_id) {
        case 0: settings_changed(); break;
        case 1: change_screen(); break;
        case 2: on_radioPhonon_clicked(); break;
        case 3: on_radioCLMP_clicked(); break;
        case 4: on_phononChangeScreen_clicked(); break;
        case 5: on_settingsOK_clicked(); break;
        case 6: on_settingsApply_clicked((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 7: on_settingsApply_clicked(); break;
        case 8: on_settingsCancel_clicked(); break;
        default: ;
        }
        _id -= 9;
    }
    return _id;
}

// SIGNAL 0
void Settings::settings_changed()
{
    QMetaObject::activate(this, &staticMetaObject, 0, 0);
}

// SIGNAL 1
void Settings::change_screen()
{
    QMetaObject::activate(this, &staticMetaObject, 1, 0);
}
QT_END_MOC_NAMESPACE
