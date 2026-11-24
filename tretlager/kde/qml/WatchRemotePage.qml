import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami
import org.kde.kirigamiaddons.formcard as FormCard

// Watch remote (Zwindoor): a Garmin watch steers Zwift – turns, Ride On, power-up.
ColumnsPage {
    id: page
    title: i18n("Watch remote")

    readonly property var wr: backend.watchRemote
    readonly property var resultText: ({
        "ok": i18n("delivered"), "not_focused": i18n("Zwift was not in front"),
        "not_running": i18n("Zwift is not running"), "unknown_action": i18n("unknown action"),
        "output_failed": i18n("typing failed"), "disabled": i18n("remote switched off"),
        "malformed": i18n("garbled command") })

    PageHero {
        iconName: "input-gamepad"
        title: i18n("Watch remote")
        text: i18n("Turn at junctions, give a Ride On or fire a power-up from the buttons of your Garmin watch. Tretlager types the matching Zwift keyboard shortcut.")
    }

    PageMessage {
        visible: page.wr.error !== ""
        type: Kirigami.MessageType.Error
        text: i18n("Bluetooth: %1", page.wr.error)
    }
    PageMessage {
        visible: page.wr.running && page.wr.keyboardError !== ""
        type: Kirigami.MessageType.Warning
        text: i18n("Tretlager cannot type into Zwift (%1). The watch still connects, but the commands have no effect.", page.wr.keyboardError)
    }

    PageMessage {
        visible: page.wr.running && page.wr.keyboardBlocked
        type: Kirigami.MessageType.Warning
        text: i18n("The desktop is holding back Tretlager's key presses. Plasma shows the dialog “Remote Control – python3 is asking to control input devices”: python3 is Tretlager. Click Allow, otherwise the commands do not reach Zwift.")
    }
    PageMessage {
        visible: page.wr.enabled && !page.wr.keyboardBlocked && page.wr.keyboardError === ""
        type: Kirigami.MessageType.Information
        text: i18n("On the first command Plasma asks “python3 is asking to control input devices” – python3 is Tretlager. Try a button below before the ride and click Allow; with “Always allow” it does not ask again.")
    }

    leftCards: [
        FormCard.FormHeader {
            title: i18n("Remote")
            trailing: Kirigami.ContextualHelpButton {
                toolTipText: i18n("The watch connects over Bluetooth LE to this computer, on the same adapter as the sensor bridge. It also works when the sensors come through the Zwift Companion app.")
            }
        },
        FormCard.FormCard {
            FormCard.FormSwitchDelegate {
                text: i18n("Watch remote")
                description: page.wr.enabled ? (page.wr.running ? i18n("Waiting for the watch") : i18n("Starting…"))
                                             : i18n("Off – the computer is not visible to the watch")
                checked: page.wr.enabled
                onToggled: backend.setWatchRemote(checked)
            }
            FormCard.FormDelegateSeparator {}
            FormCard.FormTextDelegate {
                text: i18n("Watch")
                icon.name: page.wr.watch ? "data-success" : "network-disconnect"
                description: page.wr.watch ? i18n("connected") : i18n("not connected – start ZWindoor on the watch")
            }
            FormCard.FormDelegateSeparator {}
            FormCard.FormTextDelegate {
                text: i18n("Zwift window")
                icon.name: page.wr.zwiftFocused ? "data-success" : page.wr.zwiftRunning ? "data-information" : "media-playback-stop"
                description: page.wr.zwiftFocused ? i18n("in front, ready")
                           : page.wr.zwiftRunning ? i18n("in the background – brought to the front on the next command")
                                                  : i18n("Zwift is not running")
            }
            FormCard.FormDelegateSeparator {}
            FormCard.FormSwitchDelegate {
                text: i18n("Bring Zwift to the front")
                description: i18n("Raise the Zwift window before typing if another window has the focus")
                checked: page.wr.bringToFront
                onToggled: backend.setWatchRemoteOption("bring_to_front", checked)
            }
            FormCard.FormDelegateSeparator {}
            FormCard.FormSwitchDelegate {
                text: i18n("Zwift Companion link")
                description: !page.wr.companionAllowed
                    ? i18n("Not available while the sensors come through the Zwift Companion app: Zwift accepts only one phone per account.")
                    : !page.wr.companion ? i18n("Show junctions and the power-up on the watch and steer without the keyboard – also straight on. Tretlager poses as the Companion app and replaces it on your phone.")
                    : page.wr.companionLinked ? i18n("Connected to the game – commands go straight to Zwift")
                    : page.wr.companionNoLogin ? i18n("Sign in to Zwift first (overview)")
                    : page.wr.companionError !== "" ? i18n("Zwift: %1", page.wr.companionError)
                    : i18n("Waiting for Zwift – the game connects once it runs")
                enabled: page.wr.companionAllowed
                checked: page.wr.companion && page.wr.companionAllowed
                onToggled: backend.setWatchRemoteOption("companion", checked)
                trailing: Kirigami.ContextualHelpButton {
                    toolTipText: i18n("Uses the same undocumented connection as the Zwift Companion app, with your Zwift sign-in. This contradicts Zwift's terms of service. While it is on, the Companion app on your phone loses its connection to the game.")
                }
            }
            FormCard.FormDelegateSeparator {}
            FormCard.FormSwitchDelegate {
                text: i18n("OpenBikeControl on the network")
                description: page.wr.obcConnected ? i18n("A trainer app is connected")
                    : i18n("Also offer the watch to trainer apps such as MyWhoosh or TrainingPeaks Virtual")
                checked: page.wr.obc
                onToggled: backend.setWatchRemoteOption("obc", checked)
            }
        },

        FormCard.FormHeader { title: i18n("Watch buttons") },
        FormCard.FormCard {
            Repeater {
                model: [
                    [i18n("Up (left)"), i18n("Turn left"), i18n("hold: menu")],
                    [i18n("Down (left)"), i18n("Ride On"), i18n("hold: straight on")],
                    [i18n("Start (right)"), i18n("Turn right"), i18n("hold: U-turn")],
                    [i18n("Back (right)"), i18n("Power-up"), i18n("hold: quit")]
                ]
                delegate: ColumnLayout {
                    required property var modelData
                    required property int index
                    Layout.fillWidth: true
                    spacing: 0
                    FormCard.FormDelegateSeparator { visible: index > 0 }
                    FormCard.FormTextDelegate {
                        Layout.fillWidth: true
                        text: modelData[1]
                        description: modelData[0] + " · " + modelData[2]
                    }
                }
            }
        }
    ]

    rightCards: [
        FormCard.FormHeader { title: i18n("Last actions") },
        FormCard.FormCard {
            FormCard.FormPlaceholderMessageDelegate {
                visible: page.wr.events.length === 0
                icon.name: "input-gamepad"
                text: i18n("No commands yet")
                explanation: i18n("Press a button on the watch or try one below.")
            }
            Repeater {
                model: page.wr.events
                delegate: ColumnLayout {
                    required property var modelData
                    required property int index
                    Layout.fillWidth: true
                    spacing: 0
                    FormCard.FormDelegateSeparator { visible: index > 0 }
                    FormCard.FormTextDelegate {
                        Layout.fillWidth: true
                        text: modelData.action
                        icon.name: modelData.result === "ok" ? "data-success" : "data-warning"
                        description: i18n("%1 · %2 · %3 ms", modelData.time,
                                          page.resultText[modelData.result] || modelData.result, modelData.ms)
                    }
                }
            }
        },

        FormCard.FormHeader {
            title: i18n("Try without the watch")
            trailing: Kirigami.ContextualHelpButton {
                toolTipText: i18n("Sends the command as if it came from the watch. Zwift has to be running; Tretlager brings it to the front first.")
            }
        },
        FormCard.FormCard {
            GridLayout {
                Layout.fillWidth: true
                Layout.margins: Kirigami.Units.largeSpacing
                columns: 3
                columnSpacing: Kirigami.Units.smallSpacing
                rowSpacing: Kirigami.Units.smallSpacing
                Repeater {
                    model: [["left", i18n("Left"), "go-previous"], ["straight", i18n("Straight on"), "go-up"],
                            ["right", i18n("Right"), "go-next"], ["rideon", i18n("Ride On"), "emblem-favorite"],
                            ["powerup", i18n("Power-up"), "games-highscores"], ["uturn", i18n("U-turn"), "edit-undo"]]
                    delegate: Controls.Button {
                        required property var modelData
                        Layout.fillWidth: true
                        text: modelData[1]
                        icon.name: modelData[2]
                        enabled: page.wr.running
                        onClicked: backend.testWatchAction(modelData[0])
                    }
                }
            }
        },

        FormCard.FormHeader { title: i18n("Set up the watch") },
        FormCard.FormCard {
            FormCard.FormTextDelegate {
                text: i18n("Install ZWindoor on the watch")
                description: i18n("Copy zwindoor.prg to the folder GARMIN/APPS on the watch (USB), then start ZWindoor from the apps list. It finds this computer by itself.")
                icon.name: "smartphone"
            }
        }
    ]
}
