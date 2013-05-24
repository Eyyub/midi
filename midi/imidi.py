# -*- coding: utf-8 -*-
# imidi.py

import midiformat
from utils import read_VLV, write_VLV
import struct

class HeaderChunk:
  def read(self, file):
		header = midiformat.HeaderChunk()
		header.id = file.read(4)
		header.size, header.format_type, header.nbTracks, header.timediv = struct.unpack('>IHHH', file.read(10))
		return header

	def write(self, file, header):
		file.write(header.id)
		file.write(struct.pack('>IHHH', header.size, header.format_type, header.nbTracks, header.timediv))

class MidiFile:
	def read(self, filename):
		midi_ = midiformat.MidiFile()
		file = open(filename, 'rb')
		file.seek(0)
		temp = HeaderChunk()
		midi_.header = temp.read(file)
		
		for i in xrange(midi_.header.nbTracks):
			temp = TrackChunk()
			midi_.tracks.append(temp.read(file))

		file.close()
		return midi_

	def write(self, filename, midi):
		file = open(filename, 'wb')
		file.seek(0)
		header = HeaderChunk()
		header.write(file, midi.header)

		for cur in midi.tracks:
			track = TrackChunk()
			track.write(file, cur)
		file.close()

class TrackChunk:
	def read(self, file):
		track = midiformat.TrackChunk()
		self._readHeader(file, track)

		track.data = [self._readData(file, track)]
		while not(isinstance(track.data[-1].event, midiformat.EndOfTrack)): #Tant qu'on ne rencontre pas un EndOfTrack event, les events appartiennent au TrackChunk actuel
			track.data.append(self._readData(file, track))
		return track

	def _readHeader(self, file, track):
		track.id = file.read(4)
		track.size, = struct.unpack('>I', file.read(4))

	def _readData(self, file, track):
		dt = read_VLV(file)

		value, = struct.unpack('>B', file.read(1))

		if value == 0xFF:
			temp = MetaEvent()			
			return  temp.read(file, dt)
		elif value in [0xF0, 0xF7]:
			file.seek(file.tell() - 1)
			temp = SysExEvent()
			
			return temp.read(file, dt)
		elif ((value & 0xF0) >> 4) in [0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE]: # le type d'un MidiEvent est decrit sur les bits y : yyyynnnn et les bits n signifient le channel
			temp = MidiEvent()
			
			return temp.read(file, dt, value)
		else: # On passe par ici lorsque la valeur censee correspondre a un type d'event n'y correspond pas,
			  # l'on sait donc d'après la spec MIDI que cette valeur ne correspond pas a un event
			  # et qu'il faut instancier le dernier event joue

			file.seek(file.tell() - 1) # on retourne d'un octet en arriere vu que la valeur ne correspond pas a un event
			before_event = track.data[-1].__class__(dt) # on instancie le type d'event du dernier event

			if isinstance(before_event, midiformat.MidiEvent):
				temp = MidiEvent()
				return temp.read(file, dt, (((track.data[-1].event.value << 4) & 0xF0) | (track.data[-1].event.midichan & 0x0F)), before=True) # le parametre before permettra au programme de garder en memoire qu'il ne faut pas ecrire la valeur d'un event à ce moment la
			elif isinstance(before_event, midiformat.MetaEvent):
				temp = MetaEvent()
				return temp.read(file, dt, before=True)
			elif isinstance(before_event, midiformat.SysExEvent):
				temp = SysExEvent()
				return temp.read(file, dt, before=True)

	def write(self, file, track):
		file.write(track.id)
		file.write(struct.pack('>I', track.size))

		for curdata in track.data:
			type_event = TypeEventFactory.get(curdata.name)
			type_event.write(file, curdata)


class MidiEvent:
	def read(self, file, dt, buffer, before = False):
		data = midiformat.MidiEvent(dt)
		type = (buffer & 0xF0) >> 4
		chan = buffer & 0xF
		data.event = midiformat.MidiEventFactory.get(type, chan, before)

		temp = MidiEventFactory.get(data.event.value)
		temp.read(file, data.event)
		return data

	def write(self, file, data):
		write_VLV(data.dt, file)
		event = MidiEventFactory.get(data.event.value)
		event.write(file, data.event)

class NoteOffEvent:
	def read(self, file, event):
		event.noteNumber, event.velocity = struct.unpack('>BB', file.read(2))

	def write(self, file, event):
		if event.before:
			file.write(struct.pack('>BB', event.noteNumber, event.velocity))
		else:
			file.write(struct.pack('>BBB', (((event.value & 0xF) << 4) | (event.midichan & 0xF)), event.noteNumber, event.velocity))		

class NoteOnEvent:
	def read(self, file, event):
		event.noteNumber, event.velocity = struct.unpack('>BB', file.read(2))

	def write(self, file, event):
		if event.before:
			file.write(struct.pack('>BB', event.noteNumber, event.velocity))
		else:
			file.write(struct.pack('>BBB', (((event.value & 0xF) << 4) | (event.midichan & 0xF)), event.noteNumber, event.velocity))

class NoteAftertouchEvent:
	def read(self, file, event):
		event.noteNumber, event.amount = struct.unpack('>BB', file.read(2))

	def write(self, file, event):
		if event.before:
			file.write(struct.pack('>BB', event.noteNumber, event.amount))
		else:
			file.write(struct.pack('>BBB', (((event.value & 0xF) << 4) | (event.midichan & 0xF)), event.noteNumber, event.amount))

class ControllerEvent:
	def read(self, file, event):
		event.controllerType, event.controllerValue = struct.unpack('>BB', file.read(2))

	def write(self, file, event):
		if event.before:
			file.write(struct.pack('>BB', event.controllerType, event.controllerValue))
		else:
			file.write(struct.pack('>BBB', (((event.value & 0xF) << 4) | (event.midichan & 0xF)), event.controllerType, event.controllerValue))

class ProgramChangeEvent:
	def read(self, file, event):
		event.programNumber, = struct.unpack('>B', file.read(1))

	def write(self, file, event):
		if event.before:
			file.write(struct.pack('>B', event.programNumber))
		else:
			file.write(struct.pack('>BB', (((event.value & 0xF) << 4) | (event.midichan & 0xF)), event.programNumber))

class ChannelAftertouchEvent:
	def read(self, file, event):
		event.amount, = struct.unpack('>B', file.read(1))

	def write(self, file, event):
		if event.before:
			file.write(struct.pack('>B', event.amount))
		else:
			file.write(struct.pack('>BB', (((event.value & 0xF) << 4) | (event.midichan & 0xF)), event.amount))

class PitchBendEvent:
	def read(self, file, event):
		event.LSB_value, event.MSB_value = struct.unpack('>BB', file.read(2))

	def write(self, file, event):
		if event.before: #before signifie est-ce que cet event est du meme type que celui d'avant, si oui alors on le l'inscrit pas, en effet cela fait moins d'octet utilises et de plus on a pas a recalculer la size du trackchunk
			file.write(struct.pack('>BB', event.LSB_value, event.MSB_value))
		else:
			file.write(struct.pack('>BBB', (((event.value & 0xF) << 4) | (event.midichan & 0xF)), event.LSB_value, event.MSB_value))

class MetaEvent:
	def read(self, file, dt, before = False):
		data = midiformat.MetaEvent(dt)
		type, = struct.unpack('>B', file.read(1))

		data.event = midiformat.MetaEventFactory.get(type, before)

		if data.event is None:
			raise UnknownMetaEvent('Meta event ' + str(hex(type)) + ' non connu.')
		temp = MetaEventFactory.get(data.event.type)
		temp.read(file, data.event)
		return data

	def write(self, file, data):
		write_VLV(data.dt, file)
		file.write(struct.pack('>B', data.value))
		event = MetaEventFactory.get(data.event.type)
		event.write(file, data.event)

class SequenceNumber:
	def read(self, file, event):
		event.length = read_VLV(file)
		event.MSB_number, event.LSB_number = struct.unpack('>BB', file.read(2)) 

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(struct.pack('>BB', event.MSB_number, event.LSB_number))		

class TextEvent:
	def read(self, file, event):
		event.length = read_VLV(file)
		event.text = file.read(event.length)

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(event.text)

class CopyrightNotice:
	def read(self, file, event):
		event.length = read_VLV(file)
		event.text = file.read(event.length)

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(event.text)

class TrackName:
	def read(self, file, event):
		event.length = read_VLV(file)
		event.text = file.read(event.length)

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(event.text)

class SequenceName(TrackName): #Cette evenement est le meme qu'un TrackName d'apres la spec
	pass

class InstrumentName:
	def read(self, file, event):
		event.length = read_VLV(file)
		event.text = file.read(event.length)

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(event.text)

class Lyrics:
	def read(self, file, event):
		event.length = read_VLV(file)
		event.text = file.read(event.length)

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(event.text)

class Marker:
	def read(self, file, event):
		event.length = read_VLV(file)
		event.text = file.read(event.length)

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(event.text)

class CuePoint:
	def read(self, file, event):
		event.length = read_VLV(file)
		event.text = file.read(event.length)

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(event.text)

class MidiChannelPrefix:
	def read(self, file, event):
		event.length = read_VLV(file)
		event.chan, = struct.unpack('>B', file.read(1))	

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(struct.pack('>B', event.chan))

class MidiPortPrefix:
	def read(self, file, event):
		event.length = read_VLV(file)
		event.chan, = struct.unpack('>B', file.read(1))	

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(struct.pack('>B', event.chan))

class EndOfTrack:
	def read(self, file, event):
		event.length = read_VLV(file)

	def write(self, file, event):
		file.write(struct.pack('>B', event.type)) #pas de not before car il doit y avoir qu'un seul EoT par trackchunk
		write_VLV(event.length, file)

class SetTempo:
	def read(self, file, event):
		event.length = read_VLV(file)
		tup = struct.unpack('>' + ('B' * event.length), file.read(event.length))
		event.MPQN = ((tup[0] << 16) | ((tup[1] << 8) | tup[2])) #MPQN est code sur 3 octets qu'on a recupere sous forme de tuple un par un, il faut donc effectuer une operation binaire pour retrouver la vraie valeur

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(struct.pack('>' + ('B' * event.length), (event.MPQN >> 16) & 0xFF, (event.MPQN >> 8) & 0xFF, event.MPQN & 0xFF))

class SMPTEOffset:
	def read(self, file, event):
		event.length = read_VLV(file)

		buffer, = struct.unpack('>B', file.read(1))

		event.framep = (buffer & 0x60) >> 5
		event.hour = buffer & 0x1F

		event.min, event.sec, event.fr, event.subfr = struct.unpack('>' + ('B' * (event.length - 1)), file.read(event.length-1))

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(struct.pack('>BBBBB', ((event.framep & 0x03) << 5 | (event.hour & 0x1F)), event.min, event.sec, event.fr, event.subfr))

class TimeSignature:
	def read(self, file, event):
		event.length = read_VLV(file)
		event.numer, event.denom, event.metro, event._32nds = struct.unpack('>' + ('B' * event.length), file.read(event.length))

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(struct.pack('>BBBB', event.numer, event.denom, event.metro, event._32nds))

class KeySignature:
	def read(self, file, event):
		event.length = read_VLV(file)
		event.key, event.scale = struct.unpack('>bB', file.read(2))

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		file.write(struct.pack('>bB', event.key, event.scale))

class SequencerSpecific:
	def read(self, file, event):
		event.length = read_VLV(file)
		for i in xrange(event.length):
			event.data.append(struct.unpack('>B', file.read(1))[0])

	def write(self, file, event):
		if not event.before:
			file.write(struct.pack('>B', event.type))
		write_VLV(event.length, file)
		for i in xrange(event.length):
			file.write(struct.pack('>B', event.data[i]))

class SysExEvent:
	def read(self, file, dt, before = False):
		data = midiformat.SysExEvent(dt)
		type, = struct.unpack('>B', file.read(1))
		length = read_VLV(file)
		datas = list(struct.unpack('>' + ('B' * length), file.read(length)))
		temp = None 
		if type == 0xF0 and datas[-1] == 0xF7:
			data.event = midiformat.NormalSysExEvent(before)
			temp = NormalSysExEvent()
			temp.read(length, datas, data.event)
		elif type == 0xF7:
			data.event = midiformat.AuthSysExEvent(before)
			temp = AuthSysExEvent()
			temp.read(length, datas, data.event)
		else:
			raise Exception('DivSysEx non implemente')
		#DivSysEx Unsupported, manque de documentation

		return data
		

	def write(self, file, data):
		write_VLV(data.dt, file)
		if data.event.value == 0xF0 and data.event.data[-1] == 0xF7:
			temp = NormalSysExEvent()
			temp.write(file, data.event)
		elif data.event.value == 0xF7:
			temp = AuthSysExEvent()
			temp.write(file, data.event)

class NormalSysExEvent:
	def read(self, length, datas, event):
		event.length = length
		event.data = datas

	def write(self, file, event):
		file.write(struct.pack('>B', event.value))
		write_VLV(event.length, file)

		for i in xrange(event.length):
			file.write(struct.pack('>B', event.data[i]))

class AuthSysExEvent:
	def read(self, length, datas, event):
		event.length = length
		event.data = datas

	def write(self, file, event):
		file.write(struct.pack('>B', event.value))
		write_VLV(event.length, file)

		for i in xrange(event.length):
			file.write(struct.pack('>B', event.data[i]))

class TypeEventFactory(midiformat.EventFactory):
	types = {"MidiEvent"  : MidiEvent,
			 "MetaEvent"  : MetaEvent,
			 "SysExEvent" : SysExEvent}

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

class UnknownMetaEvent(Exception):
	pass
