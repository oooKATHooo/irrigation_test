import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from Layout.css_to_streamlit import insert_style, transform_css
from typing import Callable
import json
from pathlib import Path
import os
os.chdir(Path(__file__).parent)


state = st.session_state

css_origin_file = "./Layout/styles_.css"
css_transf_vars = "./Layout/st_styles_test.css"
style_vars = "./Layout/st_style_vars.json"


if "config" not in state:
    transform_css(file_from=css_origin_file,
                file_to=css_transf_vars,
                get_vars=style_vars)
    insert_style(css=css_transf_vars,
                variables=style_vars,
                key="css")

    with open("./config_data.json", mode="r") as f:
        d = json.load(f)
    state.h_sensor = d["h_sensor"]
    state.h_max = d["h_max"]
    state.h_min = d["h_min"]
    state.config = False


with open("./shadow.json", mode="r") as f:
        state.h_act = json.load(f)["h_act"]


def colored_button(label:str,
                   on_click:Callable|None=None,
                   args:tuple|None=None):
    with stylable_container(key="btn_" + label,
                       css_styles=f"""
        button {{   width: 50%; 
            margin-left: 10px;
            margin-bottom:10px;
            
            color: #eee8aa;
            box-shadow: 2px 2px 3px 0px rgb(61, 71, 18);
            background-color: rgb(175, 188, 92);
            border: 0.5px solid rgb(61, 71, 18);
        }}
        """):
        btn = st.button(label,on_click=on_click,args=args)
    return btn


def config_system(h_sensor,h_max,h_min):
    with st.spinner('Werte werden gespeichert.'):
        state.h_sensor = h_sensor
        state.h_max = h_max
        state.h_min = h_min
        
        with open("./config_data.json", mode="r") as f:
            d = json.load(f)
            d["h_sensor"] = h_sensor
            d["h_max"] = h_max
            d["h_min"] = h_min
        with open("../config_data.json", mode="w") as f:
            json.dump(d,f,indent=2)
    state.config = False


def show_data():
    table = f"""|  |  |                                                                                                                                                   
| ---         | ---  |                                                                                                                                                   
| Sensorhöhe: | {state.h_sensor} cm |
| max. Wasserstand: | {state.h_max} cm|
| min. Wasserstand: | {state.h_min} cm|
| akt. Wasserstand: | {state.h_act} cm|"""
    st.markdown(table)


def water_level(height:int=200,
                max_:float = 10.0,
                min_:float = 1.0,
                value:float = 5.0):
    if max_ <= min_:
        return None     # div.st-emotion-cache-xs09jm > div
    value = min(max(value,min_),max_)
    height_bottom = int((value - min_) * height // (max_ - min_))
    height_top = height - height_bottom
    area = st.container()
    with area:
        stylable_container(key="water_top",
                             css_styles=f"""
            *{{  margin-top: 0px;
                margin-bottom: 0px;
                padding-right: 1em;
                border-radius: 1px;
                gap: 0.1px;
                height: {height_top}px;
                background-color: Aquamarine;
                }}
            """)
        stylable_container(key="water_bottom",
                            css_styles=f"""
            *{{  height: {height_bottom}px;
                margin-top: 0px;
                margin-bottom: 0px;
                background-color: MediumBlue;
                border-radius: 1px;
                gap :0px;
                }}""")
        st.container(height=10,border=False)
    return None


def area_for_configuration():
    """Sensor must be at least 20 cm above the maximum water level."""
    with st.container():
        st.write("Bitte gib die verschiedenen Höhen deines Bewässerungssystems ein.")
        h_sensor = st.number_input("Sensorhöhe:",0,180,state.h_sensor,1,)
        h_max = st.number_input("max. Wasserstand:",1,160,state.h_max,1,)
        h_min = st.number_input("min. Wasserstand:",
                            min_value=0,
                            max_value=25,
                            value=state.h_min,
                            step=1)
        if h_min < h_max < h_sensor -20:
            colored_button("Speichern",
                    on_click=config_system,
                    args=(h_sensor,h_max,h_min))


def application():
    st.title("Bewässerung")
    # css-style einfügen:
    box = stylable_container(key="css",
                            css_styles=state.css)
    c0,c1,c2,c3 = st.columns([1,8,4,1])
    with c1:
        show_data()
        btn = colored_button("bearbeiten")
    with c2:
        water_level(220,state.h_max,state.h_min,state.h_act)

    if btn:
        state.config = True
    if state.config:
        with c1:
            area_for_configuration()


application()