from random import Random
from datasets import Dataset
from PIL import Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
from PIL import ImageEnhance, ImageOps
from pathlib import Path
from IPython.display import display
import concurrent.futures
import time

random = Random()

font_cache = {}
data_dir = Path(__file__).joinpath('../../data').resolve()
fonts_dir = data_dir.joinpath('fonts/').resolve()

available_backgrounds = list(data_dir.joinpath('backgrounds/').glob('*.jpg'))
available_fonts = list(fonts_dir.glob('*.ttf'))

def get_font(size: float, family: str) -> ImageFont.FreeTypeFont:
	"""
		Returns a PIL font from the fonts/ folder with the given family and size.
		Note that [family] should end with a file extension (e.g. `Test.ttf`).
	"""
	size = int(size)
	# If the font size is less than 1, PIL raises an Exception.
	if size < 1:
		size = 1

	cache_key = '{}-{}'.format(family, size)
	if cache_key in font_cache:
		return font_cache[cache_key]
	f = ImageFont.truetype(
		fonts_dir.joinpath(Path(family)), size
	)
	font_cache[size] = f
	return f

def safe_randint(a: int, b: int):
	""" A version of [random.randint] that does not raise an exception when its endpoints are equal. """
	a = int(a)
	b = int(b)
	start = min(a, b)
	end = max(a, b)
	if start == end:
		return a
	return random.randint(start, end)

def add_background(image: Image.Image):
	""" Adds a random paper-like background to the given [image] """
	random_background_path = random.choice(available_backgrounds)
	background = Image.open(random_background_path).convert('RGBA')
	# Adjust the scale/rotation of the background prior to using it
	if random.random() > 0.5:
		background = background.transpose(Image.Transpose.ROTATE_90)
	scale = random.random() + 0.5
	background_new_width = int(max(background.size[0] * scale, image.size[0]))
	background_new_height = int(max(background.size[1] * scale, image.size[1]))
	# The background needs to be at least as large as the given image:
	background = background.resize((background_new_width, background_new_height))
	# The background can be at most as large as the given image:
	crop_x, crop_y = safe_randint(0, background.size[0] - image.size[0]), safe_randint(0, background.size[1] - image.size[1])
	background = background.crop((crop_x, crop_y, crop_x + image.size[0], crop_y + image.size[1]))
	# Adjust the background's style
	background = ImageEnhance.Brightness(background).enhance(random.random() * 0.6 + 0.8)
	background = ImageEnhance.Color(background).enhance(random.random() + 0.45)
	# Blend them:
	return Image.alpha_composite(background, image)

def hide_content_near_edge_mask(
	source_image: Image.Image, text_min_x: int, text_max_x: int, text_min_y: int, text_max_y: int,
):
	""" Creates a partially transparent image that simulates the white border used by Kraken """
	mask = Image.new('RGBA', (source_image.width, source_image.height), color=(255, 255, 255, 255))
	draw = ImageDraw.ImageDraw(mask)
	points = []
	x = text_min_x + safe_randint(-6, 3)
	points.append((x, safe_randint(-1, text_min_y)))
	
	max_step = max(10, text_max_x // 10)
	# Top half
	while x < text_max_x:
		x += safe_randint(0, max_step)
		points.append((x, safe_randint(0, text_min_y)))
	# Middle
	x = text_max_x + safe_randint(-2, 5)
	points.append((x, safe_randint(text_max_y, source_image.height)))
	# Bottom half
	while x > text_min_x:
		x -= safe_randint(0, max_step)
		points.append((x, safe_randint(text_max_y, source_image.height)))
	draw.polygon(points, fill=(255, 255, 255, 0))
	return mask

def distort(image: Image.Image, mask: Image.Image):
	"""
		Randomly transforms and recolors [image]. The given [mask] is transformed alongside
		the given [image], but filled with solid color rather than transparency.
	"""
	# Transformations
	rotate_deg = (random.random() - 0.5) * 5
	image = image.rotate(rotate_deg, fillcolor=(255, 255, 255, 0))
	mask = mask.rotate(rotate_deg, fillcolor=(255, 255, 255, 255))
	# image = ImageOps.expand(image, safe_randint(0, 5), fill=(255, 255, 255, 0))
	# Recolor
	image = ImageEnhance.Brightness(image).enhance(random.random() * 0.2 + 0.9)
	image = ImageEnhance.Sharpness(image).enhance(random.random() * 0.3 + 0.75)
	return image, mask

def render_text_with_font(text: str, font_family: str, img_size: tuple[int, int] = (512,40)):
	img_width = img_size[0]
	img_height = img_size[1]
	image = Image.new('RGBA', size=(img_width, img_height), color=(255, 255, 255, 0))
	draw = ImageDraw.Draw(image)

	def random_fg_color():
		# Bias towards blue and black (blue and black ink)
		return (safe_randint(0, 24), safe_randint(0, 14), safe_randint(0, 64), 255)

	test_font_size = 10
	test_font = get_font(test_font_size, font_family)
	bbox = draw.textbbox((2, 2), text, font=test_font, font_size=test_font_size)
	font_size = (test_font_size - 1) * min((img_width - 5)/bbox[2], (img_height - 3) / bbox[3])
	text_color = random_fg_color()

	font = get_font(font_size, font_family)
	unstable_baseline = random.random() > 0.5
	text_min_x = safe_randint(0, 10)
	text_min_y = 0
	text_max_x = 0
	text_max_y = 0
	if unstable_baseline:
		vary_font_size = random.random() > 0.6
		vary_color = random.random() > 0.6
		x = text_min_x
		y = 5.0
		color = text_color
		font_size -= 1 # Prevent overflow
		for char in text:
			# Adjust the baseline
			if y < 0 or y > img_height / 10:
				y = 5.0
			y += safe_randint(-img_height, img_height) / 100.0
			y_rounded = int(y) + safe_randint(-1, 1)
			# Adjust the font size
			size = font_size
			if vary_font_size:
				size += safe_randint(-2, 1)
			current_font = get_font(size, font_family)
			# Draw the text
			pos = (x, y_rounded)
			if vary_color:
				color = tuple([
					max(0, min(component + safe_randint(-1, 1), 255)) for component in color
				])
			draw.text(pos, char, font=current_font, font_size=size, fill=color)
			# Update the location for the next letter
			length = draw.textlength(char, font=current_font, font_size=size)
			bbox = draw.textbbox(pos, char, font=current_font, font_size=size)
			if char == ' ': # More space between words
				length += safe_randint(2, 4)
			x += length + safe_randint(-1, 2)
			text_min_x = min(text_min_x, bbox[0])
			text_min_y = min(text_min_y, bbox[1])
			text_max_x = max(text_max_x, bbox[2])
			text_max_y = max(text_max_y, bbox[3])
	else:
		x = text_min_x
		y = safe_randint(2, 8)
		draw.text(
			(x, y), text, font=font, font_size=font_size, fill=text_color
		)
		if random.random() < 0.1:
			draw.text(
				(x + 1, y), text, font=font, font_size=font_size, fill=text_color
			)
		bbox = draw.textbbox((x, y), text, font=font, font_size=font_size)
		text_min_x = bbox[0]
		text_min_y = bbox[1]
		text_max_x = bbox[2]
		text_max_y = bbox[3]

	text_min_x = int(text_min_x)
	text_min_y = int(text_min_y)
	text_max_x = int(text_max_x)
	text_max_y = int(text_max_y)

	# Handle the case where no text was drawn (prevents
	# empty range errors):
	if text_min_x == text_max_x:
		text_max_x += 1
	if text_min_y == text_max_y:
		text_max_y = 24

	# Distort & add other information that should be ignored by the renderer
	for _i in range(0, safe_randint(0, 35)):
		draw.point((safe_randint(0, img_width), safe_randint(0, img_height)), fill=random_fg_color())

	for _i in range(0, safe_randint(0, 4)):
		letter = chr(safe_randint(ord('a'), ord('z')))
		y = random.choice([-safe_randint(20, 30), text_max_y + safe_randint(-7, 10)])
		draw.text(
			(safe_randint(0, text_max_x), y),
			letter,
			fill=random_fg_color(),
			font=font,
		)
	mask = hide_content_near_edge_mask(image, text_min_x, text_max_x, text_min_y, text_max_y)
	image, mask = distort(image, mask)
	crop_rectangle = (0, 0, min(text_max_x + 10, image.size[0]), min(text_max_y + 10, image.size[1]))
	image = image.crop(crop_rectangle)
	mask = mask.crop(crop_rectangle)
	return Image.alpha_composite(add_background(image), mask)


def render_text_with_random_font(text: str, img_size: tuple[int, int] = (512,40)):
	font = random.choice(available_fonts)
	font_name = font.name
	return render_text_with_font(text, font_name, img_size)

def add_image_from_text(text: str):
	img_width = safe_randint(8, 13) * len(text)
	img_height = safe_randint(41, 51)
	image = render_text_with_random_font(text, (img_width, img_height))

	return {
		'text': text,
		'image': image.convert('RGB'),
	}

def process_line(text: str)->list:
	result = []
	words = text.split(' ')
	num_words = len(words)
	# Build shorter examples from longer phrases
	if num_words > 7 and random.random() > 0.65:
		for j in range(0, num_words, 5):
			result.append(add_image_from_text(' '.join(words[j:min(j + 5, num_words)])))
	else:
		result.append(add_image_from_text(text))

	return result


def make_font_dataset():
	data_list = []

	print('Total available font count:', len(available_fonts))

	with concurrent.futures.ProcessPoolExecutor() as executor:
		lines = []
		with open(data_dir.joinpath('./french_text.txt')) as f:
			for text in f.readlines():
				# Clean up the text and remove characters that show up unnecessarily in
				# the output.
				text = text.strip()\
					.replace('—', '')\
					.replace('«', '')\
					.replace('»', '')\
					.replace('_', '')\
					.replace('[', '')\
					.replace(']', '')\
					.replace('�', '')\
					.replace('’', "'")\
					.replace('°', 'o')\
					.replace('  ', ' ')
				if text == '':
					continue
				
				lower_words = text.lower().split(' ')
				# Filter out most of the (English) license text
				if ('you' in lower_words) or ('the' in lower_words) or ('new' in lower_words) or ('by' in lower_words) or ('and' in lower_words):
					continue

				lines.append(text)
		
		line_count = len(lines)
		lines_processed = 0
		start_time = time.monotonic()
		for processed_data in executor.map(process_line, lines):
			lines_processed += 1
			for image_data in processed_data:
				data_list.append(image_data)
			
				image_count = len(data_list)
				# Output status
				if image_count % 2000 == 0:
					image_data = data_list[-1]
					print('image', image_count, 'has been rendered')
					print('Example {}: {}'.format(image_count, image_data['text']))
					display(image_data['image'])

					now = time.monotonic()
					if now - start_time > 0:
						samples_per_second = lines_processed / (now - start_time)
						print('Lines/s: {:.2f}'.format(samples_per_second))
						print('Estimated time remaining: {:.0f}s'.format((line_count - lines_processed) / samples_per_second))
					print()
		
		print('All tasks complete!')

	return Dataset.from_list(data_list)
