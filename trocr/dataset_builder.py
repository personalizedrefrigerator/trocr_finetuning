from datasets import load_dataset, Dataset, interleave_datasets
from transformers import TrOCRProcessor
from PIL import Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
from random import Random
from IPython.display import HTML, display
from data_generator.make_font_dataset import make_font_dataset
from pathlib import Path

import torch

class FineTuningDataset:
	def __init__(self, processor: TrOCRProcessor):
		self.processor_ = processor

		data_directory = Path(__file__).parent / 'data'
		font_dataset_path = (data_directory / 'dataset-saves' / 'font_data')
		if not font_dataset_path.exists():
			font_dataset = make_font_dataset().shuffle(seed=13)
			font_dataset_path.mkdir(parents = True, exist_ok=True)
			font_dataset.save_to_disk(font_dataset_path)
		else:
			font_dataset = Dataset.load_from_disk(font_dataset_path)

		#revision = 'ba3e6b5'
		#dataset_train_rimes_raw = load_dataset('Teklia/RIMES-2011-line', revision=revision, split='train')

		font_first_100 = font_dataset.take(100)
		dataset_train_raw = font_dataset.skip(100).to_iterable_dataset()

		#dataset_test_rimes_raw = load_dataset('Teklia/RIMES-2011-line', revision=revision, split='test')
		dataset_test_raw = font_first_100

		self.dataset_train_raw = dataset_train_raw
		self.dataset_test_raw = dataset_test_raw

		remove_cols = ['text', 'image']
		self.dataset_train = self.dataset_train_raw.map(self.data_row_to_torch, remove_columns=remove_cols).with_format('torch')
		self.dataset_test = self.dataset_test_raw.map(self.data_row_to_torch, remove_columns=remove_cols).with_format('torch')
	
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

