import pdb
import argparse
import calendar

import numpy
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
import iris.coord_categorisation
import cmocean

def read_data(fname, month):
    """Read an input data file"""
    
    cube = iris.load_cube(fname, 'precipitation_flux')
    
    iris.coord_categorisation.add_month(cube, 'time')
    cube = cube.extract(iris.Constraint(month=month))
    
    return cube


def convert_pr_units(cube):
    """Convert kg m-2 s-1 to mm day-1"""
    
    cube.data = cube.data * 86400
    cube.units = 'mm/day'
    
    return cube

def apply_mask(pr_cube, sftlf_cube, realm):
    """Apply a land or ocean mask"""
    
    if realm == 'ocean':
        mask = numpy.where(sftlf_cube.data < 50, True, False)
    else:
        mask = numpy.where(sftlf_cube.data >= 50, True, False)
    pr_cube.data.mask = mask
        
    return pr_cube
    
def plot_data(cube, month, gridlines=False, levels=None):
#def plot_data(cube, month, gridlines=False):
    """Plot the data."""
        
    fig = plt.figure(figsize=[12,5])    
    iplt.contourf(cube, cmap=cmocean.cm.haline_r, 
                  levels=levels,
                  extend='max')
    #iplt.contourf(cube, cmap=cmocean.cm.haline_r, 
    #              levels=numpy.arange(0, 10),
    #              extend='max')

    plt.gca().coastlines()
    if gridlines:
        plt.gca().gridlines()
    cbar = plt.colorbar()
    cbar.set_label(str(cube.units))
    
    title = '%s precipitation climatology (%s)' %(cube.attributes['model_id'], month)
    plt.title(title)


def main(inargs):
    """Run the program."""

    cube = read_data(inargs.infile, inargs.month)    
    cube = convert_pr_units(cube)
    clim = cube.collapsed('time', iris.analysis.MEAN)
    if inargs.mask:
        sftlf_file, realm = inargs.mask
        sftlf_cube = iris.load_cube(sftlf_file, 'land_area_fraction')
        clim = apply_mask(clim, sftlf_cube, realm)
    plot_data(clim, inargs.month, gridlines=inargs.gridlines,
             levels=inargs.cbar_levels)
    #plot_data(clim, inargs.month, gridlines=inargs.gridlines)
    plt.savefig(inargs.outfile)


if __name__ == '__main__':
    description='Plot the precipitation climatology for a given month.'
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("month", type=str, help="Month to plot", choices=calendar.month_abbr[1:])
    #parser.add_argument("month", type=str, help="Month to plot", choices=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    parser.add_argument("outfile", type=str, help="Output file name")
    parser.add_argument("--gridlines", help="Add gridlines if specified",
                    action="store_true")
    #parser.add_argument("-cmin", type=int, help="Specify colorbar min tick level")
    #parser.add_argument("-cmax", type=int, help="Specify colorbar max tick level")
    parser.add_argument("--cbar_levels", type=float, nargs='*', default=None,
                        help='list of levels / tick marks to appear on the colourbar')
    parser.add_argument("--mask", type=str, nargs=2,
                        metavar=('SFTLF_FILE', 'REALM'), default=None,
                        help='Apply a land or ocean mask (specify the realm to mask)')

    args = parser.parse_args()
    
    main(args)
