# -*- coding: utf-8 -*-

"""
Code modified from https://github.com/neuralensemble/python-neo.
"""

import sys
from datetime import datetime

import numpy as np
import quantities as pq
import matplotlib
from matplotlib import pyplot
from matplotlib.patches import Rectangle, Arc, RegularPolygon
from matplotlib.font_manager import FontProperties

import neo
from neo.test.generate_datasets import fake_neo

##### plotting utilities

line_heigth = .22
fontsize = 10.5
left_text_shift = .1
dpi = None


def get_rect_height(name, obj):
    '''
    calculate rectangle height
    '''
    nlines = 1.5
    nlines += len(getattr(obj, '_all_attrs', []))
    nlines += len(getattr(obj, '_single_child_objects', []))
    nlines += len(getattr(obj, '_multi_child_objects', []))
    nlines += len(getattr(obj, '_multi_parent_objects', []))
    return nlines * line_heigth


def annotate(ax, coord1, coord2, connectionstyle, color, alpha):
    arrowprops = dict(arrowstyle='fancy',
                      # ~ patchB=p,
                      shrinkA=.3, shrinkB=.3,
                      fc=color, ec=color,
                      connectionstyle=connectionstyle,
                      alpha=alpha)
    bbox = dict(boxstyle="square", fc="w")
    a = ax.annotate('', coord1, coord2,
                    # xycoords="figure fraction",
                    # textcoords="figure fraction",
                    ha="right", va="center",
                    size=fontsize,
                    arrowprops=arrowprops,
                    bbox=bbox)
    a.set_zorder(-4)


def calc_coordinates(pos, height):
    x = pos[0]
    y = pos[1] + height - line_heigth * .5

    return pos[0], y
    
    
def draw_circ(ax,radius,centX,centY,angle_,theta2_,color_='black'):
    #========Line
    arc = Arc([centX,centY],radius,radius,angle=angle_,
          theta1=0,theta2=theta2_,capstyle='round',linestyle='-',lw=3,color=color_)
    ax.add_patch(arc)


    #========Create the arrow head
    endX=centX+(radius/2)*np.cos(np.radians(theta2_+angle_)) #Do trig to determine end position
    endY=centY+(radius/2)*np.sin(np.radians(theta2_+angle_))

    ax.add_patch(                    #Create triangle as arrow head
        RegularPolygon(
            (endX, endY),            # (x,y)
            3,                       # number of vertices
            radius/9,                # radius
            np.radians(angle_+theta2_),     # orientation
            color=color_
        )
    )
    ax.set_xlim([centX-radius,centY+radius]) and ax.set_ylim([centY-radius,centY+radius]) 
    # Make sure you keep the axes scaled or else arrow will distort


####### Dummy classes to include future plans into plot of current neo version
class View_Dummy(neo.core.container.Container):
    _ignorant_child_objects = ('AnalogSignal', 'IrregularlySampledSignal', 'SpikeTrain', 'Event', 'Epoch')
    _single_child_objects = ()
    _container_child_objects = ()
    _single_parent_objects = ()
    _multi_child_objects = ()
    _child_properties = ()
    _necessary_attrs = (('data_object',neo.core.dataobject.DataObject), ('indices',np.ndarray, 1, np.dtype('i')))
    _recommended_attrs = (('name', str), ('description',str),('file_origin',str))
    _all_attrs = _necessary_attrs + _recommended_attrs
    def __init__(self):
        super(View_Dummy, self).__init__()

class Group_Dummy(neo.core.container.Container):
    _single_child_objects = ('Group', 'View')
    _container_child_objects = ()
    _single_parent_objects = ('Block',)
    _multi_child_objects = ()
    _child_properties = ()
    _necessary_attrs = (('mode', str),)
    _ignorant_child_objects = ('View',)
    _recommended_attrs = (('name', str), ('description',str),('file_origin',str))
    _all_attrs = _necessary_attrs + _recommended_attrs
    def __init__(self):
        super(Group_Dummy, self).__init__()

class Block_Enhanced(neo.core.Block):
    _single_child_objects = ('Segment', 'Group')
    
    def __init(self):
        self._single_child_objects = ('Segment', 'Group')
        super(Block_future).__init()
 
                
fake_classes = {'Group': Group_Dummy,
                'View': View_Dummy}


def generate_diagram(filename, rect_pos, rect_width, figsize):
    rw = rect_width

    fig = pyplot.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])

    all_h = {}
    objs = {}
    for name in rect_pos:
        try:
            objs[name] = fake_neo(name)
        except:
            objs[name] = fake_classes[name]()
        all_h[name] = get_rect_height(name, objs[name])
        
        
    # update references to include dummy classes
        objs['Block'] = Block_Enhanced()

    # draw connections
    color = ['c', 'm', 'y', 'k']
    alpha = [1., 1., 0.3, 0.6]
    for name, pos in rect_pos.items():
        obj = objs[name]
        relationships = [getattr(obj, '_single_child_objects', []),
                         getattr(obj, '_multi_child_objects', []),
                         getattr(obj, '_child_properties', []),
                         getattr(obj, '_ignorant_child_objects', [])]

        for r in range(4):
            for ch_name in relationships[r]:
                if ch_name not in rect_pos:
                    continue
                x1, y1 = calc_coordinates(rect_pos[ch_name], all_h[ch_name])
                x2, y2 = calc_coordinates(pos, all_h[name])

                if r in [0, 3]:
                    x2 += rect_width
                    connectionstyle = "arc3,rad=-0.1"
                elif y2 >= y1:
                    connectionstyle = "arc3,rad=0.7"
                else:
                    connectionstyle = "arc3,rad=-0.7"
                    
                if ch_name == name:
                    x = (x1+x2)/2
                    y = (y1+y2)/2 +0.6
                    draw_circ(ax,1,x,y,310,270,color_='c')
                    continue
                annotate(ax=ax, coord1=(x1, y1), coord2=(x2, y2),
                         connectionstyle=connectionstyle,
                         color=color[r], alpha=alpha[r])

    # draw boxes
    for name, pos in rect_pos.items():
        htotal = all_h[name]
        obj = objs[name]
        allrelationship = (list(getattr(obj, '_child_containers', []))
                           + list(getattr(obj, '_multi_parent_containers', [])))

        rect = Rectangle(pos, rect_width, htotal,
                         facecolor='w', edgecolor='k', linewidth=2.)
        ax.add_patch(rect)

        # title green
        pos2 = pos[0], pos[1] + htotal - line_heigth * 1.5
        rect = Rectangle(pos2, rect_width, line_heigth * 1.5,
                         facecolor='g', edgecolor='k', alpha=.5, linewidth=2.)
        ax.add_patch(rect)

        # single relationship
        relationship = getattr(obj, '_single_child_objects', [])
        pos2 = pos[1] + htotal - line_heigth * (1.5 + len(relationship))
        rect_height = len(relationship) * line_heigth

        rect = Rectangle((pos[0], pos2), rect_width, rect_height,
                         facecolor='c', edgecolor='k', alpha=.5)
        ax.add_patch(rect)

        # multi relationship
        relationship = (list(getattr(obj, '_multi_child_objects', []))
                        + list(getattr(obj, '_multi_parent_containers', [])))
        pos2 = (pos[1] + htotal - line_heigth * (1.5 + len(relationship))
                - rect_height)
        rect_height = len(relationship) * line_heigth

        rect = Rectangle((pos[0], pos2), rect_width, rect_height,
                         facecolor='m', edgecolor='k', alpha=.5)
        ax.add_patch(rect)

        # necessary attr
        pos2 = (pos[1] + htotal
                - line_heigth * (1.5 + len(allrelationship) + len(obj._necessary_attrs)))
        rect = Rectangle((pos[0], pos2), rect_width,
                         line_heigth * len(obj._necessary_attrs),
                         facecolor='r', edgecolor='k', alpha=.5)
        ax.add_patch(rect)

        # name
        if hasattr(obj, '_quantity_attr'):
            post = '* '
        else:
            post = ''
        name = name.replace('_', '\\_')
        ax.text(pos[0] + rect_width / 2., pos[1] + htotal - line_heigth * 1.5 / 2.,
                name + post,
                horizontalalignment='center', verticalalignment='center',
                fontsize=fontsize + 2,
                fontproperties=FontProperties(weight='bold'),
                )

        # relationship
        for i, relat in enumerate(allrelationship):
            relat = relat.replace('_', '\\_')
            ax.text(pos[0] + left_text_shift, pos[1] + htotal - line_heigth * (i + 2),
                    relat + ': list',
                    horizontalalignment='left', verticalalignment='center',
                    fontsize=fontsize,
                    )
        # attributes
        for i, attr in enumerate(obj._all_attrs):
            attrname, attrtype = attr[0], attr[1]
            t1 = attrname
            if (hasattr(obj, '_quantity_attr')
                    and obj._quantity_attr == attrname):
                t1 = attrname + '(object itself)'
            else:
                t1 = attrname

            if attrtype == pq.Quantity:
                if attr[2] == 0:
                    t2 = 'Quantity scalar'
                else:
                    t2 = 'Quantity %dD' % attr[2]
            elif attrtype == np.ndarray:
                t2 = "np.ndarray %dD dt='%s'" % (attr[2], attr[3].kind)
            elif attrtype == datetime:
                t2 = 'datetime'
            else:
                t2 = attrtype.__name__

            t = t1 + ' :  ' + t2
            t = t.replace('_', '\\_')
            ax.text(pos[0] + left_text_shift,
                    pos[1] + htotal - line_heigth * (i + len(allrelationship) + 2),
                    t,
                    horizontalalignment='left', verticalalignment='center',
                    fontsize=fontsize,
                    )

    xlim, ylim = figsize
    ax.set_xlim(0, xlim)
    ax.set_ylim(0, ylim)

    ax.set_xticks([])
    ax.set_yticks([])
    fig.savefig(filename, bbox_inches='tight',  dpi=dpi)


def generate_diagram_simple(output_filename):
    figsize = (18, 13)
    rw = rect_width = 3.
    bf = blank_fact = 1.5
    rect_pos = {'Block': (.5 + rw * bf * 0, 6.0),
                'Segment': (.5 + rw * bf * 1.5, 4.4),
                'Event': (.5 + rw * bf * 3, 3.0),
                'Epoch': (.5 + rw * bf * 3, 1.0),
                'Group': (.5 + rw * bf * 1.0, 9.4),
                'View': (.5 + rw * bf * 1.8, 9.4),
                'SpikeTrain': (.5 + rw * bf * 3, 5.0),
                'IrregularlySampledSignal': (.5 + rw * bf * 3, 8.1),
                'AnalogSignal': (.5 + rw * bf * 3, 10.0),
                }


    # set parameters for saving latex compatible pgf plots
    pgf_with_custom_preamble = {
        "font.family": "serif",  # use serif/main font for text elements
        "text.usetex": True,  # use inline math for ticks
        "pgf.rcfonts": False,  # don't setup fonts from rc parameters
        "pgf.preamble": [
            "\\usepackage{units}",  # load additional packages
            "\\usepackage{metalogo}",
            "\\usepackage{unicode-math}",  # unicode math setup
            r"\setmathfont{xits-math.otf}",
            r"\setmainfont{DejaVu Serif}",  # serif font via preamble
        ]
    }
    matplotlib.rcParams.update(pgf_with_custom_preamble)
    generate_diagram(output_filename, rect_pos, rect_width, figsize)

if __name__ == '__main__':
    generate_diagram_simple(sys.argv[1])
    # pyplot.show()
