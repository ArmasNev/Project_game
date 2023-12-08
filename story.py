import textwrap

story = '''Kauan odotettu kesä on saapunut!
Vuoden ajan olette säästäneet rahaa voidaksenne matkustaa.
Ette voineet jättää rakasta lemmikkiänne yksin, joten otitte sen mukaanne.
Lentokentällä koneeseen noustessanne teidän täytyi jättää se ruumaan.
Mutta kun laskeuduitte, kauhuksenne huomasitte, että lemmikkienne ei ollutkaan samassa lennossa kanssanne.
Se oli erehdyksen vuoksi lähetetty johonkin toiseen samanaikaiseen lentoosi.
Nyt teidän täytyy löytää se mahdollisimman nopeasti, vaikka se vaatisikin kaikkien lomansäästöjen käyttämistä.'''

wrapper = textwrap.TextWrapper(width=80, break_long_words=False, replace_whitespace=False)
word_list = wrapper.wrap(text=story)


def getStory():
    return word_list