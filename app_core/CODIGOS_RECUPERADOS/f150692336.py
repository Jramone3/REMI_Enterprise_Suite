// SPDX-FileCopyrightText: 2022 Felipe Kinoshita <kinofhek@gmail.com>
// SPDX-License-Identifier: GPL-2.0-or-later

import QtQuick 2.15
import QtQuick.Templates 2.15 as T

/**
 * A AbstractCard is the base for chips. A Chip is a visual object that provides
 * an very friendly way to display predetermined options.
 * providing just the look and the base properties and signals for an AbstractButton.
 *
 * @see Chip
 * @inherit QtQuick.Controls.AbstractButton
 * @since 2.19
 */
T.AbstractButton {
    id: chip

    /**
     * This property holds whether or not to display a close button.
     *
     * Defaults to true.
     */
    property bool closable: true

    /**
     * Emitted when the close button has been clicked.
     */
    signal removed()
}
