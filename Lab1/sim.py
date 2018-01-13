from Queue import PriorityQueue
import random

## we need to make an intermediate object named as connection which will keep the info
# of which switch is connected to with source

class Switch:

	def __init__(self, output_bandwidth = 10000 , source_list = None ,queue_size = float("inf") ): #  bndwitch of 1000 bits/sec
		self.source_list = source_list # list of sources
		self.output_bandwidth = output_bandwidth
		self.queue_size = queue_size # initial size of queue_set to zero
		self.data_recieved_uptil_now = 0 # to keep a track of total data recieved uptil now
		self.data_transmitted_uptil_now = 0 # to keep track of data transmitted till now
		self.packets_in_queue = [] # will keep track of packets in
		self.data_left_transmit = 0 # immediate data left for transmission
		self.data_left_last_time = 0 # the start time of data transmission started
	@property
	def incoming_rate(self):
		if self.source_list is None:
			self.incoming_rate = 0
		else:
			self.incoming_rate = 0
			for s in self.source_list:
				self.incoming_rate = s.packet_size*s.transfer_rate # bits/sec

	def get_number_packets(self):
		return len(self.packets_in_queue)

	def get_queue_size(self):
		size = 0
		for p in self.packets_in_queue:
			size += p.source.packet_size
		return size
	def insert_packet_queue(self,packet):
		self.packets_in_queue.append(packet)

	def remove_packet_queue(self,packet):
		if packet in self.packets_in_queue:
			self.packets_in_queue.remove(packet)
		else:
			print "[ERROR] : Packet not in Queue "



	def set_sources(self,sources): # to set the sources list
		self.source_list = sources



	def add_source(self,source):
		if self.source_list is not None and source is not None and source not in self.source_list:
			self.source_list.append(source)
		elif self.source_list is None:
			self.source_list = []
			self.source_list.append(source)
		return self.source_list


	def remove_source(self,source):
		if source in self.source_list:
			self.source_list.remove(source)
		return self.source_list


	def list_sources(self):
		if self.source_list is None:
			print "No sources at present"
		else:
			for s in self.source_list:
				print s



class Source:
	""" this is the class for the source variable"""
	def __init__(self, start_time , transfer_rate = 1, packet_size = 100 , bandwidth = 1000, switch = None):
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
		self.switch = None
	def connect_to_switch(self, switch):
		self.switch = switch

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

	def __repr__(self):
		return "Source Start time {}".format(self.start_time)

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
		# self.source = packet.source # cntains the source object
		self.packet = packet # the packet assigned to the event
		self.event_time = time # the time for event_id to occur

		if event_id == 0: # packet is generated
			self.event_time = packet.packet_generate_time # not sure about this



		# if event_id == 0:
		# 	# we should automatically set the time for event to
	def __cmp__(self, other):
		return ( self.event_time > other.event_time )


	def Next_Event(self):
		# whenever and event occur we should update the switch transmission status

		data_left = self.packet.source.switch.data_left_transmit - (self.event_time - self.packet.source.switch.data_left_last_time)*self.packet.source.switch.output_bandwidth
		if data_left <= 0:
			self.packet.source.switch.data_left_transmit = 0
			self.packet.source.switch.data_left_last_time = self.event_time
		else:
			self.packet.source.switch.data_left_transmit = data_left
			self.packet.source.switch.data_left_last_time = self.event_time

		# update the info of data left
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
		e0 = self.packet.source.Produce_Event0(self.event_time) # created the new event for the packet from
		# same source
		self.event_id = self.event_id + 1
		self.event_time = self.event_time + (1.0/self.packet.source.transfer_rate)*self.packet.source.packet_size # add the bandwith delay from source to switch
 		# we have modified this to event 2
 		return [self,e0]
		# pass

	def Event1to2(self):
		# event 1 has taken place i.e. it has reached the switch now we have enqueed into the switch
		self.event_id = self.event_id + 1
		# enqeue in the switch queue


		#time_new = time_prdouce + time_sendSwitch + N*output_bandwidth*sizeofpacket + currentTransmission(not considering at the moment)
		self.event_time = self.event_time + (self.packet.source.switch.get_queue_size() + self.packet.source.switch.data_left_transmit)/self.packet.source.switch.output_bandwidth
		# print the queue size in between

		# now we will modify the queue etc
		self.packet.source.switch.insert_packet_queue(self.packet)


		return [self] # here we have returned back

	def Event2to3(self): # this transition event will pop the element from switch queue and put it into the transmission buffer
		# first we need to check if really the buffer is empty or not
		if self.packet.source.switch.data_left_transmit > 0 :
			print "[Error] : Buffer not empty and trying to transmit"
		self.event_id = self.event_id + 1
		self.packet.source.switch.remove_packet_queue(self.packet) # we have removed the packet from queue
		# we should also print the queue size inn between

		self.packet.source.switch.data_left_transmit = self.packet.source.packet_size
		self.packet.source.switch.data_left_last_time = self.event_time
		self.event_time = self.event_time + self.packet.source.packet_size/self.packet.source.switch.output_bandwidth

		return self

	def Event3toFinish(self):
		# this is the last where packet reaches the sink



class Packet:
	def __init__(self, source, packet_id, packet_generate_time):
		self.source = source
		self.packet_id = packet_id
		self.packet_generate_time = packet_generate_time
		# self.packet_switch = None # we assign this value
		#initially the packet is not in switch



# describe initial sources
gQueue = PriorityQueue() # global Queue
TimeLimit = 1000
globalTime = 0

# first we create a switch for our world
switch1 = Switch()
# create a list of sources in the world
source = []
for i in range(4):
	s = Source(random.random())
	source.append(s)

# now we will connect the switch and sources
switch1.list_sources()

switch1.add_source(source)
# sources added to the switch1
switch1.list_sources()

# now we need to add the switch to the source
for s in source:
	s.connect_to_switch(switch1)

# sources are connected to the switch now

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
	# print globalTime
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
