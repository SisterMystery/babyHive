import midi, os, sys
#requires python-midi from https://github.com/vishnubob/python-midi.git

def gather_midis(directory):
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".mid"):
                yield os.path.join(root, f)

def split_tracks(m_file):
    if m_file:
        return [midi.Pattern([remove_events(m_file[0]), flatten_melody(remove_events(m_file[i]))], m_file.resolution, m_file.tick_relative)
                for i in range(1,len(m_file)) if any([isinstance(e, midi.NoteEvent) for e in m_file[i]]) and
                not any([(isinstance(e, midi.NoteEvent) and e.channel == 9)  for e in m_file[i]])]
    return []



def try_readmidi(m_file):
    try:
        return midi.read_midifile(m_file)
    except Exception as e:
        print type(e)
        print e.args
        print e
        return None

def note_on_equals(note, other_note):
    return (isinstance(note, midi.NoteOnEvent) and
            isinstance(other_note, midi.NoteOnEvent) and
            note.get_pitch() == other_note.get_pitch() and
            other_note.get_velocity() != 0)

def note_off_equals(note, other_note):
    return (isinstance(note, midi.NoteOnEvent) and
            isinstance(other_note, midi.NoteEvent) and
            note.pitch == other_note.pitch and 
            ((isinstance(other_note, midi.NoteOnEvent) and other_note.velocity == 0) or 
                isinstance(other_note, midi.NoteOffEvent)))

def is_stacked(note, stack_ranges):
    if not isinstance(note, midi.NoteEvent): return False
    for r in stack_ranges:
        if note.tick == r[0].tick:
            return r[0].velocity != 0 and not note_on_equals(r[0], note)
        if note.tick > r[0].tick and note.tick < r[1].tick:
            return True
        if note.tick == r[1].tick and note != r[1]:
            return note.velocity == 0
    return False

def flatten_melody(track):
    track.tick_relative = True
    track.make_ticks_abs()
    tick_ranges = []
    on_note = None
    i = 0
    for event in track:
        if isinstance(event, midi.NoteOnEvent) and not on_note:
            on_note = event
        elif on_note and  note_off_equals(on_note, event):
            tick_ranges.append((on_note, event))
            on_note = None
    flat_track = midi.Track([ev for ev in track if not is_stacked(ev, tick_ranges)], tick_relative=False) 
    flat_track.make_ticks_rel()
    
    return flat_track



def remove_events(track, event_list=[midi.ControlChangeEvent, midi.ProgramChangeEvent, midi.MetaEventWithText]):
    return midi.Track([e for e in track if all([not isinstance(e, e_type) for e_type in event_list])],track.tick_relative)

if __name__ == "__main__":
    midi_dir = sys.argv[1]
    out_dir = sys.argv[2]

    midis = {p:split_tracks(try_readmidi(p)) for p in gather_midis(midi_dir)}
    for name, pat_list in midis.items():
        for idx, mid in enumerate(pat_list):
            midi.write_midifile(os.path.join(out_dir, os.path.basename(name).replace(".mid",'')+"_t"+str(idx)+".mid"), mid)

