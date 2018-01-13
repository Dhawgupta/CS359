from Queue import PriorityQueue
import random

## we need to make an intermediate object named as connection which will keep the info 
# of which switch is connected to with source

class Switch:

	def __init__(self, output_bandwidth ,queue_size = float("inf"), source_list = None ):
		self.source_list = source# list of sources
		self.output_bandwidth = output_bandwidth
		self.queue_size = queue_size # initial size of queue_set to zero
		self.elements_in_queue = 0 # initla elements set to zero
		self.data_recieved_uptil_now = 0 # to keep a track of total data recieved uptil now
		self.data_transmitted_uptil_now = 0 # to keep track of data transmitted till now
		# calculate the incoming rate
		# if source_list is None:
		# 	self.incoming_rate = 0
		# else:
		# 	self.incoming_rate = 0
		# 	for s in self.source_list:
		# 		self.incoming_rate = s.packet_size*s.transfer_rate # bits/sec

	@property
	def incoming_rate(self):
		if source_list is None:
			self.incoming_rate = 0
		else:
			self.incoming_rate = 0
			for s in self.source_list:
				self.incoming_rate = s.packet_size*s.transfer_rate # bits/sec


	def set_sources(self,sources): # to set the sources list
		self.source_list = sources

	

	def add_source(self,source):
		if source not in self.source_list and source is not None and self.source_list is not None:
			self.source_list.append(source)
		elif self.source_list is None:
			self.source_list = []
			self.source_list.append(source)
		return self.source_list
	

	def remove_source(self,source):
		if source in self.source_list:
			self.source_list.remove(source)
		return self.source_list



class Source:
	""" this is the class for the source variable"""
	def __init__(self, start_time , transfer_rate = 1, packet_size = 100 , bandwidth = 1000): 
		"""
		the default values for the variables are :
		transfer_rate : 1 packet /sec
		packet_size : 100 bits
		bandwidth : 1000 bits/sec
		All the values will be in bits and bits per second
		"""
		self.transfer_rate = transfer_rate
		self.packet_size = packet_size
		self.bandwidth = bandwidth
		self.start_time = start_time
		self.packet_produced = 0


	def Produce_Packet(self,globalTime): # send the globalTime to produce 
		self.packet_produced = self.packet_produced + 1
		if globalTime < self.start_time:
			packet_generate_time = self.start_time
		else:
			packet_generate_time = globalTime + 1.0/self.transfer_rate # here we dont mulitply by size because it produciton of packets
		p = Packet(self, self.packet_produced, packet_generate_time )
		return p

	def Produce_Event0(self, globalTime):
		p = self.Produce_Packet(globalTime)
		time = p.packet_generate_time
		event_id = 0
		e = Event(p, time, event_id)
		return e

class Event:
	"""
	This class will serve as the event class
	with 4 possible events
	E0 : Packet generation
	E1 : Packet reaches switch / enqueue
	E2 : Packet dequeue from the queue of switch and starts to transfer
	E3 : Packet transfer complete and packet reaches the sink
	"""
	def __init__(self, packet, time ,event_id = 0):
		self.event_id =event_id # initlise the packet with event
		self.source = packet.source # cntains the source object
		self.packet = packet # the packet assigned to the event 
		self.event_time = time # the time for event_id to occur

		if event_id == 0: # packet is generated 
			self.event_time = packet.packet_generate_time # not sure about this



		# if event_id == 0:
		# 	# we should automatically set the time for event to
	def __cmp__(self, other):
		return ( self.event_time > other.event_time )


	def Next_Event(self):
		if self.event_id == 0: # packet generated
			return self.Event0to1()

		elif self.event_id == 1: # packet reached to switch and enqueued
			return self.Event1to2() 

		elif self.event_id == 2: # packet dequed from queue of the switch
			return self.Event2to3()

		elif self.event_id == 3: # packet reached to sink
			return self.Event3toFinish()

	def Event0to1(self):
		# create a new packet from the same source
		e0 = self.source.Produce_Event0(self.event_time) # created the new event for the packet from 
		# same source
		self.event_id = self.event_id + 1
		self.event_time = self.event_time + (1.0/self.source.transfer_rate)*self.source.packet_size # add the bandwith delay from source to switch
 		# we have modified this to event 2 
 		return [self,e0]
		# pass

	def Event1to2(self):
		self.event_id = self.event_id + 1
		# self.event_time = self.event_time + 

	def Event2to3(self):
		pass
	
	def Event3toFinish(self):
		pass


class Packet:
	def __init__(self, source, packet_id, packet_generate_time):
		self.source = source
		self.packet_id = packet_id
		self.packet_generate_time = packet_generate_time
		self.packet_switch = None # we assign this value 
		#initially the packet is not in switch



# describe initial sources 
gQueue = PriorityQueue() # global Queue
TimeLimit = 1000
globalTime = 0

# first we create a switch for our world
switch  = Switch()


source = []
for i in range(4):
	s = Source(random.random())
	source.append(s)




initial_events = []
for s in source:
	e = s.Produce_Event0(globalTime)
	initial_events.append(e)
	gQueue.put(e)

# this loads the initial packetformed from the sourced into the queue

while TimeLimit > globalTime:
	# Contains the initial packet creatoin events from all sources
	# now we will extract next event in the global queue

	e = gQueue.get()

	# equate the global time to the event occurence time
	globalTime = e.event_time # assginrs the global time the current time from the event
	print globalTime
	events = e.Next_Event()
	if events is not None:
		for e in events:
			gQueue.put(e)


# while not gQueue.empty():
# 	e = gQueue.get()
# 	print e.event_time
# # print initial_events






##### the diagnostic for all 
# print p.source
# print p.packet_id
# print p.packet_generate_time
# print p3.source
# print p3.packet_id
# print p3.packet_generate_time

### to print the events

# for e in initial_events:
# 	print e.event_id
# 	print e.source
# 	print e.packet
# 	print e.event_time