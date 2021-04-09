import heapq
import random
import math
import time
import numpy
import matplotlib.pyplot as plt


serForDept = 0
arrDeptCount = 0
busyCount = 0
unSatisfiedService = 0
unSatisfiedServiceTime = 0.0
lastServiceTimeGenerated = 0.0
arrival_continue = 0
arrival_continue_value = 0.0
one_unsatisfied_service = 0
inc_unsatisfied = 0 
forUnsatisfiedDeparture = 0.0
i_ii_flag = 0
# Parameters
class Params:
    def __init__(self, lambd, omega, k):        
        self.lambd = lambd 
        self.omega = omega
        self.k = k

# States and statistical counters        
class States:
    def __init__(self):
        
        # States
        self.queue = []        
        
        # Statistics
        self.util = 0.0         
        self.avgQdelay = 0.0
        self.avgQlength = 0.0
        self.served = 0


        #new
        self.serverStatus = []
        self.numberOfInTheQueue = 0
        self.numberDelayed = 0
        self.totalDelay = 0.0
        self.auQt = 0.0
        self.auBt =0.0
        self.nextInService = 0.0
        self.maxQlength = 0
        self.service_requirement_a = 2.0
        self.service_requirement_b = 2.8
        self.last_arrival_time = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.unsatisfied_probability = 0.6
        self.totalUnsatisfied = []
        self.adqueue = []
        self.i_or_ii = 1   #used for selecting the two methods for unsatisfied service, 1 for (i) and 2 for (ii)










    def update(self, sim, event):
        global busyCount
        global unSatisfiedServiceTime
        global unSatisfiedService
        global inc_unsatisfied
        global forUnsatisfiedDeparture
        global one_unsatisfied_service
        global i_ii_flag
        if event.eventType == 'Arrival':
            for i in range(sim.params.k):
                if self.serverStatus[i] == 0:
                    self.serverStatus[i] = 1
                    self.served += 1
                    self.last_arrival_time[i] = event.eventTime
                    #print('%d number server e service e dhukse %lf' % (i, self.last_arrival_time[i]))
                    break
                elif self.serverStatus[i] == 1:
                    busyCount += 1
            if busyCount == sim.params.k:
                self.numberOfInTheQueue += 1
                if self.i_or_ii == 1:
                    self.queue.append(event.eventTime)
                elif self.i_or_ii == 2 and i_ii_flag == 1:
                    self.queue.insert(0,event.eventTime)
                    i_ii_flag = 0
                else:
                    self.queue.append(event.eventTime)
                self.auQt += len(self.queue)*(event.eventTime - sim.simclock)
                self.qSize = len(self.queue)
                if self.qSize > self.maxQlength:
                    self.maxQlength = self.qSize
                #busyCount = 0
            #for i in range(sim.params.k):
                #if self.serverStatus[i] == 1:
                    #busyCount += 1
            if self.i_or_ii == 1:
                self.adqueue.append(event.eventTime)
            elif self.i_or_ii == 2 and i_ii_flag == 1:
                self.adqueue.insert(0,event.eventTime)
                i_ii_flag = 0
            else:
                self.adqueue.append(event.eventTime)
            #print(self.adqueue)
            if inc_unsatisfied == 0:
                self.totalUnsatisfied.append(0)
            else:
                self.incre = self.totalUnsatisfied[0] + 1
                self.totalUnsatisfied.pop(0)
                inc_unsatisfied = 0
                if self.i_or_ii == 1:
                    self.totalUnsatisfied.append(self.incre)
                else:
                    self.totalUnsatisfied.insert(0,self.incre)
            #print(self.totalUnsatisfied)
            print("%lf --> its unsatisfaction number is %d" % (event.eventTime, self.totalUnsatisfied[len(self.totalUnsatisfied)-1]))
            self.auBt += (busyCount/sim.params.k)*(event.eventTime - sim.simclock)
            busyCount = 0
        elif event.eventType == 'Departure':
            self.satisfied_or_not = numpy.random.uniform(0.0,1.0)
            print('unsatisfied probability: %lf' % (self.satisfied_or_not))
            for i in range(sim.params.k):
                if self.serverStatus[i] == 1:
                    if self.queue:
                        #print('%lf er arrival hoisilo %lf e' % (event.eventTime, self.last_arrival_time[i]))
                        self.unsatisfied_customers_previous_arrival = self.last_arrival_time[i]
                        forUnsatisfiedDeparture = self.unsatisfied_customers_previous_arrival
                        self.nextInService = self.queue.pop(0)
                        self.last_arrival_time[i] = self.nextInService
                        #print('%d number server e service e dhukse %lf' % (i, self.last_arrival_time[i]))
                        self.numberOfInTheQueue -= 1
                        self.served += 1
                        self.totalDelay += event.eventTime - self.nextInService
                        global serForDept
                        serForDept = 1
                        self.auQt += len(self.queue)*(event.eventTime - sim.simclock)
                        self.ind = 0
                        for i in range(len(self.adqueue)):
                            if self.adqueue[i] == self.unsatisfied_customers_previous_arrival:
                                self.ind = i
                                break
                        if self.satisfied_or_not <= self.unsatisfied_probability/(self.totalUnsatisfied[self.ind]+1):
                            #p/(i+1) here
                            #self.queue.append(event.eventTime)
                            print(".......Unsatisfied.......")
                            print('%lf is unsatisfied whose arrival was at %lf' % (event.eventTime, self.unsatisfied_customers_previous_arrival))
                            print('%lf enters queue after a temporary departure' % (event.eventTime))
                            unSatisfiedServiceTime = event.eventTime
                            unSatisfiedService = 1
                            inc_unsatisfied = 1
                            self.served -= 1
                    else:
                        self.serverStatus[i] = 0
                        #print('%lf er arrival hoisilo %lf e' % (event.eventTime, self.last_arrival_time[i]))
                        if self.satisfied_or_not <= self.unsatisfied_probability:
                            #self.serverStatus[i] = 1
                            unSatisfiedServiceTime = event.eventTime
                            unSatisfiedService = 1
                            inc_unsatisfied = 1
                            self.served -= 1
                            one_unsatisfied_service = 1
                            print(".......Unsatisfied.......")
                            print('%lf is unsatisfied whose arrival was at %lf' % (event.eventTime, self.last_arrival_time[i]))
                            print('%lf enters directly to another service after a temporary departure' % (event.eventTime))
                    self.adqueue.pop(0)
                    #print(self.adqueue)
                    if inc_unsatisfied == 0:
                        self.totalUnsatisfied.pop(0)
                    break
            for i in range(sim.params.k):
                if self.serverStatus[i] == 1:
                    busyCount += 1
            self.auBt += (busyCount/sim.params.k)*(event.eventTime - sim.simclock)
            busyCount = 0

    def printVariables(self):
        #print(self.queue)
        None    
    
    def finish(self, sim):
        #None
        self.avgQdelay = self.totalDelay/self.served
        self.avgQlength = self.auQt/sim.simclock
        #print(self.avgQdelay)
        #print(self.avgQlength)
        self.util = abs(self.auBt/sim.simclock)
        
    def printResults(self, sim):
        # DO NOT CHANGE THESE LINES
        print('MMk Results: lambda = %lf, omega = %lf, k = %d' % (sim.params.lambd, sim.params.omega, sim.params.k))
        print('MMk Total customer served: %d' % (self.served))
        print('MMk Average queue length: %lf' % (self.avgQlength))
        print('MMk Average customer delay in queue: %lf' % (self.avgQdelay))
        print('MMk Time-average server utility: %lf' % (self.util))
        print('Maximum Queue Length: %d' % (self.maxQlength))
     
    def getResults(self, sim):
        return (self. avgQlength, self.avgQdelay, self.util)
   
class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None
        
    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')
    
    def __repr__(self):
        return self.eventType

class StartEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim
        
    def process(self, sim):
        self.first_event_time = -(1/sim.params.lambd) * math.log(random.uniform(0,1),math.e)
        #sim.states.adqueue.append(self.first_event_time)
        #print(sim.states.adqueue)
        self.sim.scheduleEvent(ArrivalEvent(self.first_event_time, self.sim))
        global arrDeptCount
        arrDeptCount += 1
        #print("beginning e ",arrDeptCount)
        #None
                
class ExitEvent(Event):    
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim
    
    def process(self, sim):
        #if sim.simclock > 10:
            #print("ergrgrhtghfgtjykgyhjfgdfjjggkgfjfgjgkhkjkkkhkyrik")
            #self.sim.scheduleEvent(ExitEvent(eventTime, self.sim))
        None

                                
class ArrivalEvent(Event):
    #new
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'Arrival'
        self.sim = sim
        #new








    def process(self, sim):
        global one_unsatisfied_service
        global unSatisfiedServiceTime
        global arrival_continue
        global arrival_continue_value
        global unSatisfiedService
        if one_unsatisfied_service == 1:
            #self.naTime = unSatisfiedServiceTime
            #unSatisfiedService = 0
            #unSatisfiedServiceTime = 0.0
            #arrival_continue = 1
            #arrival_continue_value = sim.simclock
            #self.sim.scheduleEvent(ArrivalEvent(self.naTime, self.sim))
            #None
            one_unsatisfied_service = 0
        else:
            self.iaTime = -(1/sim.params.lambd) * math.log(random.uniform(0,1),math.e)
            #print(self.iaTime)
            if arrival_continue == 0:
                self.naTime = self.iaTime + sim.simclock
            else:
                self.naTime = self.iaTime + sim.simclock
                arrival_continue = 0
                arrival_continue_value = 0.0
            #print(self.naTime)
            #sim.states.adqueue.append(self.naTime)
            #print(sim.states.adqueue)
            self.sim.scheduleEvent(ArrivalEvent(self.naTime, self.sim))
            #time.sleep(0.5)
            #print(sim.states.queue)
        global arrDeptCount
        arrDeptCount += 1
        #print("normal arrival e ",arrDeptCount)
        if sim.simclock >= (480*60):
            self.sim.scheduleEvent(ExitEvent(0.1, self.sim))
            #time.sleep(5)
        if not sim.states.queue:
            self.serTime = numpy.random.uniform(sim.states.service_requirement_a,sim.states.service_requirement_b)
            self.nsTime = self.serTime + sim.simclock
            #sim.states.adqueue.pop(0)
            #print(sim.states.adqueue)
            self.sim.scheduleEvent(DepartureEvent(self.nsTime, self.sim))
            #time.sleep(0.5)
            arrDeptCount -= 1
            #print("prothom departure e ",arrDeptCount)
            if unSatisfiedService == 1:
                self.naTime = unSatisfiedServiceTime
                unSatisfiedService = 0
                unSatisfiedServiceTime = 0.0
                arrival_continue = 1
                arrival_continue_value = self.naTime
                one_unsatisfied_service = 1
                if sim.states.i_or_ii == 2:
                    i_ii_flag = 1
                #sim.states.adqueue.append(self.naTime)
                #print(sim.states.adqueue)
                self.sim.scheduleEvent(ArrivalEvent(self.naTime, self.sim))
                arrDeptCount += 1
                #print("unsatisfied arrival e ", arrDeptCount)
        
class DepartureEvent(Event): 
    #new
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'Departure'
        self.sim = sim
        #new




    def process(self, sim):
        global serForDept
        global unSatisfiedService
        global unSatisfiedServiceTime
        global arrival_continue
        global arrival_continue_value
        global arrDeptCount
        global one_unsatisfied_service
        global forUnsatisfiedDeparture
        global i_ii_flag
        if serForDept == 1:
            #self.serTime = -(1/sim.params.omega) * math.log(random.uniform(0,1),math.e)
            self.indx = 0
            for i in range(len(sim.states.adqueue)):
                if sim.states.adqueue[i] == forUnsatisfiedDeparture:
                    self.indx = i
                    break
            self.sr_a = sim.states.service_requirement_a/(sim.states.totalUnsatisfied[self.indx]+1)   #a/(i+1)
            self.sr_b = sim.states.service_requirement_b/(sim.states.totalUnsatisfied[self.indx]+1)   #b/(i+1)
            self.serTime = numpy.random.uniform(self.sr_a,self.sr_b)
            self.nsTime = self.serTime + sim.simclock
            serForDept = 0
            #sim.states.adqueue.pop(0)
            #print(sim.states.adqueue)
            self.sim.scheduleEvent(DepartureEvent(self.nsTime, self.sim))
            #time.sleep(0.5)
            arrDeptCount -= 1
            #print("notun in service e ",arrDeptCount)
        if unSatisfiedService == 1:
            self.naTime = unSatisfiedServiceTime
            unSatisfiedService = 0
            unSatisfiedServiceTime = 0.0
            arrival_continue = 1
            arrival_continue_value = self.naTime
            one_unsatisfied_service = 1
            if sim.states.i_or_ii == 2:
                i_ii_flag = 1
            #sim.states.adqueue.append(self.naTime)
            #print(sim.states.adqueue)
            self.sim.scheduleEvent(ArrivalEvent(self.naTime, self.sim))
            arrDeptCount += 1
            #print("unsatisfied arrival e ", arrDeptCount)

class Simulator:
    def __init__(self, seed):
        self.eventQ = []
        self.simclock = 0   
        self.seed = seed
        self.params = None
        self.states = None
        
    def initialize(self):
        self.simclock = 0        
        self.scheduleEvent(StartEvent(0, self))
        
    def configure(self, params, states):
        self.params = params
        self.states = states
        for i in range(self.params.k):
            self.states.serverStatus.append(0)
    def now(self):
        return self.simclock
        
    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))        
    
    def run(self):
        random.seed(self.seed)        
        self.initialize()
        
        while len(self.eventQ) > 0:
            time, event = heapq.heappop(self.eventQ)
            
            if event.eventType == 'EXIT':
                break
            
            if self.states != None:
                self.states.update(self, event)
                
            print (event.eventTime, 'Event', event)
            #print (self.states.served)
            self.simclock = event.eventTime
            event.process(self)
            #new
            print("The updated queue: ",self.states.queue)
            print("\n\n\n")
     
        self.states.finish(self)   
    
    def printResults(self):
        self.states.printResults(self)
        
    def getResults(self):
        return self.states.getResults(self)
        

def experiment1():
    seed = 101    
    sim = Simulator(seed)
    sim.configure(Params(5.0/60, 8.0/60, 5), States())
    sim.run()
    sim.printResults()

def experiment2():
    seed = 110
    omega = 1000.0 / 60
    ratios = [u / 10.0 for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []
    
    for ro in ratios:
        sim = Simulator(seed)
        sim.configure(Params(omega * ro, omega, 5), States())    
        sim.run()
        
        length, delay, utl = sim.getResults()
        avglength.append(length)
        avgdelay.append(delay)
        util.append(utl)
        
    plt.figure(1)
    plt.subplot(311)
    plt.plot(ratios, avglength)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q length')    

    
    plt.subplot(312)
    plt.plot(ratios, avgdelay)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q delay (sec)')    

    plt.subplot(313)
    plt.plot(ratios, util)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Util')    
    
    plt.show()          
    
def experiment3():
    # Similar to experiment2 but for different values of k; 1, 2, 3, 4
    # Generate the same plots
    #None
    seed = 110
    omega = 1000.0 / 60
    sim = Simulator(seed)
    ratios = [u / 10.0 for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []

    for i in range(1,5,1):
        for ro in ratios:
            sim = Simulator(seed)
            sim.configure(Params(omega * ro, omega, i), States())
            sim.run()

            length, delay, utl = sim.getResults()
            avglength.append(length)
            avgdelay.append(delay)
            util.append(utl)

        plt.figure(1)
        plt.subplot(311)
        plt.plot(ratios, avglength)
        plt.xlabel('Ratio (ro)')
        plt.ylabel('Avg Q length')

        plt.subplot(312)
        plt.plot(ratios, avgdelay)
        plt.xlabel('Ratio (ro)')
        plt.ylabel('Avg Q delay (sec)')

        plt.subplot(313)
        plt.plot(ratios, util)
        plt.xlabel('Ratio (ro)')
        plt.ylabel('Util')

        plt.show()
        avglength = []
        avgdelay = []
        util = []




                            
def main():
    experiment1()
    #experiment2()
    #experiment3()        

          
if __name__ == "__main__":
    main()
                  
