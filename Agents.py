import mesa as ms
from math import ceil
from Models import *
from random import choice, randrange
import random

class GrassAgent(ms.Agent):
    def __init__(self, id_t, model):
        super().__init__(id_t, model)
        self.id = id_t

class VaccumAgentModel(ms.Agent):
    myCoordinates = (0, 0)
    def __init__(self, id_t, model):
        super().__init__(id_t, model)
        self.id = id_t
        self.state = False

    def move(self):
        next_move = self.model.grid.get_neighborhood(
		    self.pos, moore = True, include_center = False
	    )
        new_position = self.random.choice(next_move)
        self.model.grid.move_agent(self, new_position)
    def step(self):
        pass
"""
{
    "type": 0,
    "direction": ([1, 0] || [0, 1] || [-1, 0] || [0, -1]),
    "velocity" 2 u/s
}
"""

class TrafficLightAgent(ms.Agent):
    first_it = True

    # Data collector variables
    counterStepsBeingGreen = 0
    
    def __init__(self, unique_id, model, lane):
        super().__init__(unique_id, model)
        self.lane = lane    #0 = up, 1 = down, 2 = left, 3 = right
        self.light = 1      #0 = red, 1 = yellow, 2 = green
        self.localArrival = ()
        self.globalArrivals = {}
        self.tfs = {}
        new_pos = (17, 14)
        self.nextArrival = (-1, 100000, -1)

    def setTFS(self, tfs):
        self.tfs = tfs

    def checkCar(self):
        if self.distLeft == 0:
            self.velocity = 0
        elif self.distLeft <= self.velocity:
            self.velocity = ceil(self.velocity/2)

        dx = (self.direction[0] * self.velocity)
        dy = (self.direction[1] * self.velocity)

        newPos = (self.pos[0] + dx, self.pos[1] + dy)
        self.distLeft -= self.velocity
        self.model.grid.move_agent(self, newPos)
    
    def checkLane(self, coords_before_crossroad, coords_start_of_street):
        if coords_before_crossroad[0] == coords_start_of_street[0]:    # Case horizontal
            it_coords = list(coords_before_crossroad)
            if coords_before_crossroad < coords_start_of_street:
                for i in range(coords_before_crossroad[1], coords_start_of_street[1]):
                    it_coords[1] = i
                    current_cell = self.model.grid.get_cell_list_contents([tuple(it_coords)])
                    car = [obj for obj in current_cell if isinstance(obj, CarAgent)]
                    if len(car)>0:
                        return car[0]
            else:
                for i in reversed(range(coords_start_of_street[1], coords_before_crossroad[1])):
                    it_coords[1] = i
                    current_cell = self.model.grid.get_cell_list_contents([tuple(it_coords)])
                    car = [obj for obj in current_cell if isinstance(obj, CarAgent)]
                    if len(car)>0:
                        return car[0]
        else:
            it_coords = list(coords_before_crossroad)
            if coords_before_crossroad < coords_start_of_street:
                for i in range(coords_before_crossroad[0], coords_start_of_street[0]):
                    it_coords[0] = i
                    current_cell = self.model.grid.get_cell_list_contents([tuple(it_coords)])
                    car = [obj for obj in current_cell if isinstance(obj, CarAgent)]
                    if len(car)>0:
                        return car[0]
            else:
                for i in reversed(range(coords_start_of_street[0], coords_before_crossroad[0])):
                    it_coords[0] = i
                    current_cell = self.model.grid.get_cell_list_contents([tuple(it_coords)])
                    car = [obj for obj in current_cell if isinstance(obj, CarAgent)]
                    if len(car)>0:
                        return car[0]
        return CarAgent(33, self.model, -1, 2, [1, 0], 14, None)


    def hasTheCarPassed(self):
        if self.lane == 0:
            nextCar = self.checkLane((16, 31), (16, 15))
        elif self.lane == 1:
            nextCar = self.checkLane((15, 15), (15, 0))
        elif self.lane == 2:
            nextCar = self.checkLane((0, 16), (16, 16))
        elif self.lane == 3:
            nextCar = self.checkLane((16, 15), (32, 15))
        
        if nextCar.unique_id == self.nextArrival[0] and nextCar.unique_id != 33:
            print(f"crossed = {nextCar.unique_id},\tlane {self.lane}")
            return True
        else:
            print(f"not crossed = {self.nextArrival[0]}\tlane {self.lane}")
            return False


    def checkNextCar(self):
        nextCar = CarAgent(33, self.model, 0, 2, [1, 0], 14, None)
        if self.lane == 0:      # up
            nextCar = self.checkLane((16, 15), (16, 0))
        elif self.lane == 1:    # down
            nextCar = self.checkLane((15, 17), (15, 31))
        elif self.lane == 2:    # left
            nextCar = self.checkLane((17, 16), (32, 16))
        elif self.lane == 3:    # right
            nextCar = self.checkLane((15, 15), (0, 15))

        #print(f"TFL : {self.unique_id},\tlane: {self.lane},\tvel: {nextCar.velocity},\tCar_id: {nextCar.unique_id}, Position: {nextCar.pos}")
        return nextCar

    def stage_one(self):
        print("---")
        print(f"TFL: {self.lane}, STAGE ONE")
        #check if self should still be green
        if self.light == 2:
            self.counterStepsBeingGreen += 1
            if self.hasTheCarPassed():

                #maybe wait x steps in yellow?
                self.light = 1
        else:self.counterStepsBeingGreen = 0
        
        #change local arrivals
        
        nextCar = self.checkNextCar()
        print(f"nextCar.type: {nextCar.type}")
        if nextCar.type != -1:
            nextCarSpeed = nextCar.velocity
            if nextCarSpeed == 0:
                nextCarSpeed = 1
            self.nextArrival = (nextCar.unique_id, self.model.schedule.steps + (nextCar.distLeft/nextCarSpeed), self.lane)
        else:
            self.nextArrival = (-1, 100000, -1)
        
        print(f"TFL: {self.lane}, nextArrival: {self.nextArrival}")
        # if nextCar.pos == (self.pos[0], self.pos[1])

    def stage_two(self):
        #change global arrivals
        print("---")
        print(f"TFL: {self.lane}, STAGE TWO")
        greenLane = -1
        maxPriority = -1
        nextGlobalArrival = (-1, 100000, -1)
        for tf in self.tfs:
            if tf.light == 2:
                greenLane = tf.lane
                nextGlobalArrival = tf.nextArrival 
                break
            print(f"Comparing {tf.nextArrival} to {nextGlobalArrival}")
            if tf.nextArrival[1] < nextGlobalArrival[1]:
                nextGlobalArrival = tf.nextArrival
            
        print(f"Next global arrival: {nextGlobalArrival}")
        print(f"greenLane: {greenLane}, nextGlobalArrival: {nextGlobalArrival}, self.lane: {self.lane}")
        # if there's no cars, then nextGlobalArrival[0] == -1
        if nextGlobalArrival[0] == -1:
            self.light = 1

        # if there's no green light, a green light can be chosen based on nextGlobalArrival
        # ideally, we should wait until prior greenlight turns red
        elif self.light == 2 or (greenLane == -1 and nextGlobalArrival[2] == self.lane):
            self.light = 2
            print(f"CHANGED {self.lane} LIGHT TO {self.light}")
        else:
            self.light = 0
            print(f"CHANGED {self.lane} LIGHT TO {self.light}")

        #change lights
        #choices = [0, 1, 2]
        #self.light = random.choice(choices)
        
    def stage_three(self):
        pass

class ScheduledTrafficLightAgent(ms.Agent):
    first_it = True
    def __init__(self, unique_id, model, lane, counter):
        super().__init__(unique_id, model)
        self.lane = lane    #0 = up, 1 = down, 2 = left, 3 = right
        self.light = 0      #0 = red, 1 = yellow, 2 = green
        self.counter = counter

    def stage_one(self):
        if self.counter == 25:
            self.counter = 1
        
        if self.counter == 1:
            self.light = 2
        elif self.counter == 4:
            self.light = 1
        elif self.counter == 6:
            self.light = 0
        
        self.counter += 1

    def stage_two(self):
        pass

    def stage_three(self):
        pass

class CarAgent(ms.Agent):

    crashStatus = 0

    def __init__(self, unique_id, model, type, velocity, direction, distLeft, trafficLight):
        super().__init__(unique_id, model)
        self.type = type
        self.velocity = velocity
        self.desiredVelocity = velocity
        self.direction = direction
        self.distLeft = distLeft #14
        self.vision = 3
        self.TFL = trafficLight
        if self.type == 1: #carefull type
            self.lazyMOD = randrange(1,4)
        else:
            self.lazyMOD = 0
        
    def checkTrafficLight(self):
        if self.direction == [1, 0]:
            TFL_cell = self.model.grid.get_cell_list_contents([(14, 14)])
            TFL = [obj for obj in TFL_cell if isinstance(obj, TrafficLightAgent)][0]
            return TFL
        elif self.direction == [0, 1]:
            TFL_cell = self.model.grid.get_cell_list_contents([(17, 14)])
            TFL = [obj for obj in TFL_cell if isinstance(obj, TrafficLightAgent)][0]
            return TFL
        elif self.direction == [-1, 0]:
            TFL_cell = self.model.grid.get_cell_list_contents([(17, 17)])
            TFL = [obj for obj in TFL_cell if isinstance(obj, TrafficLightAgent)][0]
            return TFL
        else: # [0, -1]
            TFL_cell = self.model.grid.get_cell_list_contents([(14, 17)])
            TFL = [obj for obj in TFL_cell if isinstance(obj, TrafficLightAgent)][0]
            return TFL

    def checkCarFront(self, dist_t = -1):
        isACar = False
        if dist_t == -1:
            dist_t = self.velocity
        
        if ((self.direction == [1, 0]) and (self.pos[0] < 30)):
            for i in range(dist_t):
                if self.pos[0]+i+1 < 31:
                    CA_cell = self.model.grid.get_cell_list_contents([(self.pos[0]+i+1, self.pos[1])])
                    CA = [obj for obj in CA_cell if isinstance(obj, CarAgent)]
                    if (CA != []):
                        isACar = True
                return isACar
        elif ((self.direction == [0, 1]) and (self.pos[1] < 30)):
            for i in range(dist_t):
                if self.pos[1]+i+1 < 31:
                    CA_cell = self.model.grid.get_cell_list_contents([(self.pos[0], self.pos[1]+i+1)])
                    CA = [obj for obj in CA_cell if isinstance(obj, CarAgent)]
                    if (CA != []):
                        isACar = True
                return isACar
        elif ((self.direction == [-1, 0]) and (self.pos[0] >= 3)):
            for i in range(dist_t):
                CA_cell = self.model.grid.get_cell_list_contents([(self.pos[0]-i-1, self.pos[1])])
                CA = [obj for obj in CA_cell if isinstance(obj, CarAgent)]
                if (CA != []):
                    isACar = True
            return isACar
        elif ((self.direction == [0, -1]) and (self.pos[1] >= 3)): # [0, -1]
            for i in range(dist_t):
                CA_cell = self.model.grid.get_cell_list_contents([(self.pos[0], self.pos[1]-i-1)])
                CA = [obj for obj in CA_cell if isinstance(obj, CarAgent)]
                if (CA != []):
                    isACar = True
            return isACar
        else:
            return isACar
        
        return isACar

    def carHasCrashed(self):
        len(self.model.grid.get_cell_list_contents([self.pos]))
        if len(self.model.grid.get_cell_list_contents([self.pos])) > 1:
            self.crashStatus = 1
            return True
        return False

    def move(self):
        nextcar = self.checkCarFront()
        if not self.carHasCrashed():
            print(f"Car: {self.unique_id}, direction: {self.direction}, nextCar: {nextcar}")
            # print(self.velocity)

            if (nextcar == True):
                print(f"The velocity is: {self.velocity}")
                if self.velocity <= 2:
                    if self.velocity == 2:
                        self.velocity = 1
                    else:
                        self.velocity = 0
                else:
                    self.velocity = 1
                    #COMPORTAMIENTO IMPRUDENTE DEL AUTOMOVIL (LAZY)
            elif(self.distLeft >= 0 and ((self.TFL.light == 2))):
                if self.distLeft ==0:
                    self.velocity = 0
                elif self.distLeft >= self.velocity:
                    self.velocity = ceil(self.velocity/2)
                    self.distLeft -= self.velocity
            elif(self.distLeft <=0 and (self.TFL.light == 1) or (self.TFL.light == 0)):
                if self.distLeft <= self.velocity:
                    self.velocity = self.velocity*2
            dx = (self.direction[0] * self.velocity) 
            dy = (self.direction[1] * self.velocity)

            self.distLeft -= self.velocity
            print(f"prev pos: {self.pos}")
            newPos = (self.pos[0] + dx, self.pos[1] + dy)
            self.model.grid.move_agent(self, newPos)

            if self.distLeft < -17:
                if self.direction == [0, 1]:    # up
                    self.distLeft = self.TFL.pos[1] - self.pos[1]
                elif self.direction == [0, -1]: # down
                    self.distLeft = self.pos[1] - self.TFL.pos[1]
                elif self.direction == [-1, 0]: # left
                    self.distLeft = self.pos[0] - self.TFL.pos[0]
                else:                           # right
                    self.distLeft = self.TFL.pos[0] - self.pos[0]      

                # and change velocity
                self.velocity = choice([1, 2, 3, 4])          

            print(f"distLeft: {self.distLeft}")
        

    def stage_one(self):
        pass
    def stage_two(self):
        #print("stage_two")
        pass
    def stage_three(self):
        #print("stage_three")
        
        #print(f"id: {self.TFL.unique_id},\tlight: {self.TFL.light},\tagent_position: {self.pos}")
        self.move()