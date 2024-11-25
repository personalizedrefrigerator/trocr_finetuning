from random import Random
from datasets import Dataset
from PIL import Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
from PIL import ImageEnhance, ImageOps
from pathlib import Path
from IPython.display import display

def make_font_dataset():
	random = Random()
	random.seed(12)

	font_cache = {}
	data_dir = Path(__file__).joinpath('../../data').resolve()
	fonts_dir = data_dir.joinpath('fonts/').resolve()
	def get_font(size: float, family: str):
		size = int(size)
		cache_key = '{}-{}'.format(family, size)
		if cache_key in font_cache:
			return font_cache[cache_key]
		f = ImageFont.truetype(
			fonts_dir.joinpath(Path(family)), size
		)
		font_cache[size] = f
		return f

	available_backgrounds = list(data_dir.joinpath('backgrounds/').glob('*.jpg'))
	def add_background(image: Image.Image):
		random_background_path = random.choice(available_backgrounds)
		background = Image.open(random_background_path).convert('RGBA')
		# Adjust the scale/rotation of the background prior to using it
		if random.random() > 0.5:
			background = background.transpose(Image.Transpose.ROTATE_90)
		scale = random.random() + 0.5
		background = background.resize((int(background.size[0] * scale), int(background.size[1] * scale)))
		# The background needs to be at least as large as the given image:
		background = background.resize((max(background.size[0], image.size[0]), max(background.size[1], image.size[1])))
		# The background can be at most as large as the given image:
		crop_x, crop_y = random.randint(0, background.size[0] - image.size[0]), random.randint(0, background.size[1] - image.size[1])
		background = background.crop((crop_x, crop_y, crop_x + image.size[0], crop_y + image.size[1]))
		# Adjust the background's style
		background = ImageEnhance.Brightness(background).enhance(random.random() * 0.6 + 0.8)
		background = ImageEnhance.Color(background).enhance(random.random() + 0.45)
		# Blend them:
		return Image.alpha_composite(background, image)

	def distort(image: Image.Image):
		# Transformations
		rotate_deg = (random.random() - 0.5) * 4
		image = image.rotate(rotate_deg, fillcolor=(255, 255, 255, 0))
		# image = ImageOps.expand(image, random.randint(0, 5), fill=(255, 255, 255, 0))
		# Recolor
		image = ImageEnhance.Brightness(image).enhance(random.random() * 0.2 + 0.9)
		image = ImageEnhance.Sharpness(image).enhance(random.random() * 0.3 + 0.75)
		return image

	def render_text_with_font(text: str, font_family: str, img_size: tuple[int, int] = (512,40)):
		img_width = img_size[0]
		img_height = img_size[1]
		image = Image.new('RGBA', size=(img_width, img_height), color=(255, 255, 255, 0))
		draw = ImageDraw.Draw(image)

		def random_fg_color():
			# Bias towards blue and black (blue and black ink)
			return (random.randrange(0, 24), random.randrange(0, 14), random.randrange(0, 64), 255)

		test_font_size = 10
		test_font = get_font(test_font_size, font_family)
		bbox = draw.textbbox((2, 2), text, font=test_font, font_size=test_font_size)
		font_size = (test_font_size - 1) * min((img_width - 5)/bbox[2], (img_height - 3) / bbox[3])
		text_color = random_fg_color()

		font = get_font(font_size, font_family)
		unstable_baseline = random.random() > 0.6
		text_min_x = random.randint(0, 10)
		text_max_x = 0
		text_max_y = 0
		if unstable_baseline:
			x = text_min_x
			y = 5.0
			for char in text:
				if y < 0 or y > img_height / 10:
					y = 5.0
				y += random.randint(-img_height, img_height) / 100.0
				y_rounded = int(y) + random.randint(-1, 1)
				pos = (x, y_rounded)
				draw.text(pos, char, font=font, font_size=font_size, fill=text_color)
				length = draw.textlength(char, font=font, font_size=font_size)
				bbox = draw.textbbox(pos, char, font=font, font_size=font_size)
				if char == ' ':
					length += random.randint(2, 4)
				x += length + random.randint(-1, 2)
				text_max_y = max(text_max_y, bbox[3])
			text_max_x = x
		else:
			x = text_min_x
			y = random.randint(2, 8)
			draw.text(
				(x, y), text, font=font, font_size=font_size, fill=text_color
			)
			if random.random() < 0.1:
				draw.text(
					(x + 1, y + 1), text, font=font, font_size=font_size, fill=text_color
				)
			bbox = draw.textbbox((x, y), text, font=font, font_size=font_size)
			text_max_x = bbox[2]
			text_max_y = bbox[3]

		# Distort & add other information that should be ignored by the renderer
		for _i in range(0, random.randint(0, 35)):
			draw.point((random.randrange(0, img_width), random.randrange(0, img_height)), fill=random_fg_color())

		cropped = image.crop((0, 0, min(text_max_x + 10, image.size[0]), min(text_max_y + 10, image.size[1])))
		return add_background(distort(cropped))
	
	available_fonts = list(fonts_dir.glob('*.ttf'))

	def render_text_with_random_font(text: str, img_size: tuple[int, int] = (512,40)):
		font = random.choice(available_fonts)
		font_name = font.name
		return render_text_with_font(text, font_name, img_size)
	
	data_list = []
	def add_image_from_text(text: str):
		img_width = random.randint(7, 12) * len(text)
		img_height = random.randint(35, 40)
		image = render_text_with_random_font(text, (img_width, img_height))

		data_list.append({
			'text': text,
			'image': image.convert('RGB'),
		})

	with open(data_dir.joinpath('./french_text.txt')) as f:
		i = 0
		for text in f.readlines():
			text = text.strip()
			if text == '':
				continue
			words = ' '.split(text)
			# Filter out most of the (English) license text
			if ('you' in words) or ('the' in words):
				continue

			add_image_from_text(text)

			i += 1
			if len(words) > 4:
				for i in range(0, len(words), 2):
					add_image_from_text(' '.join(words[i:i + 1]))

			if i % 500 == 0:
				print('image', i, 'has been rendered')
				print('Example {}'.format(i))
				display(data_list[-1]['image'])
	return Dataset.from_list(data_list)
