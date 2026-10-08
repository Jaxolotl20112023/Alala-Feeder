from gpiozero import Motor, RotaryEncoder
from time import perf_counter

def main(): 

  motor = Motor(forward=0,backward=0)
  encoder = RotaryEncoder(a=0,b=0,max_steps=0)

  while True:

    starttime = perf_counter()

    while perf_counter() - starttime < 2:
      motor.forward(speed=0.5)

      print(encoder.steps)

    starttime = perf_counter() 

    while perf_counter - starttime < 2:
      motor.backward(speed=0.5)
      
      print(encoder.steps)


if __name__ == "__main__":
  main()