# -*- coding: utf-8 -*-
# itxt.py
import midiformat
import re
from utils import booleanize

parser = re.compile('=([A-Za-z0-9]+|\".+\n*\"|\[.+\]|\"\"|\"\n+\"|-[0-9]+)') # regex qui permet de matcher les valeurs des champs des events MIDI



class HeaderChunk:
  def read(self, line):
		data = parser.findall(line)

		header = midiformat.HeaderChunk()
		header.id = data[0]
		header.size = int(data[1])
		header.format_type = int(data[2])
		header.nbTracks = int(data[3])
		header.timediv = int(data[4])
		
		return header

	def write(self, file, header):
		file.write("id={} size={} fmt_type={} nbTracks={} timediv={}\n".format(header.id, header.size, header.format_type, header.nbTracks, header.timediv))

class MidiFile:
	def read(self, filename):
		midi_ = midiformat.MidiFile()
		file = open(filename, 'r')
		file.seek(0)
		

		# Des fois un event ayant un champ text peut contenir un \n donc il faut lire la suite de la ligne
		b = True
		l = ""
		lines = []
		for line in file.readlines():
			if "id=MThd" in line or "id=MTrk" in line or "before=" in line:
				lines.append(l+line)
				b = True
			else:
				l += line
				b = False

			if b == True:
				l = ""
				
		temp = HeaderChunk()
		midi_.header = temp.read(lines[0])
		del lines[0]
		for i in xrange(midi_.header.nbTracks):
			temp2 = TrackChunk()
			midi_.tracks.append(temp2.read(lines))
		file.close()
		return midi_

	def write(self, filename, midi):
		file = open(filename, 'w')
		file.seek(0)
		header = HeaderChunk()
		header.write(file, midi.header)

		for cur in midi.tracks:
			temp = TrackChunk()
			temp.write(file, cur)

		file.close()




class TrackChunk:

	def read(self, lines):
		track = midiformat.TrackChunk()
		self._readHeader(lines[0], track)
		del lines[0]
		track.data = [self._readData(lines[0])]
		del lines[0]
		while not(isinstance(track.data[-1].event, midiformat.EndOfTrack)):
			track.data.append(self._readData(lines[0]))
			del lines[0]
		return track

	def _readHeader(self, line, track):
		data = parser.findall(line)
		track.id = data[0]
		track.size = int(data[1])

	def _readData(self, line):
		data = parser.findall(line)

		dt = int(data[0])

		temp = TypeEventFactory.get(data[1])

		return temp.read(dt, data[2:])


	def write(self, file, track):
		file.write("id={} size={}\n".format(track.id, track.size))
		for data in track.data:
			type_event = TypeEventFactory.get(data.name)
			type_event.write(file, data)


class MidiEvent:
	def read(self, dt, _data):
		data = midiformat.MidiEvent(dt)

		data.event = MidiEventFactory_str.get(_data[0], int(_data[1]))

		event = MidiEventFactory.get(data.event.value)
		event.read(_data[2:], data.event)

		return data

	def write(self, file, data):
		file.write("dt={} event=MidiEvent ".format(data.dt))
		event = MidiEventFactory.get(data.event.value)
		event.write(file, data.event)

class NoteOffEvent:
	def read(self, data, event):
		event.noteNumber = int(data[0])
		event.velocity = int(data[1])
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write("type=NoteOffEvent chan={} noteNumber={} velocity={} before={}\n".format(event.midichan, event.noteNumber, event.velocity, event.before))

class NoteOnEvent:
	def read(self, data, event):
		event.noteNumber = int(data[0])
		event.velocity = int(data[1])
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write("type=NoteOnEvent chan={} noteNumber={} velocity={} before={}\n".format(event.midichan, event.noteNumber, event.velocity, event.before))

class NoteAftertouchEvent:
	def read(self, data, event):
		event.noteNumber = int(data[0])
		event.amount = int(data[1])
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write("type=NoteAftertouchEvent chan={} noteNumber={} amount={} before={}\n".format(event.midichan, event.noteNumber, event.amount, event.before))

class ControllerEvent:
	def read(self, data, event):
		event.controllerType = int(data[0])
		event.controllerValue = int(data[1])
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write("type=ControllerEvent chan={} controllerType={} controllerValue={} before={}\n".format(event.midichan, event.controllerType, event.controllerValue, event.before))

class ProgramChangeEvent:
	def read(self, data, event):
		event.programNumber = int(data[0])
		event.before = booleanize(data[1])

	def write(self, file, event):
		file.write("type=ProgramChangeEvent chan={} programNumber={} before={}\n".format(event.midichan, event.programNumber, event.before))

class ChannelAftertouchEvent:
	def read(self, data, event):
		event.amount = int(data[0])
		event.before = booleanize(data[1])

	def write(self, file, event):
		file.write("type=ChannelAftertouchEvent chan={} amount={} before={}\n".format(event.midichan, event.amount, event.before))

class PitchBendEvent:
	def read(self, data, event):
		event.LSB_value = int(data[0])
		event.MSB_value = int(data[1])
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write("type=PitchBendEvent chan={} LSB_value={} MSB_value={} before={}\n".format(event.midichan, event.LSB_value, event.MSB_value, event.before))

class MidiEventFactory(midiformat.EventFactory):
	types = {0x8 : NoteOffEvent,
			 0x9 : NoteOnEvent,
			 0xA : NoteAftertouchEvent,
			 0xB : ControllerEvent,
			 0xC : ProgramChangeEvent,
			 0xD : ChannelAftertouchEvent,
			 0xE : PitchBendEvent}


class MetaEvent:
	def read(self, dt, _data):
		data = midiformat.MetaEvent(dt)

		data.event = MetaEventFactory_str.get(_data[0])

		temp = MetaEventFactory.get(data.event.type)
		temp.read(_data[1:], data.event)

		return data

	def write(self, file, data):
		file.write("dt={} event=MetaEvent ".format(data.dt))
		event = MetaEventFactory.get(data.event.type)
		event.write(file, data.event)

class SequenceNumber:
	def read(self, data, event):
		event.length = int(data[0])
		event.MSB_number = int(data[1])
		event.LSB_number = int(data[2])
		event.before = booleanize(data[3])

	def write(self, file, event):
		file.write("type=SequenceNumber length={} MSB_number={} LSB_number={} before={}\n".format(event.length, event.MSB_number, event.LSB_event, event.before))

class TextEvent:
	def read(self, data, event):
		event.length = int(data[0])
		event.text = data[1].strip('"')
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write('type=TextEvent length={} text="{}" before={}\n'.format(event.length, event.text, event.before))

class CopyrightNotice:
	def read(self, data, event):
		event.length = int(data[0])
		event.text = data[1].strip('"')
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write('type=CopyrightNotice length={} text="{}" before={}\n'.format(event.length, event.text, event.before))

class TrackName:
	def read(self, data, event):
		event.length = int(data[0])
		event.text = data[1].strip('"')
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write('type=TrackName length={} text="{}" before={}\n'.format(event.length, event.text, event.before))

class SequenceName(TrackName):
	pass

class InstrumentName:
	def read(self, data, event):
		event.length = int(data[0])
		event.text = data[1].strip('"')
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write('type=InstrumentName length={} text="{}" before={}\n'.format(event.length, event.text, event.before))

class Lyrics:
	def read(self, data, event):
		event.length = int(data[0])
		event.text = data[1].strip('"')
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write('type=Lyrics length={} text="{}" before={}\n'.format(event.length, event.text, event.before))

class Marker:
	def read(self, data, event):
		event.length = int(data[0])
		event.text = data[1].strip('"')
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write('type=Marker length={} text="{}" before={}\n'.format(event.length, event.text, event.before))

class CuePoint:
	def read(self, data, event):
		event.length = int(data[0])
		event.text = data[1].strip('"')
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write('type=CuePoint length={} text="{}" before={}\n'.format(event.length, event.text, event.before))

class MidiChannelPrefix:
	def read(self, data, event):
		event.length = int(data[0])
		event.chan = int(data[1])
		event.before = booleanize(data[2])
	def write(self, file, event):
		file.write("type=MidiChannelPrefix length={} chan={} before={}\n".format(event.length, event.chan, event.before))

class MidiPortPrefix:
	def read(self, data, event):
		event.length = int(data[0])
		event.chan = int(data[1])
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write("type=MidiPortPrefix length={} chan={} before={}\n".format(event.length, event.chan, event.before))

class EndOfTrack:
	def read(self, data, event):
		event.length = int(data[0])
		event.before = booleanize(data[1])
	def write(self, file, event):
		file.write("type=EndOfTrack length={} before={}\n".format(event.length, event.before))

class SetTempo:
	def read(self, data, event):
		event.length = int(data[0])
		event.MPQN = int(data[1])
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write("type=SetTempo length={} MPQN={} before={}\n".format(event.length, event.MPQN, event.before))

class SMPTEOffset:
	def read(self, data, event):
		event.length = int(data[0])
		event.hour = int(data[1])
		event.framep = int(data[2])
		event.min = int(data[3])
		event.sec = int(data[4])
		event.fr = int(data[5])
		event.subfr = int(data[6])
		event.before = booleanize(data[7])

	def write(self, file, event):
		file.write("type=SMPTEOffset length={} hour={} framep={} min={} sec={} fr={} subfr={} before={}\n".format(event.length, event.hour, event.framep, event.min, event.sec, event.fr, event.subfr, event.before))

class TimeSignature:
	def read(self, data, event):
		event.length = int(data[0])
		event.numer = int(data[1])
		event.denom = int(data[2])
		event.metro = int(data[3])
		event._32nds = int(data[4])
		event.before = booleanize(data[5])

	def write(self, file, event):
		file.write("type=TimeSignature length={} numer={} / denom={} metro={} 32nds={} before={}\n".format(event.length, event.numer, event.denom, event.metro, event._32nds, event.before))

class KeySignature:
	def read(self, data, event):
		event.length = int(data[0])
		event.key = int(data[1])
		event.scale = int(data[2])
		event.before = booleanize(data[3])
	def write(self, file, event):
		file.write("type=KeySignature length={} key={} scale={} before={}\n".format(event.length, event.key, event.scale, event.before))

class SequencerSpecific:
	def read(self, data, event):
		event.length = int(data[0])
		event.data = [int(c) for c in data[1].strip('[').strip(']').split(', ')]
		event.before = booleanize(data[2])
	def write(self, file, event):
		file.write("type=SequencerSpecific length={} data={} before={}\n".format(event.length, event.data, event.before))

class SysExEvent:
	def read(self, dt, _data):
		data = midiformat.SysExEvent(dt)

		data.event = SysExEventFactory_str.get(_data[0])

		event = SysExEventFactory.get(data.event.value)
		event.read(_data[1:], data.event)

		return data

	def write(self, file, data):
		file.write("dt={} event=SysExEvent ".format(data.dt))
		event = SysExEventFactory.get(data.event.value)
		event.write(file, data.event)
	
class NormalSysExEvent:
	def read(self, data, event):
		event.length = int(data[0])
		event.data = [int(c) for c in data[1].strip('[').strip(']').split(', ')]
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write("type=NormalSysExEvent length={} data={} before={}\n".format(event.length, event.data, event.before))

class AuthSysExEvent:
	def read(self, data, event):
		event.length = int(data[0])
		event.data = [int(c) for c in data[1].strip('[').strip(']').split(', ')]
		event.before = booleanize(data[2])

	def write(self, file, event):
		file.write("type=AuthSysExEvent length={} data={} before={}\n".format(event.length, event.data, event.before))	

class TypeEventFactory(midiformat.EventFactory):
	types = {"MidiEvent"  : MidiEvent,
			 "MetaEvent"  : MetaEvent,
			 "SysExEvent" : SysExEvent}

class MetaEventFactory(midiformat.EventFactory):
	types = {0x00 : SequenceNumber,
			 0x01 : TextEvent,
			 0x02 : CopyrightNotice,
			 0x03 : TrackName,
			 0x04 : InstrumentName,
			 0x05 : Lyrics,
			 0x06 : Marker,
			 0x07 : CuePoint,
			 0x20 : MidiChannelPrefix,
			 0x21 : MidiPortPrefix,
			 0x2F : EndOfTrack,
			 0x51 : SetTempo,
			 0x54 : SMPTEOffset,
			 0x58 : TimeSignature,
			 0x59 : KeySignature,
			 0x7F : SequencerSpecific}


class SysExEventFactory(midiformat.EventFactory):
	types = {0xF0 : NormalSysExEvent,
			 0xF7 : AuthSysExEvent}

class MidiEventFactory_str(midiformat.EventFactory):
	types = {"NoteOffEvent" : midiformat.NoteOffEvent,
			 "NoteOnEvent"  : midiformat.NoteOnEvent,
			 "NoteAftertouchEvent" : midiformat.NoteAftertouchEvent,
			 "ControllerEvent" : midiformat.ControllerEvent,
			 "ProgramChangeEvent" : midiformat.ProgramChangeEvent,
			 "ChannelAftertouchEvent" : midiformat.ChannelAftertouchEvent,
			 "PitchBendEvent" : midiformat.PitchBendEvent}

class MetaEventFactory_str(midiformat.EventFactory):
	types = {"SequenceNumber" : midiformat.SequenceNumber,
			 "TextEvent" : midiformat.TextEvent,
			 "CopyrightNotice" : midiformat.CopyrightNotice,
			 "TrackName" : midiformat.TrackName,
			 "SequenceName" : midiformat.SequenceName,
			 "InstrumentName" : midiformat.InstrumentName,
			 "Lyrics" : midiformat.Lyrics,
			 "Marker" : midiformat.Marker,
			 "CuePoint" : midiformat.CuePoint,
			 "MidiChannelPrefix" : midiformat.MidiChannelPrefix,
			 "MidiPortPrefix" : midiformat.MidiPortPrefix,
			 "EndOfTrack" : midiformat.EndOfTrack,
			 "SetTempo" : midiformat.SetTempo,
			 "SMPTEOffset" : midiformat.SMPTEOffset,
			 "TimeSignature" : midiformat.TimeSignature,
			 "KeySignature" : midiformat.KeySignature,
			 "SequencerSpecific" : midiformat.SequencerSpecific}

class SysExEventFactory_str(midiformat.EventFactory):
	types = {"NormalSysExEvent" : midiformat.NormalSysExEvent,
			 "AuthSysExEvent" : midiformat.AuthSysExEvent}

