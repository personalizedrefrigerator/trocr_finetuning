from random import Random
from datasets import Dataset
from PIL import Image
from PIL import ImageEnhance
from pathlib import Path
from IPython.display import display
import re

def make_handwriting_dataset():
	random = Random()
	random.seed(15)
	data_dir = Path(__file__).joinpath('../../data').resolve()
	handwriting_dir = data_dir / 'handwriting'

	def distort(image: Image.Image):
		"""
			Randomly transforms and recolors [image].
		"""
		# Transformations
		rotate_deg = (random.random() - 0.5) * 5
		image = image.rotate(rotate_deg, fillcolor=(255, 255, 255, 255))
		# image = ImageOps.expand(image, random.randint(0, 5), fill=(255, 255, 255, 0))
		# Recolor
		image = ImageEnhance.Brightness(image).enhance(random.random() * 0.5 + 0.75)
		image = ImageEnhance.Sharpness(image).enhance(random.random() * 0.5 + 0.75)
		return image

	data_list = []
	text_exp_with_counter = re.compile(r'^(.+)__\d{1,3}$')
	for path in handwriting_dir.glob('*.png'):
		filename = path.name.removesuffix('.png')
		match = text_exp_with_counter.match(filename)
		if match:
			text = match.groups()[0]
		else:
			text = filename
		image = Image.open(path)
		for i in range(0, 2):
			distorted = distort(image)
			data_list.append({
				"image": distorted.convert('RGB'),
				"text": text,
			})

	return Dataset.from_list(data_list)
