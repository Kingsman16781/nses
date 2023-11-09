import requests
from bs4 import BeautifulSoup
import re
import json

host = "https://www.investorgain.com/"


def scrape_inner_data(link_url):
    merger = []
    extracted_data = None
    dumm = []

    r = requests.get(host + link_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find_all('table')
    headers = [th.get_text(strip=True)
               for th in table[0].find('thead').find_all('th')]
    data_rows = []
    for row in table[0].find('tbody').find_all('tr'):
        row_data = {}
        cells = row.find_all('td')
        for i in range(len(cells)):
            row_data[headers[i]] = cells[i].get_text(strip=True)
        data_rows.append(row_data)
    extracted_data = data_rows
    obj = new_rt(table[1])
    dumm.append(obj)
    merger.append(extracted_data)
    merger.append(dumm)
    merger.append([
        {
            "period": [],
            "Total Assets": [],
            "Total Revenue": [],
            "PAT": [],
            "Net worth": [],
            "Reserve & Surplus": [],
            "Total Borrowings": []
        }
    ])
    return merger


def new_rt(table):
    data_dict = {}
    if table:
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if len(columns) == 2:
                left_side = columns[0].get_text(strip=True)
                right_side = columns[1].get_text(strip=True)
                if right_side != '':
                    data_dict[left_side] = right_side
                else:
                    data_dict[left_side] = 'NA'

    return data_dict


r = requests.get('https://www.investorgain.com/report/live-ipo-gmp/331/?r2')

soup = BeautifulSoup(r.text, 'html.parser')
table = soup.find(id="mainTable")

extracted_data = []
columns = [th.get_text(strip=True) for th in table.find('tr').find_all('th')]

for row in table.find_all('tr')[1:]:
    row_data = {}
    first_cell = row.find('td', {'data-label': 'IPO'})
    if first_cell:
        name_element = first_cell.find('a')
        if name_element:
            name = name_element.get_text(strip=True)
            for span_element in name_element.find_all('span'):
                name = name.replace(span_element.get_text(strip=True), "")
            row_data[columns[0]] = name

        status_span = first_cell.find('span', class_='badge')
        if status_span:
            status = status_span.get_text(strip=True)
            row_data["Status"] = status

        link_element = first_cell.find('a', href=True)
        if link_element:
            link = link_element['href']
            row_data["Link"] = link
            inner_data = scrape_inner_data(link)
            row_data['Data'] = inner_data

        for index, cell in enumerate(row.find_all(['td', 'th'])[1:]):
            cell_text = cell.get_text(strip=True)
            if not cell_text:
                inner_elements = cell.find_all(True)
                if len(inner_elements) == 0:
                    row_data[columns[index + 1]] = "NA"

                for inner_element in inner_elements:
                    if inner_element.name == 'img':
                        img_title = inner_element.get('title')
                        if img_title:
                            numeric_values = re.findall(r'\d+', img_title)
                            if numeric_values:
                                row_data[columns[index + 1]
                                         ] = int(numeric_values[0])
                    else:
                        row_data[columns[index + 1]] = "NA"
            else:
                if cell_text.startswith("Rating "):
                    rating = cell_text.split("/")[0].split()[-1]
                    row_data[columns[index + 1]] = rating
                else:
                    if cell_text != '':
                        row_data[columns[index + 1]] = cell_text
                    else:
                        row_data[columns[index + 1]] = 'NA'

        extracted_data.append(row_data)

json_file_path = 'table_data.json'

with open(json_file_path, 'w') as json_file:
    json.dump(extracted_data, json_file, indent=4)

print(f"Data saved to {json_file_path}")
