__author__ = 'xwangan'
from traits.api import HasTraits, Instance
from traitsui.api import Item, View
from enable.api import ComponentEditor
from chaco.api import ArrayPlotData, Plot, ColorBar, LinearMapper, HPlotContainer, DataRange1D, ImageData
import chaco.default_colormaps
#
import numpy as np

class ImagePlot(HasTraits):
    plot = Instance(HPlotContainer)

    traits_view = View(
        Item('plot', editor=ComponentEditor(), show_label=False), width=500, height=500, resizable=True, title="Chaco Plot")

    def _plot_default(self):
        bottomImage = np.reshape(np.repeat(np.linspace(0, 5, 100),100), (100,100))
        topImage = np.eye(50)
        topImage = topImage*np.reshape(np.repeat(np.linspace(-2, 2, 50),50), (50,50))
        topImage[topImage==0] = np.nan
        #
        bottomImageData = ImageData()
        bottomImageData.set_data(bottomImage)
        #
        topImageData = ImageData()
        topImageData.set_data(topImage)
        #
        plotData = ArrayPlotData(imgData=bottomImageData, imgData2=topImageData)
        plot = Plot(plotData, name='My Plot')
        plot.img_plot("imgData")
        plot.img_plot("imgData2")
        # Note: DO NOT specify a colormap in the img_plot!
        plot.aspect_ratio = 1.0
        #
        bottomRange = DataRange1D()
        bottomRange.sources = [plotData.get_data("imgData")]
        topRange = DataRange1D()
        topRange.sources = [plotData.get_data("imgData2")]
        plot.plots['plot0'][0].color_mapper = chaco.default_colormaps.gray(bottomRange)
        plot.plots['plot1'][0].color_mapper = chaco.default_colormaps.jet(topRange)
        #
        colormapperBottom = plot.plots['plot0'][0].color_mapper
        colormapperTop = plot.plots['plot1'][0].color_mapper
        #
        colorbarBottom = ColorBar(index_mapper=LinearMapper(range=colormapperBottom.range), color_mapper=colormapperBottom, orientation='v', resizable='v', width=30, padding=20)
        colorbarBottom.padding_top = plot.padding_top
        colorbarBottom.padding_bottom = plot.padding_bottom
        #
        colorbarTop = ColorBar(index_mapper=LinearMapper(range=colormapperTop.range), color_mapper=colormapperTop, orientation='v', resizable='v', width=30, padding=20)
        colorbarTop.padding_top = plot.padding_top
        colorbarTop.padding_bottom = plot.padding_bottom
        #
        container = HPlotContainer(resizable = "hv", bgcolor='transparent', fill_padding=True, padding=0)
        container.spacing = 0
        container.add(plot)
        container.add(colorbarBottom)
        container.add(colorbarTop)
        #
        return container

if __name__ == "__main__":
    ImagePlot().configure_traits()