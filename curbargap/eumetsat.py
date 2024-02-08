import eumdac
import datetime
import shutil
import requests
import time
import fnmatch


consumer_key = 'L7APfsh_aK3ow6g8DDuLeWUm3W0a'
consumer_secret = 'NA8sF1gc8q_heeCkvAypMulqK6Qa'
cred = (consumer_key, consumer_secret)
token = eumdac.AccessToken(cred)
try:
    print(f"This token '{token}' expires {token.expiration}")
except requests.exceptions.HTTPError as exc:
    print(f"Error when trying the request to the server: '{exc}'")

datastore = eumdac.DataStore(token)
selected_collection = datastore.get_collection('EO:EUM:DAT:MSG:HRSEVIRI')

#x = 0 
#latest_available = None
#for col in selected_collection.search():
#	latest_available = col
#	if x >  3:
#		break
#	x = x+1
#breakpoint()

latest = selected_collection.search().first()

#latest = latest_available

try:
    print(latest)
except eumdac.datastore.DataStoreError as error:
    print(f"Error related to the data store: '{error.msg}'")
except eumdac.collection.CollectionError as error:
    print(f"Error related to the collection: '{error.msg}'")
except requests.exceptions.RequestException as error:
    print(f"Unexpected error: {error}")

datatailor = eumdac.DataTailor(token)
try:
    print(datatailor.quota)
except eumdac.datatailor.DataTailorError as error:
    print(f"Error related to the Data Tailor: '{error.msg}'")
except requests.exceptions.RequestException as error:
    print(f"Unexpected error: {error}")
#chain = eumdac.tailor_models.Chain(
#    product='HRSEVIRI',
#    format='png_rgb',
#    filter='hrseviri_natural_color',
#    projection='geographic',
#    roi='nw_europe'
#)
#chain = eumdac.tailor_models.Chain(
#    product='HRSEVIRI',
#    format='png_rgb',
#    filter={"bands" : ["channel_3","channel_2","channel_1"]},
#    projection='geographic',
#    roi='west_africa'
#)

chain = eumdac.tailor_models.Chain(
    id='hrseviri_nc_west-africa',
    name='Native to PNG of West Africa',
    description='Convert a SEVIRI Native product to PNG with subsetting the region of West Africa',
    product='HRSEVIRI',
    format='png_rgb',
    filter='hrseviri_natural_color',
    projection='geographic',
    roi='west_africa')

try:
    datatailor.chains.create(chain)
except eumdac.datatailor.DataTailorError as error:
    print(f"Data Tailor Error", error)
except requests.exceptions.RequestException as error:
    print(f"Unexpected error: {error}")


for chain in datatailor.chains.search(product="HRSEVIRI"):
    try:
        print(chain)
    except eumdac.datatailor.DataTailorError as error:
        print(f"Data Tailor Error", error)
    except requests.exceptions.RequestException as error:
        print(f"Unexpected error: {error}")
    print('---')
breakpoint()

chain = datatailor.chains.read('hrseviri_nc_western_europe_JPG')
customisation = datatailor.new_customisation(latest, chain)

try:
    print(f"Customisation {customisation._id} started.")
except eumdac.datatailor.DataTailorError as error:
    print(f"Error related to the Data Tailor: '{error.msg}'")
except requests.exceptions.RequestException as error:
    print(f"Unexpected error: {error}")

status = customisation.status
sleep_time = 10 # seconds

# Customisation Loop
while status:
    # Get the status of the ongoing customisation
    status = customisation.status

    if "DONE" in status:
        print(f"Customisation {customisation._id} is successfully completed.")
        break
    elif status in ["ERROR","FAILED","DELETED","KILLED","INACTIVE"]:
        print(f"Customisation {customisation._id} was unsuccessful. Customisation log is printed.\n")
        print(customisation.logfile)
        break
    elif "QUEUED" in status:
        print(f"Customisation {customisation._id} is queued.")
    elif "RUNNING" in status:
        print(f"Customisation {customisation._id} is running.")
    time.sleep(sleep_time)

breakpoint()
png, = fnmatch.filter(customisation.outputs, '*.jpg')

jobID= customisation._id

print(f"Dowloading the JPG output of the customisation {jobID}")

try:
    with customisation.stream_output(png,) as stream, \
            open(stream.name, mode='wb') as fdst:
        shutil.copyfileobj(stream, fdst)
    print(f"Dowloaded the PNG output of the customisation {jobID}")
except eumdac.datatailor.CustomisationError as error:
    print(f"Data Tailor Error", error)
except requests.exceptions.RequestException as error:
    print(f"Unexpected error: {error}")
breakpoint()
