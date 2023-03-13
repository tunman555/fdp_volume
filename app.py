import streamlit as st
import json
from fdp_utils import *

st.title("FDP Volume App. 🗺")
st.markdown("""
    **Introduction:** This interactive dashboard is designed for visualization FDP Volume Definition datasets.
    Several open-source packages are used to process the data and generate the visualization""")

st.markdown("### Update the FDP VOLUME dataset by upload file below")

new_datasets = st.file_uploader("Choose ASF file")

row4_col1, row4_col2 = st.columns(2)
with row4_col1:
    if st.button("Update FDP VOLUME.ASF"):
        with open('./tmp/datasets.asf', mode='wb') as w:
            w.write(new_datasets.getvalue())
        update_dataset()
        
        st.write("Dataset's Updated !")
        reload(fdp_utils)

with row4_col2:
    if st.checkbox("Show new datasets"):
        with open('./tmp/sector.json','r') as f:
            sector_json = json.load(f)

        with open('./tmp/fdp_volume.json' , 'r') as f:
            fdp_volume = json.load(f)

        with open('./tmp/layer.json' , 'r') as f:
            layer_json = json.load(f)

    else :
        with open('./src/sector.json','r') as f:
            sector_json = json.load(f)

        with open('./src/fdp_volume.json' , 'r') as f:
            fdp_volume = json.load(f)

        with open('./src/layer.json' , 'r') as f:
            layer_json = json.load(f)

sector_list = list(sector_json.keys())


row1_col1, row1_col2, row1_col3 = st.columns(3)

with row1_col1:
    selected_sector = st.selectbox("Sector", sector_list)
    selected_volume = sector_json[selected_sector]['volume']
    

with row1_col2:
    if selected_sector :
        volume = st.selectbox("Volume",selected_volume)

with row1_col3 :
    show_sector = st.checkbox('Show Sector')

    if show_sector:
        fig = create_sector_plot(selected_sector)
        


row2_col1,row2_col2 = st.columns([6,1])
with row2_col1:
    if show_sector:
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    else:
        fig = create_volume_plot(volume)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with row2_col2:
    if not show_sector :
        selected_layer = fdp_volume[volume]['level']
        box = get_box(selected_layer)
        st.write(f"**Volume:** {volume}")
        st.write(f"**Sector:** {selected_sector}")
        #st.write(f"**Responsibility:** ")
        st.write(f"**Layer:** \n {box[0]} - {box[1]} Ft." )


row3_col1,row3_col2 = st.columns(2)

