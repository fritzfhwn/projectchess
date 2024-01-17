import streamlit as st
import altair as alt
from pickle_loaders import DataImporter
from data_visualizer import Visualizer


def main():
    try:
        df = DataImporter.load_elo_progression("im", "blitz")
        st_correlation = Visualizer.get_streamer_correlation(DataImporter.load_data("im", 2023, "individual"),
                                                        "blitz", 3000)
        gm_loss = Visualizer.plot_result_reasons(DataImporter.load_data("gm", 2023, "individual"), "bullet", "loss")
        gm_draw = Visualizer.plot_result_reasons(DataImporter.load_data("gm", 2023, "individual"), "bullet", "draw")

        gm_opening_results = DataImporter.load_opening_results("gm", "bullet", 2023)
        fm_opening_results = DataImporter.load_opening_results("fm", "bullet", 2023)

        gm_scatterplot = Visualizer.win_rate_accuracy_scatterplot(DataImporter.load_data("gm", 2023, "individual"))
        fm_scatterplot = Visualizer.win_rate_accuracy_scatterplot(DataImporter.load_data("fm", 2023, "individual"))

        st.title('International Masters Elo Ratings in Blitz Over Time')

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
                *Leichte positive Korrelation.*
                """)

            st.title("Opening Categories and Result in Bullet: GM vs FM")
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

            st.title("Correlation of Accuracy and Win % in Blitz: GM vs FM")
            col11, col12 = st.columns(2)
            with col11:
                st.pyplot(gm_scatterplot[0])
            with col12:
                st.pyplot(fm_scatterplot[0])

            veryleft, left, col13, right = st.columns([1, 1, 2, 1])

            with left:
                st.write(gm_scatterplot[1].round(2))
                st.write(gm_scatterplot[2].round(2))
                st.write(gm_scatterplot[3].round(2))
                st.write(gm_scatterplot[4].round(2))
            with col13:
                st.markdown(f"**Win % - Standardabweichung**")
                st.markdown(f"**Win % - Mittelwert**")
                st.markdown(f"**Accuracy - Standardabweichung**")
                st.markdown(f"**Accuracy - Mittelwert**")
            with right:
                st.write(fm_scatterplot[1].round(2))
                st.write(fm_scatterplot[2].round(2))
                st.write(fm_scatterplot[3].round(2))
                st.write(fm_scatterplot[4].round(2))


    except Exception as e:
        st.error(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
