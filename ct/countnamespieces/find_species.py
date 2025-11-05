# open the csv file
# read the csv and find all the unique species for each location

import csv

def unique_species_by_location(file_path):
    location_species = {}

    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            
            lat = row['decimalLatitude']
            log = row['decimalLongitude']
            location = f"{log},{lat}"
            species = row['scientific name']
            
            if location not in location_species:
                location_species[location] = set()
            
            if species not in location_species[location]:
                location_species[location].add(species)
    
    # Convert sets to lists for easier readability
    for location in location_species:
        location_species[location] = list(location_species[location])
        print(f"Location: {location}, Unique Species Count: {len(location_species[location])}")

    return location_species

# def make_csv(location_species, output_file):
#     with open(output_file, mode='w', newline='') as file:
#         csv_writer = csv.writer(file)
#         csv_writer.writerow(['Location', 'Unique Species Count'])
        
#         for location, species in location_species.items():
#             csv_writer.writerow([location, len(species)])
            
# fucntion to add at the end of the csv the total unique spieces for each location
# find the 'full coordinartes' column and add a new column 'unique species count'
def put_number_of_unique_species_in_csv(input_file, output_file):
    location_species = unique_species_by_location(input_file)
    
    with open(input_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        fieldnames = csv_reader.fieldnames + ['unique species count']
        
        with open(output_file, mode='w', newline='') as output:
            csv_writer = csv.DictWriter(output, fieldnames=fieldnames)
            csv_writer.writeheader()
            
            for row in csv_reader:
                lat = row['decimalLatitude']
                log = row['decimalLongitude']
                location = f"{log},{lat}"
                row['unique species count'] = len(location_species.get(location, []))
                csv_writer.writerow(row)
    
            
# make_csv(unique_species_by_location('data_p_spider.csv'), 'unique_species_by_location.csv')
# unique_species_by_location('data_p_spider.csv')
put_number_of_unique_species_in_csv('CBSS spider collection 29.9.2025csv.csv', 'unique_species_by_location.csv')