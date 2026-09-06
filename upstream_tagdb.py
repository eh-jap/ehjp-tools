"""
drops chinese texts from upstream data
perserving emojis/icons, artist names, links and images

to update our database from upstream,
run under upstream's "Database" repo
then merge changes manually into ours
"""

from glob import glob
from ruamel.yaml import YAML
from traceback import print_exc
from dataclasses import dataclass
from typing import Any, Optional
from enum import Enum
import enum
import dataclasses
from re import fullmatch
from os.path import basename

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

  assert fp.readline() == '\n', 'expecting a blank after head'

  return yaml.load(''.join(yaml_lines))

class IconLocation(Enum):
  LEADING = enum.auto()
  TRAILING = enum.auto()

class IconKind(Enum):
  EMOJI = enum.auto()
  IMAGE = enum.auto()

@dataclass
class TagIcon:
  inner: str
  type_: IconKind
  placement: IconLocation

@dataclass
class GalleryTag:
  inner: str
  icon: Optional[TagIcon] = None
  links: list[str] = dataclasses.field(default_factory=list)
  # example artworks, artist profile photo
  images: list[str] = dataclasses.field(default_factory=list)

@dataclass
class LoadedFile:
  hdr: Any = None
  body: list[GalleryTag] = dataclasses.field(default_factory=list)

def is_jp(s: str) -> bool:
  """based on the upstream's policy, chinese translated tags are
     not mixed with japanese kanas."""

  for c in s:
    cp = ord(c)

    # https://ja.wikipedia.org/wiki/平仮名_(Unicodeのブロック)#収録文字
    if cp >= 0x3041 and cp <= 0x3096: return True

    # https://ja.wikipedia.org/wiki/片仮名_(Unicodeのブロック)#収録文字
    if cp >= 0x30A1 and cp <= 0x30FA: return True

  # whatever this is,
  # we can't unfortunately ensure it's safe for importing automatically.
  return False

def contains_chinese(s) -> bool:
  """currently only performing trivial check. not a full check."""

  for c in s:
    cp = ord(c)

    # https://ja.wikipedia.org/wiki/CJK統合漢字_(Unicodeのブロック)
    if cp >= 0x4E00 and cp <= 0x9FFF: return True

  return False

def handle_line(line: str, out: LoadedFile, allow_jp: bool):
  if not line.startswith('|'):
    # effectively skips "template"s
    return

  m = fullmatch(r'\| ([^|]*) \| (.*) \| (.*) \| (.*) \|', line.removesuffix('\n'))
  assert m is not None, f'could not parse line: {line!r}'

  raw = m.group(1)
  if raw == '':
    # drop tag group, which is written in chinese
    return

  tag_obj = GalleryTag(raw)

  out.body.append(tag_obj)

def parse_body(fp, out: LoadedFile, allow_jp: bool):
  # skip craps
  fp.readline()  # col names in chinese
  assert fp.readline() == '| -------- | ---- | ---- | -------- |\n', 'expecting table separator'

  while (line := fp.readline()) != '':
    handle_line(line, out, allow_jp)

# upstream allow pure japanese labels to exist in only these
ALLOW_JP = ('artist.md', 'cosplayer.md', 'group.md')

def allow_jp(path: str):
  if basename(path) in ALLOW_JP:
    return True
  return False

def parse(path: str, yaml: YAML) -> LoadedFile:
  res = LoadedFile()
  with open(path, 'r') as fp:
    res.hdr = parse_header(fp, yaml)
    parse_body(fp, res, allow_jp(path))
  return res

def write_hdr(fp, yaml: YAML, file: LoadedFile):
  fp.write('---\n')
  yaml.dump(file.hdr, fp)
  fp.write('---\n')
  fp.write('\n')

def format_icon(icon: TagIcon) -> str:
  match icon.type_:
    case IconKind.EMOJI:
      return icon.inner
    case IconKind.IMAGE:
      return f'![icon]({icon.inner})'
    case _:
      raise AssertionError()

def format_pretty(entry: GalleryTag) -> str:
  if entry.icon is None:
    return entry.inner  # start with untranslated tag

  match entry.icon.placement:
    case IconLocation.LEADING:
      return f'{format_icon(entry.icon)}{entry.inner}'
    case IconLocation.TRAILING:
      return f'{entry.inner}{format_icon(entry.icon)}'
    case _:
      raise AssertionError()

def format_links(entry: GalleryTag) -> str:
  # upstream links has alt texts
  # but we cant use them bcs they're in chinese
  # so just paste the link destinations directly
  return '<br>'.join(entry.links)

def format_img(url: str) -> str:
  return f'![picture]({url})'

def init_note(entry: GalleryTag) -> str:
  # start with empty note.
  return '<br>'.join(map(format_img, entry.images))

def write_body(fp, file: LoadedFile):
  fp.write('| タグ | 表示名 | 備考 | 関連リンク |\n')
  fp.write('| ---- | ------ | ---- | ---------- |\n')

  for entry in file.body:
    fp.write(f'| {entry.inner} |')  # raw tag
    fp.write(f' {format_pretty(entry)} |')
    fp.write(f' {init_note(entry)} |')
    fp.write(f' {format_links(entry)} |\n')

def dump(path: str, yaml: YAML, file: LoadedFile):
  with open(path, 'w') as fp:
    write_hdr(fp, yaml, file)
    write_body(fp, file)

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
