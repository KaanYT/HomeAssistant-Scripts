import appdaemon.plugins.hass.hassapi as hass
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#
# Gas Bill App
#
# Args:
#

class HotWaterBill(hass.Hass):

  User = "XXXXX"
  Pass = "XXXX"

  def initialize(self):
     runtime = datetime.time(6, 35, 0) # datetime.time()
     self.setTheSensorValue(runtime)
     self.run_daily(self.setTheSensorValue, runtime) # run_hourly

  def get_usage(self, current, last):
     if last > current:
       return current
     else:
       return current-last

  def getChromeOptions(self):
     chrome_options = Options()
     chrome_options.add_argument('--headless')
     chrome_options.add_argument('--no-sandbox')
     chrome_options.add_argument('--disable-gpu')
     chrome_options.add_argument('--disable-dev-shm-usage')
     return chrome_options

  def clickElementAndWait(self, web_driver, path_type, path, wait=5):
     web_driver.find_element(path_type,path).click()
     time.sleep(wait)

  def getPageAndWait(self, web_driver, page, wait=5):
     web_driver.get(page)
     time.sleep(wait)

  def setTheSensorValue(self, kwargs):
     self.log("Getting Data from UludagEnerji...")
     options = self.getChromeOptions()
     driver = webdriver.Chrome('chromedriver', options=options)
     self.getPageAndWait(driver, "http://panel.uludagenerji.com/login")
     # Select Individual Flat
     self.clickElementAndWait(driver, "id", "bab")
     # Login
     driver.find_element("id","kad").send_keys(HotWaterBill.User)
     driver.find_element("id","sifre").send_keys(HotWaterBill.Pass)
     self.clickElementAndWait(driver, "id", "Button1")

     # Open Previous Bills
     self.getPageAndWait(driver, "http://panel.uludagenerji.com/paylasimyap?q=2&d=1")
     billing_period = driver.find_element('xpath','//*[@id="ContentPlaceHolder1_GridView4"]/tbody/tr[2]/td[2]').text
     due_date = driver.find_element('xpath','//*[@id="ContentPlaceHolder1_GridView4"]/tbody/tr[2]/td[3]').text
     amount = driver.find_element('xpath','//*[@id="ContentPlaceHolder1_GridView4"]/tbody/tr[2]/td[4]').text

     # Open Usage Page
     driver.get("http://panel.uludagenerji.com/okumayap")
     time.sleep(5)
     # Open Counter Information
     self.clickElementAndWait(driver,'xpath','// *[ @ id = "ContentPlaceHolder1_GridView4_Button1_0"]')
     # Get Counter Details
     total_usage_str = driver.find_element('xpath',
        '//*[@id="ContentPlaceHolder1_ASPxPageControl1_sendeks"]').get_property(
        "value")
     flow_str = driver.find_element('xpath','//*[@id="ContentPlaceHolder1_ASPxPageControl1_TextBox6"]').get_property(
          "value")
     inlet_temp_str = driver.find_element('xpath',
          '//*[@id="ContentPlaceHolder1_ASPxPageControl1_TextBox2"]').get_property(
          "value")
     output_temp_str = driver.find_element('xpath',
          '//*[@id="ContentPlaceHolder1_ASPxPageControl1_TextBox3"]').get_property(
          "value")
     # Get Counter Details Daily
     self.clickElementAndWait(driver,'xpath','//*[@id="ContentPlaceHolder1_ASPxPageControl1_T1T"]')
     # Usage
     last_usage_str = driver.find_element('xpath',
      '//*[@id="ContentPlaceHolder1_ASPxPageControl1_GridView2"]/tbody/tr[2]/td[5]').text
     last_flow_str = driver.find_element('xpath',
      '//*[@id="ContentPlaceHolder1_ASPxPageControl1_GridView2"]/tbody/tr[2]/td[7]').text
     previous_flow_str = driver.find_element('xpath',
      '//*[@id="ContentPlaceHolder1_ASPxPageControl1_GridView2"]/tbody/tr[3]/td[7]').text

     # Convert
     total_usage = int(total_usage_str)
     monthly_usage = int(last_usage_str)

     flow = float(flow_str.replace(',', '.'))
     last_flow = float(last_flow_str.replace(',', '.'))
     previous_flow = float(previous_flow_str.replace(',', '.'))
     last_usage_flow = self.get_usage(last_flow, previous_flow)
     last_usage_flow_lt = int(last_usage_flow * 1000)

     inlet_temp = float(inlet_temp_str.replace(',', '.'))
     output_temp = float(output_temp_str.replace(',', '.'))

     # Set Information
     attributes = {}
     attributes['icon'] = 'mdi:gas-cylinder'
     attributes['inlet_temp'] = inlet_temp
     attributes['output_temp'] = output_temp
     attributes['monthly_usage'] = monthly_usage
     self.set_state("sensor.hot_water_monthly_usage", state = monthly_usage, attributes=attributes)

     attributes = {}
     attributes['icon'] = 'mdi:gas-cylinder'
     attributes['total'] = flow
     attributes['flow_in_m3'] = last_usage_flow
     self.set_state("sensor.hot_water_flow", state = last_usage_flow_lt, attributes=attributes)

     attributes = {}
     attributes['icon'] = 'mdi:gas-cylinder'
     attributes['billing_period'] = billing_period
     attributes['due_date'] = due_date
     self.set_state("sensor.hot_water_bill", state = amount, attributes=attributes)
