// SPDX-FileCopyrightText: 2022 Felipe Kinoshita <kinofhek@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

import QtQuick 2.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.19 as Kirigami

Rectangle {
    property color pressedColor: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.3)
    property color hoverSelectColor: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.2)
    property color checkedBorderColor: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.7)
    property color pressedBorderColor: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.9)

    Kirigami.Theme.colorSet:Kirigami.Theme.Header
    Kirigami.Theme.inherit: false

    color: parent.pressed ? pressedColor : (parent.checked ? hoverSelectColor : Kirigami.Theme.backgroundColor)
    border.color: parent.pressed ? checkedBorderColor : (parent.checked ? pressedBorderColor : Qt.darker(Kirigami.Theme.backgroundColor, 1.1))
    border.width: 1
    radius: 3
}
