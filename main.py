import json

import streamlit as st
import altair as alt
import api
import dataframes
import utils
import pandas as pd


def main():
    try:
        df = dataframes.load_im_elo_progression_blitz()
        st_correlation = utils.get_streamer_correlation(dataframes.load_im_individual_2023(),
                                                        "blitz", 3000)
        gm_loss = utils.plot_result_reasons(dataframes.load_gm_individual_2023(), "bullet", "loss")
        gm_draw = utils.plot_result_reasons(dataframes.load_gm_individual_2023(), "bullet", "draw")

        gm_opening_results = dataframes.load_gm_opening_results_2023_bullet()
        fm_opening_results = dataframes.load_fm_opening_results_2023_bullet()

        gm_scatterplot = utils.win_rate_accuracy_scatterplot(dataframes.load_gm_individual_2023())
        fm_scatterplot = utils.win_rate_accuracy_scatterplot(dataframes.load_fm_individual_2023())

        st.title('International Masters Elo Ratings Over Time')

        players = st.multiselect("Choose players", df["Player"].unique(), ["gothamchess", "anna_chess", "imrosen"])
        if not players:
            st.error("Please select at least one player.")
        else:
            data = df[df["Player"].isin(players)].reset_index()

            st.write("Elo Table 2017 - 2021", data)

            data = data.drop(columns=['index'])

            data = data.melt(id_vars=["Player"], var_name="Year", value_name="Elo")
            data['Year'] = data['Year'].astype(str)

            chart = (
                alt.Chart(data)
                .mark_line(opacity=0.8)
                .encode(
                    x=alt.X('Year:O', axis=alt.Axis(title='Year')),
                    y=alt.Y('Elo:Q', axis=alt.Axis(title='Elo Rating')),
                    color='Player:N',
                    tooltip=["Player", "Year", "Elo"]
                )
            )
            st.altair_chart(chart, use_container_width=True)
            st.title("Result reasons GMs Bullet 2023")

            left, col4, right = st.columns([1, 5, 1])
            with col4:
                st.pyplot(gm_loss)
                st.pyplot(gm_draw)

            st.title("Correlation of Titled Streamer and Win Rate")

            col7, col8 = st.columns([3, 2])

            with col7:
                st.pyplot(st_correlation[0])

            with col8:

                st.markdown("### Statistische Werte")
                st.markdown(f"**Korrelationskoeffizient (R):** `{st_correlation[1]:.3f}`")
                st.markdown(f"**P-Wert:** `{st_correlation[2]:.3f}`")

                st.markdown("""
                *Leichte positive Korrelation mit statistischer Signifikanz.*
                """)

            st.title("Opening Categories and Result: GM vs FM")
            left, col7, right = st.columns([2, 2, 2])

            with left:
                st.write(gm_opening_results[0])
                st.write(fm_opening_results[0])
            with col7:
                st.write(gm_opening_results[1])
                st.write(fm_opening_results[1])
            with right:
                st.write(gm_opening_results[2])
                st.write(fm_opening_results[2])

            st.title("Correlation of Accuracy and Win %: GM vs FM")
            col11, col12 = st.columns(2)
            with col11:
                st.pyplot(gm_scatterplot)
            with col12:
                st.pyplot(fm_scatterplot)


    except Exception as e:
        st.error(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
