from NetworkService import NetworkService
from DataService import DataService
from OtaService import OtaService
from LedService import LedService

import Definitions
import CommonServices
import machine
import utime
import sys
from machine import Timer

# for x in range(0, 500):
#   CommonServices.MyLogger.Insert("aaaaa" + str(x))

myLedService = LedService()
myNetworkService = NetworkService()
myDataService = DataService()
myOtaService = OtaService()

myLedService.Starting()

#process timer for special task, like restart device
#run every second
def PerformEverySecond(alarm):
  if CommonServices.MyConfig.IsDeviceRestart():
        machine.reset()
        
  if CommonServices.MyConfig.IsStartOTA():
    if CommonServices.MyConfig.OtaState is not Definitions.OTA_INPROGRESS:
      CommonServices.MyConfig.OtaState = Definitions.OTA_START

  if CommonServices.MyConfig.ReconnectServer >= 0:
    CommonServices.MyConfig.ReconnectServer = CommonServices.MyConfig.ReconnectServer - 1

myAlarm = Timer.Alarm(PerformEverySecond, 1, periodic=True)


#1. NetworkService. Init network (wifi, lora,  lte..). 
#2. DataService. it receives/tranfers data between pycom and cloud/lora gateway, pycom-UART ... base on selected network, selected destination
#3. BusinessService. Process all bussiness logic  of selected project
while True:
  try:

    #setup network,  use MyConfig.NetworkState to check this device alredy setup network or not, it will cause looping in setup network
    if CommonServices.HasNetwork(CommonServices.MyConfig.NetworkState) == False:
      #load network mode again when setup a network
      myNetworkService.NetworkMode = CommonServices.MyConfig.GetNetworkMode()
      myDataService.NetworkMode = CommonServices.MyConfig.GetNetworkMode()
      CommonServices.MyConfig.NetworkState = myNetworkService.Setup()

    #process data
    myDataService.Run()
    
    #process OTA 
    myOtaService.Run()
      
  except OSError as e:
    CommonServices.MyLogger.Insert("exception in main:" + str(e))
    sys.print_exception(e) 




