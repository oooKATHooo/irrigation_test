import streamlit as st
import json
import os
from pathlib import Path
os.chdir(Path(__file__).parent)

if __name__ == "__main__":
    state = {}
else:
    state = st.session_state


def transform_css(file_from:Path,
                file_to:Path="./Layout/css_string.txt",
                get_vars:Path|None=None) -> None:
    """transform a css-file with global variables to a string
    usable in streamlit and save it. If a path (.json) for
    get_vars is given, the global variables will be saved in this
    json-file. They can be changed and later merged with the string
    using the function 'insert_style'.  
    If no get_vars is given, the function 'transform_css' will
    immediately insert the global variables to the appropriate places.
    """
    with open(file_from,mode="r") as f:
        style = f.read()

    # extract global variables:
    vars = {}
    r = style.find(":root")
    if r>=0:
        with_vars = True
        
        m = style.find("{",r)
        n = style.find("}",m) + 1
        style_vars = style[m+1:n].split(";")
        for el in style_vars:
            el_ = el.split(":")
            if len(el_) == 2:
                el_[0] = el_[0].strip()
                vars[el_[0][2:]] = el_[1]
    else:
        with_vars = False
        n = -1

    # transform css-string:
    style = style[n+1:]
    style = style.replace(";\n",";\n    ").replace("}","}}\n")
    style = style.replace("{"," {{").replace(":",": ")
    
    # insert names or values of global variables into css-string:
    if with_vars:
        for name,value in vars.items():
            var_from = "var(--" + name + ")"

            if get_vars:
                var_to = "{" + name + "}"
                style = style.replace(var_from,var_to)               
            else:
                style = style.replace(var_from,value)
                    
    if get_vars:
        with open(get_vars, mode="w") as f:
            json.dump(vars,f,indent=2)

    with open(file_to, mode="w") as f:
        f.write(style)
    return None


def insert_style(css:Path,
                 variables:Path|None,
                 key:str|int=0) -> None:
    """Add transformed css string to st.session_state.
    If global variables need to be inserted from a json file,
    the path will be specified under 'variables'.
    To get access to the css string use string-format of
    your 'key'-argument as st.session_state key."""
    k = str(key)
    
    # load css:
    with open(css,mode="r") as f:
        string = f.read()
    
    if variables:
        # load global variables:
        with open(variables, mode="r") as f:
            vars = json.load(f)
        
        # insert variables into string:
        css = string.format(**vars)
    
    else:
        css = string.format()
    
    # add css-string to st.session_state:
    state[k] = css
    return None

if __name__ == "__main__":

    def example(with_variables:bool) -> str:
        if with_variables:
            transform_css(file_from="./styles.css",
                          file_to=  "./st_styles_var.css",
                          get_vars= "./st_variable_values.json")
            insert_style(css="./st_styles_var.css",
                          variables="./st_variable_values.json",
                          key=1)
        else:
            transform_css(file_from="./styles.css",
                        file_to=  "./st_styles_quick.css",
                        get_vars=None)
            insert_style(css="./st_styles_quick.css",
                        variables=None,
                        key=1)
        return

    example(with_variables=True)
    preview = state["1"][:100]
    print(preview)
