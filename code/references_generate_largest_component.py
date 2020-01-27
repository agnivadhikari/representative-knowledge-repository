from __future__ import division
import os
import commands
import re
import regex
#from graph_tool.all import *
import json
import cairo
import numpy as np
#import matplotlib.pyplot as plt
#import networkx as nx
import copy
import pickle
import operator
from operator import itemgetter, attrgetter
import pprint
import logging
logging.basicConfig(filename='myProgramLog.txt', level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(filename='myProgramLog.txt', level=logging.WARN, format=' %(asctime)s - %(levelname)s - %(message)s')
import StringIO

def process_html_files():
  beginning_year = 2013
  beginning_range = 5
  all_unique_conference_names = []
  yearly_conference_names_dict = {}
  yearly_filename_conference_names_dict = {}  
  yearly_array_dict = {}
  yearly_graph_dict = {}
  filename_conference_names_dict = {}
  yearly_conference_name_count = {}
  conference_name_statistics_list = []
  connected_components_dict = {}
  temp_weighted_graph_dict = {}
  for i in range(beginning_range):
    #directory = 'downloaded_conference_names/'+str(beginning_year+i)+'/'
    directory = 'downloaded_references/'+str(beginning_year+i)+'/'
    year_str = str(beginning_year+i)
    filenames = os.listdir(directory)
    IEEE_filename_conference_names_dict = {}
    weighted_graph_dict = {}
    unique_edge_tuple_list = []
    unique_vertex_list = []
    unique_taxonomy_list = []
    unique_conference_names = []
    for filename in filenames:
      #print '\n=========================== Processing '+filename+'============================\n'
      with open(directory+filename,"rU") as content_file:
        text = content_file.read()
      #Gets the list of conference_names for the particular paper
      conference_names_list = get_conferences(directory+filename)
      if conference_names_list == []:
        continue
      # Populate the filename_conference_names_dict 
      filename_conference_names_dict[filename+' '+year_str] = conference_names_list
  """
  print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
  pprint.pprint(filename_conference_names_dict)
  print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
  """
  # Gets the list of unique conference conference_names for all the years
  all_unique_conference_names = generate_conference_name_list(filename_conference_names_dict)
  print "Number of Conferences:",len(all_unique_conference_names)
  all_unique_conference_names.sort()
  pprint.pprint(all_unique_conference_names)
  print 'unique conference completed'
  weighted_graph_dict = create_edge_list_with_conference_names(filename_conference_names_dict)
  conference_name_vertices_dict = {}
  for conference_name in all_unique_conference_names:
    vertices = []    
    for vertex in filename_conference_names_dict:
      if conference_name in filename_conference_names_dict[vertex]:
        if vertex not in vertices:
          vertices.append(vertex)
    conference_name_vertices_dict[conference_name] = vertices
  for k in sorted(conference_name_vertices_dict, key=lambda k: len(conference_name_vertices_dict[k]), reverse=True): # Sort the dictionary based on length of the vertices list    
    conference_name_vertices_dict[k].sort(key=lambda k:int(k.split()[-1])) # Sort the vertices list based on the year substring in each vertices list of each conference_name
    yearly_conference_name_count = {}
    for i in range(beginning_range):  
      year_str = str(beginning_year+i)
      yearwise_count = 0
      for item in conference_name_vertices_dict[k]:
        if item.endswith(year_str):
          yearwise_count=yearwise_count+1
      yearly_conference_name_count[year_str]=yearwise_count
    sd = np.std(yearly_conference_name_count.values())
    priority = get_priority(k, filename_conference_names_dict, conference_name_vertices_dict)
    #conference_name_statistics_list.append({"conference_name":k, "2013":yearly_conference_name_count['2013'], "2014":yearly_conference_name_count['2014'], "2015":yearly_conference_name_count['2015'],"2016":yearly_conference_name_count['2016'], "2017":yearly_conference_name_count['2017'],"total":len(conference_name_vertices_dict[k]), "priority":priority, "sd":sd})
    #conference_name_statistics_list.append({"conference_name":k, "2013":yearly_conference_name_count['2013'], "2014":yearly_conference_name_count['2014'], "2015":yearly_conference_name_count['2015'],"2016":yearly_conference_name_count['2016'], "2017":yearly_conference_name_count['2017'],"2018":yearly_conference_name_count['2018'],"total":len(conference_name_vertices_dict[k]), "priority":priority, "sd":sd})
    conference_name_statistics_list.append({"conference_name":k, "2017":yearly_conference_name_count['2017'],"total":len(conference_name_vertices_dict[k]), "priority":priority, "sd":sd})
  sorted_on_specific_parameter = sorted(sorted(conference_name_statistics_list, key=lambda k: (k['priority'])),key=lambda k: (k['total']), reverse=True)
  #logging.debug('starting of main portion')
  conn_conference_names_index = 0
  conn_conference_names_set_dict = {}
  conn_conference_names_vertices_set_dict = {}
  conn_conference_names_temp_dict_len_dict = {}
  conn_conference_names_iteration_len_dict = {}
  list_of_largest_component_size = []
  total_vertices_count = len(filename_conference_names_dict.keys())
  all_vertices_set = set()
  for vertex in filename_conference_names_dict.keys():
    all_vertices_set.add(vertex)
  logging.debug('Total vertices count: '+str(total_vertices_count))
  print 'Total vertices count: '+str(total_vertices_count)
  total_obtained_vertices_count = 0

  """     Greedy algo  """"""""""""
  ---------------------------------
  
  
  print "{0:<60s} {1:>8d} {2:>8d} {3:>8d} {4:>8d} {5:>8d} {6:>8s} {7:>10s}".format('conference_name', 2013, 2014, 2015, 2016, 2017, 'Total', 'Std.Dev.')
  print "----------------------------------------------------------------------------------------------------------------------"
  for item in sorted_on_specific_parameter:
    print "{0:<60s} {1:>8d} {2:>8d} {3:>8d} {4:>8d} {5:>8d} {6:>8d} {7:>10.2f}".format(item["conference_name"], item["2013"], item["2014"], item["2015"], item["2016"], item["2017"], item["total"], item["sd"])

  conference_gist_set = set()
  current_vertices_set = set()
  for item in sorted_on_specific_parameter:
    current_conference_name = item["conference_name"]
    current_vertices = conference_name_vertices_dict[current_conference_name]
    
    for element in current_vertices:
      current_vertices_set.add(element)
    conference_gist_set.add(current_conference_name)
    print('Current vertices length: '+str(len(current_vertices))+', Count of remaining vertices: '+str(len(all_vertices_set-current_vertices_set)))
    if (current_vertices_set==all_vertices_set):
      print 'Run complete'
      break

  print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
  pprint.pprint(conference_gist_set)
  print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
  pprint.pprint(current_vertices_set)
  print '############################################'
  """


  while get_count_conn_conference_names_vertices_set_dict(conn_conference_names_vertices_set_dict) < total_vertices_count:
    conn_conference_names_index+=1
    logging.debug('while get_count_conn_conference_names_vertices_set_dict loop: conn_conference_names_index: '+str(conn_conference_names_index))
    (conn_conference_names_set,conn_conference_names_vertices_set,conn_conference_names_temp_dict_len_dict,conn_conference_names_iteration_len_dict,list_of_largest_component_size) = update_conference_names_gist_set(filename_conference_names_dict,conference_name_vertices_dict,sorted_on_specific_parameter,conn_conference_names_set_dict,conn_conference_names_vertices_set_dict,conn_conference_names_temp_dict_len_dict,conn_conference_names_iteration_len_dict,list_of_largest_component_size)
    conn_conference_names_set_dict[conn_conference_names_index] = conn_conference_names_set
    conn_conference_names_vertices_set_dict[conn_conference_names_index] = conn_conference_names_vertices_set
    logging.debug('Run completed for component: '+str(conn_conference_names_index))
    logging.debug('The set of conference_names for this component is: '+str(conn_conference_names_set))
    logging.debug('The set of vertices for this component is: '+str(conn_conference_names_vertices_set))
    print 'The total number of vertices obtained for component: '+str(conn_conference_names_index)+' is '+ str(get_count_conn_conference_names_vertices_set_dict(conn_conference_names_vertices_set_dict))
  pprint.pprint(conn_conference_names_set_dict) 
  print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  total_set_length = 0
  gist_vertices_set = set()
  for index in conn_conference_names_set_dict:
    conference_names_set = conn_conference_names_set_dict[index]
    total_set_length = total_set_length+len(conference_names_set)
    for conference_name in conference_names_set:
      vertices_list = conference_name_vertices_dict[conference_name]
      for vertex in vertices_list:
	gist_vertices_set.add(vertex)
    s = StringIO.StringIO()
    pprint.pprint(all_vertices_set - gist_vertices_set,s)
    logging.debug('Remaining vertices after index: '+str(index)+' is '+s.getvalue())
    pprint.pprint('Remaining vertices after index: '+str(index)+' is '+s.getvalue())

  print 'Length of minimum spanning set: '+str(total_set_length)
  print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  print 'Statistics of temporary dictionary length for each conference_name in minimum spanning set of conference_names'
  temp_dict_iteration_len_list = []
  for item in conn_conference_names_temp_dict_len_dict.items():
    conference_name = item[0]
    temp_dict_len = conn_conference_names_temp_dict_len_dict[conference_name]
    iteration_len = conn_conference_names_iteration_len_dict[conference_name]
    list_item = (conference_name, temp_dict_len)
    temp_dict_iteration_len_list.append(list_item)
  pprint.pprint(temp_dict_iteration_len_list)
  print 'list_of_largest_component_size'
  pprint.pprint(list_of_largest_component_size)

def get_conferences(full_filename):
  #print 'Hello World'
  """
  strings_to_remove = ['',
         '1991.',
         '1995',
         '1995.',
         '1997.',
         '2000.',
         '2001.',
         '2007.',
         '2009.',
         '2011.',
         '2012.',
         '2013',
         '2015',
         '1992.',
         '1999.',
         '2006.',
         '2013.',
         '2008.',
         '1996.']
  """
  conference_names = []
  filtered_conference_name = ''
  number_of_conference_names = 0
  with open(full_filename,"rU") as content_file:
    for line in content_file.readlines():
      number_of_conference_names += 1
      #print line
      #logging.debug(line)
      first_time_split = 'N/A'
      if '", ' in line:
        first_time_split = line.split('", ')
      elif '" in ' in line:
        first_time_split = line.split('" in ')
      elif '," ' in line:
        first_time_split = line.split('," ')
      elif "', " in line:
        first_time_split = line.split("', ")
        #logging.debug('Working!!!')
      elif '". ' in line:
        first_time_split = line.split('". ')
      elif '" ' in line:
        first_time_split = line.split('" ')
      else: 
        #logging.debug('Noooooo..... ')
        continue
      if first_time_split != 'N/A':
        #logging.debug(first_time_split[1])
        conference_name = first_time_split[1].split(',')        
        if conference_name[0].startswith('in '):
          conference_name[0]=conference_name[0][3:]              
        filtered_conference_name = filter_conference_name(conference_name[0])
          #logging.debug('get_conferences filtered_conference_name: '+filtered_conference_name)
        if filtered_conference_name not in conference_names:
          conference_names.append(filtered_conference_name)
        """
          if conference_name[0] not in strings_to_remove:      
            if conference_name[0].startswith('in '):
              conference_name[0]=conference_name[0][3:]              
            filtered_conference_name = filter_conference_name(conference_name[0])
            logging.debug('get_conferences filtered_conference_name: '+filtered_conference_name)
            conference_names.append(filtered_conference_name)
        """     

  """
  print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
  pprint.pprint(conference_names)
  print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
  """
  logging.debug('Filename: '+full_filename+', number of conference_names: '+str(number_of_conference_names)+', conferences: '+str(len(conference_names)))
  return conference_names

def filter_conference_name(name_of_conference):
  strings_to_remove_list = ['in: ',
    'proceedings of the ',
    'proceeding of the ',
    'procedings of the ',
    'procceddings of ',
    'proceedings of ',
    'proceeding of ',
    'procedings of ',
    'proceedings ',
    'proc. of ',
    'proc. of ',
    'proc of ',
    'proc.of ',
    'proc. ',
    'proc.',
    'proc ']

  alias_dict = {
  'annual international conference of the ieee engineering in medicine and biology society':'annual international conference of the ieee embs',
  'applied physics letters':'appl. phys. lett.',
  'flow measurement and instrumentation':'flow meas. instrum.',
  'flow. meas. instrum.':'flow meas. instrum.',
  'ieee imtc':'ieee international instrumentation and measurement technology conference',
  'ieee conference on instrumentation and measurement technology':'ieee international instrumentation and measurement technology conference',
  'ieee instrumentation and measurement technology conference':'ieee international instrumentation and measurement technology conference',
  'ieee instrumentation and measurement technology conference (imtc)':'ieee international instrumentation and measurement technology conference',
  'ieee international instrumentation and measurement technology conference (i':'ieee international instrumentation and measurement technology conference',
  'ieee international instrumentation and measurement technology conference (imtc)':'ieee international instrumentation and measurement technology conference',
  'ieee international instrumentation and measurement technology conference':'ieee international instrumentation and measurement technology conference',
  'instrumentation and measurement technology conference':'ieee international instrumentation and measurement technology conference',
  'instrumentation and measurement technology conference (iieee international':'ieee international instrumentation and measurement technology conference',
  'instrumentation and measurement technology conference (iieee international. ieee':'ieee international instrumentation and measurement technology conference',
  'instrumentation and measurement technology conference (imtc)':'ieee international instrumentation and measurement technology conference',
  'ieee international instrumentation and measurement technology conference proceedings':'ieee international instrumentation and measurement technology conference',
  'ieee international instrumentation and measurement technology conference (iproceedings':'ieee international instrumentation and measurement technology conference',
  'instrumentation and measurement technology conference proceedings imtc':'ieee international instrumentation and measurement technology conference',
  'ieee instrumentation & measurement magazine':'ieee instru meas mag',
  'ieee instrumentation and measurement magazine':'ieee instru meas mag',
  'ieee journal of solid-state circuits':'ieee j. solid-state circuits',
  'ieee t. instrumentation and measurement':'ieee trans. instrum. meas.',
  'ieee trans. instr. meas.':'ieee trans. instrum. meas.',
  'ieee trans. instrumentation and measurement':'ieee trans. instrum. meas.',
  'ieee trans. on instrum. and measur.':'ieee trans. instrum. meas.',
  'ieee trans. on instrumentation and measurement':'ieee trans. instrum. meas.',
  'ieee transactions on instrumentation and measurement':'ieee trans. instrum. meas.',
  'instrumentation and measurement ieee transactions on':'ieee trans. instrum. meas.',
  'ieee trans. on industry applications':'ieee trans. ind. appl.',
  'ieee trans. microwave theory and techniques':'ieee trans. microw. theory tech.',
  'ieee transactions on microwave theory and techniques':'ieee trans. microw. theory tech.',
  'ieee trans. microw. theory techn.':'ieee trans. microw. theory tech.',
  'ieee trans. signal processing':'ieee trans. signal process.',
  'ieee transactions on image processing':'ieee trans. image process.',
  'ieee transactions on nuclear science':'ieee trans. nucl. sci.',
  'ieee transactions on pattern analysis and machine intelligence':'ieee trans. pattern anal. machine intell.',
  'industrial electronics ieee transactions on':'ieee transactions on industrial electronics',
  'international journal of computer vision':'int. j. comput. vis.',
  'mechanical systems and signal processing':'mech. syst. and signal process',
  'power delivery ieee transactions on':'ieee transactions on power delivery',
  'precision clock synchronization for measurement control and communication (ispcs) international ieee symposium on':'ieee ispcs',
  'sens. actuators a':'sensors and actuators a: physical',
  'sensor actuat. a-phys':'sensors and actuators a: physical',
  'sensors and actuators b':'sensors and actuators b: chemical',
  'sensors and actuators b-chemical vol':'sensors and actuators b: chemical',
  'sensors actuators b chem.':'sensors and actuators b: chemical',
  'volume':'vol',
  'measurement science & technology':'measurement science and technology',
  }
  
  #name_of_conference = re.sub('^Path=', '', name_of_conference)
  #logging.debug('name_of_conference: '+name_of_conference)
  name_of_conference = name_of_conference.lower()
  for string_to_remove in strings_to_remove_list:
    name_of_conference=re.sub('^'+string_to_remove, '', name_of_conference)
  name_of_conference = re.sub('\d\d*\w*\W* ', '', name_of_conference) # Removes any string that starts with a number, even within the conference name, but not at the end.
  name_of_conference = re.sub('\W*\d\d*\W*$', '', name_of_conference) # Removes numeric string from the end.
  name_of_conference = re.sub('\d\d*\W*', '', name_of_conference) # Removes single numeric string.  
  name_of_conference = re.sub('&amp;', '&', name_of_conference) # Removes  &amp; with & placed anywhere in the conference name.

  #logging.debug('After numeric filter - name_of_conference: '+name_of_conference)
  if name_of_conference in alias_dict:
    name_of_conference = alias_dict[name_of_conference]
  return name_of_conference
def get_conference_name_index(conference_name, sorted_on_specific_parameter):
  i=0
  for item in sorted_on_specific_parameter:
    i+=1
    if item["conference_name"]==conference_name:
      break
  return i
def update_conference_names_gist_set(filename_conference_names_dict,conference_name_vertices_dict,sorted_on_specific_parameter,conn_conference_names_set_dict,conn_conference_names_vertices_set_dict,conn_conference_names_temp_dict_len_dict,conn_conference_names_iteration_len_dict, list_of_largest_component_size):
  #logging.debug('starting of update_conference_names_gist_set')
  continue_loop = True
  current_cumulative_conference_names_set = set()
  current_cumulative_vertices_set = set()
  previous_item = None
  temp_vertices_dict = {}
  temp_vertices_len_dict = {}
  item_updated_in_between = False
  no_of_iterations_performed = 0
  actual_no_of_iterations_performed = 0
  previous_selected_conference_name = None
  while(continue_loop):
    #logging.debug('starting of while(continue_loop)')
    continue_loop = False
    item_updated_in_between = False
    for item in sorted_on_specific_parameter:
      #logging.debug('starting of for item in sorted_on_specific_parameter')
      no_of_iterations_performed += 1
      conference_name = item["conference_name"]
      #logging.debug('current conference_name: '+conference_name)
      #logging.debug('no_of_iterations_performed: '+str(no_of_iterations_performed))
      vertices_set = set(conference_name_vertices_dict[conference_name])
      conn_vertices_set = get_conn_vertices_set(conn_conference_names_vertices_set_dict)
      if not current_cumulative_conference_names_set:
	if check_conference_name_in_gist_set(conference_name, conn_conference_names_set_dict) or vertices_set.issubset(conn_vertices_set.union(current_cumulative_vertices_set)):
	  #logging.debug('conference_name already in gist set or vertices are subset, so skip: '+conference_name)
	  continue
	else:
          current_cumulative_conference_names_set.add(conference_name)
	  temp_list = []	
	  temp_list = conference_name_vertices_dict[conference_name]	
	  for temp_item in temp_list:
	    current_cumulative_vertices_set.add(temp_item)
	  #logging.debug('conference_name added in empty set: '+conference_name)
          list_of_largest_component_size.append(len(conn_vertices_set.union(current_cumulative_vertices_set)))
	  conn_conference_names_temp_dict_len_dict[conference_name] = len(temp_vertices_len_dict)
	  #logging.debug('conference_name: '+conference_name+', length of temp_vertices_len_dict: '+str(len(temp_vertices_len_dict)))
	  actual_no_of_iterations_performed = get_conference_name_index(conference_name,sorted_on_specific_parameter)
	  conn_conference_names_iteration_len_dict[conference_name] = actual_no_of_iterations_performed
	  #logging.debug('conference_name: '+conference_name+', No. of iterations performed: '+str(actual_no_of_iterations_performed))
	  previous_selected_conference_name = conference_name
	  continue

      if conference_name in current_cumulative_conference_names_set or check_conference_name_in_gist_set(conference_name, conn_conference_names_set_dict):
        #logging.debug('conference_name skipped as already added: '+conference_name)
        continue

      if vertices_set.issubset(conn_vertices_set.union(current_cumulative_vertices_set)):
        #logging.debug('conference_name skipped as subset: '+conference_name)	
	continue
      if vertices_set.isdisjoint(conn_vertices_set.union(current_cumulative_vertices_set)):
        #logging.debug('conference_name skipped as disjoint: '+conference_name)
	continue
      temp_vertices_dict[conference_name] = vertices_set - current_cumulative_vertices_set
      temp_vertices_len_dict[conference_name] = len(temp_vertices_dict[conference_name])
      #logging.debug('conference_name in temp dict: '+conference_name+', number of augmented nodes: '+str(len(temp_vertices_dict[conference_name])))
      if previous_item is None:
	#logging.debug('previous_item is None: ')
	previous_item = item
	#logging.debug('Now the previous_item is: '+previous_item["conference_name"]+', count: '+str(previous_item["total"]))
	continue	
      if (item["total"] < temp_vertices_len_dict[previous_item["conference_name"]]):
	#logging.debug('item count is less than number of augmented vertices - stop condition satisfied\nconference_name: '+item["conference_name"]+'\tcount: '+str(item["total"])+'\nprevious conference_name: '+previous_item["conference_name"]+'\tnumber of augmented vertices: '+str(temp_vertices_len_dict[previous_item["conference_name"]]))	      
	s = StringIO.StringIO()
	pprint.pprint(temp_vertices_len_dict,s)
	#logging.debug('temp_vertices_len_dict: '+s.getvalue())
	max_item = max(temp_vertices_len_dict.iteritems(), key=operator.itemgetter(1))
	#logging.debug('max item: '+str(max_item[0])+', count: '+str(max_item[1]))
	current_cumulative_conference_names_set.add(max_item[0])
        item_updated_in_between = True
	temp_list = []
	temp_list = temp_vertices_dict[max_item[0]]
	for temp_item in temp_list:
	  current_cumulative_vertices_set.add(temp_item)
	conn_conference_names_temp_dict_len_dict[max_item[0]] = len(temp_vertices_len_dict)
	#logging.debug('conference_name: '+max_item[0]+', length of temp_vertices_len_dict: '+str(len(temp_vertices_len_dict)))
	actual_no_of_iterations_performed = get_conference_name_index(max_item[0],sorted_on_specific_parameter) - get_conference_name_index(previous_selected_conference_name,sorted_on_specific_parameter)
	conn_conference_names_iteration_len_dict[max_item[0]] = actual_no_of_iterations_performed
	#logging.debug('conference_name: '+max_item[0]+', No. of iterations performed: '+str(actual_no_of_iterations_performed))
	previous_selected_conference_name = max_item[0]
	temp_vertices_dict = {}
	temp_vertices_len_dict = {}
	previous_item = None
	no_of_iterations_performed = 0
	continue_loop = True
        #logging.debug('conference_name added: '+max_item[0])
        list_of_largest_component_size.append(len(conn_vertices_set.union(current_cumulative_vertices_set)))
	#logging.debug('Break')	      
	break
	  
      else:
	#logging.debug('Just the loop is continued')
	continue
	
    if not item_updated_in_between:
      #logging.debug('After traversing the entire loop')
      s = StringIO.StringIO()
      pprint.pprint(temp_vertices_len_dict,s)
      #logging.debug('temp_vertices_len_dict: '+s.getvalue())
      if not temp_vertices_len_dict:
        #logging.debug('No more elements will be augmented in this run. Stopping the loop.')
        continue_loop = False
        break  
      max_item = max(temp_vertices_len_dict.iteritems(), key=operator.itemgetter(1))
      #logging.debug('max item: '+str(max_item[0])+', count: '+str(max_item[1]))
      current_cumulative_conference_names_set.add(max_item[0])
      temp_list = []
      temp_list = temp_vertices_dict[max_item[0]]
      for temp_item in temp_list:
        current_cumulative_vertices_set.add(temp_item)
      conn_conference_names_temp_dict_len_dict[max_item[0]] = len(temp_vertices_len_dict)
      #logging.debug('conference_name: '+max_item[0]+', length of temp_vertices_len_dict: '+str(len(temp_vertices_len_dict)))
      actual_no_of_iterations_performed = get_conference_name_index(max_item[0],sorted_on_specific_parameter) - get_conference_name_index(previous_selected_conference_name,sorted_on_specific_parameter)
      conn_conference_names_iteration_len_dict[max_item[0]] = actual_no_of_iterations_performed
      #logging.debug('conference_name: '+max_item[0]+', No. of iterations performed: '+str(actual_no_of_iterations_performed))
      previous_selected_conference_name = max_item[0]
      temp_vertices_dict = {}
      temp_vertices_len_dict = {}
      previous_item = None
      no_of_iterations_performed = 0
      continue_loop = True
      #logging.debug('conference_name added: '+max_item[0])
      list_of_largest_component_size.append(len(conn_vertices_set.union(current_cumulative_vertices_set)))
    if len(conn_vertices_set.union(current_cumulative_vertices_set)) == len(filename_conference_names_dict.keys()):
      #logging.debug('All vertices are added!!!')
      break
    
  return (current_cumulative_conference_names_set, current_cumulative_vertices_set,conn_conference_names_temp_dict_len_dict,conn_conference_names_iteration_len_dict,list_of_largest_component_size)

def get_max_item(temp_vertices_len_dict,current_cumulative_conference_names_set,current_cumulative_vertices_set,temp_vertices_dict):
  s = StringIO.StringIO()
  pprint.pprint(temp_vertices_len_dict,s)
  #logging.debug('temp_vertices_dict: '+s.getvalue())
  max_item = max(temp_vertices_len_dict.iteritems(), key=operator.itemgetter(1))
  #logging.debug('max item: '+str(max_item[0])+', count: '+str(max_item[1]))
  current_cumulative_conference_names_set.add(max_item[0])
  #print "conference_name:",max_item[0]
  temp_list = []
  temp_list = temp_vertices_dict[max_item[0]]
  for temp_item in temp_list:
    current_cumulative_vertices_set.add(temp_item)
  temp_vertices_dict = {}
  temp_vertices_len_dict = {}
  previous_item = None
  continue_loop = True
  #logging.debug('conference_name added: '+max_item[0])
  #logging.debug('Break')
def update_max_augmented_vertices():
  temp_vertices_dict = {}
  for key, value in conn_conference_names_vertices_set_dict.items():	  
    temp_vertices_dict[key] = vertices_set - set(value)
  max_item = max(temp_vertices_dict.iteritems(), key=operator.itemgetter(1))
  
def get_conn_vertices_set(conn_conference_names_vertices_set_dict):
  conn_vertices_set = set()
  for key in conn_conference_names_vertices_set_dict:
    conn_vertices_set.update(conn_conference_names_vertices_set_dict[key])
  return conn_vertices_set
def check_conference_name_in_gist_set(conference_name, conn_conference_names_set_dict):
  for key in conn_conference_names_set_dict:
    if conference_name in conn_conference_names_set_dict[key]:
      return True
  return False
def check_conference_name_in_disjoint_conference_names_set(conference_name, disjoint_conference_names_set):
  if conference_name in disjoint_conference_names_set:
    return True
  else:
    return False
def check_conference_name_in_rejected_conference_names_set(conference_name, rejected_conference_names_set):
  if conference_name in rejected_conference_names_set:
    return True
  else:
    return False
def get_count_conn_conference_names_vertices_set_dict(conn_conference_names_vertices_set_dict):
  count = 0
  for key in conn_conference_names_vertices_set_dict.keys():
    count = count + len(conn_conference_names_vertices_set_dict[key])
  return count
def get_priority(conference_name, filename_conference_names_dict, conference_name_vertices_dict):
  priority = 0.00
  priority_list = []
  for key in filename_conference_names_dict.keys():
    conference_name_list = filename_conference_names_dict[key]
    if conference_name in conference_name_list:
      priority_list.append(conference_name_list.index(conference_name))

  priority = sum(priority_list)/len(conference_name_vertices_dict[conference_name])
  return priority

    
  
def get_no_of_common_papers_consecutive_conference_name(previous_conference_name, current_conference_name, conference_name_vertices_dict):
  no_of_common_papers_consecutive_conference_name = 0
  if previous_conference_name =='':
    no_of_common_papers_consecutive_conference_name = len(conference_name_vertices_dict[current_conference_name])
  else:
    previous_list = conference_name_vertices_dict[previous_conference_name]
    current_list = conference_name_vertices_dict[current_conference_name]
    for paper in previous_list:
      if paper in current_list:
        no_of_common_papers_consecutive_conference_name = no_of_common_papers_consecutive_conference_name + 1  
  return no_of_common_papers_consecutive_conference_name
 
def pickle_unique_conference_name_frequency(sorted_on_specific_parameter):
  unique_conference_name_frequency_dict = {}
  for item in sorted_on_specific_parameter:
    conference_name = item["conference_name"]
    frequency = item["total"]
    unique_conference_name_frequency_dict[conference_name] = frequency

  with open('unique_conference_name_frequency_dict.txt', 'wb') as handle:
    pickle.dump(unique_conference_name_frequency_dict, handle)

  #with open('unique_conference_name_frequency_dict.txt', 'rb') as handle:
    #temp_unique_conference_name_frequency_dict = pickle.loads(handle.read())  
  
  #print temp_unique_conference_name_frequency_dict

def create_graph(unique_vertex_list, conference_name_graph_dict):
  unique_edge_tuple_list = conference_name_graph_dict.keys()
  # Creates an undirected Graph object
  g = Graph(directed=False)
  vprop = g.new_vertex_property("string") 
  g.vertex_properties["name"]=vprop 

  eprop = g.new_edge_property("string")
  g.edge_properties["name"]=eprop
  
  # Creates vertex object i.e. node for each author
  for item in unique_vertex_list:
    vertex = g.add_vertex()
    vprop[vertex] = item

  # Creates the edges according to the unique edge tuples
  for edge_tuple in unique_edge_tuple_list:
    edge = g.add_edge(find_vertex(g, vprop, edge_tuple[0])[0],find_vertex(g, vprop, edge_tuple[1])[0])
    eprop[edge] = str(conference_name_graph_dict[edge_tuple]).replace("[", "").replace("]", "").replace("'", "")
    #print edge_tuple,eprop[edge]
  return g

def  generate_conference_name_list(filename_conference_names_dict):
  unique_conference_names = []
  #print filename_conference_names_dict.keys()
  for key in filename_conference_names_dict.keys():
    temp_conference_name_list = filename_conference_names_dict[key]
    for conference_name in temp_conference_name_list:
      if conference_name not in unique_conference_names:
        unique_conference_names.append(conference_name)
  return unique_conference_names

def create_IEEE_filename_conference_names_dict(filename_conference_names_dict, unique_IEEE_taxonomy_list):
  IEEE_filename_conference_names_dict = {}
  
  for filename in filename_conference_names_dict:
    IEEE_temp_conference_names = []
    conference_names = filename_conference_names_dict[filename]
    for conference_name in conference_names:
      if conference_name in unique_IEEE_taxonomy_list:
        IEEE_temp_conference_names.append(conference_name)
    IEEE_filename_conference_names_dict[filename] = IEEE_temp_conference_names
  return IEEE_filename_conference_names_dict

def create_unique_vertex_list(weighted_graph_dict):
  unique_vertex_list = []
  for item in weighted_graph_dict.keys():
    filename1, filename2 = item
    if filename1 not in unique_vertex_list:
      unique_vertex_list.append(filename1)
    if filename2 not in unique_vertex_list:
      unique_vertex_list.append(filename2)
  return unique_vertex_list


def create_edge_list_with_conference_names(filename_conference_names_dict):
  weighted_graph_dict = {}
  unique_weighted_graph_dict = {}
  for item in filename_conference_names_dict.items():
    filename, conference_names = item
    for key in filename_conference_names_dict.keys():
      if key == filename:
        continue
      weighted_graph_dict_key = (filename,key)      
      conference_names_temp = filename_conference_names_dict[key]
      for conference_name in conference_names:
        if conference_name in conference_names_temp:
          if weighted_graph_dict_key in weighted_graph_dict: 
            weighted_graph_dict[weighted_graph_dict_key].append(conference_name)
          else:
            weighted_graph_dict[weighted_graph_dict_key] = []
            weighted_graph_dict[weighted_graph_dict_key].append(conference_name)
  for item in weighted_graph_dict.keys():
    filename1, filename2 = item
    reverse_item = (filename2, filename1)
    if item not in unique_weighted_graph_dict:
      if reverse_item not in unique_weighted_graph_dict:
        unique_weighted_graph_dict[item] = weighted_graph_dict[item]
  
  weighted_graph_dict = unique_weighted_graph_dict
  return weighted_graph_dict

# Create graph and visualization

def create_graph_and_visualization(unique_vertex_list, weighted_graph_dict, filename):
  unique_edge_tuple_list = weighted_graph_dict.keys()
  # Creates an undirected Graph object
  g = Graph(directed=False)
  vprop = g.new_vertex_property("string") 
  g.vertex_properties["name"]=vprop 

  eprop = g.new_edge_property("string")
  g.edge_properties["name"]=eprop
  
  # Creates vertex object i.e. node for each author
  for item in unique_vertex_list:
    vertex = g.add_vertex()
    vprop[vertex] = item

  # Creates the edges according to the unique edge tuples
  for edge_tuple in unique_edge_tuple_list:
    edge = g.add_edge(find_vertex(g, vprop, edge_tuple[0])[0],find_vertex(g, vprop, edge_tuple[1])[0])
    eprop[edge] = str(weighted_graph_dict[edge_tuple]).replace("[", "").replace("]", "").replace("'", "")
    #print edge_tuple,eprop[edge]
  # Draws the graph
  graph_draw(
    g,
    vertex_text=g.vertex_properties["name"],
    edge_text=g.edge_properties["name"],
    bg_color=[1,1,1,1],
    vertex_fill_color=[1,1,1,1],
    edge_pen_width = 0.25,
    edge_text_distance = 10,
    vertex_size = 40,
    #edge_text_parallel = False,
    #vertex_text_color = "blue",
    edge_font_weight = cairo.FONT_WEIGHT_BOLD,
    edge_font_slant = cairo.FONT_SLANT_ITALIC,
    #edge_text_color = "red",
    vertex_font_size=10,
    edge_font_size=14,
    output_size=(3000, 3000), 
    output=filename
  )
"""
def get_conference_names(text):
  conference_names_list = []
  match = re.search(r'(?<="IEEE conference_names","kwd":\[)[\s\S]+(?=]},{"type":"INSPEC: Controlled Indexing")',text)
  if match:
    conference_names_text = match.group()
    conference_names_text = conference_names_text.replace('"', '')
    conference_names_list = re.split(r',',conference_names_text)
    conference_names_list = [x.strip().lower() for x in conference_names_list]
    if '' in conference_names_list:
      conference_names_list.remove('')
    return conference_names_list 
  match = re.search(r'(?<="IEEE conference_names","kwd":\[)[\s\S]+(?=]},{"type":"Author conference_names ")',text) 
  if match:
    conference_names_text = match.group()
    conference_names_text = conference_names_text.replace('"', '')
    conference_names_list = re.split(r',',conference_names_text)
    conference_names_list = [x.strip().lower() for x in conference_names_list]
    if '' in conference_names_list:
      conference_names_list.remove('')
    return conference_names_list 
  else:
    conference_names_list = []
  return conference_names_list
"""

def main():
  process_html_files()
if __name__=="__main__":
  main()
