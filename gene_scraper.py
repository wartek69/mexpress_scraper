import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import Select
import sys

input_file_name = 'other'
genes_file_path = '/home/alex/scraping_genes/gene_files'
chrome_driver_loc = '/home/alex/chromedriver_linux64/chromedriver'
class GeneScraper:
    def __init__(self):

        chrome_options = webdriver.ChromeOptions()
        prefs = {"download.default_directory" : f"{genes_file_path}/{input_file_name}"}
        chrome_options.add_experimental_option("prefs",prefs)

        self.driver = webdriver.Chrome(chrome_driver_loc, options=chrome_options)
        self.driver.maximize_window()
        self.driver.get("https://mexpress.be/")

    def search_gene(self, gene_name):
        name_input = self.driver.find_element(By.ID, 'name-input')
        name_input.clear()
        name_input.send_keys(gene_name)

    def select_type(self, cancer_type):
        type_input = self.driver.find_element(By.ID,'cancer-type')
        type_input.clear()
        type_input.send_keys(cancer_type)
        cancer_type_list = self.driver.find_element(By.XPATH, '//html/body/aside/div/section[3]/div[2]/ul')
        time.sleep(1)
        cancer_type_list.find_element(By.CSS_SELECTOR, "li:not([style*='display: none;'])").click()
    
    def plot(self):
        self.driver.find_element(By.CLASS_NAME, 'button--plot').click()
        time.sleep(1)
        error_message = self.driver.find_element(By.CLASS_NAME, 'message--error')
        if error_message.is_displayed():
            return False
        plot_button_classes = self.driver.find_element(By.XPATH, '/html/body/aside/div/section[4]/div').get_attribute('class')
        while 'button--inactive' in plot_button_classes:
            print('Waiting till new gene is plotted...')
            time.sleep(1)
            plot_button_classes = self.driver.find_element(By.XPATH, '/html/body/aside/div/section[4]/div').get_attribute('class')
        return True
    
    def is_correct_cancer_type_plotted(self, cancer_type_slug, expected_gene_name):
        """Checks if we are scraping the correct page to make sure our data is correct.
        Atm only way to be sure that correct files are downloaded, no cancer type identifier is present in the file itself.
        """

        if cancer_type_slug == 'lgg':
            expected_cancer_type =  'brain lower grade glioma'
        elif cancer_type_slug == 'luad':
            expected_cancer_type = 'lung adenocarcinoma'
        else: 
            print('unsupported genetype received!')
            return False
        
        report_title = self.driver.find_element(By.XPATH, "/html/body/main/div[2]/div[2]/p[1]").text
        report_title_parts = report_title.split('—')
        report_gene_name = report_title_parts[0].strip().upper()
        report_cancer_type = report_title_parts[1].strip().lower()
        print(f'Extracted cancer type {report_cancer_type} and gene name {report_gene_name}')
        return report_gene_name == expected_gene_name.upper() and report_cancer_type == expected_cancer_type.lower()

    def select_data_type(self):
        data_type_selector = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//html/body/main/div[2]/ul/li[11]/select'))
        )
        select_box = Select(data_type_selector)
        select_box.select_by_value('methylation data')
    
    def download_file(self):
        time.sleep(2)
        #WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//html/body/main/div[2]/ul/li[10]/select")))
        #WebDriverWait(self.driver, 20).until(lambda d: d.execute_script('return (document.readyState == "complete" || document.readyState == "interactive")'))
        download_select_box = Select(self.driver.find_element(By.XPATH,'//html/body/main/div[2]/ul/li[10]/select'))
        download_select_box.select_by_value('tsv')
        print('clicked')
        #cself.driver.find_element(By.XPATH,'//html/body/main/div[2]/ul/li[10]/select').click()
        #self.driver.find_element(By.XPATH,'//html/body/main/div[2]/ul/li[10]/select/optgroup[2]/option[1]').click()
    
    def dispose(self):
        self.driver.close()
    
def rename_downloaded_file(new_name):
    downloaded_file_path = f'{genes_file_path}/{input_file_name}/plottedData.txt'
    while not os.path.exists(downloaded_file_path):
        print('waiting till file is downloaded...')
        time.sleep(1)

    os.rename(downloaded_file_path, f'{genes_file_path}/{input_file_name}/{new_name}')

if __name__ == '__main__':
    gene_scraper = GeneScraper()
    cancer_types = ['lgg', 'luad']
    with open(f'{input_file_name}.txt') as lines:
        for line in lines:
            for cancer_type in cancer_types:
                gene_name = line.strip()
                print(f'Downloading {gene_name} gene files')
                gene_scraper.search_gene(gene_name)
                gene_scraper.select_type(cancer_type)
                plot_succesfull = gene_scraper.plot()
                if not plot_succesfull:
                    print('Element cannot be downloaded from the site!')
                    continue
                is_correct_plot = gene_scraper.is_correct_cancer_type_plotted(cancer_type, gene_name)
                if not is_correct_plot:
                    print('Analysing wrong plot, check why this might be happening! Exiting script!!')
                    sys.exit()
                gene_scraper.select_data_type()
                gene_scraper.download_file()
                rename_downloaded_file(f'{gene_name}_{cancer_type}.txt')
                #time.sleep(5)
    gene_scraper.driver.close()
