# -*- coding: utf-8 -*-

from collections import Counter
from pymongo import *
from mpl_toolkits.basemap import Basemap

import ast
import matplotlib.pyplot as plt
import numpy as np
import wolframalpha


"""
chicagobus.py -- a number of methods working with a mongodb of Chicago bus route
data to display various aggregates of the data.

Created on Wed Jan 08 23:27:37 2014

@author: James Barney
"""

chicago_client = MongoClient()
wolfram_client = wolframalpha.Client('8XR347-UXW4WJP9EX') #this should obviously not be plaintext if distributed


db = chicago_client.chicago_bus

bus_stops_collection = db.chicago_bus_collection
daily_routes_collection = db.daily_routes_collection


def stops_on_route(route):
    """
    returns the other stops on the route associated with the given route
    """
    stops_list = []
    for stop in bus_stops_collection.find():
        try:
            if route in stop['routes'].split(','):
                stops_list.append(stop)
            elif str(route) in stop['routes'].split(','):
                stops_list.append(stop)
        except:
            if route == stop['routes']:
                stops_list.append(stop)
        
    return stops_list
        

def all_bus_routes():
    """
    list of all bus routes in the bus_stops_collection from every stop
    """
    bus_routes = []
    
    for stop in bus_stops_collection.find():
        try:
            for route in stop["routes"].split(','):
                bus_routes.append( str(route).strip() )
        except:
            bus_routes.append( str(stop["routes"]).strip() )
                
    return bus_routes
    
    
def most_routes(n=1):
    """
    returns the n most-common route numbers in Chicago
    @param n: specify number of routes returned in descending order
    """
    
    routes = all_bus_routes()    
    route_counter = Counter()
    
    for word in routes:
        route_counter[word] += 1
        
    return route_counter.most_common(n)
    
    
def unique_routes():
    """
    returns the unique set of routes for Chicago
    """    
    unique_routes = set(all_bus_routes())
    try:
        unique_routes.remove('')
    except:
        print "no gap found"
    
    return unique_routes
 
    
def freq_stop():    
    """
    returns the stop with the most routes that pass through it 
    """
    
    biggest_stop = 0
    most_freq = None
    
    for stop in bus_stops_collection.find():
        try:
            try:
                if len(map(int, stop["routes"].split(',')) ) > biggest_stop:
                    biggest_stop = len(map(int, stop["routes"].split(',')) )
                    most_freq = stop
            except:
                if len(map(str, stop["routes"].split(',')) ) > biggest_stop:
                    biggest_stop = len(map(str, stop["routes"].split(',')) )
                    most_freq = stop
        except:
            #ints won't be the most frequented by nature
            continue
        
    return most_freq    
    

def stop_id(stop_id):
    """
    returns the stop of the given stop id
    """
    return bus_stops_collection.find({"stop_id": stop_id})
    
def wolfram_gps_query(given_stop):
    """
    does wolfram alpha stuff using the given stop's gps coordinates
    """   
    
    location = ast.literal_eval(given_stop["location"])
    latti = location[0]
    longi = -1 * location[1]
    
    print latti, longi
    
    results = wolfram_client.query(str(latti) + ' deg N, ' + str(longi) + ' deg W')
    
    print results


def route_map(given_route):
    """  
    *semi-functional
    returns a map of the given route using stops' GPS coordinates
    """ 
    route_locations = []
    x = []
    y = []

    for stop in bus_stops_collection.find({"routes": given_route}):
        route_locations.append(ast.literal_eval(stop["location"]))
    
    for loc in route_locations:
        x.append(float(loc[1]) )
        y.append(float(loc[0]) )

    m = Basemap(llcrnrlon=-88.0696,llcrnrlat=41.8428,urcrnrlon=-87.4502,urcrnrlat=42.5326,
                projection='merc',resolution='h')
    # draw coastlines.
    m.drawcoastlines()
    m.drawstates()
    #m.fillcontinents()

    m.drawmapboundary(fill_color='white')
    # fill continents, set lake color same as ocean color.
    x1, y1 = m(x,y)
    #print x1,y1
    m.scatter(y1,x1,c='r',marker="o",cmap=cm.jet,alpha=1.0)
    plt.title("Map of Chicago Bus Stops:\nRoute " + str(given_route))
    plt.show() 
    

def passenger_on_off(given_stop):
    """
    returns the average passenger change from a given stop
    """
    return given_stop['boardings'] - given_stop['alightings']
    
    
def stop_busyness(given_stop):
    """
    returns the given route's "busyness", Boardings + Alightings
    """
    return given_stop['boardings'] + given_stop['alightings']
    
    
def max_passenger_flux(route=None, sign='positive', daytype='Weekday'):
    """
    finds the stop with the largest change in the number of people using the bus
    
    @param sign: 'positive' indicates people board but don't alight. 'negative' indicates people alight but don't board.
    @param daytype: 'Weekday' for week day routes. 'Weekend' for weekend routes 
    (WEEKEND ROUTES DON'T SHOW UP FROM CHICAGO'S DATA)
    
    """
    
    if sign == 'positive':  
        max_flux = 0
        max_flux_stop = None
        for stop in bus_stops_collection.find({"daytype": daytype}):
            flux = stop['boardings'] - stop['alightings']
            if flux > max_flux:
                max_flux = flux
                max_flux_stop = stop
            else:
                continue
        return max_flux_stop
    elif sign == 'negative':
        min_flux = 0
        min_flux_stop = None
        for stop in bus_stops_collection.find({"daytype": daytype}):
            flux = stop['boardings'] - stop['alightings']
            if flux < min_flux:
                min_flux = flux
                min_flux_stop = stop
            else:
                continue
        return min_flux_stop
        
        
def avg_flux(given_route):
    """
    returns a given route's average passenger flux over all stops in the route
    """
    sum_flux = []

    for stop in stops_on_route(given_route):
        sum_flux.append(passenger_on_off(stop))
        
    return np.average(sum_flux)
    
                
def same_street(given_stop):
    """
    finds stops on the same street as a given stop
    """
    
    street = given_stop["on_street"]
    
    longroad = []
    
    for stop in bus_stops_collection.find({"on_street": street}):
        longroad.append(stop)
    
    return longroad
    
    
def transfer(given_stop):
    """
    returns the routes you can transfer from a given stop.
    """
    try:
        return given_stop["routes"].split(',')
    except:
        return str(given_stop["routes"])
        
        
def route_annotations(given_route, anno_div=0.0075):
    """
    returns more detailed information about each annotation in the given 
    route's scatter plot, where 
    
    @param anno_div: divisor of average flux of figure. Determines annotation cut-off. Default 0.0075. (ex: 4.3/0.0075 = 573.333)

    """
    annotations = []
    avg = avg_flux(given_route)
    
    for stop in stops_on_route(given_route):
        if abs(passenger_on_off(stop)) > abs(avg/anno_div):
            annotations.append(stop)
            
    return annotations
    
    
def graph_flux(given_route, save=False, show_boardings=True, show_alightings=True, annotate=True, anno_div=0.0075):
    """
    graphs the passenger change for each stop on a given route
    
    @param save: saves the output figure to a .pdf image. Default=False
    @param show_alightings: shows alightings on figure. Default=True
    @param show_boardings: show boardings on figure. Default=True
    @param annotate: annotate outliers on figure. Default=True
    @param anno_div: divisor of average flux of figure. Determines annotation cut-off. Default 0.0075. (ex: 4.3/0.0075 = 573.333)
    """
    stops = []
    diff = []
    board = []
    alight = []
    annotations = []
    i = 1
    
    for stop in stops_on_route(given_route or str(given_route)):
        stops.append(i)
        avg = avg_flux(given_route)
        flux = passenger_on_off(stop)
        diff.append(flux)
        if annotate and (flux > abs(avg/anno_div) or flux < -1*abs(avg/anno_div)):
            annotations.append((stop['stop_id'], i, flux))
           
        i += 1
        
        if show_boardings:
            board.append(stop['boardings'])
        if show_alightings:
            alight.append(stop['alightings']*-1)
        
    flux = plt.figure()
    
    if show_boardings:
        board_plot = plt.scatter(stops, board, marker='x', color='g')
    if show_alightings:
        alight_plot = plt.scatter(stops, alight, marker='x', color='b')
        
    diff_plot = plt.scatter(stops, diff, marker='.', color='r')
      
    if annotate:
        for note in annotations:
            label = note[0]
            x = note[1]
            y = note[2]
    
            plt.annotate(
                label, 
                xy = (x, y), xytext = (-20, 20),
                textcoords = 'offset points', ha = 'right', va = 'bottom',
                bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
                arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0') )        
        
    plt.title("Passenger Flux of Route " + str(given_route))
    plt.ylabel("Change in Passengers at Stop (Flux)")
    plt.xlabel("Stop")
    plt.legend((diff_plot,board_plot,alight_plot),
           ('Difference','Boardings','Alightings'),
           scatterpoints=1,
           loc='lower left',
           ncol=1,
           fontsize=8)
        
    if save:
        flux.savefig(str(given_route) + '.pdf', dpi=flux.dpi)
        plt.close()
    else:
        plt.show()
        
    
def all_graph_flux(show_boardings=True, show_alightings=True):
    """
    Saves the figures from each route showing Boardings vs. Alightings
    """
    for stop in unique_routes():
        graph_flux(stop, True)
    
    
    
####################### Daily routes info below #########################

def unique_daily_routes():
    """
    returns a set of all the unique routes in the daily routes collection
    """
    unique = set()
    
    for route in daily_routes_collection.find():
        unique.add(str(route['route']) )
        
    return unique
    
def route_rides(given_route):
    """
    returns a list of the date and ride number for a given route
    """
    pass
    
    
    
    
    