from datasets import load_dataset, Dataset, interleave_datasets
from transformers import TrOCRProcessor
from PIL import Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
from random import Random
from IPython.display import HTML, display

import torch

def make_font_dataset():
	data_list = []
	fonts = {}
	def font(size: float):
		size = int(size)
		if size in fonts:
			return fonts[size]
		f = ImageFont.truetype('LiberationSans-Regular.ttf', size)
		fonts[size] = f
		return f
	with open('./data/french_text.txt') as f:
		i = 0
		random = Random()
		random.seed(12)
		for text in f.readlines():
			text = text.strip()
			if text == '':
				continue

			# Limit the size of the printed text database
			i += 1
			if i % 10 != 0:
				continue

			img_width = 512
			img_height = 40
			image = Image.new('RGB', size=(img_width, img_height), color=(255, 255, 255))
			draw = ImageDraw.Draw(image)

			bbox = draw.textbbox((2, 2), text, font=font(10), font_size=10)
			font_size = 10 * min((img_width - 5)/bbox[2], (img_height - 3) / bbox[3])
			text_color = (random.randrange(0, 24), random.randrange(0, 24), random.randrange(0, 24))
			draw.text(
				(2, 5), text, font=font(font_size), font_size=font_size, fill=text_color
			)

			# Overlay a new copy of the text, slightly offset:
			if random.random() > 0.5:
				draw.text(
					(random.randrange(1, 3), random.randrange(4, 6)), text, font=font(font_size), font_size=font_size, fill=text_color
				)

			rotate_deg = (random.random() - 0.5) * 3
			image = image.rotate(rotate_deg, fillcolor=(255, 255, 255))

			data_list.append({
				'text': text,
				'image': image
			})
	return Dataset.from_list(data_list)

class FineTuningDataset:
	def __init__(self, processor: TrOCRProcessor):
		self.processor_ = processor

		revision = 'ba3e6b5'
		dataset_train_rimes_raw = load_dataset('Teklia/RIMES-2011-line', revision=revision, split='train')
		font_dataset = make_font_dataset()

		dataset_train_raw = interleave_datasets([
			dataset_train_rimes_raw,
			font_dataset.shard(2, 0),
		], [0.85, 0.15], stopping_strategy='all_exhausted')

		dataset_test_rimes_raw = load_dataset('Teklia/RIMES-2011-line', revision=revision, split='test')
		dataset_test_raw = interleave_datasets([
			dataset_test_rimes_raw,
			font_dataset.shard(2, 1),
		], [0.85, 0.15])

		self.dataset_train_raw = dataset_train_raw
		self.dataset_test_raw = dataset_test_raw

		remove_cols = ['text', 'image']
		self.dataset_train = self.dataset_train_raw.map(self.data_row_to_torch, remove_columns=remove_cols)
		self.dataset_test = self.dataset_test_raw.map(self.data_row_to_torch, remove_columns=remove_cols)
		# Converts the content of each column to a PyTorch tensor.
		self.dataset_train.set_format(type='torch', columns=['pixel_values', 'labels'])
		self.dataset_test.set_format(type='torch', columns=['pixel_values', 'labels'])
	
	def data_row_to_torch(self, row):
		tokenizer = self.processor_.tokenizer
		labels = tokenizer(row['text'], padding='max_length', max_length = 128).input_ids
		labels_pt = torch.tensor(labels)

		# Make Transformers ignore padding tokens ("any label of -100 will be ignored" from the docs)
		labels_pt[labels_pt == tokenizer.pad_token_id] = -100

		def process_image(image: Image.Image):
			return image.convert('RGB')

		image = row['image']
		if isinstance(row['image'], list):
			image = [ process_image(image) for image in row['image'] ]
		else:
			image = process_image(image)

		# return_tensors='pt': PyTorch
		return {
			"pixel_values": self.processor_(
				image,
				return_tensors='pt'
			).pixel_values.squeeze(),
			"labels": labels_pt
		}

