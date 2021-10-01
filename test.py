from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
import time


calculator_link = "https://calculator.aws/#/estimate"
ec2_link = "https://calculator.aws/#/createCalculator/EC2"


def click_element(driver, element_id: str):
    element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
    try:
        element.click()
    except ElementClickInterceptedException:  # occasionally we have to use jscript
        driver.execute_script("arguments[0].click();", element)


def type_and_enter(driver, element_id: str, entry: str):
    element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
    element.clear()
    element.send_keys(entry)
    element.send_keys(Keys.ENTER)


def select_region_in_ec2(driver):
    """
    Selects region in EC2 menu
    :param driver:
    :return:
    """
    region_xpath = '//*[@id="e-c2next"]/div/div[2]/awsui-form/div/div[2]/span/span/div[1]/div/awsui-form-field/div/div[2]/div/div/span/awsui-select'
    singapore_path = '//*[@id="awsui-select-1-dropdown-option-8"]/div/div/div'  # number correspond to region
    change_region_button_xpath = '//*[@id="e-c2next"]/div/div[2]/awsui-form/div/div[2]/span/span/awsui-modal/div[2]/div/div/div[3]/span/div/span[2]/awsui-button[2]/button'

    region = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, region_xpath))
        )
    region.click()
    singapore = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, singapore_path))
        )
    singapore.click()

    change_region = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, change_region_button_xpath))
    )
    change_region.click()


def choose_os(os: str = "Linux") -> str:
    os_map = {
        "Linux": "0",
        "Windows Server": "1",
        "Windows Server with SQL Server Standard": "2",
        "Windows Server with SQl Server Web": "3"
    }

    return os_map[os]


def choose_storage(storage: str = "gp3") -> str:
    storage_map = {
        "gp2": "0",
        "gp3": "1",
        "io2": "3",
        "st1": "4"
    }
    return storage_map[storage]


def add_ec2(driver,
            ec2_description: str,
            instance: str,
            storage_type: str = "gp3",
            operating_system: str = 'Windows Server',
            storage_amount_in_GB: int = 200,
            units: int = 1,
            set_region: bool = False):
    # Visit EC2 page
    driver.get(ec2_link)
    time.sleep(1)
    ids = driver.find_elements_by_xpath('//*[@id]')

    # Enter Description
    description_id = ids[30].get_attribute('id')
    type_and_enter(driver, element_id=description_id, entry=ec2_description)

    # Set the region if needed
    if set_region:
        select_region_in_ec2(driver)

    # Get ids of the important fields
    os = ids[43].get_attribute('id')
    os_selection = f"{'-'.join(os.split('-')[:3])}-dropdown-option-{choose_os(operating_system)}"
    instance_name = ids[49].get_attribute('id')
    quantity = ids[66].get_attribute('id')
    storage = ids[100].get_attribute('id')
    storage_selection = f"{'-'.join(storage.split('-')[:3])}-dropdown-option-{choose_storage(storage_type)}"
    storage_amount = ids[104].get_attribute('id')
    submit_button_xpath = '//*[@id="e-c2next"]/div/div[2]/div/div/awsui-button[2]/button'

    # Start clicking those elements
    click_element(driver, element_id=os)
    click_element(driver, element_id=os_selection)
    click_element(driver, element_id=instance_name)

    # Get id of the newly appearing textbox for instance type
    ids = driver.find_elements_by_xpath('//*[@id]')
    instance_type = ids[50].get_attribute('id')  # f"awsui-autosuggest-{id + 15}"

    # Continue clicking
    type_and_enter(driver, element_id=instance_type, entry=instance)
    type_and_enter(driver, element_id=quantity, entry=str(units))
    click_element(driver, element_id=storage)
    click_element(driver, element_id=storage_selection)
    type_and_enter(driver, element_id=storage_amount, entry=str(storage_amount_in_GB))

    # Submit
    submit_button = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.XPATH, submit_button_xpath))
    )
    submit_button.click()


if __name__ == '__main__':
    chrome_driver = webdriver.Chrome()
    chrome_driver.get(calculator_link)
    add_ec2(driver=chrome_driver, ec2_description="EC2-1", set_region=True, instance="t3.small")
    add_ec2(driver=chrome_driver, ec2_description="EC2-2", instance="t3.xlarge", storage_type="io2", storage_amount_in_GB=1000)
    add_ec2(driver=chrome_driver, ec2_description="EC2-3", instance="t3.medium", operating_system="Linux")
    add_ec2(driver=chrome_driver, ec2_description="EC2-3", instance="t3.2xlarge", storage_type="gp2")
