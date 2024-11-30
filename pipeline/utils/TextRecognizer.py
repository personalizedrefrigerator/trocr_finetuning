from PIL import Image
from transformers import VisionEncoderDecoderModel, TrOCRProcessor
import torch
from pathlib import Path
from utils.segment_image import segment_image


class TextRecognizer:
	def __init__(self):
		local_path = Path('/media/sf_vbox-share/model-20241128T173856Z-001/model/').resolve()
		processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
		model = VisionEncoderDecoderModel.from_pretrained(local_path)

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
		return result

	def recognize_page(self, page: Image.Image)->list[str]:
		return self.recognize_lines(segment_image(page))
