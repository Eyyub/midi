# -*- coding: utf-8 -*-
# ijson.py

from collections import OrderedDict
import midiformat
import json

class MidiFile:
  def read(self, filename):

		file = open(filename, 'r')
		file.seek(0)
		midi_ = midiformat.MidiFile()

		data = OrderedDict(json.load(file))

		temp = HeaderChunk()

		midi_.header = temp.read(data["HeaderChunk"])

		for i in xrange(midi_.header.nbTracks):
			temp2 = TrackChunk()
			midi_.tracks.append(temp2.read(data[str(i)]))

		file.close()
		return midi_ 

	def write(self, filename, midi):
		file = open(filename, 'w')
		file.seek(0)
		dico = OrderedDict()
		dico["HeaderChunk"] = {}
		header = HeaderChunk()
		header.write(dico, midi.header)

		i = 0
		for cur in midi.tracks:
			dico[i] = OrderedDict()
			temp = TrackChunk()
			temp.write(dico[i], cur)
			i += 1

		file.write(json.dumps(dico, indent=5))
		file.close()

class HeaderChunk:
	def read(self, dico):
		header = midiformat.HeaderChunk()

		header.id = dico["id"]
		header.size = dico["size"]
		header.format_type = dico["fmt_type"]
		header.nbTracks = dico["nbTracks"]
		header.timediv = dico["timediv"]

		return header

	def write(self, dico, header):
		temp = OrderedDict()

		temp["id"] = header.id
		temp["size"] = header.size
		temp["fmt_type"] = header.format_type
		temp["nbTracks"] = header.nbTracks
		temp["timediv"] = header.timediv

		dico["HeaderChunk"] = temp

class TrackChunk:
	def read(self, dico):
		track = midiformat.TrackChunk()
		self._readHeader(dico, track)

		i = 0
		track.data = [self._readData(dico[str(i)])]

		while not(isinstance(track.data[-1].event, midiformat.EndOfTrack)):
			i += 1
			track.data.append(self._readData(dico[str(i)]))

		return track

	def _readHeader(self, dico, track):
		track.id = dico["id"]
		track.size = dico["size"]

	def _readData(self, dico):

		dt = dico["dt"]
		temp = None
		s = ""
		if "MidiEvent" in dico:
			s = "MidiEvent"
			temp = MidiEvent()
		elif "MetaEvent" in dico:
			s = "MetaEvent"
			temp = MetaEvent()
		elif "SysExEvent" in dico:
			s = "SysExEvent"
			temp = SysExEvent()
		else:
			raise UnknownTypeEvent('Unknown Type Event')

		return temp.read(dt, dico[s])

	def write(self, dico, track):
		dico["id"] = track.id
		dico["size"] = track.size

		i = 0
		for data in track.data:
			type_event = TypeEventFactory.get(data.name)
			dico[i] = OrderedDict()
			type_event.write(dico[i], data)
			i += 1

class MidiEvent:
	def read(self, dt, dico):
		data = midiformat.MidiEvent(dt)

		data.event = MidiEventFactory_str.get(dico["type"], dico["chan"])

		event = MidiEventFactory.get(data.event.value)
		event.read(dico, data.event)

		return data

	def write(self, dico, data):
		dico["dt"] = data.dt
		dico["MidiEvent"] = OrderedDict()
		event = MidiEventFactory.get(data.event.value)
		event.write(dico, data.event)

class NoteOffEvent:
	def read(self, dico, event):
		event.noteNumber = dico["noteNumber"]
		event.velocity = dico["velocity"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()
		temp["type"] = "NoteOffEvent"
		temp["chan"] = event.midichan
		temp["noteNumber"] = event.noteNumber
		temp["velocity"] = event.velocity
		temp["before"] = event.before
		
		dico["MidiEvent"] = temp

class NoteOnEvent:
	def read(self, dico, event):
		event.noteNumber = dico["noteNumber"]
		event.velocity = dico["velocity"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()
		temp["type"] = "NoteOnEvent"
		temp["chan"] = event.midichan
		temp["noteNumber"] = event.noteNumber
		temp["velocity"] = event.velocity
		temp["before"] = event.before
		
		dico["MidiEvent"] = temp

class NoteAftertouchEvent:
	def read(self, dico, event):
		event.noteNumber = dico["noteNumber"]
		event.amount = dico["amount"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()
		temp["type"] = "NoteAftertouchEvent"
		temp["chan"] = event.midichan
		temp["noteNumber"] = event.noteNumber
		temp["amount"] = event.amount
		temp["before"] = event.before

		dico["MidiEvent"] = temp

class ControllerEvent:
	def read(self, dico, event):
		event.controllerType = dico["controllerType"]
		event.controllerValue = dico["controllerValue"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "ControllerEvent"
		temp["chan"] = event.midichan
		temp["controllerType"] = event.controllerType
		temp["controllerValue"] = event.controllerValue
		temp["before"] = event.before

		dico["MidiEvent"] = temp

class ProgramChangeEvent:
	def read(self, dico, event):
		event.programNumber = dico["programNumber"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "ProgramChangeEvent"
		temp["chan"] = event.midichan
		temp["programNumber"] = event.programNumber
		temp["before"] = event.before

		dico["MidiEvent"] = temp

class ChannelAftertouchEvent:
	def read(self, dico, event):
		event.amount = data["amount"]
		event.before = data["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "ChannelAftertouchEvent"
		temp["chan"] = event.midichan
		temp["amount"] = event.amount
		temp["before"] = event.before

		dico["MidiEvent"] = temp

class PitchBendEvent:
	def read(self, dico, event):
		event.LSB_value = dico["LSB_value"]
		event.MSB_value = dico["MSB_value"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "PitchBendEvent"
		temp["chan"] = event.midichan
		temp["LSB_value"] = event.LSB_value
		temp["MSB_value"] = event.MSB_value
		temp["before"] = event.before

		dico["MidiEvent"] = temp

class MetaEvent:
	def read(self, dt, dico):
		data = midiformat.MetaEvent(dt)

		data.event = MetaEventFactory_str.get(dico["type"])

		temp = MetaEventFactory.get(data.event.type)
		temp.read(dico, data.event)

		return data 

	def write(self, dico, data):
		dico["dt"] = data.dt
		dico["MetaEvent"] = OrderedDict()
		event = MetaEventFactory.get(data.event.type)
		event.write(dico, data.event)

class SequenceNumber:
	def read(self, dico, event):
		event.length = dico["length"]
		event.MSB_number = dico["MSB_number"]
		event.LSB_number = dico["LSB_number"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "SequenceNumber"
		temp["length"] = event.length
		temp["MSB_number"] = event.MSB_number
		temp["LSB_number"] = event.LSB_number
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class TextEvent:
	def read(self, dico, event):
		event.length = dico["length"]
		event.text = dico["text"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "TextEvent"
		temp["length"] = event.length
		temp["text"] = event.text
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class CopyrightNotice:
	def read(self, dico, event):
		event.length = dico["length"]
		event.text = dico["text"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "CopyrightNotice"
		temp["length"] = event.length
		temp["text"] = event.text
		temp["before"] = event.before

		dico["MetaEvent"] = temp	

class TrackName:
	def read(self, dico, event):
		event.length = dico["length"]
		event.text = dico["text"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "TrackName"
		temp["length"] = event.length
		temp["text"] = event.text
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class SequenceName(TrackName):
	pass

class InstrumentName:
	def read(self, dico, event):
		event.length = dico["length"]
		event.text = dico["text"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "InstrumentName"
		temp["length"] = event.length
		temp["text"] = event.text
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class Lyrics:
	def read(self, dico, event):
		event.length = dico["length"]
		event.text = dico["text"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "Lyrics"
		temp["length"] = event.length
		temp["text"] = event.text
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class Marker:
	def read(self, dico, event):
		event.length = dico["length"]
		event.text = dico["text"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "Marker"
		temp["length"] = event.length
		temp["text"] = event.text
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class CuePoint:
	def read(self, dico, event):
		event.length = dico["length"]
		event.text = dico["text"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "CuePoint"
		temp["length"] = event.length
		temp["text"] = event.text
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class MidiChannelPrefix:
	def read(self, dico, event):
		event.length = dico["length"]
		event.chan = dico["chan"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "MidiChannelPrefix"
		temp["length"] = event.length
		temp["chan"] = event.chan
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class MidiPortPrefix:
	def read(self, dico, event):
		event.length = dico["length"]
		event.chan = dico["chan"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "MidiPortPrefix"
		temp["length"] = event.length
		temp["chan"] = event.chan
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class EndOfTrack:
	def read(self, dico, event):
		event.length = dico["length"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "EndOfTrack"
		temp["length"] = event.length
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class SetTempo:
	def read(self, dico, event):
		event.length = dico["length"]
		event.MPQN = dico["MPQN"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "SetTempo"
		temp["length"] = event.length
		temp["MPQN"] = event.MPQN
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class SMPTEOffset:
	def read(self, dico, event):
		event.length = dico["length"]
		event.hour = dico["hour"]
		event.framep = dico["framep"]
		event.min = dico["min"]
		event.sec = dico["sec"]
		event.fr = dico["fr"]
		event.subfr = dico["subfr"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "SMPTEOffset"
		temp["length"] = event.length
		temp["hour"] = event.hour
		temp["framep"] = event.framep
		temp["min"] = event.min
		temp["sec"] = event.sec
		temp["fr"] = event.fr
		temp["subfr"] = event.subfr
		temp["before"] = event.before

		dico["MetaEvent"]= temp

class TimeSignature:
	def read(self, dico, event):
		event.length = dico["length"]
		event.numer = dico["numer"]
		event.denom = dico["denom"]
		event.metro = dico["metro"]
		event._32nds = dico["32nds"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "TimeSignature"
		temp["length"] = event.length
		temp["numer"] = event.numer
		temp["denom"] = event.denom
		temp["metro"] = event.metro
		temp["32nds"] = event._32nds
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class KeySignature:
	def read(self, dico, event):
		event.length = dico["length"]
		event.key = dico["key"]
		event.scale = dico["scale"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "KeySignature"
		temp["length"] = event.length
		temp["key"] = event.key
		temp["scale"] = event.scale
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class SequencerSpecific:
	def read(self, dico, event):
		event.length = dico["length"]
		event.data = dico["data"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "SequencerSpecific"
		temp["length"] = event.length
		temp["data"] = event.data
		temp["before"] = event.before

		dico["MetaEvent"] = temp

class SysExEvent:
	def read(self, dt, dico):
		data = midiformat.SysExEvent(dt)

		data.event = SysExEventFactory_str.get(dico["type"])

		temp = SysExEventFactory.get(data.event.value)
		temp.read(dico, data.event)

		return data

	def write(self, dico, data):
		dico["dt"] = data.dt
		dico["SysExEvent"] = OrderedDict()
		event = SysExEventFactory.get(data.event.value)
		event.write(dico, data.event)

class NormalSysExEvent:
	def read(self, dico, event):
		event.length = dico["length"]
		event.data = dico["data"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "NormalSysExEvent"
		temp["length"] = event.length
		temp["data"] = event.data
		temp["before"] = event.before

		dico["SysExEvent"] = temp

class AuthSysExEvent:
	def read(self, dico, event):
		event.length = dico["length"]
		event.data = dico["data"]
		event.before = dico["before"]

	def write(self, dico, event):
		temp = OrderedDict()

		temp["type"] = "AuthSysExEvent"
		temp["length"] = event.length
		temp["data"] = event.data
		temp["before"] = event.before

		dico["SysExEvent"] = temp

class TypeEventFactory(midiformat.EventFactory):
	types = {"MidiEvent"  : MidiEvent,
			 "MetaEvent"  : MetaEvent,
			 "SysExEvent" : SysExEvent}

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


class MidiEventFactory(midiformat.EventFactory):
	types = {0x8 : NoteOffEvent,
			 0x9 : NoteOnEvent,
			 0xA : NoteAftertouchEvent,
			 0xB : ControllerEvent,
			 0xC : ProgramChangeEvent,
			 0xD : ChannelAftertouchEvent,
			 0xE : PitchBendEvent}

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

class UnknownTypeEvent(Exception):
	pass
