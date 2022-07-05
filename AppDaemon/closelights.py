import appdaemon.plugins.hass.hassapi as hass
import datetime
import time
#
# Close Lights
#
# Args:
#

class CloseLights(hass.Hass):

  def initialize(self):
     self.log("Hello from CloseLights")
     runtime = datetime.time(6, 35, 0)
     self.run_daily(self.turn_light_off, runtime, constrain_days = "mon,tue,wed,thu,fri")

  def turn_light_off(self, kwargs):
     self.log("Closing lights...")
     self.turn_off('light.hue_color_lamp_1')
     self.turn_off('light.hue_color_lamp_3')
     self.turn_off('light.hue_color_lamp_5')

