import sys
import json

def get_json(file_path,
    filter_func = lambda msg_dict: msg_dict['sender_name'] == 'Torrent Glenn' and msg_dict['type'] == 'Generic'):
    with open(file_path) as json_txt:
        json_dicts = [d for d in json.load(json_txt)['messages'] if filter_func(d)]
    return json_dicts

def get_files(paths):
	paths += []
	text = ""
	for path in paths:
	    text += "\n".join([d['content'] for d in get_json(path) if 'content' in d][::-1]) 
	return text   

out_file = sys.argv[1]
in_files = sys.argv[2:]

with open(out_file, "w") as out:
	out.write(get_files(in_files))