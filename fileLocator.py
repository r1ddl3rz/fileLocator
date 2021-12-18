#!/usr/bin/env python3

import fnmatch
import os
import argparse
import sys
try:
    import newzipfile as zipfile
    ziplib_found = True
except ImportError:
    ziplib_found = False


def_pattern = 'log4j*.jar'
parser = argparse.ArgumentParser()


def print_greeting():
    char_line = '-'
    char_horiz_line = '|'
    line = char_line * 40
    greetings_text = '   Dateisuche....   '
    diff_line = char_line * int((len(line) - len(greetings_text)) / 2)

    print(char_horiz_line + line + char_horiz_line)
    print(char_horiz_line + diff_line + greetings_text + diff_line + char_horiz_line)
    print(char_horiz_line + line + char_horiz_line)


def search(patterns, loc):
    for path, dirs, files in os.walk(loc):
        for file in fnmatch.filter(files, patterns):
            yield os.path.join(path, file)


def argparser():
    parser.add_argument('--default', '-d', nargs='?', const=def_pattern,
                        required=False,
                        help='Without an argument the default search pattern is used '
                             '- with an argument you can set your own search pattern')

    parser.add_argument('--remove', '-r', nargs='?', const=def_pattern,
                        required=False,
                        help='Remove JMSAppender.class from archive log4j.jar (newzipfile lib required)')
    args = parser.parse_args()
    # Alles im Dict speichern
    arg_dic = vars(args)
    # print(arg_dic)
    return arg_dic


def locate(args, remove):
    location = os.path.dirname(os.path.abspath(__file__))
    empty_obj = object()
    print('Pattern \'%s\' übergeben' % args, '\n')

    result = search(args, location)
    # print(result)
    # Elemente aus generator ausgeben
    for element in result:
        print(element)
        # Option zum Löschen aus Archiv der JMSAppender.class
        if remove and ziplib_found:
            with zipfile.ZipFile(element, 'a') as z:
                z.remove(f"org/apache/log4j/net/JMSAppender.class")

    # Bei leerem generator Meldung
    if next(result, empty_obj) == empty_obj:
        print('Keine weiteren Dateien gefunden!\n')
        if remove and ziplib_found is False:
            print('>>> Fehler beim Löschen: Modul newzipfile nicht gefunden. Keine Dateien modifiziert! <<<\n')


def main():
    # Argparser
    args_dic = argparser()
    # Anhand der Keys im Dict Optionen aufrufen
    if args_dic['default'] is not None and args_dic['remove'] is None:
        print_greeting()
        locate(args_dic['default'], False)
    elif args_dic['default'] is None and args_dic['remove'] is not None:
        print_greeting()
        locate(args_dic['remove'], True)
    elif args_dic['default'] is None and args_dic['remove'] is None:
        parser.print_help()
        sys.exit(2)


main()
