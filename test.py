from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

import time
from config.ec2_regions import ec2_region_map
from config.ec2_os import ec2_os_map
from config.ec2_storage_map import ec2_storage_map
from config.ec2_pricing_strategy import ec2_payment_options, ec2_pricing_model, ec2_reservation_term


calculator_link = "https://calculator.aws/#/estimate"
ec2_link = "https://calculator.aws/#/createCalculator/EC2"


def click_element(driver: webdriver, element_id: str):
    """
    Locates the element in the page, specified by element_id
    Clicks on it
    returns : <does not return>
    """
    element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
    try:
        element.click()
    except ElementClickInterceptedException:  # occasionally we have to use jscript
        driver.execute_script("arguments[0].click();", element)


def type_and_enter(driver: webdriver, element_id: str, entry: str):
    """
    Locates the element in the page, specified by element_id
    Clears the text, and enters new text specified by entry
    returns : <does not return>
    """
    element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
    element.clear()
    element.send_keys(entry)
    element.send_keys(Keys.ENTER)


def add_ec2(driver: webdriver,
            ec2_description: str,
            instance: str,
            storage_type: str = "gp3",
            operating_system: str = 'Windows Server',
            storage_amount_in_GB: int = 200,
            units: int = 1,
            utilization: int = 100,
            region: str = "",
            pricing_model: str = "",
            reservation_term: str = "",
            payment_option: str = ""):

    # Visit EC2 page
    driver.get(ec2_link)
    time.sleep(1)
    ids = [elem.get_attribute('id') for elem in driver.find_elements_by_xpath('//*[@id]')]
    with open('elements.txt', 'w') as id_file:
        for k, elem_id in enumerate(ids):
            id_file.write(f'{k}. {elem_id}\n')

    # Enter Description
    description_elem = ids[38]
    type_and_enter(driver, element_id=description_elem, entry=ec2_description)

    # Set the region if needed
    if region:
        region_elem = ids[41]
        click_element(driver, element_id=region_elem)
        region_selection_elem = f"{region_elem}-dropdown-option-{ec2_region_map[region]}"
        click_element(driver, element_id=region_selection_elem)

        # Not particularly proud of the following 3 lines of code ;)
        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB * 4)
        actions.send_keys(Keys.ENTER)
        actions.perform()

    # Get ids of the important fields
    # OS Selection
    os_elem = ids[51]
    os_selection_elem = f"{'-'.join(os_elem.split('-')[:3])}-dropdown-option-{ec2_os_map[operating_system]}"
    click_element(driver, element_id=os_elem)
    click_element(driver, element_id=os_selection_elem)

    # Instance Type
    instance_name_elem = ids[57]
    click_element(driver, element_id=instance_name_elem)
    # Get id of the newly appearing textbox for instance type
    new_ids = [elem.get_attribute('id') for elem in driver.find_elements_by_xpath('//*[@id]')]
    instance_type_elem = new_ids[58]
    type_and_enter(driver, element_id=instance_type_elem, entry=instance)

    # Quantity and Utilization
    quantity_elem = ids[74]
    type_and_enter(driver, element_id=quantity_elem, entry=str(units))
    utilization_elem = ids[77]
    type_and_enter(driver, element_id=utilization_elem, entry=str(utilization))

    # Pricing Model
    if pricing_model:
        pricing_elem = ids[ec2_pricing_model[pricing_model]]
        reserve_term_elem = ids[ec2_reservation_term[reservation_term]]
        payment_option_elem = ids[ec2_payment_options[payment_option]]

        click_element(driver, element_id=pricing_elem)
        click_element(driver, element_id=reserve_term_elem)
        click_element(driver, element_id=payment_option_elem)

    # Storage
    storage_elem = ids[108]
    storage_selection_elem = f"{'-'.join(storage_elem.split('-')[:3])}-dropdown-option-{ec2_storage_map[storage_type]}"
    storage_amount_elem = ids[112]
    click_element(driver, element_id=storage_elem)
    click_element(driver, element_id=storage_selection_elem)
    type_and_enter(driver, element_id=storage_amount_elem, entry=str(storage_amount_in_GB))

    # Submit
    submit_button_xpath = '//*[@id="e-c2next"]/div/div[2]/div/div/awsui-button[2]/button'
    submit_button = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.XPATH, submit_button_xpath))
    )
    submit_button.click()


if __name__ == '__main__':
    chrome_driver = webdriver.Chrome()
    chrome_driver.get(calculator_link)
    add_ec2(driver=chrome_driver,
            ec2_description="EC2-1",
            region="Asia Pacific (Jakarta)",
            instance="t3.small",
            pricing_model="Compute Savings Plans",
            reservation_term="1 Year",
            payment_option="No Upfront")
    add_ec2(driver=chrome_driver,
            ec2_description="EC2-1",
            region="Asia Pacific (Jakarta)",
            instance="t3.small",
            pricing_model="Compute Savings Plans",
            reservation_term="3 Year",
            payment_option="No Upfront")
    # add_ec2(driver=chrome_driver, ec2_description="EC2-2", instance="t3.xlarge", storage_type="io2", storage_amount_in_GB=1000)
    # add_ec2(driver=chrome_driver, ec2_description="EC2-3", instance="t3.medium", operating_system="Linux")
    # add_ec2(driver=chrome_driver, ec2_description="EC2-3", instance="t3.2xlarge", storage_type="gp2")
