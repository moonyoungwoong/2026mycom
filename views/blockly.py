import streamlit as st
import streamlit.components.v1 as components



def render():
    components.html(
        '<iframe style="border:1px #FFFFFF none" src="https://blockly.games/" title="iFrame" width="100%" height="1024px" scrolling="no" frameborder="no" allow="fullscreen"></iframe>',height=1040
    )