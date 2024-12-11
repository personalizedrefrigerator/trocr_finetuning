from PIL import Image
from transformers import VisionEncoderDecoderModel, TrOCRProcessor
import torch
from pathlib import Path
from utils.segment_image import segment_image
from spellchecker import SpellChecker
import re

SPACES_EXP = re.compile(r'\s+')

class TextRecognizer:
	def __init__(self):
		processor = TrOCRProcessor.from_pretrained('microsoft/trocr-small-handwritten')
		model = VisionEncoderDecoderModel.from_pretrained('personalizedrefrigerator/trocr-small-fr')

		model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
		model.config.pad_token_id = processor.tokenizer.pad_token_id
		model.config.vocab_size = model.config.decoder.vocab_size

		# For now, take beam search parameters from the tutorial
		model.generation_config.eos_token_id = processor.tokenizer.sep_token_id
		model.generation_config.max_length = 64
		model.generation_config.early_stopping = True
		model.generation_config.no_repeat_ngram_size = 3
		model.generation_config.length_penalty = 2.0
		model.generation_config.num_beams = 2

		self.model = model
		self.processor = processor
		self.spellcheck = SpellChecker(language='fr')
	
	def fix_spelling(self, text: str)->str:
		words = SPACES_EXP.split(text)
		wrong_words = self.spellcheck.unknown(words)
		corrections = {}
		for word in wrong_words:
			corrections[word] = self.spellcheck.correction(word)
		
		def fix_word(word: str):
			# If no correction is available, corrections[word] is None
			if word in corrections and corrections[word] != None:
				return corrections[word]
			return word

		return ' '.join([ fix_word(word) for word in words ])

	def recognize_lines(self, images_raw: list[Image.Image])->str:
		def convert_image(image: Image.Image):
			return self.processor(image.convert('RGB'), return_tensors='pt').pixel_values.squeeze()
		images = [ convert_image(image) for image in images_raw ]

		result = []
		batch_size = 8
		for i in range(0, len(images), batch_size):
			batch = torch.stack(images[i:i+batch_size])
			generated_labels = self.model.generate(batch)
			result += self.processor.batch_decode(generated_labels, skip_special_tokens=True)
		return [ self.fix_spelling(line) for line in result ]

	def recognize_page(self, page: Image.Image)->list[str]:
		return '\n'.join(self.recognize_lines(segment_image(page)))
