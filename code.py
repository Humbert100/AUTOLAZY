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
