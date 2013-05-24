# -*- coding: utf-8 -*-
# ixml.py
import midiformat
import codecs
from xml.etree.cElementTree import ElementTree, Element, SubElement, tostring, parse
from utils import booleanize


class MidiFile:
  def read(self, filename):
		tree = parse(filename)
		root = tree.getroot()

		midi_ = midiformat.MidiFile()

		header = HeaderChunk()

		midi_.header = header.read(root.find('HeaderChunk'))

		for i in xrange(midi_.header.nbTracks):
			track = TrackChunk()
			midi_.tracks.append(track.read(root.find('_' + str(i)).find('TrackChunk')))

		return midi_

	def write(self, filename, midi):
		

		midifile = Element('MidiFile')
		header = HeaderChunk()
		
		header.write(midifile, midi.header)

		i = 0
		for cur in midi.tracks:
			node = SubElement(midifile, '_' + str(i)) #garantit l'ordre des datas
			temp = TrackChunk()
			temp.write(node, cur)
			i += 1

		tree = ElementTree(midifile)
		tree.write(filename, encoding="utf-8")

		

		import xml.dom.minidom 

		root = xml.dom.minidom.parse(filename)

		f = open(filename, "w")
		f.write(root.toprettyxml())

class HeaderChunk:
	def read(self, node):
		header = midiformat.HeaderChunk()

		header.id = node.get('id')
		header.size = int(node.get('size'))
		header.format_type = int(node.get('format_type'))
		header.nbTracks = int(node.get('nbTracks'))
		header.timediv = int(node.get('timediv'))

		return header

	def write(self, root, header):
		node = SubElement(root, 'HeaderChunk')

		node.set("id", header.id)
		node.set("size", str(header.size))
		node.set("format_type", str(header.format_type))
		node.set("nbTracks", str(header.nbTracks))
		node.set("timediv", str(header.timediv))

class TrackChunk:
	def read(self, node):
		track = midiformat.TrackChunk()

		self._readHeader(node, track)

		i = 0
		track.data = [self._readData(node.find('_' + str(i)))]

		while not(isinstance(track.data[-1].event, midiformat.EndOfTrack)):
			i += 1
			track.data.append(self._readData(node.find('_' + str(i))))

		return track		

	def _readHeader(self, node, track):
		track.id = node.get('id')
		track.size = int(node.get('size'))

	def _readData(self, node):

		dt = int(node.find('dt').text)

		temp = None
		s = ""
		if node.find('MidiEvent') is not None:
			s = "MidiEvent"
			temp = MidiEvent()
		elif node.find('MetaEvent') is not None:
			s = "MetaEvent"
			temp = MetaEvent()
		elif node.find('SysExEvent') is not None:
			s = 'SysExEvent'
			temp = SysExEvent()
		else:
			raise UnknownTypeEvent('Unknown Type Event')

		return temp.read(dt, node.find(s))

	def write(self, root, track):
		node = SubElement(root, 'TrackChunk')
		node.set("id", track.id)
		node.set("size", str(track.size))

		i = 0
		for data in track.data:
			type_event = TypeEventFactory.get(data.name)
			event_node = SubElement(node, '_'+str(i))
			type_event.write(event_node, data)
			i += 1

class MidiEvent:
	def read(self, dt, node):
		data = midiformat.MidiEvent(dt)

		data.event = MidiEventFactory_str.get(node.get('type'), int(node.get('chan')))
		event = MidiEventFactory.get(data.event.value)
		event.read(node, data.event)

		return data

	def write(self, node, data):
		dt = SubElement(node, 'dt')
		dt.text = str(data.dt)

		midi_event = SubElement(node, 'MidiEvent')

		event = MidiEventFactory.get(data.event.value)
		event.write(midi_event, data.event)

class NoteOffEvent:
	def read(self, node, event):
		event.noteNumber = int(node.get('noteNumber'))
		event.velocity = int(node.get('velocity'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "NoteOffEvent")
		node.set("chan", str(event.midichan))
		node.set("noteNumber", str(event.noteNumber))
		node.set("velocity", str(event.velocity))
		node.set("before", str(event.before))

class NoteOnEvent:
	def read(self, node, event):
		event.noteNumber = int(node.get('noteNumber'))
		event.velocity = int(node.get('velocity'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "NoteOnEvent")
		node.set("chan", str(event.midichan))
		node.set("noteNumber", str(event.noteNumber))
		node.set("velocity", str(event.velocity))
		node.set("before", str(event.before))

class NoteAftertouchEvent:
	def read(self, node, event):
		event.noteNumber = int(node.get('noteNumber'))
		event.amount = int(node.get('amount'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "NoteAftertouchEvent")
		node.set("chan", str(event.midichan))
		node.set("noteNumber", str(event.noteNumber))
		node.set("amount", str(event.amount))
		node.set("before", str(event.before))

class ControllerEvent:
	def read(self, node, event):
		event.controllerType = int(node.get('controllerType'))
		event.controllerValue = int(node.get('controllerValue'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "ControllerEvent")
		node.set("chan", str(event.midichan))
		node.set("controllerType", str(event.controllerType))
		node.set("controllerValue", str(event.controllerValue))
		node.set("before", str(event.before))

class ProgramChangeEvent:
	def read(self, node, event):
		event.programNumber = int(node.get('programNumber'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "ProgramChangeEvent")
		node.set("chan", str(event.midichan))
		node.set("programNumber", str(event.programNumber))
		node.set("before", str(event.before))

class ChannelAftertouchEvent:
	def read(self, node, event):
		event.amount = int(node.get('amount'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "ChannelAftertouchEvent")
		node.set("chan", str(event.midichan))
		node.set("amount", str(event.amount))
		node.set("before", str(event.before))

class PitchBendEvent:
	def read(self, node, event):
		event.LSB_value = int(node.get('LSB_value'))
		event.MSB_value = int(node.get('MSB_value'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "PitchBendEvent")
		node.set("chan", str(event.midichan))
		node.set("LSB_value", str(event.LSB_value))
		node.set("MSB_value", str(event.MSB_value))
		node.set("before", str(event.before))

class MetaEvent:
	def read(self, dt, node):
		data = midiformat.MetaEvent(dt)

		data.event = MetaEventFactory_str.get(node.get('type'))

		event = MetaEventFactory.get(data.event.type)
		event.read(node, data.event)

		return data

	def write(self, node, data):
		dt = SubElement(node, 'dt')
		dt.text = str(data.dt)

		meta_event = SubElement(node, 'MetaEvent')

		event = MetaEventFactory.get(data.event.type)
		event.write(meta_event, data.event)

class SequenceNumber:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.MSB_number = int(node.get('MSB_number'))
		event.LSB_number = int(node.get('LSB_number'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "SequenceNumber")
		node.set("length", str(event.length))
		node.set("MSB_number", str(event.MSB_number))
		node.set("LSB_number", str(event.LSB_number))
		node.set("before", str(event.before))

class TextEvent:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.text = node.get('text')
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "TextEvent")
		node.set("length", str(event.length))
		node.set("text", event.text.decode("utf-8", errors='ignore').encode('utf-8')) #permet d'utiliser de l'utf-8 dans le xml
		node.set("before", str(event.before))

class CopyrightNotice:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.text = node.get('text')
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "CopyrightNotice")
		node.set("length", str(event.length))
		node.set("text", event.text.decode("utf-8").encode('utf-8'))
		node.set("before", str(event.before))

class TrackName:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.text = node.get('text')
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "TrackName")
		node.set("length", str(event.length))
		node.set("text", event.text.decode("utf-8", errors='ignore').encode('utf-8'))
		node.set("before", str(event.before))

class SequenceName(TrackName):
	pass

class InstrumentName:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.text = node.get('text')
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "InstrumentName")
		node.set("length", str(event.length))
		node.set("text", event.text.decode("utf-8", errors='ignore').encode('utf-8'))
		node.set("before", str(event.before))

class Lyrics:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.text = node.get('text')
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "Lyrics")
		node.set("length", str(event.length))
		node.set("text", event.text.decode("utf-8", errors='ignore').encode('utf-8'))
		node.set("before", str(event.before))

class Marker:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.text = node.get('text')
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "Marker")
		node.set("length", str(event.length))
		node.set("text", event.text.decode("utf-8", errors='ignore').encode('utf-8'))
		node.set("before", str(event.before))

class CuePoint:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.text = node.get('text')
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "CuePoint")
		node.set("length", str(event.length))
		node.set("text", event.text.decode("utf-8", errors='ignore').encode('utf-8'))
		node.set("before", str(event.before))

class MidiChannelPrefix:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.chan = int(node.get('chan'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "MidiChannelPrefix")
		node.set("length", str(event.length))
		node.set("chan", str(event.chan))
		node.set("before", str(event.before))

class MidiPortPrefix:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.chan = int(node.get('chan'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "MidiPortPrefix")
		node.set("length", str(event.length))
		node.set("chan", str(event.chan))
		node.set("before", str(event.before))

class EndOfTrack:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "EndOfTrack")
		node.set("length", str(event.length))
		node.set("before", str(event.before))

class SetTempo:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.MPQN = int(node.get('MPQN'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "SetTempo")
		node.set("length", str(event.length))
		node.set("MPQN", str(event.MPQN))
		node.set("before", str(event.before))

class SMPTEOffset:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.hour = int(node.get('hour'))
		event.framep = int(node.get('framep'))
		event.min = int(node.get('min'))
		event.sec = int(node.get('sec'))
		event.fr = int(node.get('fr'))
		event.subfr = int(node.get('subfr'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "SMPTEOffset")
		node.set("length", str(event.length))
		node.set("hour", str(event.hour))
		node.set("framep", str(event.framep))
		node.set("min", str(event.min))
		node.set("sec", str(event.sec))
		node.set("fr", str(event.fr))
		node.set("subfr", str(event.subfr))
		node.set("before", str(event.before))

class TimeSignature:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.numer = int(node.get('numer'))
		event.denom = int(node.get('denom'))
		event.metro = int(node.get('metro'))
		event._32nds = int(node.get('_32nds'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "TimeSignature")
		node.set("length", str(event.length))
		node.set("numer", str(event.numer))
		node.set("denom", str(event.denom))
		node.set("metro", str(event.metro))
		node.set("_32nds", str(event._32nds))
		node.set("before", str(event.before))

class KeySignature:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.key = int(node.get('key'))
		event.scale = int(node.get('scale'))
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "KeySignature")
		node.set("length", str(event.length))
		node.set("key", str(event.key))
		node.set("scale", str(event.scale))
		node.set("before", str(event.before))

class SequencerSpecific: 
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.data = [int(c) for c in node.get('data').split(' ')]
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "SequencerSpecific")
		node.set("length", str(event.length))
		node.set("data", " ".join([str(c) for c in event.data]))
		node.set("before", str(event.before))

class SysExEvent:
	def read(self, dt, node):
		data = midiformat.SysExEvent(dt)

		data.event = SysExEventFactory_str.get(node.get('type'))
		event = SysExEventFactory.get(data.event.value)
		event.read(node, data.event)

		return data

	def write(self, node, data):
		dt = SubElement(node, 'dt')
		dt.text = str(data.dt)

		sysex_event = SubElement(node, 'SysExEvent')

		event = SysExEventFactory.get(data.event.value)
		event.write(sysex_event, data.event)

class NormalSysExEvent:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.data = [int(c) for c in node.get('data').split(' ')]
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "NormalSysExEvent")
		node.set("length", str(event.length))
		node.set("data", " ".join([str(c) for c in event.data]))
		node.set("before", str(event.before))

class AuthSysExEvent:
	def read(self, node, event):
		event.length = int(node.get('length'))
		event.data = [int(c) for c in node.get('data').split(' ')]
		event.before = booleanize(node.get('before'))

	def write(self, node, event):
		node.set("type", "AuthSysExEvent")
		node.set("length", str(event.length))
		node.set("data", " ".join([str(c) for c in event.data]))
		node.set("before", str(event.before))

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
