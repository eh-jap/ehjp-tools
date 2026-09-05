import os.path

def load_emojis(path: str, out: set[str]):
  with open(path, 'r') as f:
    while (line := f.readline()) != '':
      if line == '\n':  # blanks
        continue
      if line.startswith('#'):  # comments
        continue

      cp_s = line.split(';', 1)[0].rstrip()  # drop inline comment
      # decode character
      emoji = ''.join(map(lambda s: chr(int(s, 16)), cp_s.split(' ')))

      out.add(emoji)

def load_all_emojis(out: set[str]):
  for src in ('emoji-test.txt', 'emoji-variation-sequences.txt'):
    load_emojis(os.path.join(os.path.dirname(__file__), src), out)
