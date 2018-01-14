from Queue import PriorityQueue
import random

## we need to make an intermediate object named as connection which will keep the info
# of which switch is connected to with source
EPSILON = 1e-9

class Switch:

	def __init__(self, output_bandwidth = 10000 , source_list = None ,queue_size = float("inf"), sink = None ): #  bndwitch of 1000 bits/sec
		self.source_list = source_list # list of sources
		self.output_bandwidth = output_bandwidth
		self.queue_size = queue_size # initial size of queue_set to zero
		self.data_recieved_uptil_now = 0 # to keep a track of total data recieved uptil now
		self.packet_recieved_uptil_now = 0
		self.last_packet_recieved = 0
		self.data_transmitted_uptil_now = 0 # to keep track of data transmitted till now
		self.packets_in_queue = [] # will keep track of packets in
		self.data_left_transmit = 0 # immediate data left for transmission
		self.data_left_last_time = 0 # the start time of data transmission started
		self.sink = sink # assign the sink to the switch
		self.packets_dropped = 0
	@property
	def incoming_rate(self):
		if self.source_list is None:
			return 0
		else:
			rate = 0
			for i in range(len(self.source_list)):
				rate += self.source_list[i].packet_size*self.source_list[i].transfer_rate # bits/sec
			return rate

	def add_sink(self, sink):
		self.sink = sink
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
	def __init__(self, start_time , transfer_rate = 4, packet_size = 100 , bandwidth = 1000, switch = None):
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
		print "Packet Produced at {}".format(packet_generate_time)
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
		self.packet.source.switch.data_recieved_uptil_now += self.packet.source.packet_size
		self.packet.source.switch.packet_recieved_uptil_now += 1
		self.packet.source.switch.last_packet_recieved = self.event_time
		# log the information for input data

		if self.packet.source.switch.queue_size > self.packet.source.switch.get_number_packets():
			# there is space in the queue to add another packet
			#time_new = time_prdouce + time_sendSwitch + N*output_bandwidth*sizeofpacket + currentTransmission(not considering at the moment)
			self.event_time = self.event_time + (self.packet.source.switch.get_queue_size() + self.packet.source.switch.data_left_transmit)/self.packet.source.switch.output_bandwidth
			# print the queue size in between

			# now we will modify the queue etc

			self.packet.source.switch.insert_packet_queue(self.packet)
			return [self] # here we have returned back
		else:
			self.packet.source.switch.packets_dropped += 1
			print "Packet Dropped"
			return None




		# self.data_recieved_uptil_now = 0 # to keep a track of total data recieved uptil now
		# self.packet_recieved_uptil_now = 0
		# self.last_pacet_recieved = 0

	def Event2to3(self): # this transition event will pop the element from switch queue and put it into the transmission buffer
		# first we need to check if really the buffer is empty or not
		if self.packet.source.switch.data_left_transmit > 0 and self.packet.source.switch.data_left_transmit > EPSILON:
			print "[Error] : Buffer not empty and trying to transmit this much data left {}".format(self.packet.source.switch.data_left_transmit)
			self.event_time = self.event_time + self.packet.source.switch.data_left_transmit/self.packet.source.switch.output_bandwidth
			return [self]
		if  self.packet.source.switch.data_left_transmit > 0 and self.packet.source.switch.data_left_transmit < EPSILON:
			print "[Warning] Approximation Error"
			self.packet.source.switch.data_left_transmit = 0

		self.event_id = self.event_id + 1
		self.packet.source.switch.remove_packet_queue(self.packet) # we have removed the packet from queue
		# we should also print the queue size inn between

		self.packet.source.switch.data_left_transmit = self.packet.source.packet_size
		self.packet.source.switch.data_left_last_time = self.event_time
		self.event_time = self.event_time + self.packet.source.packet_size/self.packet.source.switch.output_bandwidth

		return [self]
	# Event -> packet -> source -> switch -> sink
	def Event3toFinish(self):
		# now first we will log the stats in the sink
		# packet has reached the sink so
		self.packet.source.switch.sink.packets_recieved += 1
		self.packet.source.switch.sink.data_recieved += self.packet.source.packet_size
		self.packet.source.switch.sink.last_packet_recieved = self.event_time
		self.packet.source.switch.sink.totalDelay += ( self.event_time - self.packet.packet_generate_time )
		# here we can call a deconstructor for packet etc lets see later
		# del self.packet # need to know if this will aso delete the inforamtion of source
		print "Packet Recieved"
		return None

class Packet:
	def __init__(self, source, packet_id, packet_generate_time):
		self.source = source
		self.packet_id = packet_id
		self.packet_generate_time = packet_generate_time
		# self.packet_switch = None # we assign this value
		#initially the packet is not in switch

class Sink:
	def __init__(self,switch = None):
		self.switch = switch
		self.data_recieved = 0 # data in bits
		self.packets_recieved = 0
		self.totalDelay = 0 # the total delay in arrival of packets uptil now
		self.last_packet_recieved = 0 # last value of time the packet was recieved

	def add_switch(self, switch):
		if self.switch is None:
			print 'New Switch assigned'
			self.swith = switch
		else:
			print 'Switch replaced'

class Simulation:
	# here we will combine the whole simulation into occurence
	def __init__(self, no_of_Sources,source_tranfer_rate, source_bandwidth, output_bandwidth, timeLimit,packet_sizes,queue_size = float("inf")):
		self.globalQueue = PriorityQueue()
		self.timeLimit = timeLimit
		self.no_of_sources = no_of_Sources
		self.sources = []
		self.simTime = 0 # initilise the sim time to be 0
		self.queue_size = queue_size
		self.output_bandwidth = output_bandwidth
		self.source_bandwith = source_bandwidth
		self.source_tranfer_rate = source_tranfer_rate
		self.packet_sizes = packet_sizes

		for i in range(self.no_of_sources):
			# s = Source(random.random())#, transfer_rate = 4, packet_size = 100, bandwidth = 1000, switch = None)
			s = Source(random.random(), transfer_rate = self.source_tranfer_rate[i], packet_size = self.packet_sizes[i], bandwidth = self.source_bandwith[i], switch = None)
			self.sources.append(s)
		self.switch = Switch(output_bandwidth =self.output_bandwidth, source_list = self.sources, queue_size = self.queue_size, sink = None)
		self.switch.list_sources()
		self.sink = Sink(switch =self.switch)
		# connect the sink to the switch
		self.switch.add_sink(self.sink)
		# now we need to add the switch to the source
		for s in self.sources:
			s.connect_to_switch(self.switch)
		## all connections have been done
		# no packets and push into queue_size
		initial_events = []
		for s in self.sources:
			e = s.Produce_Event0(self.simTime)
			initial_events.append(e)
			self.globalQueue.put(e)


	def reset(self):
		""" will reset the sim with inital events"""
		self.globalQueue = PriorityQueue()
		self.simTime = 0
		self.sources = []
		for i in range(self.no_of_sources):
			# s = Source(random.random())#, transfer_rate = 4, packet_size = 100, bandwidth = 1000, switch = None)
			s = Source(random.random(), transfer_rate = self.source_tranfer_rate[i], packet_size = 100, bandwidth = self.source_bandwith[i], switch = None)
			self.sources.append(s)
		self.switch = Switch(output_bandwidth =self.output_bandwidth, source_list = self.sources, queue_size = self.queue_size, sink = None)
		self.switch.list_sources()
		self.sink = Sink(switch =self.switch)
		# connect the sink to the switch
		self.switch.add_sink(self.sink)
		# now we need to add the switch to the source
		for s in self.sources:
			s.connect_to_switch(self.switch)
		## all connections have been done
		# no packets and push into queue_size
		initial_events = []
		for s in self.sources:
			e = s.Produce_Event0(self.simTime)
			initial_events.append(e)
			self.globalQueue.put(e)

	def Run_Simulation(self):
		while self.timeLimit > self.simTime:
			# Contains the initial packet creatoin events from all sources
			# now we will extract next event in the global queue

			e = self.globalQueue.get()

			# equate the global time to the event occurence time
			self.simTime = e.event_time # assginrs the global time the current time from the event
			# print globalTime
			events = e.Next_Event()
			if events is not None:
				for e in events:
					self.globalQueue.put(e)


		print "Simulation finished "

			# if self.switch.last_packet_recieved == 0:
			# 	continue
			# else:
			# 	print " {} : {}".format(self.switch.incoming_rate,self.switch.data_recieved_uptil_now/self.switch.last_packet_recieved)

if __name__ ==	 "__main__":
	# sim = Simulation(no_of_Sources, source_tranfer_rate, source_bandwidth, output_bandwidth, timeLimit,packet_sizes,queue_size = float("inf"))
	sim = Simulation(no_of_Sources = 4,source_tranfer_rate =  [1,1,1,1], source_bandwidth = [1000,1000,1000,1000],output_bandwidth =  1000,
	 timeLimit = 1000, packet_sizes = [100, 100, 100, 100] ,queue_size = float("inf"))

	sim.Run_Simulation()


# # describe initial sources
# gQueue = PriorityQueue() # global Queue
# TimeLimit = 1000
# globalTime = 0
# totalDelay = 0
#
# # first we create a switch for our world
# switch1 = Switch()
# # create a list of sources in the world
# source = []
# for i in range(4):
# 	s = Source(random.random())
# 	source.append(s)
# # create a sink object and connect to the switch
# sink = Sink(switch =switch1)
#
# # now we will connect the switch and sources
# switch1.list_sources()
#
# switch1.set_sources(source)
# # sources added to the switch1
# switch1.list_sources()
#
# # connect the sink to the switch
# switch1.add_sink(sink)
#
#
# # now we need to add the switch to the source
# for s in source:
# 	s.connect_to_switch(switch1)
#
# # sources are connected to the switch now
#
# initial_events = []
# for s in source:
# 	e = s.Produce_Event0(globalTime)
# 	initial_events.append(e)
# 	gQueue.put(e)
#
# # this loads the initial packetformed from the sourced into the queue
# iter = 0
# while TimeLimit > globalTime:
# 	# Contains the initial packet creatoin events from all sources
# 	# now we will extract next event in the global queue
#
# 	e = gQueue.get()
#
# 	# equate the global time to the event occurence time
# 	globalTime = e.event_time # assginrs the global time the current time from the event
# 	# print globalTime
# 	events = e.Next_Event()
# 	if events is not None:
# 		for e in events:
# 			gQueue.put(e)
#
# 	if switch1.last_packet_recieved == 0:
# 		continue
# 	else:
# 		print " {} : {}".format(switch1.incoming_rate,switch1.data_recieved_uptil_now/switch1.last_packet_recieved)
#
# 	# iter += 1
# # at this point of time simulation has been completed and we need to get the statistics
