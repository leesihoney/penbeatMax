<Pen Beat Max> by. Siheon Lee for Fall 2017 CMU 15-112 Fundamentals of Programming and Computer Science

1. Overview

“Pen Beat Max” is a python rhythm game supported by pygame, pyaudio, and aubio. Players would directly apply the rule of pen beat to play a rhythm game. This game uses beat detection to automatically extract notes to play for any .wav file songs, and utilizes pitch and volume detection to press the key. 

2. Directions

- As the game starts, user should conduct tests to record each beats. 
- Click “test” button, and press keyboard button “s” to start record one test for beat, and player should record the beat in 1.5 seconds. 
- Player should record “Bass”, “Hi Hat”, and “Snare” for 7 times of tests(total of 21 times). 
- After testing, player get to choose .wav files in “/sound” directory. Use up and arrow button to choose which song to play, and press “enter” to start the game with selected song.
- The notes drop, you should play beat in real time to score for each dropping beat
- When the song ends, it will show how much you scored along with your performances for each beat (perfect, great, good, miss, bad). Click Test if you want to redo the testing for precision, or click “Menu” to play another song. 
- The game can also be played by pressing keyboard buttons of “z” for Hi Hat, “x” for Snare, and “c” for Bass, if testing has not been conducted.

3. Key Points:

- Aubio Module allows to pull beats from any .wav file music. The beats drop by searching what time the beat should drop to reach at the bottom.
- If you finished all 7 tests for beat but reset to test from the beginning, it is because the tested values are not significant to make a range of pitch and volume. Conduct the testing again to make a stable range of pitch and volume
- Aubio Module also allows to detect pitch and volume in realtime. This realtime sound analysis(pitch and volume returns which buttons are going to be pressed. The algorithm for returning which keys to be pressed 
	1. Whether the pitch fits in each range of beats recorded by former tests
	2. Whether the volume fits in each range of beats recorded by former tests
 and bass beat often has low pitch, and snare beat often has high volume because we put much power in hitting snare than any other beats. In other words, if your beat has low pitch, it is likely to be interpreted as bass, and if your beat has high volume,
 It is likely to be interpreted as snare (but not always! Just saying this is the prioritized settings for sound analysis algorithm.


4. Download modules

Pygame- https://qwewy.gitbooks.io/pygame-module-manual/content/installation.html
PyAudio-https://abhgog.gitbooks.io/pyaudio-manual/content/installation.html
Aubio - https://aubio.org/installation

