# -*- coding: utf-8 -*-
# main.py

import midi.imidi
import midi.ijson
import midi.itxt
import midi.ixml
import argparse
import textwrap
import os

def getMidiFile(filename):
  if '.xml' in filename.lower():
		return midi.ixml.MidiFile()
	elif '.json' in filename.lower():
		return midi.ijson.MidiFile()
	elif '.txt' in filename.lower():
		return midi.itxt.MidiFile()
	elif '.mid' in filename.lower() or '.midi' in filename.lower():
		return midi.imidi.MidiFile()
	else:
		raise Exception('Format non supporté ou extension non renseignee')

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
description=textwrap.dedent("""\
							Utilitaire permettant de transformer un fichier MIDI d'un format a une autre, 
							les formats supportes sont : .mid ou .midi, .xml, .json, .txt. \n
							Usage : python main.py -f test.ext -to test.ext2
							.ext et .ext2 peuvent être : .mid, .midi, .txt, .json, .xml
							Vous pouvez donc transformer vos donnees MIDI en un autre format et l'inverse. \n 
							Exemples d'utilisation : 
							    python main.py -f test.mid -to test.xml \n
							    python main.py -f test.txt -to test_txt.mid \n
							    python main.py -f test.xml -to test.json"""))
parser.add_argument('-f')
parser.add_argument('-to')

args = parser.parse_args()

from_ = getMidiFile(args.f)
to = getMidiFile(args.to)

print 'Veuillez patienter...'

try:

	to.write(args.to, from_.read(args.f))
	print 'Succes !'
except IOError:
	print "Le fichier : " + args.f + " n'a pas ete trouve."
except UnicodeDecodeError as e:
	print "Veuillez nous excuser, l'operation ne pourra pas etre mene a bien en raison d'un non support d'un jeu de caractere du module xml ou json de python."
	print e.message
except midi.imidi.UnknownMetaEvent as e:
	print 'Erreur : ' + e.message
	print "Ce meta event n'est pas standard."
except Exception as e:
	print 'Une erreur est survenue.' + e.message
