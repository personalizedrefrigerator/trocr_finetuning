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
]

def download_fonts():
	for url in download_urls:
		url.download()

if __name__ == '__main__':
	download_fonts()