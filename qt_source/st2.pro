#-------------------------------------------------
#
# Project created by QtCreator 2012-01-10T15:55:20
#
#-------------------------------------------------

QT += core gui\
      phonon\
      network\
      webkit

TARGET = st2
TEMPLATE = app


SOURCES += main.cpp\
        mainwindow.cpp \
    json/json_writer.cpp \
    json/json_value.cpp \
    json/json_reader.cpp

HEADERS  += mainwindow.h \
    json/writer.h \
    json/value.h \
    json/reader.h \
    json/json_batchallocator.h \
    json/json.h \
    json/forwards.h \
    json/features.h \
    json/config.h \
    json/autolink.h

FORMS    += mainwindow.ui
