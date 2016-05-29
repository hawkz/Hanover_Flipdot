from flask import Flask
import flip
import display_refactored

app = Flask(__name__)
flippy = flip.flippy


@app.route('/topic/<text>')
def topic(text):
    f = flip.place(flippy, flip.tiny(text), (0, 0))
    f = flip.place(f, flip.clock(), (-1, 0), True)
    display_refactored.main(f)
    return text


@app.route('/say/<text>')
def say(text):
    f = flip.place(flippy, flip.huge(text), (0, 6))
    f = flip.place(f, flip.clock(), (-1, 0), True)
    display_refactored.main(f)
    return text

if __name__ == '__main__':
    app.run('::')
