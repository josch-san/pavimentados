import cv2
import numpy as np
import random
from pathlib import Path
import os
from configs.utils import Config_Basic

def load_video(video_path):
	"""
	Carga el video.
	"""
	vidcap = cv2.VideoCapture(video_path)
	fps = int(vidcap.get(cv2.CAP_PROP_FPS))
	number_of_frames =  int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
	return vidcap, fps, number_of_frames


class ListImages:
	def __init__(self, images):
		self.images = images
	
	def get_altura_base(self):
		return tuple(self.image[0].shape[1:3])
	
	def get_len(self):
		return self.images.shape[0]
		
	def get_section(self, idx_inicial, idx_final):
		return self.images[idx_inicial:idx_final]
	
	def get_batch(self, idx_inicial, batch_size = 8):
		return self.get_section(idx_inicial, idx_inicial+batch_size)
	
class ListRoutesImages:
	def __init__(self, routes):
		self.routes = routes
		
	def get_altura_base(self):
		return tuple(cv2.imread(str(self.routes[0])).shape[:2])
	
	def get_len(self):
		return len(self.routes)
	
	def get_section(self, idx_inicial, idx_final):
		return self.routes[idx_inicial:idx_final]
	
	def get_batch(self, idx_inicial, batch_size = 8):
		return np.array([cv2.imread(str(img_path)) for img_path in self.get_section(idx_inicial,idx_inicial+batch_size)])

class FolderRoutesImages(ListRoutesImages, Config_Basic):
    def __init__(self, route, config_file = Path('configs') / 'images_processor.json' ):
        self.load_config(config_file)
        folder = Path(route)
        self.routes = list(filter(lambda x: str(x).lower().split('.')[-1] in self.config['images_allowed'], map(lambda x: folder / x , os.listdir(folder))))

class VideoCaptureImages:
	def __init__(self, route):
		self.route = str(route)
		vidcap, fps, number_of_frames = load_video(self.route)
		self.lenght = number_of_frames
		vidcap.set(cv2.CAP_PROP_POS_FRAMES, random.randint(0,number_of_frames))
		state, img = vidcap.read()
		self.img_shape = img.shape[:2]
		self.vidcap, fps, number_of_frames = load_video(self.route)

	def get_altura_base(self):
		return self.img_shape
	
	def get_len(self):
		return self.lenght
	
	def get_batch(self, idx_inicial, batch_size = 8):
		images = []
		for i in range(batch_size):
			state, img = self.vidcap.read()
			if state:
				images.append(img)
		return np.array(images)

source_options_dict = {
	'image_routes' : ListRoutesImages, 
    'image_folder' : FolderRoutesImages,
	'images' : ListImages, 
	'video'  : VideoCaptureImages
}

def Image_Source_Loader(source_type, *args):
	if source_type not in source_options_dict:
		raise NameError(f'{source_type} not implemented on the method')
	return source_options_dict[source_type](*args)