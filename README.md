# LickCorea

LickCorea is a domain-specific programming language designed for generating jazz licks based on harmonic structures. It parses function-based syntax inspired by musical scales and produces MIDI files as output. For a detailed explanation of the programming language and the possibilities, see the 'documentation.pdf' file in the root directory of this source tree.
## Features
- Write licks using a variaty of different functions
- Use a `.rb` harmony file to define the harmony of your lick.
- Generate MIDI files from `.lc` melody files.
- Built with Python and utilizes multiple essential libraries.

## Installation
```sh
# Clone the repository
git clone git@github.com:oliverkoell/lick_corea.git
```
## Usage - writeLick
To generate a lick from a `.rb` and `.lc` files:
```sh
python lickcorea.py writeLick
Enter Harmony-File name: example.rb
Enter Melody-File name: example.lc
Enter MIDI-File name: example.mid
```
This will create a corresponding MIDI file with the generated lick.

## Usage - readLick
To read an existing midi lick into the shredMode database:
```sh
python lickcorea.py readLick
Enter Harmony-File name: example.rb
Enter MIDI-File name: example.mid
Enter MIDI-File tag: example_tag
```
This will read your midi lick and add it to the lick database according to the style tag. New tags can be created and old ones can be extended indefinitely.

## Dependencies
LickCorea requires the following Python modules:
- `re`
- `pretty_midi`
- `random`
- `itertools`
- `json`
- `os`
- `sys`

## Example
Two simple examples can be found in the example folder. The first creates the famous Blue Bossa theme and improvises using the shred mode function. The second example creates the "Back to Earth" lick by Dave Burbeck and improvises using the random function.

## Contribution
Feel free to contribute by submitting pull requests or reporting issues. Contributions should follow standard open-source best practices.

## License
This project is licensed under the MIT License.

## Author
Created by Michael Žutić, Oliver Köll. Reach out via [o.koell36@gmail.com] or GitHub issues.

Enjoy jamming with LickCorea! 🎷🎶

