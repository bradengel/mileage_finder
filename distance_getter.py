#!/usr/bin/python

# import libraries
import csv
import requests
import getpass
import json
import datetime
import argparse

# variable definition
origins_headers = ['first name', 'last name', 'street address', 'city', 'state', 'zip code']
destinations_headers = ['name', 'street address', 'city', 'state', 'zip code']
validated_address_header = "Validated Address"
address_validation_endpoint = "https://addressvalidation.googleapis.com/v1:validateAddress"

# route api variables
routes_endpoint = "https://routes.googleapis.com/directions/v2:computeRoutes"
travel_mode = "DRIVE"
routing_preference = "TRAFFIC_UNAWARE"
alternate_routes = "False"

# handle command line arguments
parser = argparse.ArgumentParser(
    prog = "Distance Finder",
    description = "Script to get the distance between each origin and each destination in the provided csv files."
)

parser.add_argument(
    "-o",
    "--Origins",
    default='origins.csv',
    help="Path of origins csv file. Defaults to origins.csv in the directory of the script."
    )

parser.add_argument(
    "-d",
    "--Destinations",
    default='destinations.csv',
    help="Path of destinations csv file. Defaults to destinations.csv in the directory of the script."
    )

parser.add_argument(
    "-pl",
    "--Polyline",
    type=bool,
    choices=['True', 'False'],
    default='True',
    help="Add polyline filed to distances csv file (Recommended). Defaults to True."
    )

args = parser.parse_args()

origins_file = args.Origins
destinations_file = args.Destinations
return_polyline = args.Polyline

# address class
class address(object):
    def __init__(self, street, city, state, zip):
        self.street = street
        self.city = city
        self.state = state
        self.zip = zip
        self.validation_status = "null"
        self.validated_address = "null"
        self.complete = "null"
        self.lat = "null"
        self.lon = "null"
        self.id = "null"

    def __str__(self):
        return "Street: " + str(self.street) + "\nCity: " + str(self.city) + "\nState: " + str(self.state) + "\nZip: " + str(self.zip) + "\nValidation Status: " + str(self.validation_status) + "\nValidated Address: " + str(self.validated_address) + "\nIs Complete: " + str(self.complete) + "\nLatitude: " + str(self.lat) + "\nLongitude: " + str(self.lon) + "\nPlace ID: " + str(self.id)

    def validate(self, params):
        validation_request = {
            "address": {
                "regionCode": "US",
                "postalCode": self.zip,
                "locality": self.city,
                "addressLines": [ self.street ]
            }
        }

        # api call to google maps address validation
        validation_result = requests.post(url=address_validation_endpoint, json=validation_request, params=params)

        # set attributes
        self.validation_status = validation_result.json()['result']['verdict']['possibleNextAction']
        self.validated_address = validation_result.json()['result']['address']['formattedAddress']
        self.complete = validation_result.json()['result']['verdict']['addressComplete']
        self.lat = validation_result.json()['result']['geocode']['location']['latitude']
        self.lon = validation_result.json()['result']['geocode']['location']['longitude']
        self.id = validation_result.json()['result']['geocode']['placeId']

# compare required headers with headers in files.  If headers are incorrect, state as such and exit.
def header_validation(required_header, file):
    # get origin file header
    with open(file, newline='', encoding='utf-8-sig') as origins:
        reader = csv.reader(origins, delimiter=',', quotechar='|')
        header = next(reader)
        lower_header = [s.casefold() for s in header]
        lines = sum(1 for row in reader)

        # check to see if required headers are present, case insensitive
        if all(x in lower_header for x in required_header):
            print(file + ' contains the required headers')

            # if true, initialize list for headers, case sensitive
            # actual_headers = []

            # for i in required_header:
            #     actual_headers.append(header[lower_header.index(i)])

            return header, lines

        else:
            # initialize missing headers list
            missing_headers = []

            # check to see which headers are missing
            for i in required_header:
                if i not in lower_header:
                    missing_headers.append(i)

            # output missing headers
            print(file + ' is missing the following headers')
            return missing_headers
            exit()

def index_header(reference_header, actual_header):

    return_dict = {}

    for i in reference_header:
        return_dict[i] = next(j for j,v in enumerate(actual_header) if v.lower() == i)

    return return_dict

# distance api call, requires placeIDs for origin and destination
def get_distance(origin, destination, api_key):
    # format request

    route_request = {
        "origin": {
            "placeId": origin
        },
        "destination": {
            "placeId": destination
        },
        "routingPreference": routing_preference,
        "travelMode": travel_mode
    }

    # return polyline or not
    if return_polyline:
        field_mask = "routes.distanceMeters,routes.polyline.encodedPolyline"
    else:
        field_mask = "routes.distanceMeters"

    # headers
    headers = {
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': field_mask
    }

    result = requests.post(url=routes_endpoint, json=route_request, headers=headers)

    routes = result.json()['routes'][0]
    distanceMeters = routes['distanceMeters']
    distanceMiles = round(distanceMeters * 0.0006213712, 2)

    polyline = routes['polyline']['encodedPolyline']

    return distanceMiles, polyline

def main():
    # header validation and variable assignment
    # ensure that required headers exist and get the correct case of header
    actual_origins_headers, origin_lines  = header_validation(origins_headers, origins_file)
    actual_destinations_headers, destination_lines = header_validation(destinations_headers, destinations_file)

    # index values of headers for easy, case-insensitive reference
    dest_header_index = index_header(destinations_headers, actual_destinations_headers)
    origin_header_index = index_header(origins_headers, actual_origins_headers)

    # print(origin_header_index)

    # ask for the api key
    api_key = getpass.getpass("Please input your api key: ")
    params = {'key': api_key}

    # initialize destaion dictionary
    dest_dict = {}

    with open(destinations_file, newline='', encoding='utf-8-sig') as destinations:
        destinationreader = csv.DictReader(destinations, delimiter=',', quotechar='|', dialect='excel')
        for row in destinationreader:

            # set variables
            destination = row[actual_destinations_headers[dest_header_index['name']]]
            street = row[actual_destinations_headers[dest_header_index['street address']]]
            city = row[actual_destinations_headers[dest_header_index['city']]]
            state = row[actual_destinations_headers[dest_header_index['state']]]
            zip = row[actual_destinations_headers[dest_header_index['zip code']]]

            # set class attributes
            dest_dict[destination] = address(street, city, state, zip)

            # run validation
            dest_dict[destination].validate(params)

            # if validation is not successful, tell user which address cannot be validated and exit
            if dest_dict[destination].validation_status != 'ACCEPT':
                print(destination + " has an address that could use fixing.  Please manually validate address using a maps website and try again.")
                exit()

    # # have user confirm destinations
    for i in dest_dict:
        print("\nPlease press 'y' then 'enter' to confirm that the address for " + i + " is correct.")
        print(dest_dict[i].validated_address)
        key = input()
        if key != "y":
            print("address not confirmed, exiting")
            exit()

    print("addresses confirmed, getting distances")

    # calculate rough number of requests
    num_distances = origin_lines * destination_lines
    api_calls = num_distances + origin_lines
    print("\n" + str(num_distances) + " distances will be calculated.  This will total roughly " +  str(api_calls) + " API calls.")
    print("\n Please press 'y' then 'enter' to continue.")
    key = input()
    if key != "y":
        print("Exiting")
        exit()
    # generate headers
    dist_dest_header = []

    # add distance to header
    for i in dest_dict:
        dist_dest_header.append(i + " Distance")

    # add polyline to header
    if return_polyline is True:
        for i in dest_dict:
            dist_dest_header.append(i + " Polyline")

    dist_headers = []
    dist_headers = actual_origins_headers
    dist_headers.append(validated_address_header)
    dist_headers = (dist_headers + dist_dest_header)

    # create and open new file
    filename = datetime.datetime.now().strftime("%Y%m%d") + "_distances_" + datetime.datetime.now().strftime("%H%M%S") + ".csv"
    # print(filename)
    file = open(filename, "x", newline='')

    # initialize distance file dict reader and write header
    dist_writer = csv.DictWriter(file, fieldnames=dist_headers, delimiter=',', dialect='excel')
    dist_writer.writeheader()

    # get distances
    with open(origins_file, 'r', newline='', encoding='utf-8-sig') as origins:
        reader = csv.DictReader(origins, delimiter=',', quotechar='|', dialect='excel')
        for row in reader:
            # line dictionary
            line_dict = dict.fromkeys(dist_headers)

            # populate what we have from the origins file to the line_dict
            for i in row:
                line_dict[i] = row[i]

            street = line_dict[actual_origins_headers[origin_header_index['street address']]]
            city = line_dict[actual_origins_headers[origin_header_index['city']]]
            state = line_dict[actual_origins_headers[origin_header_index['state']]]
            zip = line_dict[actual_origins_headers[origin_header_index['zip code']]]

            origin_address = address(street, city, state, zip)

            origin_address.validate(params)

            # print(origin_address)

            if origin_address.validated_address:
                line_dict[validated_address_header] = origin_address.validated_address
            else:
                line_dict[validated_address_header] = "null"
            # print(line_dict)

            for dest in dest_dict:
                distance, polyline = get_distance(dest_dict[dest].id, origin_address.id, api_key)
                line_dict[dest + " Distance"] = distance

                print("Distance from " + origin_address.validated_address + " to " + dest + " is " + str(distance) + " miles.")

                if return_polyline is True:
                    line_dict[dest + " Polyline"] = polyline
                # print(line_dict)
                # print("polyline: " + polyline)
            dist_writer.writerow(line_dict)
                # print(dest_dict[dest].id)
                # print(get_distance(dest_dict[dest].id, origin_address.id))

    file.close()

if __name__ == "__main__":
    main()