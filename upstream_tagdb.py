"""
drops chinese texts from upstream data
perserving emojis/icons and artist links
"""

from glob import glob
from ruamel.yaml import YAML
from traceback import print_exc
from dataclasses import dataclass
from typing import Any

def parse_header(fp, yaml: YAML):
  # first line in file is an opening marker
  assert fp.readline() == '---\n', 'expecting three dashes'

  yaml_lines = []
  while True:
    line = fp.readline()

    if line == '':  # early eof
      raise AssertionError('cant find closing marker')
    if line == '---\n': break

    yaml_lines.append(line)

  return yaml.load(''.join(yaml_lines))

@dataclass
class LoadedFile:
  hdr: Any = None

def parse(path: str, yaml: YAML) -> LoadedFile:
  res = LoadedFile()
  with open(path, 'r') as fp:
    res.hdr = parse_header(fp, yaml)
  return res

def dump(path: str, yaml: YAML, file: LoadedFile):
  with open(path, 'w') as fp:
    fp.write('---\n')
    yaml.dump(file.hdr, fp)
    fp.write('---\n')

def patch_hdr(dat: Any):
  # required fields to pass db.html.json emission
  # always present
  # are these for the web Editor? (we dont use it yet)
  # null them out for now
  dat['name'] = ''
  dat['description'] = ''

  # unwanted (contains chinese texts)
  # copyright is not relevant bcs we drop everything anyway
  for key in ('copyright', 'rules', 'example'):
    if key in dat: del dat[key]

def clean(path: str):
  yaml = YAML()
  yaml.indent(offset=2)

  file = parse(path, yaml)
  patch_hdr(file.hdr)
  dump(path, yaml, file)

def main():
  for md_file in glob('database/*.md'):
    print(f'cleaning file {md_file!r}')
    try:
      clean(md_file)
    except AssertionError:
      print_exc()
      print(f'error processing file {md_file!r}')

main()
