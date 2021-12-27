## Gene scraper
Scrapes mexpress.be DNA methylation data for cancer types LGG and LUAD. Built in checks are provided to check if the correct file is being downloaded as mexpress file format does not specify the cancer type and a naive scraping implementation would download wrong files without the user noticing.
## Usage
To use the script python3 and selenium with a chrome driver has to be installed.
Before running the script you have to edit the following lines:
```
input_file_name = 'other'
genes_file_path = '/home/alex/scraping_genes/gene_files'
chrome_driver_loc = '/home/alex/chromedriver_linux64/chromedriver'
```
Example input files are provided in this repo. You need to create with the same name as the input file in this project's root/gene_files directory before running the script, this directory will be used to download the files to.
