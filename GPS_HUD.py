import sys
import os
from PyQt4 import QtCore, QtGui, uic
import animateHUD

__version__ = 'v1.0.0b'

# add working directory temporarily to PYTHONPATH
if getattr(sys, 'frozen', False):
	# program runs in a bundle (pyinstaller)
	execdir = sys._MEIPASS
else:
	execdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(execdir)

qtCreatorFile_main = os.path.join(execdir, "GPS_HUD.ui")
Ui_WidgetWindow, QtBaseClass = uic.loadUiType(qtCreatorFile_main)


class MainWidget(QtGui.QMainWindow, Ui_WidgetWindow):
	def __init__(self):
		QtGui.QWidget.__init__(self)
		Ui_WidgetWindow.__init__(self)
		self.setupUi(self)

		## Initialize default values
		self.lastPath_export = execdir
		self.lastPath_template = execdir
		self.lastPath_gpx = execdir
		self.p_color = (255,180,0)
		self.p_glow_Color = (255,120,0)
		self.gpx_path = None
		self.processBarActive = False
		self.cancelExport = False

		## Buttons
		self.toolButton_template_select.clicked.connect(self.selectTemplate)
		self.toolButton_gpx_select.clicked.connect(self.selectGPX)
		self.toolButton_p_color_select.clicked.connect(self.getPointerColor)
		self.toolButton_p_glow_color_select.clicked.connect(self.getPointerGlowColor)
		self.toolButton_preview.clicked.connect(self.preview)
		self.toolButton_export.clicked.connect(self.export)
		self.toolButton_cancelExport.clicked.connect(self.setCancelExport)

		self.animate = animateHUD.AnimateHUD(self)
		self.loadImage(None)

	def selectTemplate(self):
		path = str(QtGui.QFileDialog.getOpenFileName(
			None,"Select image file as template", self.lastPath_template,"Image Files (*.png);; All (*.*)"))
		if path:
			self.template_path = path
			self.lineEdit_template_path.setText(path)
			self.lastPath_template = path
			self.loadImage(path)

	def loadImage(self,path=None):
		self.scene = QGraphicsSceneCustom(self.graphicsView, mainWidget=self)
		if path is None:
			try:
				self.pixmap = QtGui.QPixmap(os.path.join(execdir,'templates/blank.png'))
				self.template_path = os.path.join(execdir,'templates/blank.png')
			except Exception as e:
				raise e
		else:
			self.pixmap = QtGui.QPixmap(path)
		QtGui.QGraphicsPixmapItem(self.pixmap, None, self.scene)
		## Add frame
		self.scene.addRect(0,0,self.pixmap.width(),self.pixmap.height(), pen=QtGui.QPen(QtCore.Qt.black))
		## connect scenes to GUI elements
		self.graphicsView.setScene(self.scene)
		## reset scaling (needed for reinitialization)
		self.graphicsView.resetMatrix()
		## scaling scene, not image
		canvas_size = min([self.graphicsView.width(), self.graphicsView.height()])
		img_size = max(self.pixmap.width(), self.pixmap.height())
		# print canvas_size, img_size
		if img_size > canvas_size:
			scaling_factor = canvas_size/(float(img_size)+4)
			self.graphicsView.scale(scaling_factor,scaling_factor)

	def selectGPX(self):
		path = str(QtGui.QFileDialog.getOpenFileName(
			None,"Select gpx file", self.lastPath_gpx,"Image Files (*.gpx);; All (*.*)"))
		if path:
			self.gpx_path = path
			self.lastPath_gpx = path
			self.lineEdit_gpx_path.setText(path)

	def getPointerColor(self):
		color = QtGui.QColorDialog.getColor()
		if color.isValid():
			self.p_color = (color.red(), color.green(), color.blue())
			self.label_p_color.setStyleSheet("background-color: rgb{0};".format((color.red(), color.green(), color.blue())))

	def getPointerGlowColor(self):
		color = QtGui.QColorDialog.getColor()
		if color.isValid():
			self.p_glow_Color = (color.red(), color.green(), color.blue())
			self.label_p_glow_color.setStyleSheet("background-color: rgb{0};".format((color.red(), color.green(), color.blue())))

	def preview(self,t=0):
		self.animate.loadParams()
		self.animate.generateClips()
		self.animate.preview(t=t)
		try:
			self.loadImage('preview.png')
		except Exception as e:
			print 'Loading template due to error:', e
			self.loadImage(self.template_path)

	def export(self):
		self.animate.loadParams()
		self.animate.generateClips()
		self.processBarActive = True
		self.processBarExport(p=None,initialize=True)
		QtGui.QApplication.processEvents()
		exportFormat = None

		if self.comboBox_export_format.currentText() == 'image sequence (.png)':
			path = str(QtGui.QFileDialog.getExistingDirectory(self, "Select image sequence destination folder", self.lastPath_export))
			if path:
				exportFormat = 'imageSequence'
				self.lastPath_export = path
		elif self.comboBox_export_format.currentText() == 'gif':
			path = str(QtGui.QFileDialog.getSaveFileName(
				self, "Save File", os.path.join(self.lastPath_export,'gauge_export.gif'), "GIF (*.gif)"))
			if path:
				exportFormat = 'gif'
				self.lastPath_export = os.path.split(path)[0]
		elif self.comboBox_export_format.currentText() == 'mp4 (h264)':
			path = str(QtGui.QFileDialog.getSaveFileName(
				self, "Save File", os.path.join(self.lastPath_export,'gauge_export.mp4'), "h.264 (*.mp4)"))
			if path:
				exportFormat = 'mp4'
				self.lastPath_export = os.path.split(path)[0]
		elif self.comboBox_export_format.currentText() == 'avi (raw)':
			path = str(QtGui.QFileDialog.getSaveFileName(
				self, "Save File", os.path.join(self.lastPath_export,'gauge_export.avi'), "AVI (rawvideo) (*.avi)"))
			if path:
				exportFormat = 'aviRAW'
				self.lastPath_export = os.path.split(path)[0]
		elif self.comboBox_export_format.currentText() == 'avi (png)':
			path = str(QtGui.QFileDialog.getSaveFileName(
				self, "Save File", os.path.join(self.lastPath_export,'gauge_export.avi'), "AVI (PNG) (*.avi)"))
			if path:
				exportFormat = 'aviPNG'
				self.lastPath_export = os.path.split(path)[0]

		if exportFormat is not None:
			self.toolButton_export.setEnabled(False)
			self.toolButton_cancelExport.setEnabled(True)
			try:
				self.animate.export(path, exportFormat, fps=self.doubleSpinBox_fps.value())
			except Exception as e:
				print e
				os.remove(path)
			self.processBarActive = False
			self.toolButton_export.setEnabled(True)
			self.toolButton_cancelExport.setEnabled(False)
			self.cancelExport = False
			QtGui.QApplication.processEvents()

	def setCancelExport(self):
		self.cancelExport = True

	def processBarExport(self,p=None,initialize=False):
		if initialize is True:
			self.progressBar_export.setValue(0)
			self.progressBar_export.reset()
			self.progressBar_export.setMaximum(2*int(self.animate.duration*self.doubleSpinBox_fps.value()))
			QtGui.QApplication.processEvents()
		if p and self.processBarActive:
			self.progressBar_export.setValue(self.progressBar_export.value()+p)
			QtGui.QApplication.processEvents()


class QGraphicsSceneCustom(QtGui.QGraphicsScene):
	def __init__(self,parent=None,mainWidget=None):
		self.mainWidget = mainWidget
		## parent is QGraphicsView
		QtGui.QGraphicsScene.__init__(self,parent)
		self.parent().setDragMode(QtGui.QGraphicsView.NoDrag)
		## Initialize variables
		self.lastScreenPos = QtCore.QPoint(0, 0)
		self.lastScenePos = 0

	def wheelEvent(self, event):
		## Scaling
		if event.delta() > 0:
			scalingFactor = 1.15
		else:
			scalingFactor = 1 / 1.15
		self.parent().scale(scalingFactor, scalingFactor)
		## Center on mouse pos only if mouse moved mor then 25px
		if (event.screenPos() - self.lastScreenPos).manhattanLength() > 25:
			self.parent().centerOn(event.scenePos().x(), event.scenePos().y())
			self.lastScenePos = event.scenePos()
		else:
			self.parent().centerOn(self.lastScenePos.x(), self.lastScenePos.y())
		## Save pos for precise scrolling, i.e. centering view only when mouse moved
		self.lastScreenPos = event.screenPos()

	def mousePressEvent(self, event):
		modifiers = QtGui.QApplication.keyboardModifiers()
		if event.button() == QtCore.Qt.LeftButton and modifiers != QtCore.Qt.ControlModifier:
			# print 'Mouse left button'
			self.parent().setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
		# elif event.button() == QtCore.Qt.LeftButton and modifiers == QtCore.Qt.ControlModifier:
			# print 'Mouse left button + ctrl'
		elif event.button() == QtCore.Qt.RightButton:
			# print 'Mouse right button at', event.scenePos().x(), event.scenePos().y()
			self.mainWidget.spinBox_p_rot_center_x.setValue(int(event.scenePos().x()))
			self.mainWidget.spinBox_p_rot_center_y.setValue(int(event.scenePos().y()))
		# elif event.button() == QtCore.Qt.MiddleButton:
			# print 'Mouse middle button'

	def mouseReleaseEvent(self, event):
		super(QGraphicsSceneCustom, self).mouseReleaseEvent(event)
		self.parent().setDragMode(QtGui.QGraphicsView.NoDrag)


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = MainWidget()
	window.show()
	window.raise_()
	sys.exit(app.exec_())
