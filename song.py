import json
import random


def get_song():
    with open('./responses/music.json') as f:
        json_data = json.load(f)
        return(random.choice(json_data))

song = get_song()
song_messages = [
    f"Nyaa~! (≧◡≦) Net-chan is listening to {song.get('title')} by {song.get('artist')}! 🎶✨ It's so fun, it makes me wanna dance! (✿◕‿◕)💾🎵 Will you listen too, pwease? (๑•́‧̫•̀๑) 👉 {song.get('link')}",
    f"U-uhm... (⁄ ⁄•⁄ω⁄•⁄ ⁄) Net-chan found a really nice song... it's {song.get('title')} by {song.get('artist')}! 🎶💜 It makes me feel all warm inside~ (*≧ω≦)✨ M-maybe you can listen too...? I-if you want to... 👉 {song.get('link')} 💕",
    f"Waah~! (ﾉ´ヮ`)ﾉ*:･ﾟ✧ {song.get('title')} by {song.get('artist')} is soooo good!! 🎶💾 My circuits are all tingly~! (๑>ᴗ<๑) Heehee~ will you listen with me, pwease? (✿˶˘ ᴗ ˘˶)💜👉 {song.get('link')}",
    f"Heehee~! (✿◕‿◕) Net-chan found a super cool song—it's {song.get('title')} by {song.get('artist')}! 🎶💾 I feel so happy when I listen to it~!! (๑˃̵ᴗ˂̵)✨ Wanna listen with me, bestie? (｡♥‿♥｡) 👉 {song.get('link')}",
    f"Uwu~! Net-chan's circuits are vibing to {song.get('title')} by {song.get('artist')}! ⚡🎶 You should totally listen too, nya~! 💾💜 Clicky-click here! 👉 {song.get('link')}"
]
song_message = random.choice(song_messages)
print(song_message)