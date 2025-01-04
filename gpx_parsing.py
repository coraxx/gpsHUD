import gpxpy
import gpxpy.gpx
import time
import numpy as np
from pykalman import KalmanFilter


debug = False
path = '2016-06-02 20_35_20.gpx'


def get_interpolated_coordinate_list(path):
	gpx_file = open(path, 'r')
	gpx = gpxpy.parse(gpx_file)
	interpolated_list = []
	interpolated = 0  # for debugging

	# for track in gpx.tracks:
	# 	for segment in track.segments:
	# 		for point in segment.points:
	# 			print 'Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation)

	for point in range(len(gpx.tracks[0].segments[0].points)-1):
		aTim = time.mktime(gpx.tracks[0].segments[0].points[point].time.timetuple())
		aLat = gpx.tracks[0].segments[0].points[point].latitude
		aLon = gpx.tracks[0].segments[0].points[point].longitude
		aEle = gpx.tracks[0].segments[0].points[point].elevation

		bTim = time.mktime(gpx.tracks[0].segments[0].points[point+1].time.timetuple())
		bLat = gpx.tracks[0].segments[0].points[point+1].latitude
		bLon = gpx.tracks[0].segments[0].points[point+1].longitude
		bEle = gpx.tracks[0].segments[0].points[point+1].elevation

		interpolated_list.append([aLat, aLon, aEle])

		## if time difference is greater than one second, the missing seconds are interpolated linear
		if bTim-aTim > 1:
			for second in range(int(bTim-aTim-1)):
				interpolated_list.append([
					(((bLat-aLat)/(bTim-aTim))*(second+1))+aLat,
					((bLon-aLon)/(bTim-aTim))*(second+1)+aLon,
					((bEle-aEle)/(bTim-aTim))*(second+1)+aEle])
			if debug:
				print(aTim, bTim, bTim-aTim)
				print(point, ':', aLat, aLon, aEle)
				for second in range(int(bTim-aTim-1)):
					print((
						'>>>>>', (((bLat-aLat)/(bTim-aTim))*(second+1))+aLat, ((bLon-aLon)/(bTim-aTim))*(second+1)+aLon, ((bEle-aEle)/(bTim-aTim))*(second+1)+aEle))
					interpolated += 1
				print(point+1, ':', bLat, bLon, bEle)
				print('='*10)

	if debug:
		print('Duration from file: ', gpx.get_duration())
		print('Duration calculated:', time.mktime(
			gpx.tracks[0].segments[0].points[-1].time.timetuple())-time.mktime(gpx.tracks[0].segments[0].points[0].time.timetuple()))
		print('Data points:        ', len(gpx.tracks[0].segments[0].points))
		print('Interpolated Points:', interpolated)
		print('New Data Points:    ', len(gpx.tracks[0].segments[0].points) + interpolated)
		print('#'*50)
		print(interpolated_list)

	return interpolated_list


def get_interpolated_speed_list(path,kalman=False,smoothFactor=0.01):
	gpx_file = open(path, 'r')
	gpx = gpxpy.parse(gpx_file)
	interpolated_list = []
	previous_speed = 0

	for point in range(len(gpx.tracks[0].segments[0].points)-1):
		p1 = gpx.tracks[0].segments[0].points[point]
		p1_time = time.mktime(p1.time.timetuple())

		p2 = gpx.tracks[0].segments[0].points[point+1]
		p2_time = time.mktime(p2.time.timetuple())

		## average speed between data points
		speed = p1.speed_between(p2)
		if speed is None or speed == 0:
			if previous_speed > 7:
				if speed == 0:
					speed = previous_speed-1
				else:
					speed = previous_speed
			else:
				speed = 0
		previous_speed = speed

		interpolated_list.append(speed)

		## if time difference is greater than one second, the missing seconds are filled with average speed
		if p2_time-p1_time > 1:
			seconds = int(p2_time-p1_time-1)
			for second in range(seconds):
				interpolated_list.append(speed)
	if kalman is True:
		kf = KalmanFilter(transition_matrices=np.array([[1, 1], [0, 1]]), transition_covariance=smoothFactor*np.eye(2))
		states_pred = kf.em(interpolated_list).smooth(interpolated_list)[0]
		return states_pred[:, 0]
	else:
		return interpolated_list

if __name__ == '__main__':
	# get_interpolated_coordinate_list(path)
	i = 0
	for speed in get_interpolated_speed_list(path):
		# if i in [630,631,632]:
		print(i, speed*3.6)
		i += 1
