from matplotlib import pyplot
from matplotlib.patches import Circle
from shapely.geometry import Polygon, Point
from descartes.patch import PolygonPatch
import math

#from figures import SIZE

COLOR = {
    True:  '#6699cc',
    False: '#ff3333'
    }

SampleCellData = [
    ["Cell1", -3.68003, 42.36526, 150, 65, 15],
    ["Cell2", -3.689498889, 42.33775583, 150, 65, 15]
]

cells_g = {}

class Cell(object):
    def __init__(self, name, lat, long, azimuth, bw, radius):
        self.name = name
        self.lat  = lat
        self.long = long
        self.azimuth = azimuth
        self.bw = bw
        self.radius = radius
        self.geo = Geometry(self)

class Geometry(object):
    def __init__(self, cell):
        self.cell = cell
        cell.geo = self
        self.poly_lines = 16
        self.edgeL = 0.0
        self.edgeR = 0.0

    def getOriginLatLong(self):
        cellitems = list(cells_g)
        return (math.radians(cells_g[cellitems[0]].lat), math.radians(cells_g[cellitems[0]].long))

    def get_distance_from_origin(self):
        '''
        Using Haversine formula
        '''
        radius_of_earth = 6371
        latR = math.radians(self.cell.lat)
        lonR = math.radians(self.cell.long)
        originlatR, originlongR = self.getOriginLatLong()
        deltaLon = lonR - originlongR
        deltaLat = latR - originlatR
        a = math.sin(deltaLat/ 2) ** 2 + math.cos(originlatR) * math.cos(latR) * math.sin(deltaLon/2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        dist = radius_of_earth * c
        print "Computed Distance %d" %(dist)
        '''
        Reference
        http://www.movable-type.co.uk/scripts/latlong.html
        '''
        y = math.sin(deltaLon) * math.cos(latR)
        x = math.cos(originlatR) * math.sin(latR) - math.sin(originlatR) * math.cos(latR) * math.cos(deltaLon)
        brng = math.degrees(math.atan2(y, x)) % 360
        print "Computed bearing %d" %(brng)

        return dist,brng

    def get_coordinates(self):
        cellitems = list(cells_g)
        print cellitems[0]
        print "CellName %s, First Cell Name %s" %(self.cell.name, cellitems[0])
        if self.cell.name == cellitems[0]:
            print 0,0
            return 0,0
        else:
            dist,brng = self.get_distance_from_origin()
            rfx = math.radians((90-brng) % 360)
            return ( dist*math.cos(rfx), dist*math.sin(rfx))

    def get_cone_edges(self, azimuth, beamwidth):
        half_sector = float(beamwidth)/2
        left_edge = (azimuth-half_sector) % 360
        right_edge = (azimuth+half_sector) % 360
        return(left_edge, right_edge)

    def create_polygon(self):
        center = (self.x, self.y)
        polygon_vertex = [(self.x, self.y)]
        step = float(self.cell.bw)/self.poly_lines
        for i in range(self.poly_lines + 1):
            angle_from_x = (90 - (self.edgeL + step*i)) % 360
            xrad = math.radians(angle_from_x)
            polygon_vertex.append(((self.x + math.cos(xrad) * self.cell.radius),
                                      (self.y + math.sin(xrad) * self.cell.radius)))
        polygon1 = Polygon(polygon_vertex)
        self.polygon = polygon1
        for delta in (0, 0.01, -0.01):
            self.polygon = polygon1.union(Point(center).buffer(0.6 + delta))
            if self.polygon.is_valid:
                break;

    def generate_beam_form(self):
        self.x,self.y =  self.get_coordinates()
        print self.x,self.y
        self.edgeL, self.edgeR = self.get_cone_edges(self.cell.azimuth, self.cell.bw)
        self.create_polygon()
        print self.polygon

class Plotter:
    def __init__(self):
        self.fig = pyplot.figure(1,figsize=(40,5), dpi=90)
        self.xrange = [-15, 15]
        self.yrange = [-15, 15 ]
        self.polygons = []
        self.ext = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        self.subplotter()

    def subplotter(self):
        self.ax = self.fig.add_subplot(121)
        self.ax.set_title('Cell Cone')
        self.ax.set_xlim(*(self.xrange))
        self.ax.set_xticks(range(*self.xrange) + [self.xrange[-1]])
        self.ax.set_ylim(*self.yrange)
        self.ax.set_yticks(range(*self.yrange) + [self.yrange[-1]])
        self.ax.set_aspect(1)

    def addtosubplot(self, polygon):
        x,y = polygon.xy
        self.ax.plot(x,y, 'o', color='#FF9999', zorder = 1)

    def plotCoords(self, vertexlist):
        #for polygon in self.polygons:
        #   self.addtosubplot(polygon.interiors)
        #self.addtosubplot(self.polygon.interiors[0])
        #self.addtosubplot(self.polygon.interiors[1])
        #self.addtosubplot(self.polygon.exterior)
        self.addtosubplot(vertexlist)

    def plotterColor(self, ob):
        return COLOR[ob.is_valid]

    def updateCellsToPlot(self):
        for key,cell in cells_g.items():
            #polygon = Polygon(self.ext, list(cell.geo.polygon.exterior.coords))
            #self.polygons.append(plot_vertex_list)
            self.plotCoords(cell.geo.polygon.exterior)
        #self.polygon = Polygon(self.ext, self.polygons)
        #self.plotCoords()
        #patch = PolygonPatch(self.polygon, facecolor=self.plotterColor(self.polygon), edgecolor=self.plotterColor(self.polygon), alpha=0.5, zorder=2)
        #self.ax.add_patch(patch)


    def display(self):
        pyplot.xlim(5,40)
        pyplot.show()



def readCellData():
    for data in SampleCellData:
        cells_g[str(data[0])]=Cell(data[0], data[1], data[2], data[3], data[4], data[5])
    for key,cell in cells_g.items():
        cell.geo.generate_beam_form()


if __name__ == "__main__":
    readCellData()
    plotter = Plotter()
    plotter.updateCellsToPlot()
    plotter.display()

