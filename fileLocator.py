#!/usr/bin/env python3

import fnmatch
import os
import argparse
import PySimpleGUI as sg
try:
    import newzipfile as zipfile
    ziplib_found = True
except ImportError:
    zipfile = None
    ziplib_found = False


def_pattern = 'log4j*.jar'
parser = argparse.ArgumentParser()
result_list = []


def print_greeting():
    char_line = '-'
    char_horiz_line = '|'
    line = char_line * 40
    greetings_text = '   Dateisuche....   '
    diff_line = char_line * int((len(line) - len(greetings_text)) / 2)

    print(char_horiz_line + line + char_horiz_line)
    print(char_horiz_line + diff_line + greetings_text + diff_line + char_horiz_line)
    print(char_horiz_line + line + char_horiz_line)


def gui_start():
    # Layout für das Suchfenster
    layout = [[sg.Text('Bitte Suchmuster eingeben:')],
              [sg.InputText()], [sg.Checkbox('JMSAppender.class löschen?')],
              [sg.Submit(), sg.Cancel()]]

    window = sg.Window('Dateisuche...', layout)
    # Event und Text-tupel
    event, values = window.read()
    window.close()
    # Text auslesen
    text_input = values[0]
    check_del = values[1]
    return text_input, check_del, event


def gui_popup_result(result_data):
    layout = [[sg.Listbox(result_data, expand_x=True, expand_y=True)], [sg.Button('OK', key='OK')]]
    window = sg.Window('Ergebnis', layout, resizable=True, size=(800, 600), finalize=True)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == 'OK':
            break
        else:
            print('Ende')
    window.close()


def search(patterns, loc):
    for path, dirs, files in os.walk(loc):
        for file in fnmatch.filter(files, patterns):
            yield os.path.join(path, file)


def argparser():
    parser.add_argument('--default', '-d', nargs='?', const=def_pattern,
                        required=False,
                        help='Without an argument the default search pattern "log4*.jar" is used '
                             '- with an argument you can set your own search pattern')

    parser.add_argument('--remove', '-r', nargs='?', const=def_pattern,
                        required=False,
                        help='Remove JMSAppender.class from archive log4j.jar (newzipfile lib required)')
    args = parser.parse_args()
    # Alles im Dict speichern
    arg_dic = vars(args)
    # print(arg_dic)
    return arg_dic


def locate(args, remove, guimode):
    no_more_data = 'Keine weiteren Dateien gefunden!\n'
    err_module = '>>> Fehler beim Löschen: Modul newzipfile nicht gefunden. Keine Dateien modifiziert! <<<\n'
    location = os.path.dirname(os.path.abspath(__file__))
    empty_obj = object()
    result_list.append('Pattern \'%s\' übergeben' % args)

    result = search(args, location)
    # Elemente aus generator ausgeben
    for element in result:
        result_list.append(element)
        # Option zum Löschen aus Archiv der JMSAppender.class
        if remove and ziplib_found:
            with zipfile.ZipFile(element, 'a') as z:
                z.remove(f"org/apache/log4j/net/JMSAppender.class")

    # Bei leerem generator Meldung, dass keine weiteren Ergebnisse gefunden wurden
    if next(result, empty_obj) == empty_obj:
        result_list.append(no_more_data)
        if remove and ziplib_found is False:
            result_list.append(err_module)

    if guimode:
        gui_popup_result(result_list)
    else:
        for element in result_list:
            print(element)


def main():
    # Argparser
    args_dic = argparser()
    # Anhand der Keys im Dict Optionen aufrufen
    if args_dic['default'] is not None and args_dic['remove'] is None:  # DEFAULT
        print_greeting()
        locate(args_dic['default'], False, False)
    elif args_dic['default'] is None and args_dic['remove'] is not None:  # REMOVE
        print_greeting()
        locate(args_dic['remove'], True, False)
    elif args_dic['default'] is None and args_dic['remove'] is None:  # NONE
        text_input, check_del, event = gui_start()
        locate(text_input, check_del, True)


main()
