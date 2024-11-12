# %%
import streamlit as st

from streamlit_jupyter import StreamlitPatcher, tqdm

StreamlitPatcher().jupyter()  # register streamlit with jupyter-compatible wrappers

st.title("FST Tool Test", anchor=None, help="Help on this FST Tool")

# %%
st.markdown("This tool is for testing Streamlit for FST", unsafe_allow_html=False, help=None)

# %%
# set up authorization and boards access
import requests
import io

auth_token = 'eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_a2h5Elu6Rlw0tzGOr1eTGgTuBC4'

FSdev_teamId = "3458764541999930027" 
FScore_teamId = "3074457355121995573" # https://miro.com/app/settings/company/3074457355121995573/users 

fs_header = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer " + auth_token 
}



# %%
# data for a new board
board_name = 'Name of the board4'
board_description = 'What this board is about'
board_team_ID = FSdev_teamId

# data for which board to use
#board_id = 'uXjVMHvRrew='  # our current test board. We can create as many boards as we like, but can only edit the last 3 under our current dev plan
#board_id = 'uXjVMHku6Ds=' #CMP75
#board_id = 'uXjVMlq2l34=' #gamechangers
#board_id = 'uXjVM3ByY0w=' #Road to Regeneration
#board_id = 'uXjVM3BdvFQ=' #Endless Energy
board_id = 'uXjVLWCtNJQ=' # Miro-FST prototype


# standards for Starting Points
shape_text = "blank starting point"
startingpoint_color = '#33FFF6'
color_white = '#FFFFFF'
color_black = '#000000'
shape_width = 140
shape_height = 120
shape_offset = 0 #10

url = "https://api.miro.com/v2/boards/" + board_id + "/shapes"

MIRO_API_BASE_URL = f'https://api.miro.com/v2/boards/{board_id}'



# %%
'''
This Tool takes a Lab collection or imports a csv file with a collection of Starting Points ("Subjects"), and 
return it as a dataframe `df_startingpoints. Functions below will place each imported starting point as a 
shape (blue hexagon) on Miro, with the name of the subject and hyperlinks to that subject on FST and FS Cards.

The required fields in the csv are:
- ent_name 
- ent_fsid
- frame_name: the name of the frame in Miro where the starting points should be added, e.g. Category 1, Category 2...
- x_col: the column in which the starting point should be placed 
- y_row: the row in which the starting point should be placed 

A dataframe with these fields can also be passed directly to the placement function.

'''


df_startingpoints = ""

# display(uploader)
import pandas as pd
from io import StringIO


# %%
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    # st.write(bytes_data)

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    # st.write(stringio)

    # To read file as string:
    string_data = stringio.read()
    # st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
    df_startingpoints = pd.read_csv(uploaded_file)
    # st.write(df_startingpoints)
    

# %%
# these functions get data from Miro into FST

# get the properties of all the objects on a board
def fs_get_all_object_properties(board_id):
    url = "https://api.miro.com/v2/boards/" + board_id + "/items?limit=50"  #/items?limit=10
    
    response = requests.get(url, headers=fs_header)

    #print(response.text)
    
    pd_object = pd.read_json(response.text, typ='series')
    data_field = pd_object['data']
    df = pd.DataFrame(data_field)
    return df


# get the properties of all the objects on a board
# this is not very useful because it can get max 50 objects at a time.
# there is a way to return the cursor position, and then tile
# through the entire board to get all the objects, 50 at a time


def fs_get_all_frames_on_board(board_id):
    url = "https://api.miro.com/v2/boards/" + board_id + "/items?limit=50&type=frame"  

    response = requests.get(url, headers=fs_header)
       
    pd_object = pd.read_json(response.text, typ='series')
    data_field = pd_object['data']
    df = pd.DataFrame(data_field)
    return df

def get_frames_id_position(df):
    try:   
        # type and title
        df['title'] = df['data'].apply(lambda x: x['title'])
        df['type'] = 'frame'

        # position = maturity (x) and category (y)
        df['x'] = df['position'].apply(lambda x: x['x']).astype('int')
        df['y'] = df['position'].apply(lambda x: x['y']).astype('int')

        df['width'] = df['geometry'].apply(lambda x: x['width']).astype('int')
        df['height'] = df['geometry'].apply(lambda x: x['height']).astype('int')
        
        df['x_left'] = df['x'] - (df['width']/2)
        df['y_top'] = df['y'] - (df['height']/2)

        df['x_left'] = df['x_left'].astype('int')
        df['y_top'] = df['y_top'].astype('int')
        
        df2 = df[['title', 'type', 'x','x_left','y','y_top', 'id']].copy()

    except:
        df2 = df[['title', 'type', 'x','x_left','y','y_top', 'id']].copy()
        
    return df2


# get the properties of all the objects in a frame
def fs_get_all_objects_in_frames_on_board(board_id, frame_id):
    url = "https://api.miro.com/v2/boards/" + board_id + "/items?&limit=50&parent_item_id=" + frame_id #3458764554744189000

    response = requests.get(url, headers=fs_header)
        
    pd_object = pd.read_json(response.text, typ='series')
    data_field = pd_object['data']
    df = pd.DataFrame(data_field)
    
    df2 = df
    
    try:   
        # type and title
        df['title'] = df['data'].apply(lambda x: x['content'])
        df['type'] = df['data'].apply(lambda x: x['shape'])

        # position = maturity (x) and category (y)
        df['x'] = df['position'].apply(lambda x: x['x']).astype('int')
        df['y'] = df['position'].apply(lambda x: x['y']).astype('int')

        # size = impact
        df['width'] = df['geometry'].apply(lambda x: x['width']).astype('int')
        df['height'] = df['geometry'].apply(lambda x: x['height']).astype('int')

        # color and opacity = desirability and probability
        df['color'] = df['style'].apply(lambda x: x['fillColor'])
        df['opacity'] = df['style'].apply(lambda x: x['fillOpacity'])
        
        df2 = df[['title', 'type', 'x','y','width', 'height', 'color', 'opacity', 'id']].copy()

    except:
        df2=[['title', 'type', 'x','y','width', 'height', 'color', 'opacity', 'id']]
        
    return df2

def fs_get_all_connectors_in_frames_on_board(board_id, frame_id):
    url = "https://api.miro.com/v2/boards/" + board_id + "/connectors?&limit=50&parent_item_id=" + frame_id 

    response = requests.get(url, headers=fs_header)
        
    pd_object = pd.read_json(response.text, typ='series')
    data_field = pd_object['data']
    df = pd.DataFrame(data_field)
    
    df_rels = df
    
    try:   
        # source, target, and type
        df['source'] = df['startItem'].apply(lambda x: x['id'])
        df['target'] = df['endItem'].apply(lambda x: x['id'])
        df['relationship_type'] = df['style'].apply(lambda x: x['strokeStyle'])
        
        try:
            df['relationship_text'] = df['captions'].apply(lambda x: x['content'])
        except:
            df['relationship_text'] = "none"

        df_rels = df[['source', 'target', 'relationship_type','relationship_text']].copy()

    except:
        df_rels = [['source', 'target', 'relationship_type','relationship_text']]
        
    return df_rels

# %%
# These functions put things onto Miro from FST



# create a new board
def fs_create_miroboard(board_name, board_description, board_team_ID):

    url = "https://api.miro.com/v2/boards"

    payload = {
        "name": board_name,
        "policy": {
            "permissionsPolicy": {
                "collaborationToolsStartAccess": "all_editors",
                "copyAccess": "anyone",
                "sharingAccess": "team_members_with_editing_rights"
            },
            "sharingPolicy": {
                "access": "private",
                "inviteToAccountAndBoardLinkAccess": "no_access",
                "organizationAccess": "private",
                "teamAccess": "private"
            }
        },
        "description": board_description,
        "teamId": board_team_ID
    }

    response = requests.post(url, json=payload, headers=fs_header)

    st.write(response.text)
    
    
def fs_create_startingpoint(frame_id, ent_name, ent_fsid, x_pos, y_pos, i=0):
        
        # &#9732; is the comet icon 
        # &#128301; is the telescope icon, for FST
        # FS.cards source data is in https://docs.google.com/spreadsheets/d/1W9z2OsIdfngDZlGpYwEAy4jClliaMb1_y6NFXOu_2DI/edit#gid=0
        cards_text_hyperlink = '<a href=\"https://fs.cards/a/' + ent_fsid + '\">&#9732;</a>'
        shape_text_hyperlink = '<a href=\"https://tools.futurity.science/snapshot/' + ent_fsid + '\">&#128301;</a>'
        shape_text_hyperlink = ent_name + '<br />' + shape_text_hyperlink + ' - ' + cards_text_hyperlink
        shape_text = shape_text_hyperlink

        payload = {
            "parent": { "id": frame_id },
            "data": {
                "content": shape_text,
                "shape": "hexagon"
            },
            "style": {
                "color": color_black,
                "fillColor": startingpoint_color,
                "borderColor": color_white,
                "borderOpacity": "0",
                "fillOpacity": "0.5",
                "textAlign": "center",
                "textAlignVertical": "middle"
            },
          "geometry" : {
            "width" : shape_width,
            "height" : shape_height
            },
            "position": {
                "origin": "center",
                "x": x_pos, # + (i * shape_offset),
                "y": y_pos  # + (i * shape_offset)
                
                # in the future, we could get the height and width of the Category Frame, 
                # and calculate the row and column spacing and placement of the 
                # startingpoints based on the area available
             }
        }
     
        response = requests.post(url, json=payload, headers=fs_header)
          
    
    
# create a bunch of starting points

def fs_create_multiple_startingpoints(df):
    
    i=0
    
    shape_list = df['ent_fsid'].tolist()
    
    for i in range(len(shape_list)):
        
        print(i, end=" ")
        
        # get the frame it belongs in and return the location
        frame_name = str(df.loc[i,'frame_name'])
        frame_id = str(df.loc[i,'id'])
        
        ent_name = str(df.loc[i,'ent_name'])
        ent_fsid = str(df.loc[i,'ent_fsid'])
        ent_fsid = ent_fsid[5:]
        
        x_pos = int(df.loc[i, 'x_pos'].item())
        y_pos = int(df.loc[i, 'y_pos'].item()) 
        
        fs_create_startingpoint(frame_id, ent_name, ent_fsid, x_pos, y_pos, i)

        

# %%
def calculate_starting_point_coordinates(df):
# calculate the xy position of each starting point

    shape_list = df['ent_fsid'].tolist()
    for i in range(len(shape_list)):

        x_col = df.loc[i,'x_col']
        y_row = df.loc[i,'y_row']
        x_frame = df.loc[i,'x_left']
        y_frame = df.loc[i,'y_top']
        
        x_pos = (x_col * shape_width) + shape_offset
        y_pos = (y_row * shape_height) + shape_offset

        df.loc[i,'x_pos'] = x_pos
        df.loc[i,'y_pos'] = y_pos

    return df


# %%
def fs_populate_startingpoints_on_miro(board_id, df_startingpoints):
    # get all frames on board
    frameslist = fs_get_all_frames_on_board(board_id)

    # get name, ID, x, and y for category frames
    framesinfo = get_frames_id_position(frameslist)

    framesinfo['title'] = framesinfo['title'].astype(str)
    df_startingpoints['frame_name'] = df_startingpoints['frame_name'].astype(str)

    # match category frame names to IDs and append them to the startingpoints
    df_points_and_frames = pd.merge(df_startingpoints, framesinfo, left_on='frame_name', right_on='title', how='inner')
    df_points_and_frames = df_points_and_frames.rename(columns={"x": "x_frame", "y": "y_frame"})

    df_positions = calculate_starting_point_coordinates(df_points_and_frames)

    print("Placing Starting Points on board "+ board_id)
    
    fs_create_multiple_startingpoints(df_positions)

    st.write(" ")
    st.write("Starting Points placed on board "+ board_id)

# %%
#st.button("Send Starting Points", type="primary")
if st.button("Send Starting Points"):
    fs_populate_startingpoints_on_miro(board_id, df_startingpoints)
else:
    st.write("Waiting to send Starting Points")




