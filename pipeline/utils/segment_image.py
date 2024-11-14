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
		return [ tuple(point) for point in boundary ]
	boundaries = [ process_boundary(line.boundary) for line in blla.segment(image).lines ]
	return [
		crop_image_to_polygon(image, boundary) for boundary in boundaries
	]