import streamlit as st
from streamlit import session_state as ss
from my_crew import MyCrew
import db_utils
from i18n import t

class PageCrews:
    def __init__(self):
        self.name = t("page.crews")

    def create_crew(self):
        crew = MyCrew()
        if 'crews' not in ss:
            ss.crews = [MyCrew]
        ss.crews.append(crew)
        crew.edit = True
        db_utils.save_crew(crew)  # Save crew to database
        return crew

    def draw(self):
        with st.container():
            st.subheader(self.name)
            editing = False
            if 'crews' not in ss:
                ss.crews = db_utils.load_crews()  # Load crews from database
            for crew in ss.crews:
                crew.draw()
                if crew.edit:
                    editing = True
            if len(ss.crews) == 0:
                st.write(t("crew.none_defined"))
            st.button(t("button.create_crew"), on_click=self.create_crew, disabled=editing)
