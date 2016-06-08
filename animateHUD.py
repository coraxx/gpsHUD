import gizeh as gz
import moviepy.editor as mpy
import math
import sys
import os
import time
import skimage.filters as skf  # gaussian blur

import gpx_parsing

## data must be at least 2 seconds long (with one point per second)

# For Windows:
# http://lvserver.ugent.be/gtk-win64/gtk2-runtime/
# pip install gizeh
# pip install moviepy
# pip install scikit-image

ping = time.time()


class AnimateHUD():
	def __init__(self, parent=None):
		self.parent = parent

	def loadParams(self):
		if self.parent is not None:
			## Load data points
			if self.parent.gpx_path is None:
				self.gps_speed = [self.parent.spinBox_g_min.value(),self.parent.spinBox_g_max.value(),self.parent.spinBox_g_min.value()]
			else:
				self.gps_speed = gpx_parsing.get_interpolated_speed_list(
					self.parent.gpx_path,
					kalman=self.parent.checkBox_smoothing.isChecked(),
					smoothFactor=self.parent.doubleSpinBox_smoothing_factor.value())
			# print len(self.gps_speed)
			if self.parent.checkBox_render_interval.isChecked():
				self.gps_speed = self.gps_speed[self.parent.spinBox_render_interval_from.value():self.parent.spinBox_render_interval_to.value()+1]
				# print len(self.gps_speed)
			if self.parent.gpx_path is None:
				self.unit_conversion_factor = 1
			elif self.parent.comboBox_unit.currentText() == "km/h":
				self.unit_conversion_factor = 3.6  # km/h
			elif self.parent.comboBox_unit.currentText() == "mph":
				self.unit_conversion_factor = 2.2369362920544  # mph
			else:
				raise TypeError('Wrong conversion factor')
			# print self.unit_conversion_factor

			## Load gauge and set canvas size
			self.duration = len(self.gps_speed)-1  # duration in seconds
			self.template = mpy.ImageClip(self.parent.template_path).set_duration(self.duration)
			self.width, self.height = self.template.size
			self.g_min = self.parent.spinBox_g_min.value()
			self.g_max = self.parent.spinBox_g_max.value()
			self.g_angle_min = math.radians(self.parent.doubleSpinBox_g_angle_min.value())
			self.g_angle_max = math.radians(self.parent.doubleSpinBox_g_angle_max.value())
			self.g_angle_range = self.g_angle_max-self.g_angle_min
			self.g_speedDeadzone = self.parent.spinBox_g_speedDeadzone.value()
			self.g_text_x = self.parent.spinBox_g_text_x.value()
			self.g_text_y = self.parent.spinBox_g_text_y.value()
			self.g_text_size = self.parent.spinBox_g_text_size.value()
			self.g_text_fontFamily = str(self.parent.lineEdit_fontFamily.text())
			self.g_text_visible = self.parent.checkBox_g_text.isChecked()

			## Pointer properties
			self.p_length = self.parent.spinBox_p_length.value()
			self.p_width = self.parent.spinBox_p_width.value()
			self.p_shift = self.parent.doubleSpinBox_p_shift.value()
			self.p_rot_center_x = self.parent.spinBox_p_rot_center_x.value()
			self.p_rot_center_y = self.parent.spinBox_p_rot_center_y.value()
			self.p_color = self.rgb2percent(*self.parent.p_color)
			self.p_opacity = self.parent.doubleSpinBox_p_opacity.value()
			self.p_glow_color = self.rgb2percent(*self.parent.p_glow_Color)
			self.p_glow_opacity = self.parent.doubleSpinBox_p_glow_opacity.value()
			self.p_glow_margin = self.parent.spinBox_p_glow_margin.value()
			self.p_glow_blur = self.parent.spinBox_p_glow_blur.value()

		else:
			## Load data points
			self.gpx_path = '2016-06-02 20_35_20.gpx'
			self.gps_speed = gpx_parsing.get_interpolated_speed_list(self.gpx_path)
			# print len(self.gps_speed)
			self.gps_speed = self.gps_speed[0:5]
			# print len(self.gps_speed)
			self.unit_conversion_factor = 3.6  # km/h
			# self.unit_conversion_factor = 2.2369362920544  # mph

			## Load gauge and set canvas size
			self.template_path = "templates/gauge4.png"
			self.duration = len(self.gps_speed)-1  # duration in seconds
			self.template = mpy.ImageClip(self.template_path).set_duration(self.duration)
			self.width, self.height = self.template.size
			self.g_min = 0
			self.g_max = 240
			self.g_angle_min = math.radians(125.5)
			self.g_angle_max = math.radians(414.5)
			self.g_angle_range = self.g_angle_max-self.g_angle_min
			self.g_speedDeadzone = 0
			self.g_text_x = 250
			self.g_text_y = 325
			self.g_text_size = 40
			self.g_text_fontFamily = "Impact"
			self.g_text_visible = True

			## Pointer properties
			self.p_length = 180  # in px
			self.p_width = 5  # in px
			self.p_shift = 0.45  # translation shift from rotation center in percent
			self.p_rot_center_x, self.p_rot_center_y = self.width/2, self.height/2
			self.p_color = self.rgb2percent(255,180,0)
			self.p_opacity = 0.8
			self.p_glow_color = self.rgb2percent(255,120,0)
			self.p_glow_opacity = 1.0
			self.p_glow_margin = 1  # in px
			self.p_glow_blur = 4  # sigma of gaussian blur

	def generateClips(self):
		"""Generate clips"""
		## get pointer clip
		self.clip_pointer = mpy.VideoClip(self.make_frame, duration=self.duration)
		## get pointer mask
		self.clip_pointer_mask = mpy.VideoClip(self.make_frame_mask, duration=self.duration)
		self.clip_pointer_mask = self.clip_pointer_mask.to_mask(canal=1)

		## generate glow mask
		self.filtr = lambda im: skf.gaussian(im, sigma=self.p_glow_blur)
		self.clip_pointer_glow_mask = self.clip_pointer_mask.fl_image(self.filtr)

		## assign masks
		self.clip_pointer = self.clip_pointer.set_mask(self.clip_pointer_mask)
		self.clip_pointer_glow = self.clip_pointer.set_mask(self.clip_pointer_glow_mask)

		## generate composite
		self.clip = mpy.CompositeVideoClip([
			self.template,
			self.clip_pointer_glow.set_opacity(self.p_glow_opacity),
			self.clip_pointer.set_opacity(self.p_opacity)])

	def export(self,path='',exportFormat=None,fps=24):
		"""Export clip"""
		if exportFormat == 'imageSequence':
			self.clip.write_images_sequence(os.path.join(path,'gauge_export_frame%03d.png'), fps=fps, withmask=True)
		elif exportFormat == 'gif':
			self.clip.write_gif(path,fps=fps, opt="OptimizePlus")
		elif exportFormat == 'mp4':
			self.clip.write_videofile(path, bitrate='10000000', fps=fps)
		elif exportFormat == 'aviPNG':
			self.clip.write_videofile(path, codec='png', fps=fps)
		elif exportFormat == 'aviRAW':
			self.clip.write_videofile(path, codec='rawvideo', fps=fps)

	def preview(self,t=0):
		self.clip.save_frame("preview.png", t=t)
		# self.parent.processBarExport(p=None,initialize=True)

	def rgb2percent(self,r,g,b):
		rgb = (r/255.0,g/255.0,b/255.0)
		return rgb

	def speed2angle(self,t):
		"""
		Returns gauge angle from speed in m/s at time point t from self.gps_speed list.
		"""
		tf = int(math.floor(t))
		tc = int(math.ceil(t))

		if tf == tc:
			speed = self.gps_speed[tf]*self.unit_conversion_factor  # speed in kmh
			if speed < self.g_min or speed < self.g_min+self.g_speedDeadzone:
				return self.g_angle_min
			elif speed > self.g_max:
				return self.g_angle_max
			else:
				return (self.g_angle_range/self.g_max-self.g_min)*speed+self.g_angle_min
		else:
			speed_a = self.gps_speed[tf]*self.unit_conversion_factor  # speed in kmh
			speed_b = self.gps_speed[tc]*self.unit_conversion_factor  # speed in kmh
			speed_interpolated = (speed_b-speed_a)*(t-tf)+speed_a
			return (self.g_angle_range/self.g_max-self.g_min)*speed_interpolated+self.g_angle_min

	def make_frame(self,t):
		"""
		Creates colored pointer. Background color is the blur color, pointer (rect) color is the color
		of the pointer.
		"""
		surface = gz.Surface(self.width, self.height, bg_color=self.p_glow_color)
		# rect = gz.rectangle(lx=150, ly=5, xy=(250,250), fill=(0,1,0), angle=3.1415926/(2*t+1))
		rect = gz.rectangle(
			lx=self.p_length,
			ly=self.p_width,
			xy=(self.p_rot_center_x+self.p_length*self.p_shift, self.p_rot_center_y),
			fill=self.p_color)
		rect = rect.rotate(self.speed2angle(t), center=[self.p_rot_center_x, self.p_rot_center_y])
		rect.draw(surface)
		if self.g_text_visible:
			txt = gz.text(
				'{0}'.format(int(self.gps_speed[int(t)]*self.unit_conversion_factor)),
				fontfamily=self.g_text_fontFamily, fontsize=self.g_text_size, xy=(self.g_text_x, self.g_text_y), fill=self.p_color)
			txt.draw(surface)
		arr = surface.get_npimage()
		if self.parent is not None:
			self.parent.processBarExport(p=1)
			if self.parent.cancelExport is True:
				raise TypeError('Canceling...')
		return arr

	def make_frame_mask(self,t):
		"""
		Creates pointer mask.
		"""
		surface = gz.Surface(self.width, self.height, bg_color=(0,0,0))
		# rect = gz.rectangle(lx=150, ly=5, xy=(250,250), fill=(1,1,1), angle=3.1415926/(2*t+1))
		rect = gz.rectangle(
			lx=self.p_length+2*self.p_glow_margin,
			ly=self.p_width+2*self.p_glow_margin,
			xy=(self.p_rot_center_x+self.p_length*self.p_shift, self.p_rot_center_y),
			fill=(1,1,1))
		rect = rect.rotate(self.speed2angle(t), center=[self.p_rot_center_x, self.p_rot_center_y])
		rect.draw(surface)
		if self.g_text_visible:
			txt = gz.text(
				'{0}'.format(int(self.gps_speed[int(t)]*self.unit_conversion_factor)),
				fontfamily=self.g_text_fontFamily, fontsize=self.g_text_size, xy=(self.g_text_x, self.g_text_y), fill=(1,1,1))
			txt.draw(surface)
		arr = surface.get_npimage()
		if self.parent is not None and self.parent.cancelExport is True:
			raise TypeError('Canceling...')
		return arr

if __name__ == '__main__':
	animateHUD = AnimateHUD()
	animateHUD.loadParams()
	animateHUD.generateClips()
	animateHUD.preview(t=0)
	# animateHUD.export('imageSequence',path='./seq')

# pong = time.time()
# print 'Time in s:', pong - ping
