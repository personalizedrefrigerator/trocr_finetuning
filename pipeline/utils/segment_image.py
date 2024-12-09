from PIL import Image, ImageDraw
import PIL
import PIL.ImageDraw
from kraken import blla

# NOTE: Requires Python 3.11.


def mask_image_with_polygon(image: Image.Image, polygon: list[tuple]):
	mask = Image.new('1', image.size, 0) # Black/white image
	draw = ImageDraw.Draw(mask)
	draw.polygon(polygon, fill = 1)
	background = Image.new('RGB', image.size, color=(255, 255, 255))
	# Adds a clipped version of the original image to the background:
	background.paste(image, mask=mask)
	return background

def crop_image_to_polygon(image: Image.Image, polygon: list[tuple]):
	polygon_bbox_top_x = min(point[0] for point in polygon)
	polygon_bbox_top_y = min(point[1] for point in polygon)
	polygon_bbox_bottom_x = max(point[0] for point in polygon)
	polygon_bbox_bottom_y = max(point[1] for point in polygon)

	clipped = mask_image_with_polygon(image, polygon)
	return clipped.crop(
		(polygon_bbox_top_x, polygon_bbox_top_y, polygon_bbox_bottom_x, polygon_bbox_bottom_y)
	)

def segment_image(image: Image.Image)->list[Image.Image]:
	""" Divides an input [image] into cropped lines of text.
	"""
	def process_boundary(boundary):
		avg_y = sum(point[1] for point in boundary) / len(boundary)
		def process_point(point: list[int]):
			x = point[0]
			y = point[1]
			if y < avg_y:
				y -= 10
			else:
				y += 10
			y = min(image.height, max(y, 0))
			return (x, y)
		return [ process_point(point) for point in boundary ]
	boundaries = [ process_boundary(line.boundary) for line in blla.segment(image).lines ]
	return [
		crop_image_to_polygon(image, boundary) for boundary in boundaries
	]


def combine_neighboring_lines(images: list[Image.Image]):
	result = []
	for i in range(0, len(images), 1):
		if i + 1 >= len(images):
			result.append(images[i])
		else:
			first = images[i]
			second = images[i + 1]
			spacing = 0
			combined_width = first.width + second.width + spacing
			combined_height = max(first.height, second.height)
			composite = Image.new('RGB', (combined_width, combined_height), color=(255, 255, 255))
			composite.paste(first, (0, 0))
			composite.paste(second, (first.width + spacing, 0))
			result.append(composite)
	return result
