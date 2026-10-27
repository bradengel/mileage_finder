# mileage calculator

## requirements

### Python modules
- requests

### input files
- must be in csv format
- state must be in two letter notation
- by default, origins file is origins.csv in the same directory as the script
- by default, destinations file is destinations.csv in the same directory as the script

#### origin file
- must have columns
    - `first name`
    - `last name`
    - `Street address`
    - `city`
    - `state`
    - `Zip Code`

#### destination file
- must have columns:
    - `name`
    - `Street address`
    - `city`
    - `state`
    - `Zip Code`

### Google APIs
- The following APIs must be enabled in the google cloud account
    - Address Validation
    - Routes
- A valid API key must be provided during the script runtime

## Output
This script generates a csv named `[yyyymmdd]_distances_[hhmmss].csv` using the date and time of when the distances are being found in the script (after address validation, though it doesn't really matter).  This csv uses the excel dialect.

## CLI Arguments
- `-h, --help`
    - description of cli arguments
- `-o, --Origins ORIGINS`
    - ORIGINS is the path (absolute or relative) of the origins csv file.
    - defaults to origins.csv
- `-d, --Destinations DESTINATIONS`
    - DESTINATIONS is the bath (absolute or relative) of the destinations csv file.
    - defauts to destinations.csv
- `-pl, --Polyline {True,False}`
    - boolean of whether to include the encoded polyline in the csv file.
    - defaults to True

## Polyline
The script will return a polyline by default that can be used to verify routes.  More information on what a polyline is can be found here: https://developers.google.com/maps/documentation/utilities/polylinealgorithm

Last known location of the polyline decoder: https://developers.google.com/maps/documentation/utilities/polylineutility