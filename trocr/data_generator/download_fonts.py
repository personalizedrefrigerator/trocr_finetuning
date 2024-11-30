from pathlib import Path
import requests

fonts_out_dir = Path(__file__).joinpath('../../data/fonts/').resolve()
class FontSpec:
	def __init__(self, name: str, font_dir: str, font_filename: str = '', type: str = 'ofl'):
		base_url = 'https://github.com/google/fonts/raw/refs/heads/main/{}/'.format(type)
		if not font_dir.endswith('/'):
			font_dir += '/'
		base_url += font_dir

		if not font_filename:
			font_filename = name + '-Regular.ttf'

		license_path = 'OFL.txt'
		if type == 'apache':
			license_path = 'LICENSE.txt'

		self.font_url = base_url + font_filename
		self.liscense_url = base_url + license_path
		font_ext = Path(font_filename).suffix
		self.output_ttf_path = fonts_out_dir.joinpath(name + font_ext)
		self.output_liscense_path = self.output_ttf_path.with_name(name + '.liscense.txt')
	def download(self):
		def save_from_url(url: str, target_path: Path):
			if target_path.exists():
				return
			print('Downloading', url)
			r = requests.get(url, stream=True)
			if not r.ok:
				raise Exception('Download failed at url {}'.format(url))
			with open(target_path, 'wb') as f:
				for chunk in r.iter_content(chunk_size=4096):
					f.write(chunk)
		
		save_from_url(self.font_url, self.output_ttf_path)
		save_from_url(self.liscense_url, self.output_liscense_path)

download_urls = [
	FontSpec(
		name='Caveat',
		font_dir='caveat/',
		font_filename='Caveat[wght].ttf',
	),
	FontSpec(
		name='ShadowsIntoLight',
		font_dir='shadowsintolight/',
		font_filename='ShadowsIntoLight.ttf',
	),
	FontSpec(
		name='PermanentMarker',
		font_dir='permanentmarker',
		type='apache',
	),
	FontSpec(
		name='NothingYouCouldDo',
		font_dir='nothingyoucoulddo',
		font_filename='NothingYouCouldDo.ttf',
	),
	FontSpec(
		name='JustAnotherHand',
		font_dir='justanotherhand',
		type='apache',
	),
	FontSpec(
		name='Stalemate',
		font_dir='stalemate',
	),
	FontSpec(
		name='Festive',
		font_dir='festive',
	),
	FontSpec(
		name='Chilanka',
		font_dir='chilanka',
	),
	FontSpec(
		name='Kavoon',
		font_dir='kavoon',
	),
	FontSpec(
		name='MrBedfort',
		font_dir='mrbedfort',
	),
	FontSpec(
		name='ButterflyKids',
		font_dir='butterflykids',
	),
	FontSpec(
		name='Devonshire',
		font_dir='devonshire',
	),
	FontSpec(
		name='Splash',
		font_dir='splash',
	),
	FontSpec(
		name='IslandMoments',
		font_dir='islandmoments',
	),
	FontSpec(
		name='MySoul',
		font_dir='mysoul',
	),
	FontSpec(
		name='Sacramento',
		font_dir='sacramento',
	),
	FontSpec(
		name='SassyFrass',
		font_dir='sassyfrass',
	),
	FontSpec(
		name='Zeyada',
		font_dir='zeyada',
		font_filename='Zeyada.ttf',
	),
	FontSpec(
		name='WaitingfortheSunrise',
		font_dir='waitingforthesunrise',
		font_filename='WaitingfortheSunrise.ttf',
	),
	FontSpec(
		name='ZenLoop',
		font_dir='zenloop',
	),
	FontSpec(
		name='Ruthie',
		font_dir='ruthie',
	),
	FontSpec(
		name='MrsSaintDelafield',
		font_dir='mrssaintdelafield',
	),
	FontSpec(
		name='SueEllenFrancisco',
		font_dir='sueellenfrancisco',
	),
	FontSpec(
		name='MrDeHaviland',
		font_dir='mrdehaviland',
	),
	FontSpec(
		name='MouseMemoirs',
		font_dir='mousememoirs',
	),
	FontSpec(
		name='GrandHotel',
		font_dir='grandhotel',
	),
	FontSpec(
		name='Mansalva',
		font_dir='mansalva',
	),
	FontSpec(
		name='HomemadeApple',
		font_dir='homemadeapple',
		type='apache',
	),
	FontSpec(
		name='BadScript',
		font_dir='badscript',
	),
	FontSpec(
		name='GochiHand',
		font_dir='gochihand',
	),
	FontSpec(
		name='ShortStack',
		font_dir='shortstack',
	),
	FontSpec(
		name='Hurricane',
		font_dir='hurricane',
	),
	FontSpec(
		name='Petemoss',
		font_dir='petemoss',
	),
	FontSpec(
		name='Hubballi',
		font_dir='hubballi',
	),
	FontSpec(
		name='Corinthia',
		font_dir='corinthia',
	),
	FontSpec(
		name='WindSong',
		font_dir='windsong',
	),
	FontSpec(
		name='Caramel',
		font_dir='caramel',
	),
	FontSpec(
		name='Qwigley',
		font_dir='qwigley',
	),
	FontSpec(
		name='Inspiration',
		font_dir='inspiration',
	),
	FontSpec(
		name='Bilbo',
		font_dir='bilbo',
	),
	FontSpec(
		name='JustMeAgainDownHere',
		font_dir='justmeagaindownhere',
		font_filename='JustMeAgainDownHere.ttf',
	),
	FontSpec(
		name='PrincessSofia',
		font_dir='princesssofia',
	),
	FontSpec(
		name='MsMadi',
		font_dir='msmadi',
	),
	FontSpec(
		name='Miniver',
		font_dir='miniver',
	),
	FontSpec(
		name='Mynerve',
		font_dir='mynerve',
	),
	FontSpec(
		name='Schoolbell',
		font_dir='schoolbell',
		type='apache'
	),
	FontSpec(
		name='BethEllen',
		font_dir='bethellen',
	),
	FontSpec(
		name='PlaywriteBR',
		font_dir='playwritebr',
		font_filename='PlaywriteBR[wght].ttf',
	),
	FontSpec(
		name='PlaywriteFRModerne',
		font_dir='playwritefrmoderne',
		font_filename='PlaywriteFRModerne[wght].ttf',
	),
	FontSpec(
		name='PlaywriteFRModerne',
		font_dir='playwritefrmoderne',
		font_filename='PlaywriteFRModerne[wght].ttf',
	),
	FontSpec(
		name='PlaywriteFRTrad',
		font_dir='playwritefrtrad',
		font_filename='PlaywriteFRTrad[wght].ttf',
	),
	FontSpec(
		name='IndieFlower',
		font_dir='indieflower',
	),
	FontSpec(
		name='Parisienne',
		font_dir='parisienne',
	),
	FontSpec(
		name='Montez',
		font_dir='montez',
		type='apache',
	),
	FontSpec(
		name='ComforterBrush',
		font_dir='comforterbrush',
	),
	FontSpec(
		name='Licorice',
		font_dir='licorice',
	),
	FontSpec(
		name='MoonDance',
		font_dir='moondance',
	),
	FontSpec(
		name='Allison',
		font_dir='allison',
	),
	FontSpec(
		name='CoveredByYourGrace',
		font_dir='coveredbyyourgrace',
		font_filename='CoveredByYourGrace.ttf',
	),
	FontSpec(
		name='Combo',
		font_dir='combo',
	),
	FontSpec(
		name='SeaweedScript',
		font_dir='seaweedscript',
	),
	FontSpec(
		name='Pangolin',
		font_dir='pangolin',
	),
	FontSpec(
		name='Chewy',
		font_dir='chewy',
		type='apache',
	),
	FontSpec(
		name='ReenieBeanie',
		font_dir='reeniebeanie',
		font_filename='ReenieBeanie.ttf',
	),
	FontSpec(
		name='CedarvilleCursive',
		font_dir='cedarvillecursive',
		font_filename='Cedarville-Cursive.ttf',
	),
]

def download_fonts():
	for url in download_urls:
		url.download()

if __name__ == '__main__':
	download_fonts()