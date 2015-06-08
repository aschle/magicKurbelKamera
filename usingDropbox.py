# Vor dem Script habe ich folgendes in der Konsole ausgefuehrt. 

# sudo apt-get install python-dev

# python setup.py install    # lieferte immer Fehler 'Permission denied' 

# sudo apt-get install python-setuptools

# mkdir python-distribute

# cd python-distribute

# curl -O http://python-distribute.org/distribute_setup.py

# sudo python distribute_setup.py 

# sudo apt-get install python-pip

# sudo pip install dropbox

#######

# Include the Dropbox SDK
import dropbox

# Get your app key and secret from the Dropbox developer website
app_key = #hier 			
app_secret = #hier

flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

# Have the user sign in and authorize this token
#authorize_url = flow.start()
#print '1. Go to: ' + authorize_url
#print '2. Click "Allow" (you might have to log in first)'
#print '3. Copy the authorization code.'
#code = raw_input("Enter the authorization code here: ").strip()

# This will fail if the user enters an invalid authorization code
#access_token, user_id = flow.finish(code)

client = dropbox.client.DropboxClient #und hier
#print 'linked account: ', client.account_info()

f = open('working-draft.txt', 'rb')
response = client.share('/magnum-opus.txt', short_url=True)		
print 'uploaded: ', response

#folder_metadata = client.metadata('/')
#print 'metadata: ', folder_metadata

#f, metadata = client.get_file_and_metadata('/magnum-opus.txt')
#out = open('magnum-opus.txt', 'wb')
#out.write(f.read())
#out.close()

#print metadata