# -*- coding: utf-8 -*-
# midiformat.py

class EventFactory: # classe mere de toutes les factorys
  @classmethod
	def get(cls, type, *args):
		return cls.types[type](*args)

class HeaderChunk:
	def __init__(self):
		self.id = ""
		self.size = 0
		self.format_type = 0
		self.nbTracks = 0
		self.timediv = 0

class MidiFile:
	def __init__(self):
		self.header = None
		self.tracks = []


class TrackChunk:
	def __init__(self):
		self.id = ""
		self.size = 0
		self.data = []

class MidiEvent:
	def __init__(self, dt = 0):
		self.dt = dt
		self.event = None
		self.name = "MidiEvent"

class NoteOffEvent:
	def __init__(self, midichan, before = False):
		self.value = 0x8
		self.midichan = midichan
		self.noteNumber = 0
		self.velocity = 0
		self.before = before

class NoteOnEvent:
	def __init__(self, midichan, before = False):
		self.value = 0x9
		self.midichan = midichan
		self.noteNumber = 0
		self.velocity = 0
		self.before = before

class NoteAftertouchEvent:
	def __init__(self, midichan, before = False):
		self.value = 0xA
		self.midichan = midichan
		self.noteNumber = 0
		self.amount = 0
		self.before = before

class ControllerEvent:
	def __init__(self, midichan, before = False):
		self.value = 0xB
		self.midichan = midichan
		self.controllerType = 0
		self.controllerValue = 0
		self.before = before

class ProgramChangeEvent:
	def __init__(self, midichan, before = False):
		self.value = 0xC
		self.midichan = midichan
		self.programNumber = 0
		self.before = before

class ChannelAftertouchEvent:
	def __init__(self, midichan, before = False):
		self.value = 0xD
		self.midichan = midichan
		self.amount = 0
		self.before = before

class PitchBendEvent:
	def __init__(self, midichan, before = False):
		self.value = 0xE
		self.midichan = midichan
		self.LSB_value = 0
		self.MSB_value = 0
		self.before = before

class MidiEventFactory(EventFactory):
	types = {0x8 : NoteOffEvent,
			 0x9 : NoteOnEvent,
			 0xA : NoteAftertouchEvent,
			 0xB : ControllerEvent,
			 0xC : ProgramChangeEvent,
			 0xD : ChannelAftertouchEvent,
			 0xE : PitchBendEvent}

class MetaEvent:
	def __init__(self, dt):
		self.value = 0xFF
		self.dt = dt
		self.name = "MetaEvent"

class SequenceNumber:
	def __init__(self, before = False):
		self.type = 0x00
		self.length = 0
		self.MSB_number = 0
		self.LSB_number = 0
		self.before = before

class TextEvent:
	def __init__(self, before = False):
		self.type = 0x01
		self.length = 0
		self.text = ""
		self.before = before

class CopyrightNotice:
	def __init__(self, before = False):
		self.type = 0x02
		self.length = 0
		self.text = ""
		self.before = before

class TrackName:
	def __init__(self, before = False):
		self.type = 0x03
		self.length = 0
		self.text = ""
		self.before = before

class SequenceName(TrackName):
	pass

class InstrumentName:
	def __init__(self, before = False):
		self.type = 0x04
		self.length = 0
		self.text = ""
		self.before = before

class Lyrics:
	def __init__(self, before = False):
		self.type = 0x05
		self.length = 0
		self.text = ""
		self.before = before

class Marker:
	def __init__(self, before = False):
		self.type = 0x06
		self.length = 0
		self.text = ""
		self.before = before

class CuePoint:
	def __init__(self, before = False):
		self.type = 0x07
		self.length = 0
		self.text = ""
		self.before = before

class MidiChannelPrefix:
	def __init__(self, before = False):
		self.type = 0x20
		self.length = 0
		self.chan = 0
		self.before = before

class MidiPortPrefix:
	def __init__(self, before = False):
		self.type = 0x21
		self.length = 0
		self.chan = 0
		self.before = before

class EndOfTrack:
	def __init__(self, before = False):
		self.type = 0x2F
		self.length = 0
		self.before = before

class SetTempo:
	def __init__(self, before = False):
		self.type = 0x51
		self.length = 0
		self.MPQN = 0
		self.before = before

class SMPTEOffset:
	def __init__(self, before = False):
		self.type = 0x54
		self.length = 0
		self.hour = 0
		self.framep = 0
		self.min = 0
		self.sec = 0
		self.fr = 0
		self.subfr = 0
		self.before = before

class TimeSignature:
	def __init__(self, before = False):
		self.type = 0x58
		self.length = 0
		self.numer = 0
		self.denom = 0
		self.metro = 0
		self._32nds = 0
		self.before = before

class KeySignature:
	def __init__(self, before = False):
		self.type = 0x59
		self.length = 0
		self.key = 0
		self.scale = 0
		self.before = before

class SequencerSpecific:
	def __init__(self, before = False):
		self.type = 0x7F
		self.length = 0
		self.data = []
		self.before = before

class MetaEventFactory(EventFactory):
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

class SysExEvent:
	def __init__(self, dt):
		self.dt = dt
		self.event = None
		self.name = "SysExEvent" 

class NormalSysExEvent:
	def __init__(self, before = False):
		self.value = 0xF0
		self.length = 0
		self.data = []
		self.before = before

class DivSysExEvent:
	def __init__(self, before = False):
		self.value = [0xF0, 0xF7, 0xF7]
		self.lengths = 0
		self.data = []
		self.before = before

class AuthSysExEvent:
	def __init__(self, before = False):
		self.value = 0xF7
		self.length = 0
		self.data = []
		self.before = before


